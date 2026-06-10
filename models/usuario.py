"""
Capa de modelos — Entity: Usuario
Representa la clase de análisis/diseño Usuario «entity» / «model».
"""

from infrastructure.errores import ErrorValidacion


class Usuario:
    """
    Entidad Usuario del sistema UMBook.
    Encapsula los datos del usuario y las reglas de validación
    de sus atributos.
    """

    def __init__(self, id: int = None, nombre: str = "", apellido: str = "",
                 email: str = "", contrasena: str = "", foto_perfil: str = None,
                 fecha_nac: str = None, dias_aviso: int = 7, activo: bool = True):
        self._id = id
        self._nombre = nombre
        self._apellido = apellido
        self._email = email
        self._contrasena = contrasena
        self._foto_perfil = foto_perfil
        self._fecha_nac = fecha_nac
        self._dias_aviso = dias_aviso
        self._activo = activo

    # ── Getters ──
    @property
    def id(self) -> int:
        return self._id

    @property
    def nombre(self) -> str:
        return self._nombre

    @property
    def apellido(self) -> str:
        return self._apellido

    @property
    def email(self) -> str:
        return self._email

    @property
    def contrasena(self) -> str:
        return self._contrasena

    @property
    def foto_perfil(self) -> str:
        return self._foto_perfil

    @property
    def fecha_nac(self) -> str:
        return self._fecha_nac

    @property
    def dias_aviso(self) -> int:
        return self._dias_aviso

    @property
    def activo(self) -> bool:
        return self._activo

    # ── Setters con validación ──
    @nombre.setter
    def nombre(self, valor: str):
        if not valor or not valor.strip():
            raise ErrorValidacion("El nombre es obligatorio.")
        if len(valor) > 50:
            raise ErrorValidacion("El nombre no puede superar los 50 caracteres.")
        self._nombre = valor.strip()

    @apellido.setter
    def apellido(self, valor: str):
        if not valor or not valor.strip():
            raise ErrorValidacion("El apellido es obligatorio.")
        if len(valor) > 50:
            raise ErrorValidacion("El apellido no puede superar los 50 caracteres.")
        self._apellido = valor.strip()

    @email.setter
    def email(self, valor: str):
        if not valor or "@" not in valor:
            raise ErrorValidacion("El email debe tener un formato válido.")
        self._email = valor.strip().lower()

    @foto_perfil.setter
    def foto_perfil(self, valor: str):
        self._foto_perfil = valor

    @fecha_nac.setter
    def fecha_nac(self, valor: str):
        self._fecha_nac = valor

    @dias_aviso.setter
    def dias_aviso(self, valor: int):
        if valor is not None and (valor < 1 or valor > 30):
            raise ErrorValidacion("Los días de aviso deben estar entre 1 y 30.")
        self._dias_aviso = valor

    @activo.setter
    def activo(self, valor: bool):
        self._activo = valor

    def __repr__(self) -> str:
        return f"Usuario(id={self._id}, nombre={self._nombre}, email={self._email})"
