"""
CU-11 — Configurar visibilidad del álbum
Permite al propietario configurar quién puede ver cada álbum.
Opciones: Solo yo, Amigos, Grupo específico, Todos.
"""

from models.repositorios import RepositorioAlbum, RepositorioGrupo
from models.gestion_usuarios import GestionUsuarios
from infrastructure.errores import ErrorValidacion, ErrorNegocio
from infrastructure.logger import Logger


class VisibilidadAlbumController:

    def __init__(self):
        self._repo_album = RepositorioAlbum()
        self._repo_grupo = RepositorioGrupo()
        self._logger = Logger()

    def listar_albumes(self, propietario_id: int) -> dict:
        """Lista los álbumes del usuario con su configuración de visibilidad."""
        try:
            albumes = self._repo_album.listar_de_usuario(propietario_id)
            grupos = self._repo_grupo.listar_de_usuario(propietario_id)
            resultado = []
            for album in albumes:
                cant_fotos = self._repo_album.contar_fotos(album.id)
                grupo_nombre = None
                if album.visibilidad == "GRUPO" and album.grupo_id:
                    try:
                        grupo = self._repo_grupo.obtener(album.grupo_id)
                        grupo_nombre = grupo.nombre
                    except Exception:
                        grupo_nombre = "Grupo eliminado"
                resultado.append({
                    "album": album,
                    "cant_fotos": cant_fotos,
                    "grupo_nombre": grupo_nombre
                })
            return {"ok": True, "albumes": resultado, "grupos": grupos}
        except Exception as e:
            return {"ok": False, "mensaje": str(e), "albumes": [], "grupos": []}

    def configurar_visibilidad(self, propietario_id: int, album_id: int,
                                visibilidad: str, grupo_id: int = None) -> dict:
        """Configura la visibilidad de un álbum."""
        try:
            self._repo_album.actualizar_visibilidad(
                album_id, propietario_id, visibilidad, grupo_id
            )
            self._logger.registrar("CONFIGURAR_VISIBILIDAD_ALBUM", "OK", propietario_id)

            etiquetas = {
                "SOLO_YO": "Solo yo",
                "AMIGOS": "Amigos",
                "GRUPO": "Grupo específico",
                "TODOS": "Todos"
            }
            return {
                "ok": True,
                "mensaje": f"Visibilidad actualizada a '{etiquetas.get(visibilidad, visibilidad)}'."
            }

        except (ErrorValidacion, ErrorNegocio) as e:
            return {"ok": False, "mensaje": str(e)}
        except Exception as e:
            return {"ok": False, "mensaje": f"Error al configurar visibilidad: {e}"}

    def crear_album(self, propietario_id: int, nombre: str,
                    visibilidad: str = "AMIGOS", grupo_id: int = None) -> dict:
        """Crea un nuevo álbum con la visibilidad especificada."""
        try:
            if not nombre or not nombre.strip():
                return {"ok": False, "mensaje": "El nombre del álbum es obligatorio."}

            from models.entidades import Album
            if visibilidad not in Album.VISIBILIDADES:
                return {"ok": False, "mensaje": f"Visibilidad inválida: {visibilidad}."}

            if visibilidad == "GRUPO" and not grupo_id:
                return {"ok": False, "mensaje": "Debés seleccionar un grupo para esta visibilidad."}

            album = self._repo_album.crear(propietario_id, nombre.strip(), visibilidad, grupo_id)
            self._logger.registrar("CREAR_ALBUM", "OK", propietario_id)
            return {"ok": True, "mensaje": "Álbum creado correctamente.", "album": album}

        except (ErrorValidacion, ErrorNegocio) as e:
            return {"ok": False, "mensaje": str(e)}
        except Exception as e:
            return {"ok": False, "mensaje": f"Error al crear álbum: {e}"}
