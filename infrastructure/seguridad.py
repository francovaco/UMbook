"""
Capa intermedia — Seguridad
Responsabilidad: cifrado de contraseñas y verificación de sesión.
"""

import hashlib
import secrets


class Seguridad:
    """
    Provee servicios de seguridad: hash de contraseñas y verificación.
    """

    @staticmethod
    def hashear_contrasena(contrasena: str) -> str:
        """Cifra la contraseña usando SHA-256 con salt."""
        salt = secrets.token_hex(16)
        hash_pwd = hashlib.sha256((salt + contrasena).encode()).hexdigest()
        return f"{salt}:{hash_pwd}"

    @staticmethod
    def verificar_contrasena(contrasena: str, hash_almacenado: str) -> bool:
        """Verifica una contraseña contra su hash almacenado."""
        try:
            salt, hash_original = hash_almacenado.split(":")
            hash_ingresado = hashlib.sha256((salt + contrasena).encode()).hexdigest()
            return hash_ingresado == hash_original
        except ValueError:
            return False
