"""
Repositorios para Amistad, Foto y Comentario.
Responsabilidad: acceso a datos para cada entidad.
"""

from models.entidades import Amistad, Foto, Comentario
from infrastructure.persistencia import Persistencia
from infrastructure.errores import ErrorNegocio, ErrorSistema
from datetime import datetime


class RepositorioAmistad:

    def __init__(self):
        self._db = Persistencia().obtener_conexion()

    def obtener(self, id: int) -> Amistad:
        row = self._db.execute(
            "SELECT * FROM amistad WHERE id = ?", (id,)
        ).fetchone()
        if not row:
            raise ErrorNegocio(f"No existe la amistad con id {id}.")
        return self._fila_a_amistad(row)

    def obtener_entre(self, usuario_a: int, usuario_b: int) -> Amistad:
        row = self._db.execute(
            """SELECT * FROM amistad
               WHERE (usuario_origen=? AND usuario_destino=?)
               OR    (usuario_origen=? AND usuario_destino=?)""",
            (usuario_a, usuario_b, usuario_b, usuario_a)
        ).fetchone()
        return self._fila_a_amistad(row) if row else None

    def listar_de_usuario(self, usuario_id: int) -> list:
        rows = self._db.execute(
            """SELECT * FROM amistad
               WHERE usuario_origen=? OR usuario_destino=?""",
            (usuario_id, usuario_id)
        ).fetchall()
        return [self._fila_a_amistad(r) for r in rows]

    def guardar(self, amistad: Amistad) -> Amistad:
        try:
            cursor = self._db.execute(
                """INSERT INTO amistad (usuario_origen, usuario_destino, fecha_creacion)
                   VALUES (?,?,?)""",
                (amistad.usuario_origen, amistad.usuario_destino,
                 datetime.now().strftime("%Y-%m-%d"))
            )
            self._db.commit()
            return self.obtener(cursor.lastrowid)
        except Exception as e:
            raise ErrorSistema(f"Error al guardar amistad: {e}")

    def eliminar(self, amistad_id: int):
        try:
            self._db.execute("DELETE FROM amistad WHERE id = ?", (amistad_id,))
            self._db.commit()
        except Exception as e:
            raise ErrorSistema(f"Error al eliminar amistad: {e}")

    def _fila_a_amistad(self, row) -> Amistad:
        return Amistad(
            id=row["id"],
            usuario_origen=row["usuario_origen"],
            usuario_destino=row["usuario_destino"],
            fecha_creacion=row["fecha_creacion"]
        )


class RepositorioFoto:

    def __init__(self):
        self._db = Persistencia().obtener_conexion()

    def obtener(self, id: int) -> Foto:
        row = self._db.execute(
            "SELECT * FROM foto WHERE id = ?", (id,)
        ).fetchone()
        if not row:
            raise ErrorNegocio(f"No existe la foto con id {id}.")
        return self._fila_a_foto(row)

    def guardar(self, foto: Foto) -> Foto:
        cursor = self._db.execute(
            """INSERT INTO foto (propietario, album_id, url_imagen, fecha_subida)
               VALUES (?,?,?,?)""",
            (foto.propietario, foto.album_id, foto.url_imagen,
             datetime.now().strftime("%Y-%m-%d"))
        )
        self._db.commit()
        return self.obtener(cursor.lastrowid)

    def _fila_a_foto(self, row) -> Foto:
        return Foto(
            id=row["id"],
            propietario=row["propietario"],
            album_id=row["album_id"],
            url_imagen=row["url_imagen"],
            fecha_subida=row["fecha_subida"]
        )


class RepositorioComentario:

    def __init__(self):
        self._db = Persistencia().obtener_conexion()

    def obtener(self, id: int) -> Comentario:
        row = self._db.execute(
            "SELECT * FROM comentario WHERE id = ?", (id,)
        ).fetchone()
        if not row:
            raise ErrorNegocio(f"No existe el comentario con id {id}.")
        return self._fila_a_comentario(row)

    def listar_de_foto(self, foto_id: int) -> list:
        rows = self._db.execute(
            "SELECT * FROM comentario WHERE foto_id = ? ORDER BY fecha_creacion",
            (foto_id,)
        ).fetchall()
        return [self._fila_a_comentario(r) for r in rows]

    def guardar(self, comentario: Comentario) -> Comentario:
        cursor = self._db.execute(
            """INSERT INTO comentario (autor_id, foto_id, contenido, fecha_creacion)
               VALUES (?,?,?,?)""",
            (comentario.autor_id, comentario.foto_id, comentario.contenido,
             datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        )
        self._db.commit()
        return self.obtener(cursor.lastrowid)

    def eliminar(self, comentario_id: int):
        self._db.execute("DELETE FROM comentario WHERE id = ?", (comentario_id,))
        self._db.commit()

    def _fila_a_comentario(self, row) -> Comentario:
        return Comentario(
            id=row["id"],
            autor_id=row["autor_id"],
            foto_id=row["foto_id"],
            contenido=row["contenido"],
            fecha_creacion=row["fecha_creacion"]
        )
