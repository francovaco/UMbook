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

### Usuario de prueba

| Campo      | Valor               |
|------------|---------------------|
| Email      | `vrodr@um.edu.ar`   |
| Contraseña | `1234`              |
| Nombre     | Valentina Rodriguez |

---

## Casos de uso implementados

### CU-02 — Editar perfil
Acceso: barra superior → avatar → **Editar perfil**

Permite al usuario modificar sus datos personales: nombre, apellido, correo, foto de perfil, fecha de nacimiento y días de aviso de cumpleaños.

Validaciones implementadas:
- Nombre y apellido obligatorios (máx. 50 caracteres)
- Email con formato válido y único en el sistema
- Foto de perfil en formato JPG o PNG, máximo 5 MB
- Días de aviso entre 1 y 30

### CU-06 — Eliminar amigo
Acceso: barra superior → **Amigos**

Permite al usuario ver su lista de amigos y eliminar un vínculo de amistad. El sistema solicita confirmación antes de ejecutar la eliminación, y al cancelar no se realizan cambios.

Validaciones implementadas:
- Verificación de existencia del vínculo antes de eliminar
- Confirmación explícita mediante modal antes de ejecutar

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
Capa de negocio  (Controlador)       →  controllers/
Capa de datos  (Modelo)         →  models/
Capa intermedia        →  infrastructure/ (seguridad, logs, errores)
```

### Patrones de diseño aplicados

- **MVC** — separación de vista, controlador y modelo en cada caso de uso.
- **Singleton** — la conexión a la base de datos se gestiona como instancia única.
- **Repository** — acceso a datos encapsulado en clases repositorio por entidad.

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
│   ├── gestion_usuarios.py             ← Servicio de usuarios
│   └── repositorios.py                 ← Acceso a datos
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