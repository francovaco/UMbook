"""
Controlador de Autenticación — Login
"""
from models.gestion_usuarios import GestionUsuarios
from infrastructure.seguridad import Seguridad
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
