# -*- coding: utf-8 -*-
"""DAO - Movimiento de Inventario (log inmutable)."""
from .base_model import BaseModel


class MovimientoInventarioModel(BaseModel):
    TABLE_NAME = "movimiento_inventario"
    PK_COLUMN = "movimiento_id"
    HAS_ESTADO = False

    def get_by_producto(self, producto_id: int, limite: int = 50) -> list[dict]:
        """Historial de movimientos de un producto."""
        sql = """SELECT mi.*, p.nombre AS producto_nombre
                 FROM movimiento_inventario mi
                 JOIN producto p ON mi.producto_id = p.producto_id
                 WHERE mi.producto_id = ?
                 ORDER BY mi.fecha_movimiento DESC
                 LIMIT ?"""
        return self.custom_query(sql, (producto_id, limite))

    def get_by_documento(self, origen: str, documento_id: int) -> list[dict]:
        """Movimientos de un documento específico (compra, venta, ajuste)."""
        sql = """SELECT * FROM movimiento_inventario
                 WHERE origen = ? AND documento_id = ?
                 ORDER BY movimiento_id"""
        return self.custom_query(sql, (origen, documento_id))

    def registrar(self, producto_id: int, tipo: str, origen: str,
                  documento_id: int, cantidad: float,
                  stock_anterior: int, stock_posterior: int) -> int:
        """Registra un movimiento de inventario (dentro de transacción)."""
        return self.insert_in_transaction({
            "producto_id": producto_id,
            "tipo_movimiento": tipo,
            "origen": origen,
            "documento_id": documento_id,
            "cantidad": cantidad,
            "stock_anterior": stock_anterior,
            "stock_posterior": stock_posterior,
        })
