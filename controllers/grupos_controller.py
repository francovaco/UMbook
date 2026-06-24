"""
Controlador — CU-08 Gestionar grupos de amigos / CU-09 Configurar permisos por grupo
Responsabilidad: coordinar la creación, edición, eliminación de grupos,
asignación de miembros y configuración de permisos por grupo.
"""

from models.gestion_usuarios import GestionUsuarios
from models.repositorios import RepositorioAmistad, RepositorioGrupo
from models.entidades import GrupoPermiso
from infrastructure.errores import ErrorNegocio, ErrorAcceso
from infrastructure.logger import Logger


class GruposController:
    """
    Controlador unificado para CU-08 y CU-09.
    Todas las operaciones verifican que el usuario sea propietario
    del grupo antes de permitir cualquier modificación.
    """

    def __init__(self):
        self._gestion = GestionUsuarios()
        self._repo_grupo = RepositorioGrupo()
        self._repo_amistad = RepositorioAmistad()
        self._logger = Logger()

    # ══════════════════════════════════════════════
    # CU-08 — Gestionar grupos
    # ══════════════════════════════════════════════

    def listar_grupos(self, propietario_id: int) -> dict:
        """
        Devuelve todos los grupos del usuario con sus miembros
        y los permisos de cada uno, más la lista de amigos disponibles
        para asignar a grupos.
        """
        try:
            grupos = self._repo_grupo.listar_de_usuario(propietario_id)

            # Enriquecer cada grupo con datos de miembros y permisos
            grupos_enriquecidos = []
            for grupo in grupos:
                miembros_data = []
                for uid in grupo.miembros:
                    try:
                        u = self._gestion.obtener_por_id(uid)
                        miembros_data.append(u)
                    except ErrorNegocio:
                        continue
                permisos = self._repo_grupo.obtener_permisos(grupo.id)
                grupos_enriquecidos.append({
                    "grupo": grupo,
                    "miembros": miembros_data,
                    "permisos": permisos,
                })

            # Lista de amigos del usuario para el formulario de asignación
            amistades = self._repo_amistad.listar_de_usuario(propietario_id)
            amigos = []
            for a in amistades:
                otro_id = (a.usuario_destino
                           if a.usuario_origen == propietario_id
                           else a.usuario_origen)
                try:
                    amigos.append(self._gestion.obtener_por_id(otro_id))
                except ErrorNegocio:
                    continue

            return {"ok": True, "grupos": grupos_enriquecidos, "amigos": amigos}

        except Exception as e:
            return {"ok": False, "mensaje": str(e)}

    def crear_grupo(self, propietario_id: int, nombre: str) -> dict:
        """
        Flujo principal CU-08: crea un nuevo grupo con nombre.
        Flujo alternativo: si el nombre está vacío, retorna error.
        """
        try:
            if not nombre or not nombre.strip():
                raise ErrorNegocio("El nombre del grupo es obligatorio.")
            grupo = self._repo_grupo.crear(propietario_id, nombre)
            self._logger.registrar(
                "CREAR_GRUPO",
                f"Usuario {propietario_id} creó el grupo '{nombre}'",
                propietario_id
            )
            return {"ok": True, "grupo": grupo,
                    "mensaje": f"Grupo '{grupo.nombre}' creado correctamente."}
        except ErrorNegocio as e:
            return {"ok": False, "mensaje": str(e)}

    def renombrar_grupo(self, propietario_id: int, grupo_id: int,
                        nuevo_nombre: str) -> dict:
        """Edita el nombre de un grupo existente (CU-08, paso 5)."""
        try:
            self._repo_grupo.renombrar(grupo_id, propietario_id, nuevo_nombre)
            self._logger.registrar(
                "EDITAR_GRUPO",
                f"Usuario {propietario_id} renombró grupo {grupo_id} a '{nuevo_nombre}'",
                propietario_id
            )
            return {"ok": True, "mensaje": "Nombre actualizado correctamente."}
        except ErrorNegocio as e:
            return {"ok": False, "mensaje": str(e)}

    def eliminar_grupo(self, propietario_id: int, grupo_id: int) -> dict:
        """
        Elimina el grupo y sus permisos en cascada (CU-08, paso 5).
        Flujo alternativo CU-08: si se elimina un grupo, los permisos
        asociados se eliminan también.
        """
        try:
            grupo = self._repo_grupo.obtener(grupo_id)
            nombre = grupo.nombre
            self._repo_grupo.eliminar(grupo_id, propietario_id)
            self._logger.registrar(
                "ELIMINAR_GRUPO",
                f"Usuario {propietario_id} eliminó grupo '{nombre}'",
                propietario_id
            )
            return {"ok": True,
                    "mensaje": f"Grupo '{nombre}' eliminado. Sus permisos fueron removidos."}
        except ErrorNegocio as e:
            return {"ok": False, "mensaje": str(e)}

    def actualizar_miembros(self, propietario_id: int, grupo_id: int,
                             amigo_ids: list) -> dict:
        """
        Asigna o reemplaza los miembros de un grupo (CU-08, pasos 3-4).
        Solo se pueden asignar usuarios que sean amigos del propietario.
        """
        try:
            # Verificar que todos los IDs sean amigos reales
            amistades = self._repo_amistad.listar_de_usuario(propietario_id)
            amigos_ids_validos = set()
            for a in amistades:
                otro = (a.usuario_destino
                        if a.usuario_origen == propietario_id
                        else a.usuario_origen)
                amigos_ids_validos.add(otro)

            ids_validos = [uid for uid in amigo_ids if uid in amigos_ids_validos]
            self._repo_grupo.actualizar_miembros(grupo_id, propietario_id, ids_validos)
            self._logger.registrar(
                "ACTUALIZAR_MIEMBROS",
                f"Usuario {propietario_id} actualizó miembros del grupo {grupo_id}",
                propietario_id
            )
            return {"ok": True, "mensaje": "Miembros actualizados correctamente."}
        except ErrorNegocio as e:
            return {"ok": False, "mensaje": str(e)}

    # ══════════════════════════════════════════════
    # CU-09 — Configurar permisos por grupo
    # ══════════════════════════════════════════════

    def configurar_permisos(self, propietario_id: int, grupo_id: int,
                             ver_albumes: bool, comentar_fotos: bool,
                             escribir_muro: bool) -> dict:
        """
        Flujo principal CU-09: define qué acciones puede realizar el grupo.
        Precondición: el grupo debe existir y pertenecer al propietario.
        Flujo alternativo: si no se asigna ningún permiso, los miembros
        no podrán realizar acciones (todos en False).
        """
        try:
            grupo = self._repo_grupo.obtener(grupo_id)
            if grupo.propietario != propietario_id:
                raise ErrorAcceso("No tenés permiso para configurar este grupo.")

            permisos = GrupoPermiso(
                grupo_id=grupo_id,
                ver_albumes=ver_albumes,
                comentar_fotos=comentar_fotos,
                escribir_muro=escribir_muro
            )
            self._repo_grupo.guardar_permisos(permisos)
            self._logger.registrar(
                "CONFIGURAR_PERMISOS",
                f"Usuario {propietario_id} configuró permisos del grupo {grupo_id}",
                propietario_id
            )
            return {"ok": True, "mensaje": "Permisos guardados correctamente."}
        except (ErrorNegocio, ErrorAcceso) as e:
            return {"ok": False, "mensaje": str(e)}