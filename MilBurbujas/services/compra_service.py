# -*- coding: utf-8 -*-
"""
Servicio de Compras.
TX-01: Registrar Compra (transacción atómica)
TX-08: Anular Compra  (transacción atómica)
"""
from datetime import datetime, timedelta

from config import IVA_PORCENTAJE
from database.connection import DatabaseConnection
from models.compra import CompraModel
from models.compra_detalle import CompraDetalleModel
from models.producto import ProductoModel
from models.proveedor import ProveedorModel
from models.proveedor_producto import ProveedorProductoModel
from models.movimiento_inventario import MovimientoInventarioModel
from models.cuenta_pagar import CuentaPagarModel
from models.configuracion import ConfiguracionModel
from services.auditoria_service import AuditoriaService


class CompraService:
    """Gestión completa de compras a proveedores."""

    def __init__(self):
        self._db = DatabaseConnection()
        self._compra = CompraModel()
        self._detalle = CompraDetalleModel()
        self._producto = ProductoModel()
        self._proveedor = ProveedorModel()
        self._pp = ProveedorProductoModel()
        self._mov = MovimientoInventarioModel()
        self._cp = CuentaPagarModel()
        self._config = ConfiguracionModel()
        self._audit = AuditoriaService()

    # ══════════════════════════════════════
    # TX-01: REGISTRAR COMPRA
    # ══════════════════════════════════════

    def registrar_compra(self, cabecera: dict, items: list[dict],
                         usuario_id: int = 1) -> dict:
        """Registra una compra completa (transacción atómica).

        Args:
            cabecera: {numero_factura, proveedor_id, fecha_compra, tipo_pago,
                       plazo_credito_dias (si crédito), observaciones}
            items: [{producto_id, cantidad, precio_unitario, incluye_iva,
                     fecha_caducidad_lote (opcional)}]
            usuario_id: ID del usuario que registra.

        Returns:
            dict con la compra registrada.

        Raises:
            ValueError: si alguna validación falla.
        """
        # ── Validaciones previas ──
        proveedor = self._proveedor.get_by_id(cabecera["proveedor_id"])
        if not proveedor or proveedor["estado"] != "ACT":
            raise ValueError("Proveedor no encontrado o inactivo.")

        if not items:
            raise ValueError("La compra debe tener al menos un ítem.")

        existente = self._compra.get_by_factura_proveedor(
            cabecera["numero_factura"], cabecera["proveedor_id"]
        )
        if existente:
            raise ValueError(
                f"Ya existe la factura '{cabecera['numero_factura']}' "
                f"para este proveedor."
            )

        # Validar productos
        for item in items:
            prod = self._producto.get_by_id(item["producto_id"])
            if not prod or prod["estado"] != "ACT":
                raise ValueError(f"Producto ID {item['producto_id']} no encontrado o inactivo.")
            if item["cantidad"] <= 0:
                raise ValueError(f"Cantidad inválida para {prod['nombre']}.")

        # ── Cálculos ──
        subtotal_sin_iva = 0.0
        monto_iva_total = 0.0

        for item in items:
            if item.get("incluye_iva", 1):
                precio_sin = round(item["precio_unitario"] / (1 + IVA_PORCENTAJE / 100), 4)
                iva_unit = item["precio_unitario"] - precio_sin
            else:
                precio_sin = item["precio_unitario"]
                iva_unit = round(precio_sin * IVA_PORCENTAJE / 100, 4)

            item["_precio_sin_iva"] = round(precio_sin, 4)
            item["_subtotal"] = round(precio_sin * item["cantidad"], 2)
            item["_iva"] = round(iva_unit * item["cantidad"], 2)
            subtotal_sin_iva += item["_subtotal"]
            monto_iva_total += item["_iva"]

        total = round(subtotal_sin_iva + monto_iva_total, 2)

        # ── Transacción ──
        try:
            with self._db.transaction():
                # 1. Cabecera
                compra_data = {
                    "numero_factura": cabecera["numero_factura"],
                    "proveedor_id": cabecera["proveedor_id"],
                    "usuario_id": usuario_id,
                    "fecha_compra": cabecera.get("fecha_compra",
                                                  datetime.now().strftime("%Y-%m-%d")),
                    "subtotal_sin_iva": round(subtotal_sin_iva, 2),
                    "monto_iva": round(monto_iva_total, 2),
                    "total": total,
                    "tipo_pago": cabecera.get("tipo_pago", "CONTADO"),
                    "plazo_credito_dias": cabecera.get("plazo_credito_dias", 0),
                    "observaciones": cabecera.get("observaciones"),
                }
                compra_id = self._compra.insert_in_transaction(compra_data)

                # 2. Detalles + stock + movimientos
                for item in items:
                    self._detalle.insert_in_transaction({
                        "compra_id": compra_id,
                        "producto_id": item["producto_id"],
                        "cantidad": item["cantidad"],
                        "precio_unitario": item["precio_unitario"],
                        "incluye_iva": item.get("incluye_iva", 1),
                        "precio_sin_iva": item["_precio_sin_iva"],
                        "subtotal": item["_subtotal"],
                        "fecha_caducidad_lote": item.get("fecha_caducidad_lote"),
                    })

                    # Actualizar stock
                    prod = self._producto.get_by_id(item["producto_id"])
                    stock_ant = prod["stock_actual"]
                    stock_new = stock_ant + int(item["cantidad"])
                    self._producto.actualizar_stock(item["producto_id"], stock_new)

                    # Movimiento de inventario
                    self._mov.registrar(
                        producto_id=item["producto_id"],
                        tipo="ENTRADA", origen="COMPRA",
                        documento_id=compra_id,
                        cantidad=item["cantidad"],
                        stock_anterior=stock_ant,
                        stock_posterior=stock_new
                    )

                    # Actualizar fecha de caducidad del producto si viene en el lote
                    fecha_lote = item.get("fecha_caducidad_lote")
                    if fecha_lote:
                        prod_actual = self._producto.get_by_id(item["producto_id"])
                        fecha_actual = prod_actual.get("fecha_caducidad") if prod_actual else None
                        # Usar la mas proxima (mas temprana) entre la actual y la nueva
                        if not fecha_actual or fecha_lote < fecha_actual:
                            self._producto.update_in_transaction(
                                item["producto_id"],
                                {"fecha_caducidad": fecha_lote}
                            )

                    # Actualizar o crear relación proveedor-producto
                    pp = self._pp.get_by_proveedor_producto(
                        cabecera["proveedor_id"], item["producto_id"]
                    )
                    if pp:
                        self._pp.update_in_transaction(pp["proveedor_producto_id"], {
                            "precio_compra": item["_precio_sin_iva"],
                            "precio_compra_con_iva": item["precio_unitario"],
                            "fecha_ultimo_precio": compra_data["fecha_compra"],
                        })
                    else:
                        # Crear la relación automáticamente al comprar por primera vez
                        self._pp.insert_in_transaction({
                            "proveedor_id": cabecera["proveedor_id"],
                            "producto_id": item["producto_id"],
                            "precio_compra": item["_precio_sin_iva"],
                            "precio_compra_con_iva": item["precio_unitario"],
                            "incluye_iva": item.get("incluye_iva", 1),
                            "es_proveedor_principal": 0,
                            "fecha_ultimo_precio": compra_data["fecha_compra"],
                        })

                    # Sincronizar precio de compra en el producto (costo de referencia)
                    # Usa precio SIN IVA como costo real y recalcula precio_venta_minimo
                    costo_ref = item["_precio_sin_iva"]
                    try:
                        margen_cfg = self._config.get_valor("MARGEN_GANANCIA_DEFAULT")
                        margen = float(margen_cfg) if margen_cfg else 23.0
                    except Exception:
                        margen = 23.0
                    pvm = round(costo_ref * (1 + margen / 100), 2) if costo_ref > 0 else 0.0
                    self._producto.update_in_transaction(
                        item["producto_id"],
                        {
                            "precio_referencia_compra": round(costo_ref, 2),
                            "precio_venta_minimo": pvm,
                        }
                    )

                # 3. Cuenta por pagar (si crédito)
                if cabecera.get("tipo_pago") == "CREDITO":
                    plazo = cabecera.get("plazo_credito_dias", proveedor.get("plazo_credito_dias", 30))
                    fecha_compra = datetime.strptime(
                        compra_data["fecha_compra"], "%Y-%m-%d"
                    )
                    fecha_venc = (fecha_compra + timedelta(days=plazo)).strftime("%Y-%m-%d")
                    seq = self._config.get_siguiente_secuencia_tx("SECUENCIA_CUENTA_PAGAR")
                    self._cp.insert_in_transaction({
                        "numero_cuenta": f"CP-{seq:06d}",
                        "proveedor_id": cabecera["proveedor_id"],
                        "compra_id": compra_id,
                        "monto_original": total,
                        "saldo_pendiente": total,
                        "fecha_emision": compra_data["fecha_compra"],
                        "fecha_vencimiento": fecha_venc,
                        "estado_pago": "PENDIENTE",
                    })

                # 4. Auditoría
                self._audit.registrar_tx(
                    usuario_id, "compra", "INSERT", compra_id,
                    datos_nuevos={"total": total, "items": len(items)}
                )

        except ValueError:
            raise
        except Exception as e:
            raise RuntimeError(f"Error al registrar compra: {e}") from e

        return self._compra.get_by_id(compra_id)

    # ══════════════════════════════════════
    # TX-08: ANULAR COMPRA
    # ══════════════════════════════════════

    def anular_compra(self, compra_id: int, usuario_id: int = 1) -> dict:
        """Anula una compra y revierte stock (transacción atómica).

        Raises:
            ValueError: si la compra no puede anularse.
        """
        compra = self._compra.get_by_id(compra_id)
        if not compra:
            raise ValueError("Compra no encontrada.")
        if compra["estado"] == "ANULADA":
            raise ValueError("La compra ya está anulada.")

        detalles = self._detalle.get_by_compra(compra_id)

        # Verificar que hay stock suficiente para revertir
        for det in detalles:
            prod = self._producto.get_by_id(det["producto_id"])
            if prod["stock_actual"] < det["cantidad"]:
                raise ValueError(
                    f"No se puede anular: stock insuficiente de '{prod['nombre']}'. "
                    f"Stock actual: {prod['stock_actual']}, requerido devolver: {det['cantidad']}"
                )

        try:
            with self._db.transaction():
                # 1. Marcar compra como ANULADA
                self._compra.update_in_transaction(compra_id, {"estado": "ANULADA"})

                # 2. Revertir stock
                for det in detalles:
                    prod = self._producto.get_by_id(det["producto_id"])
                    stock_ant = prod["stock_actual"]
                    stock_new = stock_ant - int(det["cantidad"])
                    self._producto.actualizar_stock(det["producto_id"], stock_new)

                    self._mov.registrar(
                        producto_id=det["producto_id"],
                        tipo="SALIDA", origen="ANULACION",
                        documento_id=compra_id,
                        cantidad=det["cantidad"],
                        stock_anterior=stock_ant,
                        stock_posterior=stock_new
                    )

                # 3. Anular cuenta por pagar si existe
                cp = self._cp.get_by_compra(compra_id)
                if cp:
                    self._cp.update_in_transaction(cp["cuenta_pagar_id"], {
                        "estado": "INA", "estado_pago": "PAGADO"
                    })

                # 4. Auditoría
                self._audit.registrar_tx(
                    usuario_id, "compra", "DELETE", compra_id,
                    datos_anteriores={"total": compra["total"]}
                )

        except ValueError:
            raise
        except Exception as e:
            raise RuntimeError(f"Error al anular compra: {e}") from e

        return self._compra.get_by_id(compra_id)

    # ══════════════════════════════════════
    # CONSULTAS
    # ══════════════════════════════════════

    def get_por_id(self, compra_id: int) -> dict | None:
        return self._compra.get_by_id(compra_id)

    def get_completas(self) -> list[dict]:
        return self._compra.get_completas()

    def get_detalles(self, compra_id: int) -> list[dict]:
        return self._detalle.get_by_compra(compra_id)

    def get_por_proveedor(self, proveedor_id: int) -> list[dict]:
        return self._compra.get_by_proveedor(proveedor_id)

    def get_por_periodo(self, fecha_inicio: str, fecha_fin: str) -> list[dict]:
        return self._compra.get_by_periodo(fecha_inicio, fecha_fin)

    def get_total_periodo(self, fecha_inicio: str, fecha_fin: str) -> float:
        return self._compra.get_total_periodo(fecha_inicio, fecha_fin)

    def get_historial_compras_producto(self, producto_id: int) -> list[dict]:
        return self._detalle.get_by_producto(producto_id)
