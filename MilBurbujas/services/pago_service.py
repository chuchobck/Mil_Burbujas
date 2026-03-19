# -*- coding: utf-8 -*-
"""
Servicio de Pagos a Proveedores (Cuentas por Pagar).
TX-04: Registrar Pago a Proveedor (transacción atómica).
"""
from database.connection import DatabaseConnection
from models.cuenta_pagar import CuentaPagarModel
from models.pago_proveedor import PagoProveedorModel
from services.auditoria_service import AuditoriaService


class PagoService:
    """Gestión de pagos a proveedores."""

    def __init__(self):
        self._db = DatabaseConnection()
        self._cp = CuentaPagarModel()
        self._pago = PagoProveedorModel()
        self._audit = AuditoriaService()

    # ══════════════════════════════════════
    # TX-04: REGISTRAR PAGO A PROVEEDOR
    # ══════════════════════════════════════

    def registrar_pago(self, cuenta_pagar_id: int, monto: float,
                       metodo_pago: str, fecha_pago: str,
                       referencia: str = None,
                       usuario_id: int = 1) -> dict:
        """Registra un pago (total o parcial) a un proveedor.

        Args:
            cuenta_pagar_id: ID de la cuenta por pagar.
            monto: Monto a abonar.
            metodo_pago: 'EFECTIVO' o 'TRANSFERENCIA'.
            fecha_pago: Fecha del pago (YYYY-MM-DD).
            referencia: Referencia de transferencia (si aplica).
            usuario_id: Usuario que registra.

        Returns:
            dict con el pago registrado.
        """
        cuenta = self._cp.get_by_id(cuenta_pagar_id)
        if not cuenta:
            raise ValueError("Cuenta por pagar no encontrada.")
        if cuenta["estado"] != "ACT":
            raise ValueError("La cuenta está inactiva o anulada.")
        if cuenta["estado_pago"] == "PAGADO":
            raise ValueError("La cuenta ya está completamente pagada.")

        if monto <= 0:
            raise ValueError("El monto debe ser mayor a cero.")
        if monto > cuenta["saldo_pendiente"]:
            raise ValueError(
                f"El monto (${monto:.2f}) excede el saldo pendiente "
                f"(${cuenta['saldo_pendiente']:.2f})."
            )

        nuevo_saldo = round(cuenta["saldo_pendiente"] - monto, 2)
        estado_pago = "PAGADO" if nuevo_saldo == 0 else "PARCIAL"

        try:
            with self._db.transaction():
                # 1. Registrar pago
                pago_id = self._pago.insert_in_transaction({
                    "cuenta_pagar_id": cuenta_pagar_id,
                    "usuario_id": usuario_id,
                    "monto_pago": monto,
                    "metodo_pago": metodo_pago,
                    "referencia_transferencia": referencia,
                    "fecha_pago": fecha_pago,
                })

                # 2. Actualizar cuenta
                self._cp.update_in_transaction(cuenta_pagar_id, {
                    "saldo_pendiente": nuevo_saldo,
                    "estado_pago": estado_pago,
                })

                # 3. Auditoría
                self._audit.registrar_tx(
                    usuario_id, "pago_proveedor", "INSERT", pago_id,
                    datos_nuevos={
                        "monto": monto, "cuenta": cuenta_pagar_id,
                        "saldo_anterior": cuenta["saldo_pendiente"],
                        "saldo_nuevo": nuevo_saldo,
                    }
                )

        except ValueError:
            raise
        except Exception as e:
            raise RuntimeError(f"Error al registrar pago: {e}") from e

        return self._pago.get_by_id(pago_id)

    # ══════════════════════════════════════
    # CONSULTAS
    # ══════════════════════════════════════

    def get_cuenta(self, cuenta_pagar_id: int) -> dict | None:
        return self._cp.get_by_id(cuenta_pagar_id)

    def get_cuentas_completas(self) -> list[dict]:
        return self._cp.get_completas()

    def get_pendientes_por_proveedor(self, proveedor_id: int) -> list[dict]:
        return self._cp.get_pendientes_por_proveedor(proveedor_id)

    def get_vencidas(self) -> list[dict]:
        return self._cp.get_vencidas()

    def get_total_pendiente(self) -> float:
        return self._cp.get_total_pendiente()

    def get_pagos_de_cuenta(self, cuenta_pagar_id: int) -> list[dict]:
        return self._pago.get_by_cuenta(cuenta_pagar_id)

    def get_total_pagado(self, cuenta_pagar_id: int) -> float:
        return self._pago.get_total_pagado(cuenta_pagar_id)
