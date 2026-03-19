# -*- coding: utf-8 -*-
"""DAO - Proveedor-Producto (relación N:M)."""
from .base_model import BaseModel


class ProveedorProductoModel(BaseModel):
    TABLE_NAME = "proveedor_producto"
    PK_COLUMN = "proveedor_producto_id"

    def get_proveedores_de_producto(self, producto_id: int) -> list[dict]:
        """Proveedores que ofrecen un producto, con precios para comparar."""
        sql = """SELECT pp.*, p.razon_social, p.tipo_credito
                 FROM proveedor_producto pp
                 JOIN proveedor p ON pp.proveedor_id = p.proveedor_id
                 WHERE pp.producto_id = ? AND pp.estado = 'ACT' AND p.estado = 'ACT'
                 ORDER BY pp.precio_compra ASC"""
        return self.custom_query(sql, (producto_id,))

    def get_productos_de_proveedor(self, proveedor_id: int) -> list[dict]:
        """Productos que ofrece un proveedor."""
        sql = """SELECT pp.*, pr.nombre AS producto_nombre, pr.codigo
                 FROM proveedor_producto pp
                 JOIN producto pr ON pp.producto_id = pr.producto_id
                 WHERE pp.proveedor_id = ? AND pp.estado = 'ACT' AND pr.estado = 'ACT'
                 ORDER BY pr.nombre"""
        return self.custom_query(sql, (proveedor_id,))

    def get_proveedor_principal(self, producto_id: int) -> dict | None:
        sql = """SELECT pp.*, p.razon_social
                 FROM proveedor_producto pp
                 JOIN proveedor p ON pp.proveedor_id = p.proveedor_id
                 WHERE pp.producto_id = ? AND pp.es_proveedor_principal = 1
                   AND pp.estado = 'ACT' LIMIT 1"""
        return self.custom_query_one(sql, (producto_id,))

    def get_by_proveedor_producto(self, proveedor_id: int, producto_id: int) -> dict | None:
        sql = """SELECT * FROM proveedor_producto
                 WHERE proveedor_id = ? AND producto_id = ?"""
        return self.custom_query_one(sql, (proveedor_id, producto_id))
