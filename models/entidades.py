"""
Capa de modelos — Entities: Amistad, Foto, Comentario
"""

from datetime import datetime


class Amistad:
    """
    Representa el vínculo de amistad entre dos usuarios.
    Entidad persistente con ciclo de vida propio.
    """

    def __init__(self, id: int = None, usuario_origen: int = None,
                 usuario_destino: int = None, fecha_creacion: str = None):
        self._id = id
        self._usuario_origen = usuario_origen
        self._usuario_destino = usuario_destino
        self._fecha_creacion = fecha_creacion or datetime.now().strftime("%Y-%m-%d")

    @property
    def id(self) -> int:
        return self._id

    @property
    def usuario_origen(self) -> int:
        return self._usuario_origen

    @property
    def usuario_destino(self) -> int:
        return self._usuario_destino

    @property
    def fecha_creacion(self) -> str:
        return self._fecha_creacion

    def involucra(self, usuario_id: int) -> bool:
        """Indica si un usuario participa en esta amistad."""
        return self._usuario_origen == usuario_id or self._usuario_destino == usuario_id

    def __repr__(self) -> str:
        return f"Amistad(id={self._id}, origen={self._usuario_origen}, destino={self._usuario_destino})"


class Foto:
    """
    Representa una foto subida por un usuario en un álbum.
    """

    def __init__(self, id: int = None, propietario: int = None,
                 album_id: int = None, url_imagen: str = "",
                 fecha_subida: str = None):
        self._id = id
        self._propietario = propietario
        self._album_id = album_id
        self._url_imagen = url_imagen
        self._fecha_subida = fecha_subida or datetime.now().strftime("%Y-%m-%d")

    @property
    def id(self) -> int:
        return self._id

    @property
    def propietario(self) -> int:
        return self._propietario

    @property
    def album_id(self) -> int:
        return self._album_id

    @property
    def url_imagen(self) -> str:
        return self._url_imagen

    @property
    def fecha_subida(self) -> str:
        return self._fecha_subida

    def es_propietario(self, usuario_id: int) -> bool:
        """Verifica si un usuario es dueño de esta foto."""
        return self._propietario == usuario_id

    def __repr__(self) -> str:
        return f"Foto(id={self._id}, propietario={self._propietario})"


class Comentario:
    """
    Representa un comentario publicado en una foto.
    """

    def __init__(self, id: int = None, autor_id: int = None,
                 foto_id: int = None, contenido: str = "",
                 fecha_creacion: str = None):
        self._id = id
        self._autor_id = autor_id
        self._foto_id = foto_id
        self._contenido = contenido
        self._fecha_creacion = fecha_creacion or datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    @property
    def id(self) -> int:
        return self._id

    @property
    def autor_id(self) -> int:
        return self._autor_id

    @property
    def foto_id(self) -> int:
        return self._foto_id

    @property
    def contenido(self) -> str:
        return self._contenido

    @property
    def fecha_creacion(self) -> str:
        return self._fecha_creacion

    def __repr__(self) -> str:
        return f"Comentario(id={self._id}, autor={self._autor_id}, foto={self._foto_id})"
