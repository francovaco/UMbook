"""
Capa intermedia — Manejo de Errores
Responsabilidad: jerarquía de excepciones del sistema UMBook.
"""


class ErrorUMBook(Exception):
    """Clase base para todos los errores del sistema."""
    pass


class ErrorValidacion(ErrorUMBook):
    """Error de validación de datos ingresados por el usuario."""
    pass


class ErrorNegocio(ErrorUMBook):
    """Error de regla de negocio (ej: email duplicado, no es propietario)."""
    pass


class ErrorSistema(ErrorUMBook):
    """Error interno del sistema (ej: fallo de base de datos)."""
    pass


class ErrorAcceso(ErrorUMBook):
    """Error de acceso no autorizado."""
    pass
