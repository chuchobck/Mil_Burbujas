# -*- coding: utf-8 -*-
"""
Servicio de Cobros (Cuentas por Cobrar).
TX-03: Registrar Pago de Cliente (transacción atómica).
"""
from database.connection import DatabaseConnection
from models.cuenta_cobrar import CuentaCobrarModel
from models.pago_cliente import PagoClienteModel
from models.cliente import ClienteModel
from services.auditoria_service import AuditoriaService


class CobroService:
    """Gestión de fiados y pagos de clientes."""

    def __init__(self):
        self._db = DatabaseConnection()
        self._cc = CuentaCobrarModel()
        self._pago = PagoClienteModel()
        self._cliente = ClienteModel()
        self._audit = AuditoriaService()

    # ══════════════════════════════════════
    # TX-03: REGISTRAR PAGO DE CLIENTE
    # ══════════════════════════════════════

    def registrar_pago(self, cuenta_cobrar_id: int, monto: float,
                       metodo_pago: str, fecha_pago: str,
                       referencia: str = None,
                       usuario_id: int = 1) -> dict:
        """Registra un pago (total o parcial) de un cliente.

        Args:
            cuenta_cobrar_id: ID de la cuenta por cobrar.
            monto: Monto a abonar.
            metodo_pago: 'EFECTIVO' o 'TRANSFERENCIA'.
            fecha_pago: Fecha del pago (YYYY-MM-DD).
            referencia: Referencia de transferencia (si aplica).
            usuario_id: Usuario que registra.

        Returns:
            dict con el pago registrado.
        """
        cuenta = self._cc.get_by_id(cuenta_cobrar_id)
        if not cuenta:
            raise ValueError("Cuenta por cobrar no encontrada.")
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
                    "cuenta_cobrar_id": cuenta_cobrar_id,
                    "usuario_id": usuario_id,
                    "monto_pago": monto,
                    "metodo_pago": metodo_pago,
                    "referencia_transferencia": referencia,
                    "fecha_pago": fecha_pago,
                })

                # 2. Actualizar cuenta
                self._cc.update_in_transaction(cuenta_cobrar_id, {
                    "saldo_pendiente": nuevo_saldo,
                    "estado_pago": estado_pago,
                })

                # 3. Actualizar saldo del cliente
                cliente = self._cliente.get_by_id(cuenta["cliente_id"])
                nuevo_saldo_cli = max(0, round((cliente["saldo_pendiente"] or 0) - monto, 2))
                self._cliente.actualizar_saldo(cuenta["cliente_id"], nuevo_saldo_cli)

                # 4. Auditoría
                self._audit.registrar_tx(
                    usuario_id, "pago_cliente", "INSERT", pago_id,
                    datos_nuevos={
                        "monto": monto, "cuenta": cuenta_cobrar_id,
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

    def get_cuenta(self, cuenta_cobrar_id: int) -> dict | None:
        return self._cc.get_by_id(cuenta_cobrar_id)

    def get_cuentas_completas(self) -> list[dict]:
        return self._cc.get_completas()

    def get_pendientes_por_cliente(self, cliente_id: int) -> list[dict]:
        return self._cc.get_pendientes_por_cliente(cliente_id)

    def get_vencidas(self) -> list[dict]:
        return self._cc.get_vencidas()

    def get_total_pendiente(self) -> float:
        return self._cc.get_total_pendiente()

    def get_pagos_de_cuenta(self, cuenta_cobrar_id: int) -> list[dict]:
        return self._pago.get_by_cuenta(cuenta_cobrar_id)

    def get_total_pagado(self, cuenta_cobrar_id: int) -> float:
        return self._pago.get_total_pagado(cuenta_cobrar_id)

    def get_resumen_cliente(self, cliente_id: int) -> dict:
        """Resumen financiero de un cliente."""
        cliente = self._cliente.get_by_id(cliente_id)
        cuentas = self._cc.get_pendientes_por_cliente(cliente_id)
        return {
            "cliente": cliente,
            "cuentas_pendientes": cuentas,
            "total_adeudado": sum(c["saldo_pendiente"] for c in cuentas),
            "limite_credito": cliente["limite_credito"] or 0,
            "disponible": (cliente["limite_credito"] or 0) - (cliente["saldo_pendiente"] or 0),
        }
