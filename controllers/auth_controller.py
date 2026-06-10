"""
Controlador de Autenticación — Login y Registro
"""
from models.usuario import Usuario
from models.gestion_usuarios import GestionUsuarios
from infrastructure.seguridad import Seguridad
from infrastructure.errores import ErrorValidacion, ErrorNegocio
from infrastructure.logger import Logger


class AuthController:

    def __init__(self):
        self._gestion = GestionUsuarios()
        self._seg = Seguridad()
        self._logger = Logger()

    def login(self, email: str, contrasena: str) -> dict:
        try:
            usuario = self._gestion.obtener_por_email(email)
            if not usuario:
                return {"ok": False, "mensaje": "Email o contraseña incorrectos."}
            if not usuario.activo:
                return {"ok": False, "mensaje": "Tu cuenta está deshabilitada."}
            if not self._seg.verificar_contrasena(contrasena, usuario.contrasena):
                return {"ok": False, "mensaje": "Email o contraseña incorrectos."}
            self._logger.registrar("LOGIN", "EXITOSO", usuario.id)
            return {"ok": True, "usuario": usuario}
        except Exception as e:
            return {"ok": False, "mensaje": str(e)}

    def registrar(self, datos: dict) -> dict:
        try:
            if not datos.get("nombre") or not datos.get("apellido"):
                raise ErrorValidacion("Nombre y apellido son obligatorios.")
            if not datos.get("email") or "@" not in datos["email"]:
                raise ErrorValidacion("Email inválido.")
            if not datos.get("contrasena") or len(datos["contrasena"]) < 6:
                raise ErrorValidacion("La contraseña debe tener al menos 6 caracteres.")
            if not self._gestion.email_disponible(datos["email"]):
                raise ErrorNegocio("El email ya está registrado.")
            hash_pwd = self._seg.hashear_contrasena(datos["contrasena"])
            usuario = Usuario(
                nombre=datos["nombre"], apellido=datos["apellido"],
                email=datos["email"], contrasena=hash_pwd
            )
            usuario = self._gestion.guardar(usuario)
            self._logger.registrar("REGISTRO", "EXITOSO", usuario.id)
            return {"ok": True, "usuario": usuario}
        except (ErrorValidacion, ErrorNegocio) as e:
            return {"ok": False, "mensaje": str(e)}
