"""
Controlador de Búsqueda de Usuarios — CU-03
Clase: BusquedaController «controller»
"""

from models.gestion_usuarios import GestionUsuarios
from models.repositorios import RepositorioAmistad, RepositorioSolicitudAmistad
from infrastructure.errores import ErrorValidacion, ErrorNegocio


class BusquedaController:

    def __init__(self, usuario_id: int):
        self._usuario_id = usuario_id
        self._gestion = GestionUsuarios()
        self._repo_amistad = RepositorioAmistad()
        self._repo_solicitud = RepositorioSolicitudAmistad()

    def buscarUsuarios(self, termino: str) -> dict:
        """
        Orquesta el flujo de búsqueda.
        Flujo 2a: término vacío → error de validación.
        Flujo 4a: sin resultados → lista vacía con mensaje.
        """
        try:
            self.validarTermino(termino)
            usuarios = self._gestion.buscarPorNombreApellido(termino)
            lista = []
            for u in usuarios:
                if u.id == self._usuario_id:
                    continue
                ya_es_amigo = self._repo_amistad.obtener_entre(self._usuario_id, u.id) is not None
                
                # Verificar solicitudes pendientes
                solicitud_enviada = False
                solicitud_recibida = False
                if not ya_es_amigo:
                    enviada = self._repo_solicitud.obtener_entre(self._usuario_id, u.id)
                    recibida = self._repo_solicitud.obtener_entre(u.id, self._usuario_id)
                    solicitud_enviada = enviada is not None
                    solicitud_recibida = recibida is not None
                    
                lista.append({
                    "usuario": u, 
                    "ya_es_amigo": ya_es_amigo,
                    "solicitud_enviada": solicitud_enviada,
                    "solicitud_recibida": solicitud_recibida
                })
            return self.retornarResultados(lista, termino.strip())
        except ErrorValidacion as e:
            return {"ok": False, "mensaje": str(e), "resultados": [], "termino": termino}
        except Exception as e:
            return {"ok": False, "mensaje": f"Error en la búsqueda: {e}", "resultados": []}
    def validarTermino(self, termino: str) -> bool:
        if not termino or not termino.strip():
            raise ErrorValidacion("Ingresá un nombre o apellido para buscar.")
        return True

    def retornarResultados(self, lista: list, termino: str = "") -> dict:
        return {"ok": True, "resultados": lista, "termino": termino}

    def agregar_amigo(self, amigo_id: int) -> dict:
        """Envía una solicitud de amistad en lugar de agregar directamente."""
        from controllers.solicitud_amistad_controller import SolicitudAmistadController
        ctrl = SolicitudAmistadController()
        return ctrl.enviar_solicitud(self._usuario_id, amigo_id)
