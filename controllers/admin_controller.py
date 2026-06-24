"""
Controlador — CU-18 Deshabilitar usuario / CU-19 Eliminar comentario inapropiado
Responsabilidad: operaciones administrativas sobre usuarios y contenido.
Solo accesible por usuarios con rol es_admin = 1.
"""

from models.gestion_usuarios import GestionUsuarios
from models.repositorios import RepositorioComentario
from infrastructure.persistencia import Persistencia
from infrastructure.errores import ErrorNegocio, ErrorAcceso
from infrastructure.logger import Logger


class AdminController:
    """
    Controlador para el panel de administración.
    Todas las operaciones validan que el actor tenga rol administrador
    antes de ejecutar cualquier acción.
    """

    def __init__(self):
        self._gestion = GestionUsuarios()
        self._repo_comentario = RepositorioComentario()
        self._db = Persistencia().obtener_conexion()
        self._logger = Logger()

    def _verificar_admin(self, admin_id: int):
        """Lanza ErrorAcceso si el usuario no es administrador."""
        row = self._db.execute(
            "SELECT es_admin FROM usuario WHERE id = ?", (admin_id,)
        ).fetchone()
        if not row or not row["es_admin"]:
            raise ErrorAcceso("Acceso denegado: se requieren permisos de administrador.")

    def listar_usuarios(self, admin_id: int) -> dict:
        """
        Devuelve todos los usuarios del sistema para el panel admin.
        Precondición: admin_id debe tener rol administrador.
        """
        try:
            self._verificar_admin(admin_id)
            rows = self._db.execute(
                "SELECT id, nombre, apellido, email, habilitado, es_admin FROM usuario ORDER BY apellido, nombre"
            ).fetchall()
            usuarios = [dict(r) for r in rows]
            return {"ok": True, "usuarios": usuarios}
        except (ErrorAcceso, ErrorNegocio) as e:
            return {"ok": False, "mensaje": str(e)}

    def deshabilitar_usuario(self, admin_id: int, usuario_id: int) -> dict:
        """
        Flujo principal CU-18: deshabilita la cuenta de un usuario,
        impidiendo que pueda iniciar sesión.
        Flujo alternativo: si el admin cancela, no se realiza ningún cambio
        (la confirmación se maneja en la vista).
        """
        try:
            self._verificar_admin(admin_id)

            if admin_id == usuario_id:
                raise ErrorNegocio("No podés deshabilitar tu propia cuenta.")

            row = self._db.execute(
                "SELECT id, nombre, apellido, habilitado FROM usuario WHERE id = ?",
                (usuario_id,)
            ).fetchone()
            if not row:
                raise ErrorNegocio("El usuario no existe.")
            if not row["habilitado"]:
                raise ErrorNegocio("El usuario ya se encuentra deshabilitado.")

            self._db.execute(
                "UPDATE usuario SET habilitado = 0 WHERE id = ?", (usuario_id,)
            )
            self._db.commit()

            self._logger.registrar(
                "DESHABILITAR_USUARIO",
                f"Admin {admin_id} deshabilitó al usuario {usuario_id} "
                f"({row['nombre']} {row['apellido']})",
                admin_id
            )
            return {
                "ok": True,
                "mensaje": f"Usuario {row['nombre']} {row['apellido']} deshabilitado correctamente."
            }
        except (ErrorAcceso, ErrorNegocio) as e:
            return {"ok": False, "mensaje": str(e)}

    def habilitar_usuario(self, admin_id: int, usuario_id: int) -> dict:
        """Rehabilita una cuenta previamente deshabilitada."""
        try:
            self._verificar_admin(admin_id)
            row = self._db.execute(
                "SELECT id, nombre, apellido FROM usuario WHERE id = ?", (usuario_id,)
            ).fetchone()
            if not row:
                raise ErrorNegocio("El usuario no existe.")

            self._db.execute(
                "UPDATE usuario SET habilitado = 1 WHERE id = ?", (usuario_id,)
            )
            self._db.commit()
            self._logger.registrar(
                "HABILITAR_USUARIO",
                f"Admin {admin_id} habilitó al usuario {usuario_id}",
                admin_id
            )
            return {"ok": True,
                    "mensaje": f"Usuario {row['nombre']} {row['apellido']} habilitado."}
        except (ErrorAcceso, ErrorNegocio) as e:
            return {"ok": False, "mensaje": str(e)}

    def listar_comentarios(self, admin_id: int) -> dict:
        """
        Devuelve todos los comentarios del sistema para moderación (CU-19).
        """
        try:
            self._verificar_admin(admin_id)
            rows = self._db.execute(
                """SELECT c.id, c.contenido, c.fecha_creacion,
                          u.nombre || ' ' || u.apellido AS autor,
                          f.id AS foto_id
                   FROM comentario c
                   JOIN usuario u ON u.id = c.autor_id
                   JOIN foto f    ON f.id = c.foto_id
                   ORDER BY c.fecha_creacion DESC"""
            ).fetchall()
            return {"ok": True, "comentarios": [dict(r) for r in rows]}
        except (ErrorAcceso, ErrorNegocio) as e:
            return {"ok": False, "mensaje": str(e)}

    def eliminar_comentario_inapropiado(self, admin_id: int,
                                         comentario_id: int) -> dict:
        """
        Flujo principal CU-19: elimina un comentario inapropiado
        y deja un aviso visible en su lugar.
        """
        try:
            self._verificar_admin(admin_id)
            row = self._db.execute(
                "SELECT id FROM comentario WHERE id = ?", (comentario_id,)
            ).fetchone()
            if not row:
                raise ErrorNegocio("El comentario no existe.")

            aviso = "[Este comentario fue eliminado por un administrador]"
            self._db.execute(
                "UPDATE comentario SET contenido = ?, eliminado_por_admin = 1 WHERE id = ?",
                (aviso, comentario_id)
            )
            self._db.commit()
            self._logger.registrar(
                "ELIMINAR_COMENTARIO_ADMIN",
                f"Admin {admin_id} eliminó comentario {comentario_id}",
                admin_id
            )
            return {"ok": True, "mensaje": "Comentario eliminado correctamente."}
        except (ErrorAcceso, ErrorNegocio) as e:
            return {"ok": False, "mensaje": str(e)}