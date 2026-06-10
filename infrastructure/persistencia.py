"""
Capa intermedia — Persistencia
Patrón: Singleton para la conexión a la base de datos.
Responsabilidad: administrar la conexión con el SGBD (SQLite).
"""

import sqlite3
import os


class Persistencia:
    """
    Clase Singleton que gestiona la conexión a la base de datos.
    Implementa el mecanismo de diseño genérico de Persistencia
    del diagrama de subsistemas.
    """
    _instancia = None
    _conexion = None

    def __new__(cls):
        if cls._instancia is None:
            cls._instancia = super().__new__(cls)
        return cls._instancia

    def conectar(self, ruta_bd: str = "umbook.db"):
        if self._conexion is None:
            self._conexion = sqlite3.connect(ruta_bd, check_same_thread=False)
            self._conexion.row_factory = sqlite3.Row
            self._crear_tablas()
        return self._conexion

    def _crear_tablas(self):
        cursor = self._conexion.cursor()
        cursor.executescript("""
            CREATE TABLE IF NOT EXISTS usuario (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre      TEXT    NOT NULL,
                apellido    TEXT    NOT NULL,
                email       TEXT    NOT NULL UNIQUE,
                contrasena  TEXT    NOT NULL,
                foto_perfil TEXT,
                fecha_nac   TEXT,
                dias_aviso  INTEGER DEFAULT 7,
                activo      INTEGER DEFAULT 1
            );

            CREATE TABLE IF NOT EXISTS amistad (
                id               INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_origen   INTEGER NOT NULL REFERENCES usuario(id),
                usuario_destino  INTEGER NOT NULL REFERENCES usuario(id),
                fecha_creacion   TEXT    NOT NULL,
                UNIQUE(usuario_origen, usuario_destino)
            );

            CREATE TABLE IF NOT EXISTS album (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                propietario  INTEGER NOT NULL REFERENCES usuario(id),
                nombre       TEXT    NOT NULL,
                fecha_creacion TEXT  NOT NULL
            );

            CREATE TABLE IF NOT EXISTS foto (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                propietario  INTEGER NOT NULL REFERENCES usuario(id),
                album_id     INTEGER NOT NULL REFERENCES album(id),
                url_imagen   TEXT    NOT NULL,
                fecha_subida TEXT    NOT NULL
            );

            CREATE TABLE IF NOT EXISTS comentario (
                id             INTEGER PRIMARY KEY AUTOINCREMENT,
                autor_id       INTEGER NOT NULL REFERENCES usuario(id),
                foto_id        INTEGER NOT NULL REFERENCES foto(id),
                contenido      TEXT    NOT NULL,
                fecha_creacion TEXT    NOT NULL
            );

            CREATE TABLE IF NOT EXISTS log_sistema (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha_hora TEXT    NOT NULL,
                usuario_id INTEGER,
                operacion  TEXT    NOT NULL,
                resultado  TEXT    NOT NULL
            );
        """)
        self._conexion.commit()

    def obtener_conexion(self) -> sqlite3.Connection:
        if self._conexion is None:
            raise RuntimeError("La base de datos no está conectada.")
        return self._conexion

    def cerrar(self):
        if self._conexion:
            self._conexion.close()
            self._conexion = None
