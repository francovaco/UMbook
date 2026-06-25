"""
Controlador — CU-12 Comentar fotos
Responsabilidad: publicar, editar y eliminar comentarios propios,
con verificación de permisos de grupo.
"""
from models.repositorios import RepositorioFoto, RepositorioComentario, RepositorioAmistad, RepositorioGrupo
from models.entidades import Comentario
from infrastructure.errores import ErrorValidacion, ErrorAcceso, ErrorNegocio


class ComentarFotoController:

    def __init__(self):
        self._repo_foto = RepositorioFoto()
        self._repo_comentario = RepositorioComentario()
        self._repo_amistad = RepositorioAmistad()
        self._repo_grupo = RepositorioGrupo()

    def puede_comentar(self, usuario_id: int, foto_id: int) -> bool:
        """
        Flujo 2a: verifica si el usuario tiene permiso para comentar.
        - Dueño de la foto: siempre puede.
        - Amigo del dueño en un grupo con comentar_fotos=True: puede.
        - Cualquier otro caso: no puede.
        """
        foto = self._repo_foto.obtener(foto_id)
        if foto.propietario == usuario_id:
            return True
        if not self._repo_amistad.obtener_entre(usuario_id, foto.propietario):
            return False
        grupos = self._repo_grupo.listar_de_usuario(foto.propietario)
        for grupo in grupos:
            if usuario_id in grupo.miembros:
                permisos = self._repo_grupo.obtener_permisos(grupo.id)
                if permisos.comentar_fotos:
                    return True
        return False

    def publicar(self, usuario_id: int, foto_id: int, contenido: str) -> dict:
        """
        Flujo principal: publica un comentario en una foto.
        Flujo 3a: valida que el comentario no esté vacío.
        Flujo 2a: verifica permiso antes de publicar.
        """
        try:
            if not contenido or not contenido.strip():
                raise ErrorValidacion("El comentario no puede estar vacío.")
            if not self.puede_comentar(usuario_id, foto_id):
                raise ErrorAcceso("No tenés permiso para comentar en esta foto.")
            comentario = self._repo_comentario.guardar(
                Comentario(autor_id=usuario_id, foto_id=foto_id, contenido=contenido.strip())
            )
            return {"ok": True, "mensaje": "Comentario publicado.", "comentario": comentario}
        except (ErrorValidacion, ErrorAcceso, ErrorNegocio) as e:
            return {"ok": False, "mensaje": str(e)}

    def editar(self, usuario_id: int, comentario_id: int, nuevo_contenido: str) -> dict:
        """
        Flujo 4a: el autor edita su propio comentario.
        """
        try:
            if not nuevo_contenido or not nuevo_contenido.strip():
                raise ErrorValidacion("El comentario no puede estar vacío.")
            comentario = self._repo_comentario.obtener(comentario_id)
            if comentario.autor_id != usuario_id:
                raise ErrorAcceso("Solo podés editar tus propios comentarios.")
            self._repo_comentario.actualizar(comentario_id, nuevo_contenido.strip())
            return {"ok": True, "mensaje": "Comentario actualizado."}
        except (ErrorValidacion, ErrorAcceso, ErrorNegocio) as e:
            return {"ok": False, "mensaje": str(e)}

    def eliminar_propio(self, usuario_id: int, comentario_id: int) -> dict:
        """
        Flujo 4b: el autor elimina su propio comentario.
        """
        try:
            comentario = self._repo_comentario.obtener(comentario_id)
            if comentario.autor_id != usuario_id:
                raise ErrorAcceso("Solo podés eliminar tus propios comentarios.")
            foto_id = comentario.foto_id
            self._repo_comentario.eliminar(comentario_id)
            return {"ok": True, "mensaje": "Comentario eliminado.", "foto_id": foto_id}
        except (ErrorAcceso, ErrorNegocio) as e:
            return {"ok": False, "mensaje": str(e)}
