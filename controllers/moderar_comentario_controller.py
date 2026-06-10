"""
Controlador — CU-13 Moderar comentarios en fotos propias
Patrón MVC: «controller»
Responsabilidad: verificar propiedad de la foto y coordinar
la eliminación del comentario.
"""

from models.repositorios import RepositorioFoto, RepositorioComentario
from infrastructure.errores import ErrorNegocio, ErrorAcceso
from infrastructure.logger import Logger


class ModerarComentarioController:
    """
    Controlador MVC para el caso de uso CU-13.
    Verifica que el usuario es propietario de la foto antes
    de permitir la eliminación del comentario.
    """

    def __init__(self):
        self._repo_foto = RepositorioFoto()
        self._repo_comentario = RepositorioComentario()
        self._logger = Logger()

    def eliminar_comentario(self, usuario_id: int, foto_id: int,
                            comentario_id: int) -> dict:
        """
        Flujo principal del CU-13.

        Pasos según diagrama de colaboración:
        4. Recibir solicitud de eliminación
        5. Verificar que el usuario es propietario de la foto
        6. Confirmar propiedad
        7. Obtener comentarios de la foto
        8. Retornar comentarios
        9. Eliminar el comentario
        10. Confirmado
        11. Retornar resultado

        Args:
            usuario_id: ID del usuario que realiza la moderación
            foto_id: ID de la foto que contiene el comentario
            comentario_id: ID del comentario a eliminar

        Returns:
            dict con ok=True si fue exitoso, ok=False con mensaje de error
        """
        try:
            # Paso 5: Verificar que el usuario es propietario de la foto
            foto = self._repo_foto.obtener(foto_id)

            # Flujo alternativo 5a: no es propietario → mostrar error
            if not foto.es_propietario(usuario_id):
                raise ErrorAcceso(
                    "No tenés permiso para moderar comentarios en esta foto. "
                    "Solo el propietario puede eliminar comentarios."
                )

            # Paso 7: Verificar que el comentario pertenece a esta foto
            comentario = self._repo_comentario.obtener(comentario_id)
            if comentario.foto_id != foto_id:
                raise ErrorNegocio("El comentario no pertenece a esta foto.")

            # Paso 9: Eliminar el comentario
            self._repo_comentario.eliminar(comentario_id)

            # Registrar en log
            self._logger.registrar(
                "ELIMINAR_COMENTARIO",
                f"Propietario {usuario_id} eliminó comentario {comentario_id} de foto {foto_id}",
                usuario_id
            )

            return {"ok": True, "mensaje": "Comentario eliminado correctamente."}

        except ErrorAcceso as e:
            return {"ok": False, "acceso_denegado": True, "mensaje": str(e)}
        except ErrorNegocio as e:
            return {"ok": False, "mensaje": str(e)}

    def obtener_comentarios(self, usuario_id: int, foto_id: int) -> dict:
        """
        Obtiene los comentarios de una foto.
        Paso 7-8 del diagrama de colaboración.

        Returns:
            dict con ok=True, lista de comentarios y flag es_propietario
        """
        try:
            foto = self._repo_foto.obtener(foto_id)
            comentarios = self._repo_comentario.listar_de_foto(foto_id)
            es_propietario = foto.es_propietario(usuario_id)

            return {
                "ok": True,
                "comentarios": comentarios,
                "es_propietario": es_propietario,
                "foto": foto
            }

        except ErrorNegocio as e:
            return {"ok": False, "mensaje": str(e)}
