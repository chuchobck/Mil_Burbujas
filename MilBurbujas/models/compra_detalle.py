# -*- coding: utf-8 -*-
"""DAO - Compra Detalle."""
from .base_model import BaseModel


class CompraDetalleModel(BaseModel):
    TABLE_NAME = "compra_detalle"
    PK_COLUMN = "compra_detalle_id"
    HAS_ESTADO = False

    def get_by_compra(self, compra_id: int) -> list[dict]:
        """Detalles de una compra con nombre de producto."""
        sql = """SELECT cd.*, p.nombre AS producto_nombre, p.codigo_barras AS producto_codigo
                 FROM compra_detalle cd
                 JOIN producto p ON cd.producto_id = p.producto_id
                 WHERE cd.compra_id = ?
                 ORDER BY cd.compra_detalle_id"""
        return self.custom_query(sql, (compra_id,))

    def get_by_producto(self, producto_id: int) -> list[dict]:
        """Historial de compras de un producto."""
        sql = """SELECT cd.*, c.numero_factura, c.fecha_compra, pr.razon_social
                 FROM compra_detalle cd
                 JOIN compra c ON cd.compra_id = c.compra_id
                 JOIN proveedor pr ON c.proveedor_id = pr.proveedor_id
                 WHERE cd.producto_id = ? AND c.estado != 'ANULADA'
                 ORDER BY c.fecha_compra DESC"""
        return self.custom_query(sql, (producto_id,))
