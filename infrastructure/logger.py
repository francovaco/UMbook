"""
Capa intermedia — Registro de Logs
Responsabilidad: registrar eventos críticos del sistema.
"""

from datetime import datetime
from infrastructure.persistencia import Persistencia


class Logger:
    """Registra operaciones críticas en la tabla log_sistema."""

    def __init__(self):
        self._db = Persistencia().obtener_conexion()

    def registrar(self, operacion: str, resultado: str, usuario_id: int = None):
        fecha_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._db.execute(
            "INSERT INTO log_sistema (fecha_hora, usuario_id, operacion, resultado) VALUES (?,?,?,?)",
            (fecha_hora, usuario_id, operacion, resultado)
        )
        self._db.commit()
