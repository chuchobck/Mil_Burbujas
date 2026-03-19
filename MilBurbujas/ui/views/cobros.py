# -*- coding: utf-8 -*-
"""
Mil Burbujas UI - Vista de Cobros (TX-03 Pago de Cliente).
"""
import customtkinter as ctk
from ui.theme import COLORS, FONTS, PADDING
from ui.widgets import (ScrollableTable, ActionButton, FormField,
                         Dialog, show_toast, CardFrame, hoy)
from services.cobro_service import CobroService
from services.cliente_service import ClienteService


class CobrosView(ctk.CTkFrame):
    def __init__(self, master, user):
        super().__init__(master, fg_color="transparent")
        self.user = user
        self._svc = CobroService()
        self._cli = ClienteService()
        self._build()

    # ------------------------------------------------------------------
    def _build(self):
        top = ctk.CTkFrame(self, fg_color="transparent")
        top.pack(fill="x", padx=PADDING, pady=(PADDING, 8))
        ctk.CTkLabel(top, text="Cobros a Clientes", font=FONTS["title"],
                     text_color=COLORS["text"]).pack(side="left")
        ActionButton(top, text="+ Registrar Cobro", style="success",
                     command=self._dlg_cobro, width=170).pack(side="right")

        self.tbl = ScrollableTable(
            self,
            columns=["ID CxC", "Cliente", "Monto Orig.", "Saldo",
                      "Estado", "Vencimiento"],
            col_widths=[60, 320, 130, 130, 120, 150],
            height=500,
        )
        self.tbl.pack(fill="both", expand=True, padx=PADDING, pady=(0, PADDING))
        self.tbl.on_select(lambda _i, r: self._dlg_cobro(r[0]))
        self._load()

    # ------------------------------------------------------------------
    def _load(self):
        try:
            todas = self._svc.get_cuentas_completas()
        except Exception:
            todas = []
        pendientes = [c for c in todas if c.get("estado_pago") != "PAGADO"]
        rows = []
        for c in pendientes:
            nombre = c.get("cliente_nombre", "")
            rows.append([
                c["cuenta_cobrar_id"],
                nombre,
                "${:.2f}".format(c["monto_original"]),
                "${:.2f}".format(c["saldo_pendiente"]),
                c["estado_pago"],
                c.get("fecha_vencimiento", ""),
            ])
        self.tbl.set_data(rows)

    # ------------------------------------------------------------------
    def _dlg_cobro(self, cc_id=None):
        dlg = Dialog(self, "Registrar Cobro", width=880, height=520)

        try:
            todas = self._svc.get_cuentas_completas()
        except Exception:
            todas = []
        pendientes = [c for c in todas if c.get("estado_pago") != "PAGADO"]

        cc_opts = {}
        for c in pendientes:
            nombre = c.get("cliente_nombre", "")
            label = "CxC #{} - {} - Saldo: ${:.2f}".format(
                c["cuenta_cobrar_id"], nombre, c["saldo_pendiente"])
            cc_opts[label] = c["cuenta_cobrar_id"]

        default = None
        if cc_id:
            default = next((k for k, v in cc_opts.items() if v == cc_id), None)

        ff_cc = FormField(dlg.body, "Cuenta por Cobrar", field_type="combo",
                          values=list(cc_opts.keys()), width=780, default=default)
        ff_cc.pack(pady=6)

        ff_monto = FormField(dlg.body, "Monto a Cobrar ($)",
                             placeholder="0.00", width=780)
        ff_monto.pack(pady=6)

        ff_metodo = FormField(dlg.body, "Metodo Pago", field_type="combo",
                               values=["EFECTIVO", "TRANSFERENCIA"], width=780)
        ff_metodo.pack(pady=6)

        ff_fecha = FormField(dlg.body, "Fecha", placeholder=hoy(), width=780)
        ff_fecha.set(hoy())
        ff_fecha.pack(pady=6)

        def _save():
            try:
                sel = ff_cc.get()
                ccid = cc_opts.get(sel)
                if not ccid:
                    show_toast(dlg, "Selecciona una cuenta", "warning")
                    return
                monto_txt = ff_monto.get()
                if not monto_txt:
                    show_toast(dlg, "Ingresa el monto", "warning")
                    return
                monto = float(monto_txt)
                metodo = ff_metodo.get()
                if not metodo:
                    show_toast(dlg, "Selecciona metodo de pago", "warning")
                    return
                self._svc.registrar_pago(
                    ccid, monto, metodo, ff_fecha.get(),
                    usuario_id=self.user.get("usuario_id", 1),
                )
                dlg.destroy()
                self._load()
                show_toast(self, "Cobro registrado correctamente")
            except Exception as e:
                show_toast(dlg, str(e), "error")

        ActionButton(dlg.footer, "Registrar", "success",
                     command=_save, width=160).pack(side="right", padx=6)
        ActionButton(dlg.footer, "Cancelar", "ghost",
                     command=dlg.destroy, width=120).pack(side="right", padx=6)
