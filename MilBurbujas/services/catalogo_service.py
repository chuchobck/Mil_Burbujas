# -*- coding: utf-8 -*-
"""
Servicio de Catalogo.
Gestion de productos, categorias, marcas, lineas de producto y unidades de medida.
"""
from config import IVA_PORCENTAJE
from models.configuracion import ConfiguracionModel
from models.producto import ProductoModel
from models.categoria import CategoriaModel
from models.marca import MarcaModel
from models.linea_producto import LineaProductoModel
from models.unidad_medida import UnidadMedidaModel
from models.promocion import PromocionModel
from models.promocion_producto import PromocionProductoModel
from services.auditoria_service import AuditoriaService


class CatalogoService:
    """CRUD completo de catalogo con reglas de negocio."""

    def __init__(self):
        self._producto = ProductoModel()
        self._categoria = CategoriaModel()
        self._marca = MarcaModel()
        self._linea = LineaProductoModel()
        self._unidad = UnidadMedidaModel()
        self._promocion = PromocionModel()
        self._promo_prod = PromocionProductoModel()
        self._audit = AuditoriaService()

    # ============================
    # CATEGORIAS
    # ============================

    def crear_categoria(self, datos, usuario_id=1):
        if self._categoria.exists_by_field("nombre", datos["nombre"]):
            raise ValueError("Ya existe la categoria '{}'.".format(datos["nombre"]))
        cat_id = self._categoria.insert(datos)
        self._audit.registrar(usuario_id, "categoria", "INSERT", cat_id, datos_nuevos=datos)
        return self._categoria.get_by_id(cat_id)

    def actualizar_categoria(self, categoria_id, datos, usuario_id=1):
        anterior = self._categoria.get_by_id(categoria_id)
        if not anterior:
            raise ValueError("Categoria no encontrada.")
        self._categoria.update(categoria_id, datos)
        self._audit.registrar(usuario_id, "categoria", "UPDATE", categoria_id,
                              datos_anteriores=dict(anterior), datos_nuevos=datos)
        return self._categoria.get_by_id(categoria_id)

    def desactivar_categoria(self, categoria_id, usuario_id=1):
        if self._categoria.tiene_productos_activos(categoria_id):
            raise ValueError("No se puede desactivar: tiene productos activos.")
        hijas = self._categoria.get_hijas(categoria_id)
        if hijas:
            raise ValueError("No se puede desactivar: tiene subcategorias.")
        anterior = self._categoria.get_by_id(categoria_id)
        result = self._categoria.deactivate(categoria_id)
        self._audit.registrar(usuario_id, "categoria", "DELETE", categoria_id,
                              datos_anteriores=dict(anterior))
        return result

    def get_categorias_raiz(self):
        return self._categoria.get_raices()

    def get_subcategorias(self, categoria_padre_id):
        return self._categoria.get_hijas(categoria_padre_id)

    def get_categorias_con_conteo(self):
        return self._categoria.get_con_conteo_productos()

    def get_todas_categorias(self):
        return self._categoria.get_all()

    # ============================
    # MARCAS
    # ============================

    def crear_marca(self, datos, usuario_id=1):
        if self._marca.exists_by_field("nombre", datos["nombre"]):
            raise ValueError("Ya existe la marca '{}'.".format(datos["nombre"]))
        mid = self._marca.insert(datos)
        self._audit.registrar(usuario_id, "marca", "INSERT", mid, datos_nuevos=datos)
        return self._marca.get_by_id(mid)

    def actualizar_marca(self, marca_id, datos, usuario_id=1):
        anterior = self._marca.get_by_id(marca_id)
        if not anterior:
            raise ValueError("Marca no encontrada.")
        self._marca.update(marca_id, datos)
        self._audit.registrar(usuario_id, "marca", "UPDATE", marca_id,
                              datos_anteriores=dict(anterior), datos_nuevos=datos)
        return self._marca.get_by_id(marca_id)

    def desactivar_marca(self, marca_id, usuario_id=1):
        productos = self._producto.get_by_marca(marca_id)
        if productos:
            raise ValueError("No se puede desactivar: tiene productos activos.")
        return self._marca.deactivate(marca_id)

    def get_marcas(self):
        return self._marca.get_all()

    def get_marcas_con_lineas(self):
        return self._marca.get_con_lineas()

    # ============================
    # LINEAS DE PRODUCTO
    # ============================

    def crear_linea(self, datos, usuario_id=1):
        if not self._marca.exists(datos["marca_id"]):
            raise ValueError("La marca especificada no existe.")
        lid = self._linea.insert(datos)
        self._audit.registrar(usuario_id, "linea_producto", "INSERT", lid, datos_nuevos=datos)
        return self._linea.get_by_id(lid)

    def actualizar_linea(self, linea_id, datos, usuario_id=1):
        anterior = self._linea.get_by_id(linea_id)
        if not anterior:
            raise ValueError("Linea de producto no encontrada.")
        self._linea.update(linea_id, datos)
        return self._linea.get_by_id(linea_id)

    def get_lineas(self):
        return self._linea.get_con_marca()

    def get_lineas_por_marca(self, marca_id):
        return self._linea.get_by_marca(marca_id)

    # ============================
    # UNIDADES DE MEDIDA
    # ============================

    def get_unidades(self):
        return self._unidad.get_all()

    def get_unidades_por_tipo(self, tipo):
        return self._unidad.get_by_tipo(tipo)

    # ============================
    # PRODUCTOS
    # ============================

    def _get_margen_default(self):
        """Obtiene el margen de ganancia configurado (default 30%)."""
        try:
            cfg = ConfiguracionModel()
            valor = cfg.get_valor("MARGEN_GANANCIA_DEFAULT")
            return float(valor) if valor else 30.0
        except Exception:
            return 30.0

    def calcular_precio_minimo(self, costo_compra, margen=None):
        """Calcula precio_venta_minimo = costo × (1 + margen/100)."""
        if margen is None:
            margen = self._get_margen_default()
        if costo_compra <= 0:
            return 0.0
        return round(costo_compra * (1 + margen / 100), 2)

    def _generar_codigo_interno(self):
        """Genera un codigo interno auto-incrementable: INT-000001, INT-000002, etc."""
        sql = """SELECT codigo_barras FROM producto
                 WHERE codigo_barras LIKE 'INT-%'
                 ORDER BY codigo_barras DESC LIMIT 1"""
        ultimo = self._producto.custom_query_one(sql)
        if ultimo:
            try:
                num = int(ultimo["codigo_barras"].replace("INT-", "")) + 1
            except ValueError:
                num = 1
        else:
            num = 1
        return "INT-{:06d}".format(num)

    def crear_producto(self, datos, usuario_id=1):
        """Crea un producto con validaciones de negocio.

        Si codigo_barras esta vacio, se auto-genera uno interno (INT-000001).
        """
        cb = datos.get("codigo_barras", "").strip()
        if not cb:
            cb = self._generar_codigo_interno()
            datos["codigo_barras"] = cb
        if self._producto.exists_by_field("codigo_barras", cb):
            raise ValueError("Ya existe un producto con ese codigo de barras.")
        if not self._categoria.exists(datos["categoria_id"]):
            raise ValueError("La categoria especificada no existe.")
        if not self._unidad.exists(datos.get("unidad_id", 0)):
            raise ValueError("La unidad de medida no existe.")
        # Auto-calcular precio_venta_minimo desde costo de compra + margen
        costo = float(datos.get("precio_referencia_compra", 0) or 0)
        datos["precio_venta_minimo"] = self.calcular_precio_minimo(costo)
        pv = datos.get("precio_venta", 0)
        pvm = datos["precio_venta_minimo"]
        if pv < 0:
            raise ValueError("El precio de venta no puede ser negativo.")
        # Precio minimo es solo referencia, no bloquea
        pid = self._producto.insert(datos)
        self._audit.registrar(usuario_id, "producto", "INSERT", pid, datos_nuevos=datos)
        return self._producto.get_by_id(pid)

    def actualizar_producto(self, producto_id, datos, usuario_id=1):
        anterior = self._producto.get_by_id(producto_id)
        if not anterior:
            raise ValueError("Producto no encontrado.")
        # Recalcular precio_venta_minimo si cambio el costo de compra
        costo = float(datos.get("precio_referencia_compra",
                                anterior.get("precio_referencia_compra", 0)) or 0)
        datos["precio_venta_minimo"] = self.calcular_precio_minimo(costo)
        # Precio minimo es solo referencia, no bloquea
        self._producto.update(producto_id, datos)
        self._audit.registrar(usuario_id, "producto", "UPDATE", producto_id,
                              datos_anteriores=dict(anterior), datos_nuevos=datos)
        return self._producto.get_by_id(producto_id)

    def desactivar_producto(self, producto_id, usuario_id=1):
        anterior = self._producto.get_by_id(producto_id)
        if not anterior:
            raise ValueError("Producto no encontrado.")
        result = self._producto.deactivate(producto_id)
        self._audit.registrar(usuario_id, "producto", "DELETE", producto_id,
                              datos_anteriores=dict(anterior))
        return result

    # -- Consultas de producto --

    def get_producto(self, producto_id):
        return self._producto.get_by_id(producto_id)

    def get_producto_por_barras(self, codigo_barras):
        return self._producto.get_by_codigo_barras(codigo_barras)

    def get_productos_completos(self):
        return self._producto.get_completo()

    def buscar_productos(self, termino):
        return self._producto.buscar(termino)

    def get_productos_por_categoria(self, categoria_id):
        return self._producto.get_by_categoria(categoria_id)

    def get_productos_por_marca(self, marca_id):
        return self._producto.get_by_marca(marca_id)

    def get_stock_bajo(self):
        return self._producto.get_stock_bajo()

    def get_proximos_caducar(self, dias=180):
        return self._producto.get_proximos_caducar(dias)

    def get_valor_inventario(self):
        return self._producto.get_valor_inventario()

    # -- Calculos de precio --

    def calcular_precio_con_iva(self, precio_sin_iva):
        return round(precio_sin_iva * (1 + IVA_PORCENTAJE / 100), 2)

    def calcular_precio_sin_iva(self, precio_con_iva):
        return round(precio_con_iva / (1 + IVA_PORCENTAJE / 100), 2)

    def calcular_margen(self, costo, precio_venta):
        if costo <= 0:
            return 0.0
        return round((precio_venta - costo) / costo * 100, 2)

    def sugerir_precio_venta(self, costo, margen_porcentaje=30):
        return round(costo * (1 + margen_porcentaje / 100), 2)

    # ============================
    # PROMOCIONES
    # ============================

    def crear_promocion(self, datos, productos, usuario_id=1):
        if not productos:
            raise ValueError("Una promocion necesita al menos un producto.")
        prom_id = self._promocion.insert(datos)
        for p in productos:
            p["promocion_id"] = prom_id
            self._promo_prod.insert(p)
        self._audit.registrar(usuario_id, "promocion", "INSERT", prom_id, datos_nuevos=datos)
        return self._promocion.get_by_id(prom_id)

    def get_promociones_activas(self):
        return self._promocion.get_activas()

    def get_promocion_para_producto(self, producto_id):
        return self._promocion.get_promocion_producto(producto_id)
