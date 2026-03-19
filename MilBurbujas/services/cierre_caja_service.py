# -*- coding: utf-8 -*-
"""
Servicio de Cierre de Caja.
TX-07: Cierre de Caja diario (transaccion atomica).
Incluye ventas, compras, gastos y cobros de fiados.
"""
from datetime import datetime

from database.connection import DatabaseConnection
from models.cierre_caja import CierreCajaModel
from models.venta import VentaModel
from models.compra import CompraModel
from models.gasto_operativo import GastoOperativoModel
from models.pago_cliente import PagoClienteModel
from services.auditoria_service import AuditoriaService


class CierreCajaService:
    """Cierre de caja diario."""

    def __init__(self):
        self._db = DatabaseConnection()
        self._cierre = CierreCajaModel()
        self._venta = VentaModel()
        self._compra = CompraModel()
        self._gasto = GastoOperativoModel()
        self._pago_cli = PagoClienteModel()
        self._audit = AuditoriaService()

    # ============================
    # PREPARAR CIERRE (vista previa)
    # ============================

    def preparar_cierre(self, fecha=None):
        """Calcula los totales del dia para vista previa antes de cerrar."""
        fecha = fecha or datetime.now().strftime("%Y-%m-%d")

        # Ventas del dia por metodo de pago
        totales_venta = self._venta.get_totales_dia(fecha)

        # Compras del dia (solo contado = efectivo que sale de caja)
        total_compras = self._compra.get_total_contado_dia(fecha)

        # Gastos del dia
        total_gastos = self._gasto.get_total_dia(fecha)
        gastos_detalle = self._gasto.get_del_dia(fecha)

        # Cobros de fiados del dia (pagos de clientes)
        cobros = self._get_cobros_dia(fecha)

        # Efectivo esperado = ventas_efect + cobros_efect - compras_contado - gastos
        efectivo_esperado = round(
            (totales_venta.get("total_efectivo") or 0)
            + cobros["cobros_efectivo"]
            - total_compras
            - total_gastos,
            2
        )

        return {
            "fecha": fecha,
            "total_ventas_efectivo": totales_venta.get("total_efectivo") or 0,
            "total_ventas_transferencia": totales_venta.get("total_transferencia") or 0,
            "total_ventas_credito": totales_venta.get("total_credito") or 0,
            "total_ventas_general": totales_venta.get("total_general") or 0,
            "cantidad_ventas": totales_venta.get("cantidad_ventas") or 0,
            "total_compras": total_compras,
            "total_gastos": total_gastos,
            "gastos_detalle": gastos_detalle,
            "cobros_efectivo": cobros["cobros_efectivo"],
            "cobros_transferencia": cobros["cobros_transferencia"],
            "cobros_total": cobros["cobros_total"],
            "efectivo_esperado": efectivo_esperado,
        }

    def _get_cobros_dia(self, fecha):
        """Obtiene totales de cobros (pagos de clientes) del dia."""
        sql = """SELECT
                    COALESCE(SUM(CASE WHEN metodo_pago = 'EFECTIVO' THEN monto_pago ELSE 0 END), 0) as cobros_efectivo,
                    COALESCE(SUM(CASE WHEN metodo_pago = 'TRANSFERENCIA' THEN monto_pago ELSE 0 END), 0) as cobros_transferencia,
                    COALESCE(SUM(monto_pago), 0) as cobros_total
                 FROM pago_cliente
                 WHERE date(fecha_pago) = ? AND estado = 'ACT'"""
        result = self._db.fetch_one(sql, (fecha,))
        if result:
            return dict(result)
        return {"cobros_efectivo": 0, "cobros_transferencia": 0, "cobros_total": 0}

    # ============================
    # TX-07: CIERRE DE CAJA
    # ============================

    def cerrar_caja(self, efectivo_real, fecha=None,
                    observaciones=None, usuario_id=1):
        """Realiza el cierre de caja del dia (transaccion atomica)."""
        fecha = fecha or datetime.now().strftime("%Y-%m-%d")

        if self._cierre.existe_cierre(fecha):
            raise ValueError("Ya existe un cierre de caja para la fecha {}.".format(fecha))

        # Calcular totales
        datos = self.preparar_cierre(fecha)
        diferencia = round(efectivo_real - datos["efectivo_esperado"], 2)

        try:
            with self._db.transaction():
                cierre_id = self._cierre.insert_in_transaction({
                    "usuario_id": usuario_id,
                    "fecha_cierre": fecha,
                    "total_ventas_efectivo": datos["total_ventas_efectivo"],
                    "total_ventas_transferencia": datos["total_ventas_transferencia"],
                    "total_ventas_credito": datos["total_ventas_credito"],
                    "total_compras": datos["total_compras"],
                    "total_gastos": datos["total_gastos"],
                    "efectivo_esperado": datos["efectivo_esperado"],
                    "efectivo_real": efectivo_real,
                    "diferencia": diferencia,
                    "observaciones": observaciones,
                })

                self._audit.registrar_tx(
                    usuario_id, "cierre_caja", "INSERT", cierre_id,
                    datos_nuevos={
                        "fecha": fecha,
                        "ventas": datos["total_ventas_general"],
                        "esperado": datos["efectivo_esperado"],
                        "real": efectivo_real,
                        "diferencia": diferencia,
                    }
                )

        except ValueError:
            raise
        except Exception as e:
            raise RuntimeError("Error al cerrar caja: {}".format(e))

        return self._cierre.get_by_id(cierre_id)

    # ============================
    # CONSULTAS
    # ============================

    def get_cierre(self, cierre_id):
        return self._cierre.get_by_id(cierre_id)

    def get_cierre_fecha(self, fecha):
        return self._cierre.get_by_fecha(fecha)

    def get_ultimos(self, limite=30):
        return self._cierre.get_ultimos(limite)

    def get_resumen_mensual(self, anio, mes):
        return self._cierre.get_resumen_mensual(anio, mes)

    def existe_cierre(self, fecha):
        return self._cierre.existe_cierre(fecha)
