# -*- coding: utf-8 -*-
"""DAO - Cierre de Caja (Financiero)."""
from .base_model import BaseModel


class CierreCajaModel(BaseModel):
    TABLE_NAME = "cierre_caja"
    PK_COLUMN = "cierre_id"
    HAS_ESTADO = True

    def get_by_fecha(self, fecha: str) -> dict | None:
        return self.get_one_by_field("fecha_cierre", fecha)

    def existe_cierre(self, fecha: str) -> bool:
        return self.exists_by_field("fecha_cierre", fecha)

    def get_ultimos(self, limite: int = 30) -> list[dict]:
        sql = """SELECT cc.*, u.nombre_completo AS usuario_nombre
                 FROM cierre_caja cc
                 JOIN usuario u ON cc.usuario_id = u.usuario_id
                 WHERE cc.estado = 'CERRADO'
                 ORDER BY cc.fecha_cierre DESC
                 LIMIT ?"""
        return self.custom_query(sql, (limite,))

    def get_resumen_mensual(self, anio: int, mes: int) -> dict | None:
        sql = """SELECT
                    SUM(total_ventas_efectivo) as ventas_efectivo,
                    SUM(total_ventas_transferencia) as ventas_transferencia,
                    SUM(total_ventas_credito) as ventas_credito,
                    SUM(total_compras) as compras,
                    SUM(total_gastos) as gastos,
                    SUM(diferencia) as diferencia_acumulada,
                    COUNT(*) as dias_cerrados
                 FROM cierre_caja
                 WHERE strftime('%Y', fecha_cierre) = ?
                   AND strftime('%m', fecha_cierre) = ?
                   AND estado = 'CERRADO'"""
        return self.custom_query_one(sql, (str(anio), str(mes).zfill(2)))

    def deactivate(self, record_id: int) -> bool:
        return self.update(record_id, {"estado": "ANULADO"})
