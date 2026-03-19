# -*- coding: utf-8 -*-
"""DAO - Usuario (Core/Seguridad)."""
from .base_model import BaseModel


class UsuarioModel(BaseModel):
    TABLE_NAME = "usuario"
    PK_COLUMN = "usuario_id"

    def get_by_email(self, email: str) -> dict | None:
        return self.get_one_by_field("email", email)

    def update_ultimo_acceso(self, usuario_id: int) -> bool:
        return self.update(usuario_id, {
            "ultimo_acceso": "datetime('now', 'localtime')"
        })

    def get_activos(self) -> list[dict]:
        return self.get_by_field("estado", "ACT", only_active=False)
