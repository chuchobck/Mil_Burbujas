# -*- coding: utf-8 -*-
"""
Servicio de Inventario.
TX-05: Ajuste de Inventario (transacción atómica).
Consultas de stock, movimientos y alertas.
"""
from database.connection import DatabaseConnection
from models.producto import ProductoModel
from models.ajuste_inventario import AjusteInventarioModel
from models.movimiento_inventario import MovimientoInventarioModel
from models.configuracion import ConfiguracionModel
from services.auditoria_service import AuditoriaService


class InventarioService:
    """Gestión de inventario y ajustes."""

    def __init__(self):
        self._db = DatabaseConnection()
        self._producto = ProductoModel()
        self._ajuste = AjusteInventarioModel()
        self._mov = MovimientoInventarioModel()
        self._config = ConfiguracionModel()
        self._audit = AuditoriaService()

    # ══════════════════════════════════════
    # TX-05: AJUSTE DE INVENTARIO
    # ══════════════════════════════════════

    def registrar_ajuste(self, producto_id: int, tipo_ajuste: str,
                         cantidad: int, motivo: str,
                         producto_cambio_id: int = None,
                         usuario_id: int = 1) -> dict:
        """Registra un ajuste de inventario (transacción atómica).

        Tipos de ajuste:
            CONSUMO_PERSONAL  → cantidad negativa (sale del stock)
            DANIO             → cantidad negativa
            CADUCIDAD         → cantidad negativa
            MERMA             → cantidad negativa
            DEVOLUCION_CAMBIO → cantidad negativa (puede tener producto_cambio_id)
            ENTRADA_MANUAL    → cantidad positiva (entra al stock)
            CORRECCION        → positiva o negativa

        Args:
            producto_id: Producto afectado.
            tipo_ajuste: Tipo del ajuste.
            cantidad: Unidades (negativo = sale, positivo = entra).
            motivo: Descripción del motivo.
            producto_cambio_id: Producto de reemplazo (DEVOLUCION_CAMBIO).
            usuario_id: Usuario que registra.

        Returns:
            dict con el ajuste registrado.
        """
        producto = self._producto.get_by_id(producto_id)
        if not producto or producto["estado"] != "ACT":
            raise ValueError("Producto no encontrado o inactivo.")

        if cantidad == 0:
            raise ValueError("La cantidad no puede ser cero.")

        nuevo_stock = producto["stock_actual"] + cantidad
        if nuevo_stock < 0:
            raise ValueError(
                f"Stock insuficiente. Actual: {producto['stock_actual']}, "
                f"ajuste: {cantidad}, resultaría: {nuevo_stock}"
            )

        # Determinar tipo de movimiento
        tipo_mov = "SALIDA" if cantidad < 0 else "ENTRADA"
        cantidad_abs = abs(cantidad)

        try:
            with self._db.transaction():
                seq = self._config.get_siguiente_secuencia_tx("SECUENCIA_AJUSTE")

                # 1. Registrar ajuste
                ajuste_id = self._ajuste.insert_in_transaction({
                    "numero_ajuste": f"AJ-{seq:06d}",
                    "producto_id": producto_id,
                    "usuario_id": usuario_id,
                    "tipo_ajuste": tipo_ajuste,
                    "cantidad": cantidad,
                    "motivo": motivo,
                    "producto_cambio_id": producto_cambio_id,
                })

                # 2. Actualizar stock
                self._producto.actualizar_stock(producto_id, nuevo_stock)

                # 3. Movimiento de inventario
                self._mov.registrar(
                    producto_id=producto_id,
                    tipo=tipo_mov, origen="AJUSTE",
                    documento_id=ajuste_id,
                    cantidad=cantidad_abs,
                    stock_anterior=producto["stock_actual"],
                    stock_posterior=nuevo_stock
                )

                # 4. Si es devolución con cambio, agregar stock del producto nuevo
                if producto_cambio_id and tipo_ajuste == "DEVOLUCION_CAMBIO":
                    prod_cambio = self._producto.get_by_id(producto_cambio_id)
                    if prod_cambio:
                        stock_cambio_ant = prod_cambio["stock_actual"]
                        stock_cambio_new = stock_cambio_ant - cantidad_abs
                        if stock_cambio_new < 0:
                            raise ValueError(
                                f"Stock insuficiente del producto de cambio "
                                f"'{prod_cambio['nombre']}'."
                            )
                        self._producto.actualizar_stock(producto_cambio_id, stock_cambio_new)
                        self._mov.registrar(
                            producto_id=producto_cambio_id,
                            tipo="SALIDA", origen="AJUSTE",
                            documento_id=ajuste_id,
                            cantidad=cantidad_abs,
                            stock_anterior=stock_cambio_ant,
                            stock_posterior=stock_cambio_new
                        )

                # 5. Auditoría
                self._audit.registrar_tx(
                    usuario_id, "ajuste_inventario", "INSERT", ajuste_id,
                    datos_nuevos={
                        "tipo": tipo_ajuste, "cantidad": cantidad,
                        "producto": producto["nombre"],
                        "stock_anterior": producto["stock_actual"],
                        "stock_posterior": nuevo_stock,
                    }
                )

        except ValueError:
            raise
        except Exception as e:
            raise RuntimeError(f"Error al registrar ajuste: {e}") from e

        return self._ajuste.get_by_id(ajuste_id)

    # ══════════════════════════════════════
    # CONSULTAS DE INVENTARIO
    # ══════════════════════════════════════

    def get_stock_bajo(self) -> list[dict]:
        """Productos con stock ≤ stock mínimo."""
        return self._producto.get_stock_bajo()

    def get_proximos_caducar(self, dias: int = None) -> list[dict]:
        """Productos perecederos próximos a caducar."""
        if dias is None:
            dias = int(self._config.get_valor("DIAS_ALERTA_CADUCIDAD") or "180")
        return self._producto.get_proximos_caducar(dias)

    def get_valor_inventario(self) -> dict:
        """Valor total del inventario a costo y a precio de venta."""
        return self._producto.get_valor_inventario()

    def get_movimientos_producto(self, producto_id: int, limite: int = 50) -> list[dict]:
        """Historial de movimientos de un producto."""
        return self._mov.get_by_producto(producto_id, limite)

    def get_ajustes(self) -> list[dict]:
        return self._ajuste.get_completos()

    def get_ajustes_producto(self, producto_id: int) -> list[dict]:
        return self._ajuste.get_by_producto(producto_id)

    def get_ajustes_por_tipo(self, tipo: str) -> list[dict]:
        return self._ajuste.get_by_tipo(tipo)

    def get_ajustes_del_dia(self, fecha: str = None) -> list[dict]:
        return self._ajuste.get_del_dia(fecha)

    # ══════════════════════════════════════
    # ALERTAS
    # ══════════════════════════════════════

    def get_alertas(self) -> dict:
        """Retorna un resumen de alertas del inventario."""
        stock_bajo = self.get_stock_bajo()
        prox_caducar = self.get_proximos_caducar()
        return {
            "stock_bajo": stock_bajo,
            "total_stock_bajo": len(stock_bajo),
            "proximos_caducar": prox_caducar,
            "total_proximos_caducar": len(prox_caducar),
            "hay_alertas": len(stock_bajo) > 0 or len(prox_caducar) > 0,
        }
