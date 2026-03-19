# -*- coding: utf-8 -*-
"""
Mil Burbujas UI — Vista de Gastos Operativos (TX-05).
"""
import customtkinter as ctk
from ui.theme import COLORS, FONTS, PADDING
from ui.widgets import (ScrollableTable, ActionButton, FormField,
                         Dialog, show_toast, SearchBar, hoy)
from services.gasto_service import GastoService


class GastosView(ctk.CTkFrame):
    def __init__(self, master, user):
        super().__init__(master, fg_color="transparent")
        self.user = user
        self._svc = GastoService()
        self._build()

    def _build(self):
        top = ctk.CTkFrame(self, fg_color="transparent")
        top.pack(fill="x", padx=PADDING, pady=(PADDING, 8))
        ctk.CTkLabel(top, text="🧾  Gastos Operativos", font=FONTS["title"],
                     text_color=COLORS["text"]).pack(side="left")
        ActionButton(top, text="➕ Nuevo Gasto", style="success",
                     command=self._dlg_gasto, width=160).pack(side="right")

        self.search = SearchBar(self, placeholder="Buscar gasto …",
                                on_search=self._filtrar)
        self.search.pack(fill="x", padx=PADDING, pady=(0, 6))

        self.tbl = ScrollableTable(self,
            columns=["ID", "Tipo", "Descripción", "Monto", "Método Pago", "Fecha"],
            col_widths=[50, 160, 340, 110, 140, 120], height=480)
        self.tbl.pack(fill="both", expand=True, padx=PADDING, pady=(0, PADDING))
        self._load()

    def _load(self, datos=None):
        rows_raw = datos or self._svc.get_por_periodo("2020-01-01", hoy())
        rows = []
        for g in rows_raw:
            rows.append([g["gasto_id"], g["tipo_gasto"], g.get("descripcion", ""),
                         f"${g['monto']:.2f}", g["metodo_pago"], g["fecha_gasto"]])
        self.tbl.set_data(rows)

    def _filtrar(self, txt):
        all_g = self._svc.get_por_periodo("2020-01-01", hoy())
        t = txt.lower()
        filtered = [g for g in all_g
                    if t in g.get("tipo_gasto", "").lower()
                    or t in g.get("descripcion", "").lower()
                    or t in str(g.get("monto", ""))]
        self._load(filtered)

    def _dlg_gasto(self):
        dlg = Dialog(self, "Registrar Gasto", width=880, height=560)

        ff_tipo = FormField(dlg.body, "Tipo", field_type="combo",
                            values=["ARRIENDO", "SERVICIOS", "TRANSPORTE",
                                    "ALIMENTACION", "OTROS"], width=780)
        ff_tipo.pack(pady=6)
        ff_desc = FormField(dlg.body, "Descripción", placeholder="Detalle", width=780)
        ff_desc.pack(pady=6)
        ff_monto = FormField(dlg.body, "Monto ($)", placeholder="0.00", width=780)
        ff_monto.pack(pady=6)
        ff_metodo = FormField(dlg.body, "Método Pago", field_type="combo",
                               values=["EFECTIVO", "TRANSFERENCIA"], width=780)
        ff_metodo.pack(pady=6)
        ff_fecha = FormField(dlg.body, "Fecha", placeholder=hoy(), width=780)
        ff_fecha.set(hoy())
        ff_fecha.pack(pady=6)

        def _save():
            try:
                self._svc.registrar({
                    "tipo_gasto": ff_tipo.get(),
                    "descripcion": ff_desc.get(),
                    "monto": float(ff_monto.get() or 0),
                    "fecha_gasto": ff_fecha.get(),
                    "metodo_pago": ff_metodo.get(),
                }, usuario_id=self.user["usuario_id"])
                dlg.destroy()
                self._load()
                show_toast(self, "Gasto registrado ✅")
            except Exception as e:
                show_toast(dlg, str(e), "error")

        ActionButton(dlg.footer, "💾 Guardar", "success", command=_save, width=160).pack(side="right", padx=6)
        ActionButton(dlg.footer, "Cancelar", "ghost", command=dlg.destroy, width=120).pack(side="right", padx=6)
