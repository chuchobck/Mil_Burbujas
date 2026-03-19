# -*- coding: utf-8 -*-
"""DAO - Producto (Catalogo - Tabla central)."""
from .base_model import BaseModel


class ProductoModel(BaseModel):
    TABLE_NAME = "producto"
    PK_COLUMN = "producto_id"

    def get_by_codigo_barras(self, codigo_barras):
        return self.get_one_by_field("codigo_barras", codigo_barras)

    def get_completo(self):
        """Productos con nombre de categoria, marca, linea y unidad."""
        sql = """SELECT p.*,
                        c.nombre  AS categoria_nombre,
                        m.nombre  AS marca_nombre,
                        lp.nombre AS linea_nombre,
                        um.nombre AS unidad_nombre,
                        um.abreviatura AS unidad_abrev
                 FROM producto p
                 LEFT JOIN categoria c      ON p.categoria_id = c.categoria_id
                 LEFT JOIN marca m          ON p.marca_id = m.marca_id
                 LEFT JOIN linea_producto lp ON p.linea_id = lp.linea_id
                 LEFT JOIN unidad_medida um ON p.unidad_id = um.unidad_id
                 WHERE p.estado = 'ACT'
                 ORDER BY p.nombre"""
        return self.custom_query(sql)

    def get_by_categoria(self, categoria_id):
        return self.get_by_field("categoria_id", categoria_id)

    def get_by_marca(self, marca_id):
        return self.get_by_field("marca_id", marca_id)

    def get_stock_bajo(self):
        """Productos con stock actual menor o igual al stock minimo."""
        sql = """SELECT p.*, c.nombre AS categoria_nombre, m.nombre AS marca_nombre
                 FROM producto p
                 LEFT JOIN categoria c ON p.categoria_id = c.categoria_id
                 LEFT JOIN marca m     ON p.marca_id = m.marca_id
                 WHERE p.estado = 'ACT' AND p.stock_actual <= p.stock_minimo
                 ORDER BY p.stock_actual ASC"""
        return self.custom_query(sql)

    def get_proximos_caducar(self, dias=180):
        """Productos perecederos proximos a caducar."""
        sql = """SELECT p.*, c.nombre AS categoria_nombre
                 FROM producto p
                 LEFT JOIN categoria c ON p.categoria_id = c.categoria_id
                 WHERE p.estado = 'ACT'
                   AND p.fecha_caducidad IS NOT NULL
                   AND date(p.fecha_caducidad) <= date('now', '+' || ? || ' days')
                 ORDER BY p.fecha_caducidad ASC"""
        return self.custom_query(sql, (dias,))

    def actualizar_stock(self, producto_id, nuevo_stock):
        """Actualiza el stock de un producto (para transacciones)."""
        return self.update_in_transaction(producto_id, {"stock_actual": nuevo_stock})

    def buscar(self, termino):
        """Busqueda por nombre o codigo de barras."""
        sql = """SELECT p.*, c.nombre AS categoria_nombre, m.nombre AS marca_nombre
                 FROM producto p
                 LEFT JOIN categoria c ON p.categoria_id = c.categoria_id
                 LEFT JOIN marca m     ON p.marca_id = m.marca_id
                 WHERE p.estado = 'ACT'
                   AND (p.nombre LIKE ? OR p.codigo_barras LIKE ?)
                 ORDER BY p.nombre"""
        like = "%{}%".format(termino)
        return self.custom_query(sql, (like, like))

    def get_valor_inventario(self):
        """Calcula el valor total del inventario activo."""
        sql = """SELECT COUNT(*) as total_productos,
                        SUM(stock_actual) as total_unidades,
                        SUM(stock_actual * COALESCE(precio_referencia_compra, 0)) as valor_costo,
                        SUM(stock_actual * COALESCE(precio_venta, 0)) as valor_venta
                 FROM producto
                 WHERE estado = 'ACT' AND stock_actual > 0"""
        return self.custom_query_one(sql)
