"""
Persistencia
Patrón: Singleton para la conexión a la base de datos.
Responsabilidad: administrar la conexión con SQLite).
"""

import sqlite3


class Persistencia:
    """
    Clase Singleton que gestiona la conexión a la base de datos.
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

            CREATE TABLE IF NOT EXISTS grupo (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                propietario  INTEGER NOT NULL REFERENCES usuario(id),
                nombre       TEXT    NOT NULL
            );

            CREATE TABLE IF NOT EXISTS grupo_miembro (
                grupo_id    INTEGER NOT NULL REFERENCES grupo(id),
                usuario_id  INTEGER NOT NULL REFERENCES usuario(id),
                PRIMARY KEY (grupo_id, usuario_id)
            );

            CREATE TABLE IF NOT EXISTS grupo_permiso (
                grupo_id        INTEGER PRIMARY KEY REFERENCES grupo(id),
                ver_albumes     INTEGER NOT NULL DEFAULT 0,
                comentar_fotos  INTEGER NOT NULL DEFAULT 0,
                escribir_muro   INTEGER NOT NULL DEFAULT 0
            );
        """)
        self._conexion.commit()
        # Migraciones para columnas que pueden no existir en BDs previas
        for sql in [
            "ALTER TABLE usuario ADD COLUMN habilitado     INTEGER NOT NULL DEFAULT 1",
            "ALTER TABLE usuario ADD COLUMN es_admin       INTEGER NOT NULL DEFAULT 0",
            "ALTER TABLE usuario ADD COLUMN nombre_usuario TEXT    NOT NULL DEFAULT ''",
            "ALTER TABLE usuario ADD COLUMN fecha_registro TEXT",
            "ALTER TABLE comentario ADD COLUMN eliminado_por_admin INTEGER NOT NULL DEFAULT 0",
        ]:
            try:
                cursor.execute(sql)
                self._conexion.commit()
            except Exception:
                pass  # La columna ya existe

    def obtener_conexion(self) -> sqlite3.Connection:
        if self._conexion is None:
            raise RuntimeError("La base de datos no está conectada.")
        return self._conexion

    def cerrar(self):
        if self._conexion:
            self._conexion.close()
            self._conexion = None