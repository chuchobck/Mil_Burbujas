# -*- coding: utf-8 -*-
"""DAO - Configuración (Core/Seguridad)."""
from .base_model import BaseModel


class ConfiguracionModel(BaseModel):
    TABLE_NAME = "configuracion"
    PK_COLUMN = "config_id"
    HAS_ESTADO = False

    def get_valor(self, clave: str) -> str | None:
        result = self.get_one_by_field("clave", clave)
        return result["valor"] if result else None

    def set_valor(self, clave: str, valor: str) -> bool:
        result = self.get_one_by_field("clave", clave)
        if result:
            return self.update(result["config_id"], {
                "valor": valor,
                "fecha_modificacion": "datetime('now', 'localtime')"
            })
        return False

    def get_valor_numerico(self, clave: str) -> float:
        valor = self.get_valor(clave)
        return float(valor) if valor else 0.0

    def get_siguiente_secuencia(self, clave_secuencia: str) -> int:
        """Obtiene e incrementa una secuencia (autocommit, fuera de TX)."""
        valor_actual = int(self.get_valor(clave_secuencia) or "0")
        siguiente = valor_actual + 1
        self.set_valor(clave_secuencia, str(siguiente))
        return siguiente

    def get_siguiente_secuencia_tx(self, clave_secuencia: str) -> int:
        """Obtiene e incrementa una secuencia DENTRO de una transaccion activa.

        Usa execute_in_transaction para no romper la TX del llamador.
        Si la clave no existe, la crea automaticamente.
        """
        sql_sel = "SELECT config_id, valor FROM configuracion WHERE clave = ?"
        row = self.db.fetch_one_in_transaction(sql_sel, (clave_secuencia,))
        valor_actual = int(row["valor"]) if row else 0
        siguiente = valor_actual + 1
        if row:
            sql_upd = "UPDATE configuracion SET valor = ? WHERE config_id = ?"
            self.db.execute_in_transaction(sql_upd, (str(siguiente), row["config_id"]))
        else:
            sql_ins = ("INSERT INTO configuracion (clave, valor, descripcion, tipo_dato) "
                       "VALUES (?, ?, ?, ?)")
            self.db.execute_in_transaction(
                sql_ins, (clave_secuencia, str(siguiente), "Secuencia auto", "INTEGER"))
        return siguiente
