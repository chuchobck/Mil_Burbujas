# -*- coding: utf-8 -*-
"""
Servicio de Clientes.
Gestión de clientes y validaciones de crédito (fiados).
"""
from models.cliente import ClienteModel
from services.auditoria_service import AuditoriaService


class ClienteService:
    """CRUD de clientes con control de crédito."""

    def __init__(self):
        self._model = ClienteModel()
        self._audit = AuditoriaService()

    # ── CRUD ──

    def crear(self, datos: dict, usuario_id: int = 1) -> dict:
        if self._model.exists_by_field("cedula", datos.get("cedula", "")):
            raise ValueError(f"Ya existe un cliente con cédula '{datos['cedula']}'.")
        cid = self._model.insert(datos)
        self._audit.registrar(usuario_id, "cliente", "INSERT", cid, datos_nuevos=datos)
        return self._model.get_by_id(cid)

    def actualizar(self, cliente_id: int, datos: dict, usuario_id: int = 1) -> dict:
        anterior = self._model.get_by_id(cliente_id)
        if not anterior:
            raise ValueError("Cliente no encontrado.")
        self._model.update(cliente_id, datos)
        self._audit.registrar(usuario_id, "cliente", "UPDATE", cliente_id,
                              datos_anteriores=dict(anterior), datos_nuevos=datos)
        return self._model.get_by_id(cliente_id)

    def desactivar(self, cliente_id: int, usuario_id: int = 1) -> bool:
        cliente = self._model.get_by_id(cliente_id)
        if not cliente:
            raise ValueError("Cliente no encontrado.")
        if cliente["saldo_pendiente"] > 0:
            raise ValueError("No se puede desactivar: el cliente tiene saldo pendiente.")
        result = self._model.deactivate(cliente_id)
        self._audit.registrar(usuario_id, "cliente", "DELETE", cliente_id,
                              datos_anteriores=dict(cliente))
        return result

    # ── Consultas ──

    def get_por_id(self, cliente_id: int) -> dict | None:
        return self._model.get_by_id(cliente_id)

    def get_por_cedula(self, cedula: str) -> dict | None:
        return self._model.get_by_cedula(cedula)

    def get_todos(self) -> list[dict]:
        return self._model.get_all()

    def buscar(self, termino: str) -> list[dict]:
        return self._model.buscar(termino)

    def get_con_credito(self) -> list[dict]:
        return self._model.get_con_credito()

    def get_con_saldo_pendiente(self) -> list[dict]:
        return self._model.get_con_saldo_pendiente()

    # ── Validaciones de crédito ──

    def puede_recibir_credito(self, cliente_id: int, monto: float) -> tuple[bool, str]:
        """Verifica si el cliente puede recibir un crédito adicional.

        Retorna (puede, mensaje_razon).
        """
        cliente = self._model.get_by_id(cliente_id)
        if not cliente:
            return False, "Cliente no encontrado."
        if not cliente["habilitado_credito"]:
            return False, "El cliente no está habilitado para crédito."

        limite = cliente["limite_credito"] or 0
        saldo = cliente["saldo_pendiente"] or 0
        disponible = limite - saldo

        if monto > disponible:
            return False, (
                f"Crédito insuficiente. Límite: ${limite:.2f}, "
                f"Saldo: ${saldo:.2f}, Disponible: ${disponible:.2f}"
            )

        return True, "OK"
