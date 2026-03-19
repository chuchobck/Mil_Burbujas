# -*- coding: utf-8 -*-
"""
Servicio de Ventas.
TX-02: Registrar Venta (transacción atómica)
TX-06: Anular Venta  (transacción atómica)
"""
from datetime import datetime, timedelta

from config import MONTO_MINIMO_COMPROBANTE
from database.connection import DatabaseConnection
from models.venta import VentaModel
from models.venta_detalle import VentaDetalleModel
from models.producto import ProductoModel
from models.cliente import ClienteModel
from models.movimiento_inventario import MovimientoInventarioModel
from models.cuenta_cobrar import CuentaCobrarModel
from models.promocion import PromocionModel
from models.configuracion import ConfiguracionModel
from services.auditoria_service import AuditoriaService


class VentaService:
    """Gestión completa de ventas (POS)."""

    def __init__(self):
        self._db = DatabaseConnection()
        self._venta = VentaModel()
        self._detalle = VentaDetalleModel()
        self._producto = ProductoModel()
        self._cliente = ClienteModel()
        self._mov = MovimientoInventarioModel()
        self._cc = CuentaCobrarModel()
        self._promocion = PromocionModel()
        self._config = ConfiguracionModel()
        self._audit = AuditoriaService()

    # ══════════════════════════════════════
    # TX-02: REGISTRAR VENTA
    # ══════════════════════════════════════

    def registrar_venta(self, cabecera: dict, items: list[dict],
                        usuario_id: int = 1) -> dict:
        """Registra una venta completa (transacción atómica).

        Args:
            cabecera: {cliente_id (opc), metodo_pago, monto_recibido (si efectivo),
                       referencia_transferencia (si transf), es_credito,
                       observaciones}
            items: [{producto_id, cantidad, precio_unitario (opc, usa precio_venta),
                     descuento_unitario (opc)}]
            usuario_id: ID del usuario vendedor.

        Returns:
            dict con la venta registrada.
        """
        # ── Validaciones ──
        if not items:
            raise ValueError("La venta debe tener al menos un ítem.")

        es_credito = cabecera.get("es_credito", 0)
        cliente_id = cabecera.get("cliente_id")

        # Si es crédito, validar cliente
        if es_credito:
            if not cliente_id:
                raise ValueError("Las ventas a crédito requieren un cliente.")
            cliente = self._cliente.get_by_id(cliente_id)
            if not cliente or cliente["estado"] != "ACT":
                raise ValueError("Cliente no encontrado o inactivo.")
            if not cliente["habilitado_credito"]:
                raise ValueError("El cliente no está habilitado para crédito.")

        # Validar stock y calcular
        subtotal = 0.0
        descuento_total = 0.0

        for item in items:
            prod = self._producto.get_by_id(item["producto_id"])
            if not prod or prod["estado"] != "ACT":
                raise ValueError(f"Producto ID {item['producto_id']} no encontrado o inactivo.")
            if prod["stock_actual"] < item["cantidad"]:
                raise ValueError(
                    f"Stock insuficiente de '{prod['nombre']}'. "
                    f"Disponible: {prod['stock_actual']}, solicitado: {item['cantidad']}"
                )
            if item["cantidad"] <= 0:
                raise ValueError(f"Cantidad inválida para '{prod['nombre']}'.")

            # Precio: usar el enviado o el del catálogo
            precio = item.get("precio_unitario", prod["precio_venta"])
            precio_original = prod["precio_venta"]

            # Verificar precio mínimo
            pvmin = prod.get("precio_venta_minimo") or 0
            if pvmin > 0 and precio < pvmin:
                raise ValueError(
                    f"Precio de '{prod['nombre']}' (${precio:.2f}) está bajo "
                    f"el mínimo permitido (${pvmin:.2f})."
                )

            # Verificar si hay promoción activa
            promo = self._promocion.get_promocion_producto(item["producto_id"])
            if promo and not item.get("precio_unitario"):
                if promo.get("precio_promocional"):
                    precio = promo["precio_promocional"]
                elif promo.get("descuento_porcentaje"):
                    precio = round(precio_original * (1 - promo["descuento_porcentaje"] / 100), 2)

            desc_unit = item.get("descuento_unitario", 0.0)
            item["_precio_unitario"] = precio
            item["_precio_original"] = precio_original
            item["_descuento_unitario"] = desc_unit
            item["_subtotal"] = round((precio - desc_unit) * item["cantidad"], 2)
            item["_promocion_id"] = promo["promocion_id"] if promo else None

            subtotal += round(precio * item["cantidad"], 2)
            descuento_total += round(desc_unit * item["cantidad"], 2)

        total = round(subtotal - descuento_total, 2)

        # Validar crédito del cliente
        if es_credito and cliente_id:
            limite = cliente["limite_credito"] or 0
            saldo = cliente["saldo_pendiente"] or 0
            if total > (limite - saldo):
                raise ValueError(
                    f"Crédito insuficiente. Disponible: ${limite - saldo:.2f}, "
                    f"Venta: ${total:.2f}"
                )

        # Validar pago efectivo
        metodo = cabecera.get("metodo_pago", "EFECTIVO")
        monto_recibido = cabecera.get("monto_recibido")
        cambio = 0.0
        if metodo == "EFECTIVO" and not es_credito:
            if monto_recibido is None:
                raise ValueError("Debe indicar el monto recibido en efectivo.")
            if monto_recibido < total:
                raise ValueError(
                    f"Monto recibido (${monto_recibido:.2f}) es menor al total "
                    f"(${total:.2f})."
                )
            cambio = round(monto_recibido - total, 2)

        # Comprobante obligatorio si > $3.00
        comprobante_emitido = 1 if total >= MONTO_MINIMO_COMPROBANTE else 0

        # ── Transacción ──
        try:
            with self._db.transaction():
                seq = self._config.get_siguiente_secuencia_tx("SECUENCIA_COMPROBANTE")
                numero = cabecera.get("numero_comprobante", f"NV-{seq:06d}")

                # 1. Cabecera
                venta_data = {
                    "numero_comprobante": numero,
                    "cliente_id": cliente_id,
                    "usuario_id": usuario_id,
                    "subtotal": round(subtotal, 2),
                    "descuento": round(descuento_total, 2),
                    "total": total,
                    "metodo_pago": metodo if not es_credito else "CREDITO",
                    "monto_recibido": monto_recibido,
                    "cambio": cambio,
                    "referencia_transferencia": cabecera.get("referencia_transferencia"),
                    "es_credito": es_credito,
                    "comprobante_emitido": comprobante_emitido,
                    "observaciones": cabecera.get("observaciones"),
                }
                venta_id = self._venta.insert_in_transaction(venta_data)

                # 2. Detalles + stock + movimientos
                for item in items:
                    self._detalle.insert_in_transaction({
                        "venta_id": venta_id,
                        "producto_id": item["producto_id"],
                        "promocion_id": item["_promocion_id"],
                        "cantidad": item["cantidad"],
                        "precio_unitario": item["_precio_unitario"],
                        "precio_original": item["_precio_original"],
                        "descuento_unitario": item["_descuento_unitario"],
                        "subtotal": item["_subtotal"],
                    })

                    prod = self._producto.get_by_id(item["producto_id"])
                    stock_ant = prod["stock_actual"]
                    stock_new = stock_ant - int(item["cantidad"])
                    self._producto.actualizar_stock(item["producto_id"], stock_new)

                    self._mov.registrar(
                        producto_id=item["producto_id"],
                        tipo="SALIDA", origen="VENTA",
                        documento_id=venta_id,
                        cantidad=item["cantidad"],
                        stock_anterior=stock_ant,
                        stock_posterior=stock_new
                    )

                # 3. Cuenta por cobrar (si fiado)
                if es_credito and cliente_id:
                    fecha_hoy = datetime.now().strftime("%Y-%m-%d")
                    cli = self._cliente.get_by_id(cliente_id)
                    freq = cli.get("frecuencia_pago", "QUINCENAL")
                    dias_venc = {"QUINCENAL": 15, "MENSUAL": 30, "FIN_DE_MES": 30}.get(freq, 15)
                    fecha_venc = (datetime.now() + timedelta(days=dias_venc)).strftime("%Y-%m-%d")

                    seq_cc = self._config.get_siguiente_secuencia_tx("SECUENCIA_CUENTA_COBRAR")
                    self._cc.insert_in_transaction({
                        "numero_cuenta": f"CC-{seq_cc:06d}",
                        "cliente_id": cliente_id,
                        "venta_id": venta_id,
                        "monto_original": total,
                        "saldo_pendiente": total,
                        "fecha_emision": fecha_hoy,
                        "fecha_vencimiento": fecha_venc,
                        "estado_pago": "PENDIENTE",
                    })

                    # Actualizar saldo del cliente
                    nuevo_saldo = (cli["saldo_pendiente"] or 0) + total
                    self._cliente.actualizar_saldo(cliente_id, nuevo_saldo)

                # 4. Auditoría
                self._audit.registrar_tx(
                    usuario_id, "venta", "INSERT", venta_id,
                    datos_nuevos={"total": total, "items": len(items),
                                  "metodo": metodo, "credito": es_credito}
                )

        except ValueError:
            raise
        except Exception as e:
            raise RuntimeError(f"Error al registrar venta: {e}") from e

        return self._venta.get_by_id(venta_id)

    # ══════════════════════════════════════
    # TX-06: ANULAR VENTA
    # ══════════════════════════════════════

    def anular_venta(self, venta_id: int, usuario_id: int = 1) -> dict:
        """Anula una venta y revierte stock (transacción atómica)."""
        venta = self._venta.get_by_id(venta_id)
        if not venta:
            raise ValueError("Venta no encontrada.")
        if venta["estado"] == "ANULADA":
            raise ValueError("La venta ya está anulada.")

        detalles = self._detalle.get_by_venta(venta_id)

        try:
            with self._db.transaction():
                # 1. Marcar venta como ANULADA
                self._venta.update_in_transaction(venta_id, {"estado": "ANULADA"})

                # 2. Revertir stock
                for det in detalles:
                    prod = self._producto.get_by_id(det["producto_id"])
                    stock_ant = prod["stock_actual"]
                    stock_new = stock_ant + int(det["cantidad"])
                    self._producto.actualizar_stock(det["producto_id"], stock_new)

                    self._mov.registrar(
                        producto_id=det["producto_id"],
                        tipo="ENTRADA", origen="ANULACION",
                        documento_id=venta_id,
                        cantidad=det["cantidad"],
                        stock_anterior=stock_ant,
                        stock_posterior=stock_new
                    )

                # 3. Anular cuenta por cobrar si existe
                cc = self._cc.get_by_venta(venta_id)
                if cc:
                    saldo_cc = cc["saldo_pendiente"]
                    self._cc.update_in_transaction(cc["cuenta_cobrar_id"], {
                        "estado": "INA", "estado_pago": "PAGADO"
                    })

                    # Reducir saldo del cliente
                    if venta["cliente_id"]:
                        cli = self._cliente.get_by_id(venta["cliente_id"])
                        nuevo_saldo = max(0, (cli["saldo_pendiente"] or 0) - saldo_cc)
                        self._cliente.actualizar_saldo(venta["cliente_id"], nuevo_saldo)

                # 4. Auditoría
                self._audit.registrar_tx(
                    usuario_id, "venta", "DELETE", venta_id,
                    datos_anteriores={"total": venta["total"]}
                )

        except ValueError:
            raise
        except Exception as e:
            raise RuntimeError(f"Error al anular venta: {e}") from e

        return self._venta.get_by_id(venta_id)

    # ══════════════════════════════════════
    # CONSULTAS
    # ══════════════════════════════════════

    def get_por_id(self, venta_id: int) -> dict | None:
        return self._venta.get_by_id(venta_id)

    def get_completas(self) -> list[dict]:
        return self._venta.get_completas()

    def get_detalles(self, venta_id: int) -> list[dict]:
        return self._detalle.get_by_venta(venta_id)

    def get_del_dia(self, fecha: str = None) -> list[dict]:
        return self._venta.get_del_dia(fecha)

    def get_por_periodo(self, fecha_inicio: str, fecha_fin: str) -> list[dict]:
        return self._venta.get_by_periodo(fecha_inicio, fecha_fin)

    def get_total_periodo(self, fecha_inicio: str, fecha_fin: str) -> float:
        return self._venta.get_total_periodo(fecha_inicio, fecha_fin)

    def get_totales_dia(self, fecha: str = None) -> dict:
        return self._venta.get_totales_dia(fecha)

    def get_mas_vendidos(self, limite: int = 10) -> list[dict]:
        return self._detalle.get_mas_vendidos(limite)

    def get_historial_ventas_producto(self, producto_id: int) -> list[dict]:
        return self._detalle.get_by_producto(producto_id)
