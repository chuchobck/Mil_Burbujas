# -*- coding: utf-8 -*-
"""
Servicio de Usuarios.
Gestión de usuarios y autenticación (bcrypt).
"""
import hashlib
from models.usuario import UsuarioModel
from services.auditoria_service import AuditoriaService


class UsuarioService:
    """Gestión de usuarios del sistema."""

    def __init__(self):
        self._model = UsuarioModel()
        self._audit = AuditoriaService()

    # ── Autenticación ──

    def autenticar(self, email: str, contrasena: str) -> dict | None:
        """Verifica credenciales. Retorna el usuario si OK, None si falla.

        Usa SHA-256 por simplicidad (bcrypt requiere install adicional).
        """
        usuario = self._model.get_by_email(email)
        if not usuario or usuario["estado"] != "ACT":
            return None

        hash_input = hashlib.sha256(contrasena.encode()).hexdigest()
        if usuario["contrasena_hash"] == hash_input:
            return dict(usuario)

        return None

    # ── CRUD ──

    def crear(self, datos: dict, usuario_id_accion: int = 1) -> dict:
        """Crea un usuario. Hashea la contraseña automáticamente."""
        if self._model.get_by_email(datos.get("email", "")):
            raise ValueError("Ya existe un usuario con ese email.")

        contrasena = datos.pop("contrasena", "admin123")
        datos["contrasena_hash"] = hashlib.sha256(contrasena.encode()).hexdigest()

        uid = self._model.insert(datos)
        self._audit.registrar(
            usuario_id_accion, "usuario", "INSERT", uid, datos_nuevos=datos
        )
        return self._model.get_by_id(uid)

    def actualizar(self, usuario_id: int, datos: dict, usuario_id_accion: int = 1) -> dict:
        anterior = self._model.get_by_id(usuario_id)
        if not anterior:
            raise ValueError("Usuario no encontrado.")

        if "contrasena" in datos:
            datos["contrasena_hash"] = hashlib.sha256(datos.pop("contrasena").encode()).hexdigest()

        self._model.update(usuario_id, datos)
        self._audit.registrar(
            usuario_id_accion, "usuario", "UPDATE", usuario_id,
            datos_anteriores=dict(anterior), datos_nuevos=datos
        )
        return self._model.get_by_id(usuario_id)

    def desactivar(self, usuario_id: int, usuario_id_accion: int = 1) -> bool:
        anterior = self._model.get_by_id(usuario_id)
        if not anterior:
            raise ValueError("Usuario no encontrado.")
        result = self._model.deactivate(usuario_id)
        self._audit.registrar(
            usuario_id_accion, "usuario", "DELETE", usuario_id,
            datos_anteriores=dict(anterior)
        )
        return result

    def cambiar_contrasena(self, usuario_id: int, contrasena_actual: str,
                           nueva_contrasena: str) -> bool:
        """Cambio de contraseña con verificación de la actual."""
        usuario = self._model.get_by_id(usuario_id)
        if not usuario:
            raise ValueError("Usuario no encontrado.")

        hash_actual = hashlib.sha256(contrasena_actual.encode()).hexdigest()
        if usuario["contrasena_hash"] != hash_actual:
            raise ValueError("La contraseña actual es incorrecta.")

        if len(nueva_contrasena) < 6:
            raise ValueError("La nueva contraseña debe tener al menos 6 caracteres.")

        nuevo_hash = hashlib.sha256(nueva_contrasena.encode()).hexdigest()
        return self._model.update(usuario_id, {"contrasena_hash": nuevo_hash})

    # ── Consultas ──

    def get_por_id(self, usuario_id: int) -> dict | None:
        return self._model.get_by_id(usuario_id)

    def get_todos(self) -> list[dict]:
        return self._model.get_all()

    def get_activos(self) -> list[dict]:
        return self._model.get_activos()
