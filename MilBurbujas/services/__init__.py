# -*- coding: utf-8 -*-
"""
Mil Burbujas - Capa de Servicios (Lógica de Negocio).

Servicios disponibles:
    AuditoriaService      - Registro de acciones (trazabilidad)
    UsuarioService        - Gestión de usuarios y autenticación
    CatalogoService       - Productos, categorías, marcas, líneas, unidades
    ProveedorService      - Proveedores, proveedor-producto, precios ref.
    ClienteService        - Clientes y control de crédito
    CompraService         - TX-01 Registrar Compra | TX-08 Anular Compra
    VentaService          - TX-02 Registrar Venta  | TX-06 Anular Venta
    CobroService          - TX-03 Pago de Cliente
    PagoService           - TX-04 Pago a Proveedor
    InventarioService     - TX-05 Ajuste de Inventario
    CierreCajaService     - TX-07 Cierre de Caja
    GastoService          - Gastos operativos
    ReporteService        - Reportes y dashboard
"""
from services.auditoria_service import AuditoriaService
from services.usuario_service import UsuarioService
from services.catalogo_service import CatalogoService
from services.proveedor_service import ProveedorService
from services.cliente_service import ClienteService
from services.compra_service import CompraService
from services.venta_service import VentaService
from services.cobro_service import CobroService
from services.pago_service import PagoService
from services.inventario_service import InventarioService
from services.cierre_caja_service import CierreCajaService
from services.gasto_service import GastoService
from services.reporte_service import ReporteService

__all__ = [
    "AuditoriaService",
    "UsuarioService",
    "CatalogoService",
    "ProveedorService",
    "ClienteService",
    "CompraService",
    "VentaService",
    "CobroService",
    "PagoService",
    "InventarioService",
    "CierreCajaService",
    "GastoService",
    "ReporteService",
]
