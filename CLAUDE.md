# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Run the application (port 9000)
python3 app.py

# Run automated tests
python3 tests/test_casos_de_uso.py

# Install dependencies
pip install flask
```

The app runs at `http://127.0.0.1:9000`. Demo users: `vrodr@um.edu.ar`, `mdiaz@um.edu.ar`, `lfern@um.edu.ar` (all password `1234`). Admin: `admin@um.edu.ar` / `admin123`.

## Architecture

MVC on 4 layers:

```
templates/         ← Jinja2 views (Flask)
controllers/       ← One class per use case, return {"ok": bool, "mensaje": str, ...}
models/            ← Business entities + services
infrastructure/    ← Cross-cutting: DB, security, errors, logging
```

**Key files:**
- `app.py` — Flask routes + demo data seeding (runs on first `/login` request)
- `infrastructure/persistencia.py` — Singleton SQLite connection; call `Persistencia().conectar(path)` once at startup. Schema is auto-created via `_crear_tablas()`.
- `infrastructure/errores.py` — Exception hierarchy: `ErrorValidacion`, `ErrorNegocio`, `ErrorAcceso`, `ErrorSistema` (all extend `ErrorUMBook`)
- `infrastructure/seguridad.py` — SHA-256 password hashing with salt
- `models/usuario.py` — `Usuario` entity with property setters that validate (raises exceptions on invalid data)
- `models/entidades.py` — `Amistad`, `Foto`, `Comentario`, `Grupo`, `GrupoPermiso` entities
- `models/gestion_usuarios.py` — `GestionUsuarios` facade: `guardar`, `obtener_por_id`, `obtener_por_email`, `email_disponible`, `nombre_usuario_disponible`
- `models/repositorios.py` — `RepositorioAmistad`, `RepositorioFoto`, `RepositorioComentario`, `RepositorioGrupo` (Repository pattern)

**Controller pattern:** Each controller method returns a dict `{"ok": True/False, "mensaje": str, ...}`. Controllers catch exceptions from models/services and translate them to this dict format.

**Session keys:** `usuario_id`, `nombre`, `apellido`, `es_admin`

## Implemented Use Cases

| CU | File | Description |
|----|------|-------------|
| CU-01 | `controllers/auth_controller.py` | Registration |
| CU-02 | `controllers/perfil_controller.py` | Edit profile |
| CU-03 | `app.py` (search route) | Search users |
| CU-06 | `controllers/eliminar_amigo_controller.py` | Remove friend |
| CU-08/09 | `controllers/grupos_controller.py` | Groups & permissions |
| CU-12 | `controllers/moderar_comentario_controller.py` | Comment on photos |
| CU-13 | `controllers/moderar_comentario_controller.py` | Moderate comments |
| CU-18/19 | `controllers/admin_controller.py` | Admin panel (enable/disable users, delete comments) |

## Database

SQLite file `umbook.db` is created at the project root on first run. For tests, the test `setup()` uses `:memory:` — always call `Persistencia().conectar(":memory:")` before tests to avoid polluting production DB.

The `usuario` table has columns: `id`, `nombre`, `apellido`, `email`, `nombre_usuario`, `contrasena`, `foto_perfil`, `fecha_nac`, `dias_aviso`, `activo`, `habilitado`, `es_admin`. If the DB was created before `nombre_usuario` was added, a migration step in `persistencia.py` adds the column.

## Adding a New Use Case

1. Create `controllers/cu_XX_controller.py` with a class returning `{"ok": bool, "mensaje": str}`
2. Add route(s) in `app.py` using `@login_requerido` decorator
3. Create/extend templates in `templates/`
4. Add test functions in `tests/test_casos_de_uso.py`
