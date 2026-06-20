import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from infrastructure.persistencia import Persistencia
from infrastructure.seguridad import Seguridad
from models.gestion_usuarios import GestionUsuarios
from models.repositorios import RepositorioAmistad, RepositorioFoto, RepositorioComentario
from models.usuario import Usuario
from models.entidades import Amistad, Foto, Comentario
from controllers.perfil_controller import PerfilController
from controllers.eliminar_amigo_controller import EliminarAmigoController
from controllers.moderar_comentario_controller import ModerarComentarioController


def setup():
    """Inicializa base de datos en memoria para pruebas."""
    Persistencia().conectar(":memory:")

    seg = Seguridad()
    gestion = GestionUsuarios()
    db = Persistencia().obtener_conexion()

    # Crear usuarios de prueba
    u1 = Usuario(nombre="Juan", apellido="Pérez", email="juan@test.com",
                 contrasena=seg.hashear_contrasena("pass123"))
    u2 = Usuario(nombre="María", apellido="García", email="maria@test.com",
                 contrasena=seg.hashear_contrasena("pass123"))
    u3 = Usuario(nombre="Pedro", apellido="López", email="pedro@test.com",
                 contrasena=seg.hashear_contrasena("pass123"))

    u1 = gestion.guardar(u1)
    u2 = gestion.guardar(u2)
    u3 = gestion.guardar(u3)

    # Crear amistad entre u1 y u2
    repo_amistad = RepositorioAmistad()
    amistad = repo_amistad.guardar(Amistad(usuario_origen=u1.id, usuario_destino=u2.id))

    # Crear álbum, foto y comentario para CU-13
    db.execute("INSERT INTO album (propietario, nombre, fecha_creacion) VALUES (?,?,?)",
               (u1.id, "Mis fotos", "2026-01-01"))
    db.commit()
    album_id = db.execute("SELECT last_insert_rowid()").fetchone()[0]

    repo_foto = RepositorioFoto()
    foto = repo_foto.guardar(Foto(propietario=u1.id, album_id=album_id, url_imagen="foto1.jpg"))

    repo_com = RepositorioComentario()
    comentario = repo_com.guardar(Comentario(autor_id=u2.id, foto_id=foto.id, contenido="Qué linda foto!"))

    return {
        "u1_id": u1.id, "u2_id": u2.id, "u3_id": u3.id,
        "amistad_id": amistad.id,
        "foto_id": foto.id,
        "comentario_id": comentario.id
    }


def test_cu02_editar_perfil_exitoso(ids):
    ctrl = PerfilController()
    resultado = ctrl.editar_perfil(ids["u1_id"], {
        "nombre": "Juan Actualizado",
        "email": "juan_nuevo@test.com",
        "dias_aviso": 3
    })
    assert resultado["ok"] == True, f"Esperaba ok=True, obtuvo: {resultado}"
    assert resultado["usuario"].nombre == "Juan Actualizado"
    print("  ✓ CU-02 CP-01: Edición exitosa del perfil")


def test_cu02_email_duplicado(ids):
    ctrl = PerfilController()
    resultado = ctrl.editar_perfil(ids["u1_id"], {
        "email": "maria@test.com"  # Email de u2
    })
    assert resultado["ok"] == False
    assert "email" in resultado["mensaje"].lower()
    print("  ✓ CU-02 CP-02: Email duplicado rechazado correctamente")


def test_cu02_nombre_vacio(ids):
    ctrl = PerfilController()
    resultado = ctrl.editar_perfil(ids["u1_id"], {"nombre": ""})
    assert resultado["ok"] == False
    print("  ✓ CU-02 CP-03: Nombre vacío rechazado correctamente")


def test_cu02_foto_formato_invalido(ids):
    ctrl = PerfilController()
    resultado = ctrl.editar_perfil(ids["u1_id"], {"foto_perfil": "foto.pdf"})
    assert resultado["ok"] == False
    assert "jpg" in resultado["mensaje"].lower() or "png" in resultado["mensaje"].lower()
    print("  ✓ CU-02 CP-04: Formato de foto inválido rechazado")


def test_cu02_dias_aviso_fuera_rango(ids):
    ctrl = PerfilController()
    resultado = ctrl.editar_perfil(ids["u1_id"], {"dias_aviso": 0})
    assert resultado["ok"] == False
    print("  ✓ CU-02 CP-05: Días de aviso fuera de rango rechazado")


def test_cu06_eliminar_amigo_exitoso(ids):
    ctrl = EliminarAmigoController()
    resultado = ctrl.eliminar_amigo(ids["u1_id"], ids["u2_id"])
    assert resultado["ok"] == True
    print("  ✓ CU-06 CP-01: Eliminación de amigo exitosa")


def test_cu06_eliminar_sin_amistad(ids):
    ctrl = EliminarAmigoController()
    resultado = ctrl.eliminar_amigo(ids["u1_id"], ids["u3_id"])
    assert resultado["ok"] == False
    print("  ✓ CU-06 CP-02: Eliminación sin vínculo rechazada correctamente")


def test_cu13_eliminar_comentario_propietario(ids):
    ctrl = ModerarComentarioController()
    resultado = ctrl.eliminar_comentario(
        ids["u1_id"], ids["foto_id"], ids["comentario_id"]
    )
    assert resultado["ok"] == True
    print("  ✓ CU-13 CP-01: Eliminación de comentario por propietario exitosa")


def test_cu13_eliminar_no_propietario(ids):
    # Recrear comentario porque el anterior fue eliminado
    repo_com = RepositorioComentario()
    nuevo_comentario = repo_com.guardar(
        Comentario(autor_id=ids["u2_id"], foto_id=ids["foto_id"], contenido="Otro comentario")
    )
    ctrl = ModerarComentarioController()
    resultado = ctrl.eliminar_comentario(
        ids["u2_id"],  # u2 NO es propietario de la foto
        ids["foto_id"],
        nuevo_comentario.id
    )
    assert resultado["ok"] == False
    assert resultado.get("acceso_denegado") == True
    print("  ✓ CU-13 CP-02: Acceso denegado a no propietario correctamente")


def test_cu13_obtener_comentarios(ids):
    ctrl = ModerarComentarioController()
    resultado = ctrl.obtener_comentarios(ids["u1_id"], ids["foto_id"])
    assert resultado["ok"] == True
    assert resultado["es_propietario"] == True
    print("  ✓ CU-13 CP-03: Obtención de comentarios con flag propietario correcto")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("  PRUEBAS AUTOMATIZADAS — UMBook")
    print("="*60)

    ids = setup()

    print("\n  CU-02 Editar perfil:")
    test_cu02_editar_perfil_exitoso(ids)
    test_cu02_email_duplicado(ids)
    test_cu02_nombre_vacio(ids)
    test_cu02_foto_formato_invalido(ids)
    test_cu02_dias_aviso_fuera_rango(ids)

    print("\n  CU-06 Eliminar amigo:")
    test_cu06_eliminar_amigo_exitoso(ids)
    test_cu06_eliminar_sin_amistad(ids)

    print("\n  CU-13 Moderar comentarios:")
    test_cu13_eliminar_comentario_propietario(ids)
    test_cu13_eliminar_no_propietario(ids)
    test_cu13_obtener_comentarios(ids)

    print("\n" + "="*60)
    print("  TODAS LAS PRUEBAS PASARON ✓")
    print("="*60 + "\n")
