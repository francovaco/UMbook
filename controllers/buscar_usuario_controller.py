"""
Controlador de Búsqueda de Usuarios — CU-03
"""
from models.gestion_usuarios import GestionUsuarios
from models.repositorios import RepositorioAmistad
from models.entidades import Amistad
from infrastructure.errores import ErrorValidacion, ErrorNegocio, ErrorSistema


class BuscarUsuarioController:

    def __init__(self):
        self._gestion = GestionUsuarios()
        self._repo_amistad = RepositorioAmistad()

    def buscar(self, usuario_id: int, termino: str) -> dict:
        """
        Busca usuarios por nombre o apellido.
        Flujo 2a: término vacío → error de validación.
        Flujo 4a: sin resultados → lista vacía con mensaje.
        Excluye al propio usuario de los resultados.
        """
        try:
            if not termino or not termino.strip():
                raise ErrorValidacion("Ingresá un nombre o apellido para buscar.")

            usuarios = self._gestion.buscar(termino)

            resultados = []
            for u in usuarios:
                if u.id == usuario_id:
                    continue
                ya_es_amigo = self._repo_amistad.obtener_entre(usuario_id, u.id) is not None
                resultados.append({"usuario": u, "ya_es_amigo": ya_es_amigo})

            return {"ok": True, "resultados": resultados, "termino": termino.strip()}
        except ErrorValidacion as e:
            return {"ok": False, "mensaje": str(e), "resultados": [], "termino": termino}
        except Exception as e:
            return {"ok": False, "mensaje": str(e), "resultados": [], "termino": termino}

    def agregar_amigo(self, usuario_id: int, amigo_id: int) -> dict:
        """Crea el vínculo de amistad si no existe."""
        try:
            if usuario_id == amigo_id:
                raise ErrorNegocio("No podés agregarte a vos mismo.")
            if self._repo_amistad.obtener_entre(usuario_id, amigo_id):
                raise ErrorNegocio("Ya son amigos.")
            self._repo_amistad.guardar(
                Amistad(usuario_origen=usuario_id, usuario_destino=amigo_id)
            )
            amigo = self._gestion.obtener_por_id(amigo_id)
            return {"ok": True, "mensaje": f"Ahora sos amigo de {amigo.nombre} {amigo.apellido}."}
        except (ErrorNegocio, ErrorSistema) as e:
            return {"ok": False, "mensaje": str(e)}
