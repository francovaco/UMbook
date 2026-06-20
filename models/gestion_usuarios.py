"""
Capa general de la aplicación — Gestión de Usuarios.
Responsabilidad: operaciones CRUD sobre la entidad Usuario.
"""

from models.usuario import Usuario
from infrastructure.persistencia import Persistencia
from infrastructure.errores import ErrorNegocio, ErrorSistema


class GestionUsuarios:
    """
    Servicio general para gestionar usuarios.
    Es usado por: Registro y Autenticación, Gestión de Amigos,
    Álbumes y Fotos, Administración.
    """

    def __init__(self):
        self._db = Persistencia().obtener_conexion()

    def obtener_por_id(self, usuario_id: int) -> Usuario:
        row = self._db.execute(
            "SELECT * FROM usuario WHERE id = ?", (usuario_id,)
        ).fetchone()
        if not row:
            raise ErrorNegocio(f"No existe el usuario con id {usuario_id}.")
        return self._fila_a_usuario(row)

    def obtener_por_email(self, email: str) -> Usuario:
        row = self._db.execute(
            "SELECT * FROM usuario WHERE email = ?", (email.lower(),)
        ).fetchone()
        if not row:
            return None
        return self._fila_a_usuario(row)

    def email_disponible(self, email: str, excluir_id: int = None) -> bool:
        """Verifica que el email no esté registrado por otro usuario."""
        if excluir_id:
            row = self._db.execute(
                "SELECT id FROM usuario WHERE email = ? AND id != ?",
                (email.lower(), excluir_id)
            ).fetchone()
        else:
            row = self._db.execute(
                "SELECT id FROM usuario WHERE email = ?", (email.lower(),)
            ).fetchone()
        return row is None

    def guardar(self, usuario: Usuario) -> Usuario:
        try:
            cursor = self._db.execute(
                """INSERT INTO usuario (nombre, apellido, email, contrasena,
                   foto_perfil, fecha_nac, dias_aviso, activo)
                   VALUES (?,?,?,?,?,?,?,?)""",
                (usuario.nombre, usuario.apellido, usuario.email,
                 usuario.contrasena, usuario.foto_perfil, usuario.fecha_nac,
                 usuario.dias_aviso, 1 if usuario.activo else 0)
            )
            self._db.commit()
            return self.obtener_por_id(cursor.lastrowid)
        except Exception as e:
            raise ErrorSistema(f"Error al guardar usuario: {e}")

    def actualizar(self, usuario: Usuario):
        try:
            self._db.execute(
                """UPDATE usuario SET nombre=?, apellido=?, email=?,
                   foto_perfil=?, fecha_nac=?, dias_aviso=?, activo=?
                   WHERE id=?""",
                (usuario.nombre, usuario.apellido, usuario.email,
                 usuario.foto_perfil, usuario.fecha_nac, usuario.dias_aviso,
                 1 if usuario.activo else 0, usuario.id)
            )
            self._db.commit()
        except Exception as e:
            raise ErrorSistema(f"Error al actualizar usuario: {e}")

    def _fila_a_usuario(self, row) -> Usuario:
        return Usuario(
            id=row["id"],
            nombre=row["nombre"],
            apellido=row["apellido"],
            email=row["email"],
            contrasena=row["contrasena"],
            foto_perfil=row["foto_perfil"],
            fecha_nac=row["fecha_nac"],
            dias_aviso=row["dias_aviso"],
            activo=bool(row["activo"])
        )
