# -*- coding: utf-8 -*-
"""
Servicio de Reportes.
Consultas consolidadas y métricas del negocio para dashboards.
"""
from models.producto import ProductoModel
from models.venta import VentaModel
from models.venta_detalle import VentaDetalleModel
from models.compra import CompraModel
from models.cliente import ClienteModel
from models.proveedor import ProveedorModel
from models.cuenta_cobrar import CuentaCobrarModel
from models.cuenta_pagar import CuentaPagarModel
from models.gasto_operativo import GastoOperativoModel
from models.cierre_caja import CierreCajaModel
from models.movimiento_inventario import MovimientoInventarioModel


class ReporteService:
    """Reportes y métricas del negocio."""

    def __init__(self):
        self._producto = ProductoModel()
        self._venta = VentaModel()
        self._vd = VentaDetalleModel()
        self._compra = CompraModel()
        self._cliente = ClienteModel()
        self._proveedor = ProveedorModel()
        self._cc = CuentaCobrarModel()
        self._cp = CuentaPagarModel()
        self._gasto = GastoOperativoModel()
        self._cierre = CierreCajaModel()
        self._mov = MovimientoInventarioModel()

    # ══════════════════════════════════════
    # DASHBOARD PRINCIPAL
    # ══════════════════════════════════════

    def get_dashboard(self, fecha: str = None) -> dict:
        """Indicadores principales para el dashboard de inicio.

        Retorna un dict con métricas del día actual.
        """
        totales = self._venta.get_totales_dia(fecha)
        inventario = self._producto.get_valor_inventario()
        stock_bajo = self._producto.get_stock_bajo()
        cuentas_vencidas_cc = self._cc.get_vencidas()
        cuentas_vencidas_cp = self._cp.get_vencidas()

        return {
            # Ventas del día
            "ventas_hoy": totales["total_general"] or 0,
            "ventas_efectivo": totales["total_efectivo"] or 0,
            "ventas_transferencia": totales["total_transferencia"] or 0,
            "ventas_credito": totales["total_credito"] or 0,
            "cantidad_ventas": totales["cantidad_ventas"] or 0,

            # Inventario
            "total_productos": inventario["total_productos"] or 0,
            "total_unidades": inventario["total_unidades"] or 0,
            "valor_inventario_costo": inventario["valor_costo"] or 0,
            "valor_inventario_venta": inventario["valor_venta"] or 0,

            # Alertas
            "productos_stock_bajo": len(stock_bajo),
            "cuentas_cobrar_vencidas": len(cuentas_vencidas_cc),
            "cuentas_pagar_vencidas": len(cuentas_vencidas_cp),

            # Totales deuda
            "total_por_cobrar": self._cc.get_total_pendiente(),
            "total_por_pagar": self._cp.get_total_pendiente(),
        }

    # ══════════════════════════════════════
    # REPORTE DE VENTAS
    # ══════════════════════════════════════

    def reporte_ventas_periodo(self, fecha_inicio: str, fecha_fin: str) -> dict:
        """Reporte detallado de ventas en un período."""
        ventas = self._venta.get_by_periodo(fecha_inicio, fecha_fin)
        total = self._venta.get_total_periodo(fecha_inicio, fecha_fin)
        mas_vendidos = self._vd.get_mas_vendidos(10)

        return {
            "periodo": {"inicio": fecha_inicio, "fin": fecha_fin},
            "ventas": ventas,
            "total_ventas": total,
            "cantidad_ventas": len(ventas),
            "promedio_venta": round(total / len(ventas), 2) if ventas else 0,
            "productos_mas_vendidos": mas_vendidos,
        }

    # ══════════════════════════════════════
    # REPORTE DE COMPRAS
    # ══════════════════════════════════════

    def reporte_compras_periodo(self, fecha_inicio: str, fecha_fin: str) -> dict:
        """Reporte detallado de compras en un período."""
        compras = self._compra.get_by_periodo(fecha_inicio, fecha_fin)
        total = self._compra.get_total_periodo(fecha_inicio, fecha_fin)

        return {
            "periodo": {"inicio": fecha_inicio, "fin": fecha_fin},
            "compras": compras,
            "total_compras": total,
            "cantidad_compras": len(compras),
        }

    # ══════════════════════════════════════
    # REPORTE DE GASTOS
    # ══════════════════════════════════════

    def reporte_gastos_periodo(self, fecha_inicio: str, fecha_fin: str) -> dict:
        """Reporte de gastos operativos por tipo y período."""
        gastos = self._gasto.get_by_periodo(fecha_inicio, fecha_fin)
        total = self._gasto.get_total_periodo(fecha_inicio, fecha_fin)
        por_tipo = self._gasto.get_por_tipo(fecha_inicio, fecha_fin)

        return {
            "periodo": {"inicio": fecha_inicio, "fin": fecha_fin},
            "gastos": gastos,
            "total_gastos": total,
            "por_tipo": por_tipo,
        }

    # ══════════════════════════════════════
    # REPORTE FINANCIERO (UTILIDAD)
    # ══════════════════════════════════════

    def reporte_utilidad_periodo(self, fecha_inicio: str, fecha_fin: str) -> dict:
        """Cálculo de utilidad bruta y neta en un período.

        Utilidad bruta  = Ventas - Costo de ventas
        Utilidad neta   = Utilidad bruta - Gastos operativos
        """
        total_ventas = self._venta.get_total_periodo(fecha_inicio, fecha_fin)
        total_compras = self._compra.get_total_periodo(fecha_inicio, fecha_fin)
        total_gastos = self._gasto.get_total_periodo(fecha_inicio, fecha_fin)

        utilidad_bruta = round(total_ventas - total_compras, 2)
        utilidad_neta = round(utilidad_bruta - total_gastos, 2)

        return {
            "periodo": {"inicio": fecha_inicio, "fin": fecha_fin},
            "total_ventas": total_ventas,
            "total_compras": total_compras,
            "utilidad_bruta": utilidad_bruta,
            "total_gastos": total_gastos,
            "utilidad_neta": utilidad_neta,
            "margen_bruto": round(utilidad_bruta / total_ventas * 100, 2) if total_ventas else 0,
            "margen_neto": round(utilidad_neta / total_ventas * 100, 2) if total_ventas else 0,
        }

    # ══════════════════════════════════════
    # REPORTE DE INVENTARIO
    # ══════════════════════════════════════

    def reporte_inventario(self) -> dict:
        """Reporte completo del estado del inventario."""
        valor = self._producto.get_valor_inventario()
        stock_bajo = self._producto.get_stock_bajo()
        prox_caducar = self._producto.get_proximos_caducar()

        return {
            "valor_inventario": valor,
            "stock_bajo": stock_bajo,
            "proximos_caducar": prox_caducar,
        }

    # ══════════════════════════════════════
    # REPORTE DE CUENTAS
    # ══════════════════════════════════════

    def reporte_cuentas_cobrar(self) -> dict:
        """Resumen de cuentas por cobrar (fiados)."""
        cuentas = self._cc.get_completas()
        vencidas = self._cc.get_vencidas()
        total = self._cc.get_total_pendiente()
        clientes_deudores = self._cliente.get_con_saldo_pendiente()

        return {
            "cuentas": cuentas,
            "vencidas": vencidas,
            "total_pendiente": total,
            "total_vencido": sum(c["saldo_pendiente"] for c in vencidas),
            "clientes_deudores": clientes_deudores,
        }

    def reporte_cuentas_pagar(self) -> dict:
        """Resumen de cuentas por pagar a proveedores."""
        cuentas = self._cp.get_completas()
        vencidas = self._cp.get_vencidas()
        total = self._cp.get_total_pendiente()
        proveedores = self._proveedor.get_con_saldo_pendiente()

        return {
            "cuentas": cuentas,
            "vencidas": vencidas,
            "total_pendiente": total,
            "total_vencido": sum(c["saldo_pendiente"] for c in vencidas),
            "proveedores_deuda": proveedores,
        }

    # ══════════════════════════════════════
    # REPORTE DE CIERRES
    # ══════════════════════════════════════

    def reporte_cierres_mensual(self, anio: int, mes: int) -> dict:
        """Resumen mensual de cierres de caja."""
        resumen = self._cierre.get_resumen_mensual(anio, mes)
        return resumen or {
            "ventas_efectivo": 0, "ventas_transferencia": 0,
            "ventas_credito": 0, "compras": 0, "gastos": 0,
            "diferencia_acumulada": 0, "dias_cerrados": 0,
        }
