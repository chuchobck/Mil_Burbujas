# -*- coding: utf-8 -*-
"""
Servicio de Auditoría.
Centraliza el registro de acciones del usuario para trazabilidad.
"""
from models.auditoria import AuditoriaModel


class AuditoriaService:
    """Registra acciones del usuario en la tabla auditoria."""

    def __init__(self):
        self._model = AuditoriaModel()

    # ── Registro (con commit propio) ──

    def registrar(self, usuario_id: int, tabla: str, operacion: str,
                  registro_id, datos_anteriores: dict = None,
                  datos_nuevos: dict = None) -> int:
        """Registra una entrada de auditoría (auto-commit)."""
        return self._model.registrar(
            usuario_id, tabla, operacion,
            str(registro_id), datos_anteriores, datos_nuevos
        )

    # ── Registro (dentro de transacción, sin commit) ──

    def registrar_tx(self, usuario_id: int, tabla: str, operacion: str,
                     registro_id, datos_anteriores: dict = None,
                     datos_nuevos: dict = None) -> int:
        """Registra auditoría DENTRO de una transacción activa."""
        return self._model.registrar_in_transaction(
            usuario_id, tabla, operacion,
            str(registro_id), datos_anteriores, datos_nuevos
        )

    # ── Consultas ──

    def get_por_tabla(self, tabla: str) -> list[dict]:
        return self._model.get_by_tabla(tabla)

    def get_por_periodo(self, fecha_inicio: str, fecha_fin: str) -> list[dict]:
        return self._model.get_by_periodo(fecha_inicio, fecha_fin)

    def get_todos(self, limite: int = 200) -> list[dict]:
        sql = """SELECT a.*, u.nombre_completo
                 FROM auditoria a
                 JOIN usuario u ON a.usuario_id = u.usuario_id
                 ORDER BY a.fecha_hora DESC LIMIT ?"""
        return self._model.custom_query(sql, (limite,))
