"""
UMBook — Aplicación Flask
Implementación completa de CU-02, CU-06 y CU-13
con interfaz web respetando el diseño de pantallas.
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, render_template, request, redirect, url_for, session, flash

from infrastructure.persistencia import Persistencia
from infrastructure.seguridad import Seguridad
from models.gestion_usuarios import GestionUsuarios
from models.repositorios import (RepositorioAmistad, RepositorioFoto,
                                  RepositorioComentario)
from models.usuario import Usuario
from models.entidades import Amistad, Foto, Comentario
from controllers.auth_controller import AuthController
from controllers.perfil_controller import PerfilController
from controllers.eliminar_amigo_controller import EliminarAmigoController
from controllers.moderar_comentario_controller import ModerarComentarioController

# ── Inicialización ──
app = Flask(__name__)
app.secret_key = "umbook-secret-2026"
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'fotos')
os.makedirs(os.path.join(os.path.dirname(__file__), 'static', 'fotos'), exist_ok=True)

Persistencia().conectar(os.path.join(os.path.dirname(__file__), "umbook.db"))
_inicializado = False


def inicializar_datos_demo():
    """Crea datos de demo si la BD está vacía."""
    db = Persistencia().obtener_conexion()
    if db.execute("SELECT COUNT(*) FROM usuario").fetchone()[0] > 0:
        return
    seg = Seguridad()
    gestion = GestionUsuarios()
    repo_amistad = RepositorioAmistad()
    repo_foto = RepositorioFoto()
    repo_com = RepositorioComentario()

    u1 = gestion.guardar(Usuario(nombre="Valentina", apellido="Rodriguez",
        email="vrodr@um.edu.ar", contrasena=seg.hashear_contrasena("1234"), dias_aviso=7))
    u2 = gestion.guardar(Usuario(nombre="Martín", apellido="Díaz",
        email="mdiaz@um.edu.ar", contrasena=seg.hashear_contrasena("1234")))
    u3 = gestion.guardar(Usuario(nombre="Lucía", apellido="Fernández",
        email="lfern@um.edu.ar", contrasena=seg.hashear_contrasena("1234")))

    repo_amistad.guardar(Amistad(usuario_origen=u1.id, usuario_destino=u2.id))
    repo_amistad.guardar(Amistad(usuario_origen=u1.id, usuario_destino=u3.id))

    db.execute("INSERT INTO album (propietario, nombre, fecha_creacion) VALUES (?,?,?)",
               (u1.id, "Fotos UM", "2026-01-15"))
    db.commit()
    album_id = db.execute("SELECT last_insert_rowid()").fetchone()[0]

    foto = repo_foto.guardar(Foto(propietario=u1.id, album_id=album_id,
                                  url_imagen="egresados_2026.jpg"))
    repo_com.guardar(Comentario(autor_id=u2.id, foto_id=foto.id,
                                contenido="¡Qué buena foto! Los echo de menos a todos 😁"))
    repo_com.guardar(Comentario(autor_id=u3.id, foto_id=foto.id,
                                contenido="Ese día fue genial. ¡Repetimos! 🎉"))
    repo_com.guardar(Comentario(autor_id=u2.id, foto_id=foto.id,
                                contenido="Me encanta esta foto 📸"))


def login_requerido(f):
    from functools import wraps
    @wraps(f)
    def decorador(*args, **kwargs):
        if "usuario_id" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorador


# ══════════════════════════════════════════════
# RUTAS DE AUTENTICACIÓN
# ══════════════════════════════════════════════

@app.route("/")
def index():
    if "usuario_id" in session:
        return redirect(url_for("home"))
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    global _inicializado
    if not _inicializado:
        inicializar_datos_demo()
        _inicializado = True

    if request.method == "POST":
        ctrl = AuthController()
        resultado = ctrl.login(request.form["email"], request.form["contrasena"])
        if resultado["ok"]:
            u = resultado["usuario"]
            session["usuario_id"] = u.id
            session["nombre"] = u.nombre
            session["apellido"] = u.apellido
            return redirect(url_for("home"))
        return render_template("login.html", error=resultado["mensaje"])

    exito = request.args.get("exito")
    return render_template("login.html", exito=exito)


@app.route("/registro", methods=["GET", "POST"])
def registro():
    form = {"nombre": "", "apellido": "", "email": ""}
    if request.method == "POST":
        form = {k: request.form.get(k, "") for k in ["nombre", "apellido", "email"]}
        if request.form.get("contrasena") != request.form.get("contrasena2"):
            return render_template("registro.html",
                                   error="Las contraseñas no coinciden.", form=form)
        ctrl = AuthController()
        resultado = ctrl.registrar({
            "nombre": form["nombre"], "apellido": form["apellido"],
            "email": form["email"], "contrasena": request.form.get("contrasena")
        })
        if resultado["ok"]:
            return redirect(url_for("login", exito="Cuenta creada. Podés iniciar sesión."))
        return render_template("registro.html", error=resultado["mensaje"], form=form)
    return render_template("registro.html", form=form)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# ══════════════════════════════════════════════
# HOME
# ══════════════════════════════════════════════

@app.route("/home")
@login_requerido
def home():
    return render_template("home.html")

# ── PERFIL ──
@app.route("/perfil")
@login_requerido
def perfil():
    gestion = GestionUsuarios()
    usuario = gestion.obtener_por_id(session["usuario_id"])
    return render_template("perfil.html", usuario=usuario)


# ══════════════════════════════════════════════
# CU-02 — EDITAR PERFIL
# ══════════════════════════════════════════════

@app.route("/perfil/editar", methods=["GET", "POST"])
@login_requerido
def editar_perfil():
    gestion = GestionUsuarios()
    usuario = gestion.obtener_por_id(session["usuario_id"])

    if request.method == "POST":
        datos = {}

        if request.form.get("nombre"):
            datos["nombre"] = request.form["nombre"]
        if request.form.get("apellido"):
            datos["apellido"] = request.form["apellido"]
        if request.form.get("email"):
            datos["email"] = request.form["email"]
        if request.form.get("fecha_nac"):
            datos["fecha_nac"] = request.form["fecha_nac"]
        if request.form.get("dias_aviso"):
            try:
                datos["dias_aviso"] = int(request.form["dias_aviso"])
            except ValueError:
                pass

        # Foto de perfil
        archivo = request.files.get("foto_perfil")
        if archivo and archivo.filename:
            nombre_archivo = archivo.filename.lower()
            if not (nombre_archivo.endswith(".jpg") or nombre_archivo.endswith(".jpeg")
                    or nombre_archivo.endswith(".png")):
                return render_template("editar_perfil.html", usuario=usuario,
                                       error="La foto debe ser JPG o PNG.")
            contenido = archivo.read()
            if len(contenido) > 5 * 1024 * 1024:
                return render_template("editar_perfil.html", usuario=usuario,
                                       error="La foto no puede superar los 5MB.")
            ruta = os.path.join(os.path.dirname(__file__), "static", "fotos",
                                f"user_{session['usuario_id']}{os.path.splitext(nombre_archivo)[1]}")
            with open(ruta, "wb") as f:
                f.write(contenido)
            datos["foto_perfil"] = f"user_{session['usuario_id']}{os.path.splitext(nombre_archivo)[1]}"

        ctrl = PerfilController()
        resultado = ctrl.editar_perfil(session["usuario_id"], datos)

        if resultado["ok"]:
            session["nombre"] = resultado["usuario"].nombre
            session["apellido"] = resultado["usuario"].apellido
            usuario = resultado["usuario"]
            return render_template("editar_perfil.html", usuario=usuario,
                                   exito="Perfil actualizado correctamente.")
        return render_template("editar_perfil.html", usuario=usuario,
                               error=resultado["mensaje"])

    return render_template("editar_perfil.html", usuario=usuario)


# ══════════════════════════════════════════════
# CU-06 — ELIMINAR AMIGO
# ══════════════════════════════════════════════

@app.route("/amigos")
@login_requerido
def amigos():
    ctrl = EliminarAmigoController()
    resultado = ctrl.listar_amigos(session["usuario_id"])
    exito = request.args.get("exito")
    error = request.args.get("error")
    return render_template("amigos.html",
                           amigos=resultado.get("amigos", []),
                           exito=exito, error=error)


@app.route("/amigos/eliminar", methods=["POST"])
@login_requerido
def eliminar_amigo():
    amigo_id = request.form.get("amigo_id")
    if not amigo_id:
        return redirect(url_for("amigos", error="ID de amigo inválido."))
    ctrl = EliminarAmigoController()
    resultado = ctrl.eliminar_amigo(session["usuario_id"], int(amigo_id))
    if resultado["ok"]:
        return redirect(url_for("amigos", exito=resultado["mensaje"]))
    return redirect(url_for("amigos", error=resultado["mensaje"]))


# ══════════════════════════════════════════════
# CU-13 — MODERAR COMENTARIOS
# ══════════════════════════════════════════════

@app.route("/fotos")
@login_requerido
def mis_fotos():
    repo = RepositorioFoto()
    db = Persistencia().obtener_conexion()
    rows = db.execute("SELECT * FROM foto WHERE propietario = ?",
                      (session["usuario_id"],)).fetchall()
    from models.entidades import Foto
    fotos = [Foto(id=r["id"], propietario=r["propietario"],
                  album_id=r["album_id"], url_imagen=r["url_imagen"],
                  fecha_subida=r["fecha_subida"]) for r in rows]
    return render_template("mis_fotos.html", fotos=fotos)


@app.route("/fotos/<int:foto_id>")
@login_requerido
def detalle_foto(foto_id):
    ctrl = ModerarComentarioController()
    resultado = ctrl.obtener_comentarios(session["usuario_id"], foto_id)
    if not resultado["ok"]:
        return redirect(url_for("mis_fotos"))
    exito = request.args.get("exito")
    error = request.args.get("error")
    return render_template("detalle_foto.html",
                           foto=resultado["foto"],
                           comentarios=resultado["comentarios"],
                           es_propietario=resultado["es_propietario"],
                           exito=exito, error=error)


@app.route("/comentarios/eliminar", methods=["POST"])
@login_requerido
def eliminar_comentario():
    comentario_id = request.form.get("comentario_id")
    foto_id = request.form.get("foto_id")
    if not comentario_id or not foto_id:
        return redirect(url_for("mis_fotos"))
    ctrl = ModerarComentarioController()
    resultado = ctrl.eliminar_comentario(
        session["usuario_id"], int(foto_id), int(comentario_id)
    )
    if resultado["ok"]:
        return redirect(url_for("detalle_foto", foto_id=foto_id,
                                exito=resultado["mensaje"]))
    return redirect(url_for("detalle_foto", foto_id=foto_id,
                            error=resultado["mensaje"]))


@app.route("/fotos/demo")
@login_requerido
def agregar_foto_demo():
    """Agrega una foto de demo para el usuario actual."""
    db = Persistencia().obtener_conexion()
    db.execute("INSERT OR IGNORE INTO album (propietario, nombre, fecha_creacion) VALUES (?,?,?)",
               (session["usuario_id"], "Mi álbum", "2026-01-01"))
    db.commit()
    album_id = db.execute("SELECT id FROM album WHERE propietario=? LIMIT 1",
                          (session["usuario_id"],)).fetchone()[0]
    repo_foto = RepositorioFoto()
    foto = repo_foto.guardar(Foto(propietario=session["usuario_id"],
                                  album_id=album_id, url_imagen="mi_foto.jpg"))
    repo_com = RepositorioComentario()
    repo_com.guardar(Comentario(autor_id=session["usuario_id"],
                                foto_id=foto.id, contenido="Mi comentario de demo"))
    return redirect(url_for("mis_fotos"))


if __name__ == "__main__":
    print("\n" + "="*60)
    print("  UMBook — Servidor iniciado")
    print("  Abrí http://127.0.0.1:5000 en tu navegador")
    print("  Usuarios demo:")
    print("    vrodr@um.edu.ar  / 1234  (Valentina)")
    print("    mdiaz@um.edu.ar  / 1234  (Martín)")
    print("    lfern@um.edu.ar  / 1234  (Lucía)")
    print("="*60 + "\n")
    app.run(debug=True, port=5000)
