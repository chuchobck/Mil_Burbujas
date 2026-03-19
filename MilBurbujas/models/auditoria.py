# -*- coding: utf-8 -*-
"""DAO - Auditoría (Core/Seguridad)."""
import json
from .base_model import BaseModel


class AuditoriaModel(BaseModel):
    TABLE_NAME = "auditoria"
    PK_COLUMN = "auditoria_id"
    HAS_ESTADO = False

    def registrar(self, usuario_id: int, tabla: str, operacion: str,
                  registro_id: str, datos_anteriores: dict = None,
                  datos_nuevos: dict = None) -> int:
        """Registra una entrada de auditoría."""
        return self.insert({
            "usuario_id": usuario_id,
            "tabla_afectada": tabla,
            "operacion": operacion,
            "registro_id": str(registro_id),
            "datos_anteriores": json.dumps(datos_anteriores, default=str) if datos_anteriores else None,
            "datos_nuevos": json.dumps(datos_nuevos, default=str) if datos_nuevos else None,
        })

    def registrar_in_transaction(self, usuario_id: int, tabla: str, operacion: str,
                                  registro_id: str, datos_anteriores: dict = None,
                                  datos_nuevos: dict = None) -> int:
        """Registra auditoría DENTRO de una transacción."""
        return self.insert_in_transaction({
            "usuario_id": usuario_id,
            "tabla_afectada": tabla,
            "operacion": operacion,
            "registro_id": str(registro_id),
            "datos_anteriores": json.dumps(datos_anteriores, default=str) if datos_anteriores else None,
            "datos_nuevos": json.dumps(datos_nuevos, default=str) if datos_nuevos else None,
        })

    def get_by_tabla(self, tabla: str) -> list[dict]:
        return self.get_by_field("tabla_afectada", tabla, only_active=False)

    def get_by_periodo(self, fecha_inicio: str, fecha_fin: str) -> list[dict]:
        sql = """SELECT a.*, u.nombre_completo
                 FROM auditoria a
                 JOIN usuario u ON a.usuario_id = u.usuario_id
                 WHERE a.fecha_hora BETWEEN ? AND ?
                 ORDER BY a.fecha_hora DESC"""
        return self.custom_query(sql, (fecha_inicio, fecha_fin))
