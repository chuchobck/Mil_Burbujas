# -*- coding: utf-8 -*-
"""
Servicio de Gastos Operativos.
CRUD de gastos del negocio (arriendo, servicios, transporte, etc.).
"""
from models.gasto_operativo import GastoOperativoModel
from services.auditoria_service import AuditoriaService


class GastoService:
    """Gestión de gastos operativos."""

    def __init__(self):
        self._model = GastoOperativoModel()
        self._audit = AuditoriaService()

    # ── CRUD ──

    def registrar(self, datos: dict, usuario_id: int = 1) -> dict:
        """Registra un gasto operativo.

        Args:
            datos: {tipo_gasto, descripcion, monto, fecha_gasto, metodo_pago,
                    comprobante (opcional)}
        """
        if datos.get("monto", 0) <= 0:
            raise ValueError("El monto del gasto debe ser mayor a cero.")

        datos["usuario_id"] = usuario_id
        gid = self._model.insert(datos)
        self._audit.registrar(usuario_id, "gasto_operativo", "INSERT", gid, datos_nuevos=datos)
        return self._model.get_by_id(gid)

    def actualizar(self, gasto_id: int, datos: dict, usuario_id: int = 1) -> dict:
        anterior = self._model.get_by_id(gasto_id)
        if not anterior:
            raise ValueError("Gasto no encontrado.")
        self._model.update(gasto_id, datos)
        self._audit.registrar(usuario_id, "gasto_operativo", "UPDATE", gasto_id,
                              datos_anteriores=dict(anterior), datos_nuevos=datos)
        return self._model.get_by_id(gasto_id)

    def anular(self, gasto_id: int, usuario_id: int = 1) -> bool:
        anterior = self._model.get_by_id(gasto_id)
        if not anterior:
            raise ValueError("Gasto no encontrado.")
        result = self._model.deactivate(gasto_id)
        self._audit.registrar(usuario_id, "gasto_operativo", "DELETE", gasto_id,
                              datos_anteriores=dict(anterior))
        return result

    # ── Consultas ──

    def get_por_id(self, gasto_id: int) -> dict | None:
        return self._model.get_by_id(gasto_id)

    def get_del_dia(self, fecha: str = None) -> list[dict]:
        return self._model.get_del_dia(fecha)

    def get_total_dia(self, fecha: str = None) -> float:
        return self._model.get_total_dia(fecha)

    def get_por_periodo(self, fecha_inicio: str, fecha_fin: str) -> list[dict]:
        return self._model.get_by_periodo(fecha_inicio, fecha_fin)

    def get_total_periodo(self, fecha_inicio: str, fecha_fin: str) -> float:
        return self._model.get_total_periodo(fecha_inicio, fecha_fin)

    def get_por_tipo(self, fecha_inicio: str, fecha_fin: str) -> list[dict]:
        return self._model.get_por_tipo(fecha_inicio, fecha_fin)
