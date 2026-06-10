"""
UMBook — Punto de entrada del sistema.
Inicializa la base de datos y ejecuta una demostración
de los 3 casos de uso implementados.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from infrastructure.persistencia import Persistencia
from infrastructure.seguridad import Seguridad
from models.gestion_usuarios import GestionUsuarios
from models.repositorios import RepositorioAmistad, RepositorioFoto, RepositorioComentario
from models.usuario import Usuario
from models.entidades import Amistad, Foto, Comentario
from views.vistas import FormularioEditarPerfil, ListaAmigos, DetallesFoto


def inicializar_datos_demo():
    """Crea usuarios y datos de demo para probar los CU."""
    seg = Seguridad()
    gestion = GestionUsuarios()
    db = Persistencia().obtener_conexion()

    # Verificar si ya hay datos
    if db.execute("SELECT COUNT(*) FROM usuario").fetchone()[0] > 0:
        return

    print("  Creando datos de demostración...")

    u1 = gestion.guardar(Usuario(
        nombre="Juan", apellido="Pérez", email="juan@umbook.com",
        contrasena=seg.hashear_contrasena("pass123"),
        dias_aviso=7
    ))
    u2 = gestion.guardar(Usuario(
        nombre="María", apellido="García", email="maria@umbook.com",
        contrasena=seg.hashear_contrasena("pass123")
    ))

    repo_amistad = RepositorioAmistad()
    repo_amistad.guardar(Amistad(usuario_origen=u1.id, usuario_destino=u2.id))

    db.execute("INSERT INTO album (propietario, nombre, fecha_creacion) VALUES (?,?,?)",
               (u1.id, "Fotos 2026", "2026-01-01"))
    db.commit()
    album_id = db.execute("SELECT last_insert_rowid()").fetchone()[0]

    repo_foto = RepositorioFoto()
    foto = repo_foto.guardar(Foto(
        propietario=u1.id, album_id=album_id, url_imagen="vacaciones.jpg"
    ))

    repo_com = RepositorioComentario()
    repo_com.guardar(Comentario(
        autor_id=u2.id, foto_id=foto.id, contenido="Qué lindo lugar!"
    ))

    print(f"  Usuarios creados: Juan (id={u1.id}), María (id={u2.id})")
    print(f"  Foto creada: id={foto.id}")


def demo_cu02(usuario_id: int):
    print("\n" + "="*60)
    print("  DEMO CU-02 — Editar perfil")
    print("="*60)

    vista = FormularioEditarPerfil(usuario_id)
    vista.mostrar_formulario({
        "nombre": "Juan", "apellido": "Pérez",
        "email": "juan@umbook.com", "dias_aviso": 7
    })

    # Flujo exitoso
    vista.enviar_cambios({
        "nombre": "Juan Carlos",
        "email": "juancarlos@umbook.com",
        "dias_aviso": 5
    })

    # Flujo alternativo: email duplicado
    vista.enviar_cambios({"email": "maria@umbook.com"})

    # Flujo alternativo: foto con formato inválido
    vista.enviar_cambios({"foto_perfil": "documento.pdf"})


def demo_cu06(usuario_id: int, amigo_id: int):
    print("\n" + "="*60)
    print("  DEMO CU-06 — Eliminar amigo")
    print("="*60)

    vista = ListaAmigos(usuario_id)
    vista.abrir_lista_amigos()

    # Flujo exitoso
    print(f"\n  → Eliminando amigo con id={amigo_id}...")
    vista.eliminar_amigo(amigo_id)

    # Verificar que ya no está
    print("\n  → Lista actualizada:")
    vista.abrir_lista_amigos()

    # Flujo alternativo: sin vínculo
    print("\n  → Intentando eliminar usuario sin vínculo (id=999)...")
    vista.eliminar_amigo(999)


def demo_cu13(usuario_id: int, foto_id: int, comentario_id: int, otro_usuario_id: int):
    print("\n" + "="*60)
    print("  DEMO CU-13 — Moderar comentarios en fotos propias")
    print("="*60)

    # Flujo exitoso: propietario elimina comentario
    vista = DetallesFoto(usuario_id)
    vista.abrir_foto(foto_id)
    print(f"\n  → Propietario elimina comentario id={comentario_id}...")
    vista.eliminar_comentario(foto_id, comentario_id)

    # Flujo alternativo: no propietario intenta eliminar
    # Primero agregar otro comentario
    repo_com = RepositorioComentario()
    nuevo = repo_com.guardar(Comentario(
        autor_id=otro_usuario_id, foto_id=foto_id, contenido="Otro comentario nuevo"
    ))

    print(f"\n  → Usuario no propietario (id={otro_usuario_id}) intenta eliminar...")
    vista_otro = DetallesFoto(otro_usuario_id)
    vista_otro.eliminar_comentario(foto_id, nuevo.id)


if __name__ == "__main__":
    print("\n" + "="*60)
    print("  UMBook — Sistema de Red Social Universitaria")
    print("  Implementación CU-02, CU-06, CU-13")
    print("="*60)

    # Inicializar base de datos
    Persistencia().conectar("umbook_demo.db")
    inicializar_datos_demo()

    db = Persistencia().obtener_conexion()
    u1_id = db.execute("SELECT id FROM usuario WHERE email='juancarlos@umbook.com' OR email='juan@umbook.com'").fetchone()
    if not u1_id:
        print("Error al inicializar datos.")
        sys.exit(1)
    u1_id = u1_id[0]
    u2_id = db.execute("SELECT id FROM usuario WHERE email='maria@umbook.com'").fetchone()[0]
    foto_row = db.execute("SELECT id FROM foto LIMIT 1").fetchone()
    foto_id = foto_row[0] if foto_row else None
    com_row = db.execute("SELECT id FROM comentario LIMIT 1").fetchone()
    comentario_id = com_row[0] if com_row else None

    if foto_id and comentario_id:
        demo_cu02(u1_id)
        demo_cu06(u1_id, u2_id)
        demo_cu13(u1_id, foto_id, comentario_id, u2_id)
    else:
        print("No hay datos suficientes para la demo.")

    print("\n  Demo completada.\n")
