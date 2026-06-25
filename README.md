# UMBook

**Proyecto:** Ingeniería de Software 2026.

**Franco Vaccarezza 63179**

---

## Cómo ejecutar

### Requisitos
- Python 3.10 o superior

### Pasos

```bash
# 1. Crear y activar el entorno virtual
python3 -m venv venv
source venv/bin/activate        # Mac / Linux
venv\Scripts\activate           # Windows

# 2. Instalar dependencias
pip install flask

# 3. Ejecutar la aplicación
cd umbook
python3 app.py
```

### Acceder

Abrí el navegador en `http://127.0.0.1:5000`

### Usuarios de prueba

| Nombre               | Email               | Contraseña |
|-----------------------|----------------------|------------|
| Valentina Rodriguez   | `vrodr@um.edu.ar`   | `1234`     |
| Martín Díaz           | `mdiaz@um.edu.ar`   | `1234`     |
| Lucía Fernández       | `lfern@um.edu.ar`   | `1234`     |

---

## Casos de uso implementados

### CU-01 — Registrarse en el sistema
Acceso: página de inicio → **Crear cuenta**

Permite al usuario crear una cuenta ingresando nombre, apellido, email, nombre de usuario y contraseña.

Validaciones implementadas:
- Todos los campos son obligatorios
- Email con formato válido y único en el sistema
- Nombre de usuario único en el sistema
- Contraseña de al menos 6 caracteres
- Confirmación de contraseña coincidente

### CU-02 — Editar perfil
Acceso: barra superior → avatar → **Editar perfil**

Permite al usuario modificar sus datos personales: nombre, apellido, correo, foto de perfil, fecha de nacimiento y días de aviso de cumpleaños.

Validaciones implementadas:
- Nombre y apellido obligatorios (máx. 50 caracteres)
- Email con formato válido y único en el sistema
- Foto de perfil en formato JPG o PNG, máximo 5 MB
- Días de aviso entre 1 y 30

### CU-03 — Buscar usuarios
Acceso: barra superior → **Buscar usuarios**

Permite al usuario buscar otros usuarios registrados por nombre o apellido (búsqueda parcial). Cada resultado incluye un botón para enviar una solicitud de amistad.

Validaciones implementadas:
- El campo de búsqueda no puede estar vacío
- Mensaje claro cuando no se encuentran resultados
- El usuario no aparece en sus propios resultados de búsqueda

### CU-06 — Eliminar amigo
Acceso: barra superior → **Amigos**

Permite al usuario ver su lista de amigos y eliminar un vínculo de amistad. El sistema solicita confirmación antes de ejecutar la eliminación, y al cancelar no se realizan cambios.

Validaciones implementadas:
- Verificación de existencia del vínculo antes de eliminar
- Confirmación explícita mediante modal antes de ejecutar

### CU-12 — Comentar fotos
Acceso: barra superior → **Álbumes** → seleccionar foto

Permite al usuario comentar fotos, editar sus propios comentarios y eliminarlos. El campo de comentario solo aparece si el usuario tiene permiso (es propietario o es amigo del propietario en un grupo con comentarios habilitados).

Validaciones implementadas:
- Verificación de permiso antes de mostrar el campo de comentario
- El comentario no puede estar vacío
- Solo el autor puede editar o eliminar su propio comentario
- Confirmación explícita antes de eliminar

### CU-13 — Moderar comentarios en fotos propias
Acceso: barra superior → **Álbumes** → seleccionar foto

Permite al propietario de una foto eliminar comentarios de sus amigos. El sistema verifica que el usuario sea dueño de la foto antes de mostrar la opción de eliminar. Si no es propietario, la opción no aparece.

Validaciones implementadas:
- Verificación de propiedad antes de mostrar controles de moderación
- Confirmación explícita antes de eliminar
- Eliminación permanente sin posibilidad de recuperación

---

## Arquitectura

El sistema implementa el patrón **MVC** sobre una arquitectura en 4 capas:

```
Capa de presentación (Vista)   →  templates/ (Flask)
Capa de negocio  (Controlador) →  controllers/
Capa de datos  (Modelo)        →  models/
Capa intermedia                →  infrastructure/ (seguridad, logs, errores)
```

### Patrones de diseño aplicados

| Patrón | Dónde |
|--------|-------|
| **MVC** | `templates/` (View) → `controllers/` (Controller) → `models/` (Model). Cada CU tiene su propia clase en cada capa. |
| **Singleton** | `infrastructure/persistencia.py` — una única instancia de conexión a SQLite compartida por todo el sistema. |
| **Repository** | `models/repositorios.py` — `RepositorioAmistad`, `RepositorioFoto` y `RepositorioComentario` encapsulan el acceso a datos por entidad. |
| **Facade** | `models/gestion_usuarios.py` — `GestionUsuarios` oculta la complejidad de acceso a `Usuario` y es reutilizado por los tres controllers. |

---

## Estructura del proyecto

```
umbook/
├── app.py                              ← Servidor Flask y rutas
├── infrastructure/
│   ├── persistencia.py                 ← SQLite Singleton
│   ├── seguridad.py                    ← Hash SHA-256 con salt
│   ├── errores.py                      ← Jerarquía de excepciones
│   └── logger.py                       ← Registro de eventos
├── models/
│   ├── usuario.py                      ← Entidad Usuario
│   ├── entidades.py                    ← Amistad, Foto, Comentario
│   ├── gestion_usuarios.py             ← Servicio de usuarios (Facade)
│   └── repositorios.py                 ← Acceso a datos (Repository)
├── controllers/
│   ├── auth_controller.py              ← Login y registro
│   ├── perfil_controller.py            ← CU-02
│   ├── eliminar_amigo_controller.py    ← CU-06
│   └── moderar_comentario_controller.py← CU-13
├── templates/                          ← Vistas HTML
└── static/css/umbook.css               ← Estilos
```

---

## Tecnologías utilizadas

| Tecnología | Uso |
|------------|-----|
| Python 3   | Lenguaje principal |
| Flask      | Framework web (servidor y rutas) |
| SQLite     | Base de datos embebida |
| SHA-256    | Cifrado de contraseñas |
