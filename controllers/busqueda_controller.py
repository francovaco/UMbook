"""
Controlador de Búsqueda de Usuarios — CU-03
Clase: BusquedaController «controller»
"""
from models.gestion_usuarios import GestionUsuarios
from models.repositorios import RepositorioAmistad
from models.entidades import Amistad
from infrastructure.errores import ErrorValidacion, ErrorNegocio, ErrorSistema


class BusquedaController:

    def __init__(self, usuario_id: int):
        self._usuario_id = usuario_id
        self._gestion = GestionUsuarios()
        self._repo_amistad = RepositorioAmistad()

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
                lista.append({"usuario": u, "ya_es_amigo": ya_es_amigo})
            return self.retornarResultados(lista, termino.strip())
        except ErrorValidacion as e:
            return {"ok": False, "mensaje": str(e), "resultados": [], "termino": termino}
        except Exception as e:
            return {"ok": False, "mensaje": str(e), "resultados": [], "termino": termino}

    def validarTermino(self, termino: str) -> bool:
        if not termino or not termino.strip():
            raise ErrorValidacion("Ingresá un nombre o apellido para buscar.")
        return True

    def retornarResultados(self, lista: list, termino: str = "") -> dict:
        return {"ok": True, "resultados": lista, "termino": termino}

    def agregar_amigo(self, amigo_id: int) -> dict:
        """Crea el vínculo de amistad si no existe."""
        try:
            if self._usuario_id == amigo_id:
                raise ErrorNegocio("No podés agregarte a vos mismo.")
            if self._repo_amistad.obtener_entre(self._usuario_id, amigo_id):
                raise ErrorNegocio("Ya son amigos.")
            self._repo_amistad.guardar(
                Amistad(usuario_origen=self._usuario_id, usuario_destino=amigo_id)
            )
            amigo = self._gestion.obtener_por_id(amigo_id)
            return {"ok": True, "mensaje": f"Ahora sos amigo de {amigo.nombre} {amigo.apellido}."}
        except (ErrorNegocio, ErrorSistema) as e:
            return {"ok": False, "mensaje": str(e)}
