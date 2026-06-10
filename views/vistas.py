"""
Capa de vistas — «view» (boundary en análisis)
Responsabilidad: interactuar con el usuario, capturar datos
y delegar al controlador correspondiente.
Implementa las clases boundary del diagrama de análisis como views MVC.
"""

from controllers.perfil_controller import PerfilController
from controllers.eliminar_amigo_controller import EliminarAmigoController
from controllers.moderar_comentario_controller import ModerarComentarioController


class FormularioEditarPerfil:
    """
    Vista para el CU-02 Editar perfil.
    Boundary/View que captura los datos del formulario
    y los delega al PerfilController.
    """

    def __init__(self, usuario_id: int):
        self._usuario_id = usuario_id
        self._controller = PerfilController()

    def mostrar_formulario(self, datos_actuales: dict) -> None:
        print("\n" + "="*50)
        print("  EDITAR PERFIL")
        print("="*50)
        for campo, valor in datos_actuales.items():
            print(f"  {campo:15}: {valor}")
        print("="*50)

    def enviar_cambios(self, datos: dict) -> dict:
        """
        Paso 3 del diagrama de colaboración: enviar cambios al controller.
        """
        resultado = self._controller.editar_perfil(self._usuario_id, datos)
        self._mostrar_resultado(resultado)
        return resultado

    def _mostrar_resultado(self, resultado: dict) -> None:
        if resultado["ok"]:
            print(f"\n✓ {resultado['mensaje']}")
        else:
            print(f"\n✗ Error: {resultado['mensaje']}")


class ListaAmigos:
    """
    Vista para el CU-06 Eliminar amigo.
    Boundary/View que muestra la lista de amigos
    y delega la eliminación al EliminarAmigoController.
    """

    def __init__(self, usuario_id: int):
        self._usuario_id = usuario_id
        self._controller = EliminarAmigoController()

    def abrir_lista_amigos(self) -> dict:
        resultado = self._controller.listar_amigos(self._usuario_id)
        if resultado["ok"]:
            self._mostrar_lista(resultado["amigos"])
        return resultado

    def _mostrar_lista(self, amigos: list) -> None:
        print("\n" + "="*50)
        print("  MIS AMIGOS")
        print("="*50)
        if not amigos:
            print("  No tenés amigos registrados.")
        for item in amigos:
            u = item["usuario"]
            print(f"  [{item['amistad_id']}] {u.nombre} {u.apellido} — {u.email}")
        print("="*50)

    def seleccionar_amigo(self, amistad_id: int) -> None:
        print(f"\n  Amigo seleccionado: id de amistad {amistad_id}")

    def confirmar_eliminacion(self) -> bool:
        respuesta = input("\n  ¿Confirmás la eliminación? (s/n): ").strip().lower()
        return respuesta == "s"

    def eliminar_amigo(self, amigo_id: int) -> dict:
        """
        Paso 4 del diagrama de colaboración: delegar al controller.
        """
        resultado = self._controller.eliminar_amigo(self._usuario_id, amigo_id)
        self._mostrar_resultado(resultado)
        return resultado

    def _mostrar_resultado(self, resultado: dict) -> None:
        if resultado["ok"]:
            print(f"\n✓ {resultado['mensaje']}")
        else:
            print(f"\n✗ Error: {resultado['mensaje']}")


class DetallesFoto:
    """
    Vista para el CU-13 Moderar comentarios en fotos propias.
    Boundary/View que muestra la foto con comentarios
    y delega la moderación al ModerarComentarioController.
    """

    def __init__(self, usuario_id: int):
        self._usuario_id = usuario_id
        self._controller = ModerarComentarioController()

    def abrir_foto(self, foto_id: int) -> dict:
        resultado = self._controller.obtener_comentarios(
            self._usuario_id, foto_id
        )
        if resultado["ok"]:
            self._mostrar_foto(resultado)
        else:
            print(f"\n✗ Error: {resultado['mensaje']}")
        return resultado

    def _mostrar_foto(self, datos: dict) -> None:
        foto = datos["foto"]
        comentarios = datos["comentarios"]
        es_propietario = datos["es_propietario"]

        print("\n" + "="*50)
        print(f"  FOTO ID: {foto.id} — {foto.url_imagen}")
        if es_propietario:
            print("  (Sos el propietario de esta foto)")
        print("-"*50)
        print("  COMENTARIOS:")
        if not comentarios:
            print("  No hay comentarios.")
        for c in comentarios:
            eliminar = " [puede eliminar]" if es_propietario else ""
            print(f"  [{c.id}] Usuario {c.autor_id}: {c.contenido}{eliminar}")
        print("="*50)

    def seleccionar_comentario(self, comentario_id: int) -> None:
        print(f"\n  Comentario seleccionado: id {comentario_id}")

    def confirmar_eliminacion(self) -> bool:
        respuesta = input("\n  ¿Confirmás la eliminación del comentario? (s/n): ").strip().lower()
        return respuesta == "s"

    def eliminar_comentario(self, foto_id: int, comentario_id: int) -> dict:
        """
        Paso 4 del diagrama de colaboración: delegar al controller.
        """
        resultado = self._controller.eliminar_comentario(
            self._usuario_id, foto_id, comentario_id
        )
        self._mostrar_resultado(resultado)
        return resultado

    def _mostrar_resultado(self, resultado: dict) -> None:
        if resultado["ok"]:
            print(f"\n✓ {resultado['mensaje']}")
        elif resultado.get("acceso_denegado"):
            print(f"\n✗ Acceso denegado: {resultado['mensaje']}")
        else:
            print(f"\n✗ Error: {resultado['mensaje']}")
