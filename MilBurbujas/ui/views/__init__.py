# -*- coding: utf-8 -*-
"""Mil Burbujas UI â€" views package."""
from ui.views.dashboard import DashboardView
from ui.views.catalogo import CatalogoView
from ui.views.ventas import VentasView
from ui.views.compras import ComprasView
from ui.views.clientes import ClientesView
from ui.views.proveedores import ProveedoresView
from ui.views.inventario import InventarioView
from ui.views.cobros import CobrosView
from ui.views.pagos import PagosView
from ui.views.gastos import GastosView
from ui.views.cierre_caja import CierreCajaView
from ui.views.reportes import ReportesView

__all__ = [
    "DashboardView", "CatalogoView", "VentasView", "ComprasView",
    "ClientesView", "ProveedoresView", "InventarioView", "CobrosView",
    "PagosView", "GastosView", "CierreCajaView", "ReportesView",
]
