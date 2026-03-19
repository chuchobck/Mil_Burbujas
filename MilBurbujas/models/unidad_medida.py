# -*- coding: utf-8 -*-
"""DAO - Unidad de Medida (Catálogo)."""
from .base_model import BaseModel


class UnidadMedidaModel(BaseModel):
    TABLE_NAME = "unidad_medida"
    PK_COLUMN = "unidad_id"

    def get_by_tipo(self, tipo: str) -> list[dict]:
        return self.get_by_field("tipo", tipo)

    def get_by_abreviatura(self, abreviatura: str) -> dict | None:
        return self.get_one_by_field("abreviatura", abreviatura)
