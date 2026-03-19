# -*- coding: utf-8 -*-
"""
Servicio de Proveedores.
Gestión de proveedores, relación proveedor-producto y precios de referencia.
"""
from models.proveedor import ProveedorModel
from models.proveedor_producto import ProveedorProductoModel
from models.precio_referencia import PrecioReferenciaModel
from services.auditoria_service import AuditoriaService


class ProveedorService:
    """CRUD de proveedores y gestión de precios."""

    def __init__(self):
        self._prov = ProveedorModel()
        self._pp = ProveedorProductoModel()
        self._precio_ref = PrecioReferenciaModel()
        self._audit = AuditoriaService()

    # ══════════════════════════════════════
    # PROVEEDORES
    # ══════════════════════════════════════

    def crear(self, datos: dict, usuario_id: int = 1) -> dict:
        if self._prov.exists_by_field("ruc_cedula", datos.get("ruc_cedula", "")):
            raise ValueError(f"Ya existe un proveedor con RUC/Cédula '{datos['ruc_cedula']}'.")
        pid = self._prov.insert(datos)
        self._audit.registrar(usuario_id, "proveedor", "INSERT", pid, datos_nuevos=datos)
        return self._prov.get_by_id(pid)

    def actualizar(self, proveedor_id: int, datos: dict, usuario_id: int = 1) -> dict:
        anterior = self._prov.get_by_id(proveedor_id)
        if not anterior:
            raise ValueError("Proveedor no encontrado.")
        self._prov.update(proveedor_id, datos)
        self._audit.registrar(usuario_id, "proveedor", "UPDATE", proveedor_id,
                              datos_anteriores=dict(anterior), datos_nuevos=datos)
        return self._prov.get_by_id(proveedor_id)

    def desactivar(self, proveedor_id: int, usuario_id: int = 1) -> bool:
        if self._prov.tiene_cuentas_pendientes(proveedor_id):
            raise ValueError("No se puede desactivar: tiene cuentas por pagar pendientes.")
        anterior = self._prov.get_by_id(proveedor_id)
        result = self._prov.deactivate(proveedor_id)
        self._audit.registrar(usuario_id, "proveedor", "DELETE", proveedor_id,
                              datos_anteriores=dict(anterior))
        return result

    def get_por_id(self, proveedor_id: int) -> dict | None:
        return self._prov.get_by_id(proveedor_id)

    def get_por_ruc(self, ruc_cedula: str) -> dict | None:
        return self._prov.get_by_ruc(ruc_cedula)

    def get_todos(self) -> list[dict]:
        return self._prov.get_all()

    def buscar(self, termino: str) -> list[dict]:
        return self._prov.buscar(termino)

    def get_con_saldo_pendiente(self) -> list[dict]:
        return self._prov.get_con_saldo_pendiente()

    # ══════════════════════════════════════
    # PROVEEDOR ↔ PRODUCTO
    # ══════════════════════════════════════

    def asignar_producto(self, datos: dict, usuario_id: int = 1) -> dict:
        """Asigna un producto a un proveedor (con precio de compra)."""
        existente = self._pp.get_by_proveedor_producto(
            datos["proveedor_id"], datos["producto_id"]
        )
        if existente:
            raise ValueError("Este proveedor ya tiene asignado este producto.")
        ppid = self._pp.insert(datos)
        self._audit.registrar(usuario_id, "proveedor_producto", "INSERT", ppid, datos_nuevos=datos)
        return self._pp.get_by_id(ppid)

    def actualizar_precio_proveedor(self, prov_prod_id: int, datos: dict,
                                     usuario_id: int = 1) -> dict:
        """Actualiza precio de compra de un producto con un proveedor."""
        anterior = self._pp.get_by_id(prov_prod_id)
        if not anterior:
            raise ValueError("Relación proveedor-producto no encontrada.")
        self._pp.update(prov_prod_id, datos)
        self._audit.registrar(usuario_id, "proveedor_producto", "UPDATE", prov_prod_id,
                              datos_anteriores=dict(anterior), datos_nuevos=datos)
        return self._pp.get_by_id(prov_prod_id)

    def get_proveedores_de_producto(self, producto_id: int) -> list[dict]:
        return self._pp.get_proveedores_de_producto(producto_id)

    def get_productos_de_proveedor(self, proveedor_id: int) -> list[dict]:
        return self._pp.get_productos_de_proveedor(proveedor_id)

    def get_proveedor_principal(self, producto_id: int) -> dict | None:
        return self._pp.get_proveedor_principal(producto_id)

    # ══════════════════════════════════════
    # PRECIOS DE REFERENCIA (supermercados)
    # ══════════════════════════════════════

    def registrar_precio_referencia(self, datos: dict, usuario_id: int = 1) -> dict:
        """Registra un precio de referencia (supermercado, tienda, online)."""
        prid = self._precio_ref.insert(datos)
        self._audit.registrar(usuario_id, "precio_referencia", "INSERT", prid, datos_nuevos=datos)
        return self._precio_ref.get_by_id(prid)

    def get_precios_referencia(self, producto_id: int) -> list[dict]:
        return self._precio_ref.get_by_producto(producto_id)

    def get_comparativo_precios(self, producto_id: int) -> list[dict]:
        """Comparativo: proveedores vs supermercados para un producto."""
        return self._precio_ref.get_comparativo(producto_id)
