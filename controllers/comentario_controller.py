"""
Controlador — CU-12 Comentar fotos
Clase: ComentarioController «controller»
"""
from models.repositorios import RepositorioFoto, RepositorioComentario, RepositorioAmistad, RepositorioGrupo
from models.entidades import Comentario
from infrastructure.errores import ErrorValidacion, ErrorAcceso, ErrorNegocio


class ComentarioController:

    def __init__(self, idUsuario: int):
        self.idUsuario = idUsuario
        self._repo_foto = RepositorioFoto()
        self._repo_comentario = RepositorioComentario()
        self._repo_amistad = RepositorioAmistad()
        self._repo_grupo = RepositorioGrupo()

    def publicarComentario(self, idFoto: int, texto: str) -> dict:
        """
        Flujo principal: publica un comentario en una foto.
        Flujo 3a: valida que el comentario no esté vacío.
        Flujo 2a: verifica permiso antes de publicar.
        """
        try:
            self.validarTexto(texto)
            if not self.verificarPermiso(self.idUsuario, idFoto):
                raise ErrorAcceso("No tenés permiso para comentar en esta foto.")
            comentario = self._repo_comentario.guardar(
                Comentario(autor_id=self.idUsuario, foto_id=idFoto, contenido=texto.strip())
            )
            return self.retornarResultado(True, "Comentario publicado.", comentario=comentario)
        except (ErrorValidacion, ErrorAcceso, ErrorNegocio) as e:
            return self.retornarResultado(False, str(e))

    def verificarPermiso(self, idUsuario: int, idFoto: int) -> bool:
        """
        Flujo 2a: verifica si el usuario tiene permiso para comentar.
        - Dueño de la foto: siempre puede.
        - Amigo del dueño en un grupo con comentar_fotos=True: puede.
        - Cualquier otro caso: no puede.
        """
        foto = self._repo_foto.obtener(idFoto)
        if foto.propietario == idUsuario:
            return True
        if not self._repo_amistad.obtener_entre(idUsuario, foto.propietario):
            return False
        grupos = self._repo_grupo.listar_de_usuario(foto.propietario)
        for grupo in grupos:
            if idUsuario in grupo.miembros:
                permisos = self._repo_grupo.obtener_permisos(grupo.id)
                if permisos.comentar_fotos:
                    return True
        return False

    def validarTexto(self, texto: str) -> bool:
        if not texto or not texto.strip():
            raise ErrorValidacion("El comentario no puede estar vacío.")
        return True

    def editarComentario(self, idComentario: int, texto: str) -> dict:
        """Flujo 4a: el autor edita su propio comentario."""
        try:
            self.validarTexto(texto)
            comentario = self._repo_comentario.obtener(idComentario)
            if comentario.autor_id != self.idUsuario:
                raise ErrorAcceso("Solo podés editar tus propios comentarios.")
            comentario.editar(texto)
            self._repo_comentario.actualizar(idComentario, comentario.contenido)
            return self.retornarResultado(True, "Comentario actualizado.")
        except (ErrorValidacion, ErrorAcceso, ErrorNegocio) as e:
            return self.retornarResultado(False, str(e))

    def eliminarComentario(self, idComentario: int) -> dict:
        """Flujo 4b: el autor elimina su propio comentario."""
        try:
            comentario = self._repo_comentario.obtener(idComentario)
            if comentario.autor_id != self.idUsuario:
                raise ErrorAcceso("Solo podés eliminar tus propios comentarios.")
            foto_id = comentario.foto_id
            comentario.eliminar()
            self._repo_comentario.eliminar(idComentario)
            return self.retornarResultado(True, "Comentario eliminado.", foto_id=foto_id)
        except (ErrorAcceso, ErrorNegocio) as e:
            return self.retornarResultado(False, str(e))

    def retornarResultado(self, ok: bool, mensaje: str = "", **extra) -> dict:
        resultado = {"ok": ok, "mensaje": mensaje}
        resultado.update(extra)
        return resultado
