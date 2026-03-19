# -*- coding: utf-8 -*-
"""
Mil Burbujas UI - Vista de Pagos a Proveedores (TX-04).
"""
import customtkinter as ctk
from ui.theme import COLORS, FONTS, PADDING
from ui.widgets import (ScrollableTable, ActionButton, FormField,
                         Dialog, show_toast, hoy)
from services.pago_service import PagoService
from services.proveedor_service import ProveedorService


class PagosView(ctk.CTkFrame):
    def __init__(self, master, user):
        super().__init__(master, fg_color="transparent")
        self.user = user
        self._svc = PagoService()
        self._prov = ProveedorService()
        self._build()

    # ------------------------------------------------------------------
    def _build(self):
        top = ctk.CTkFrame(self, fg_color="transparent")
        top.pack(fill="x", padx=PADDING, pady=(PADDING, 8))
        ctk.CTkLabel(top, text="Pagos a Proveedores", font=FONTS["title"],
                     text_color=COLORS["text"]).pack(side="left")
        ActionButton(top, text="+ Registrar Pago", style="success",
                     command=self._dlg_pago, width=170).pack(side="right")

        self.tbl = ScrollableTable(
            self,
            columns=["ID CxP", "Proveedor", "Monto Orig.", "Saldo",
                      "Estado", "Vencimiento"],
            col_widths=[60, 320, 130, 130, 120, 150],
            height=500,
        )
        self.tbl.pack(fill="both", expand=True, padx=PADDING, pady=(0, PADDING))
        self.tbl.on_select(lambda _i, r: self._dlg_pago(r[0]))
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
            nombre = c.get("proveedor_nombre", "")
            rows.append([
                c["cuenta_pagar_id"],
                nombre,
                "${:.2f}".format(c["monto_original"]),
                "${:.2f}".format(c["saldo_pendiente"]),
                c["estado_pago"],
                c.get("fecha_vencimiento", ""),
            ])
        self.tbl.set_data(rows)

    # ------------------------------------------------------------------
    def _dlg_pago(self, cp_id=None):
        dlg = Dialog(self, "Pago a Proveedor", width=880, height=560)

        try:
            todas = self._svc.get_cuentas_completas()
        except Exception:
            todas = []
        pendientes = [c for c in todas if c.get("estado_pago") != "PAGADO"]

        cp_opts = {}
        for c in pendientes:
            nombre = c.get("proveedor_nombre", "")
            label = "CxP #{} - {} - Saldo: ${:.2f}".format(
                c["cuenta_pagar_id"], nombre, c["saldo_pendiente"])
            cp_opts[label] = c["cuenta_pagar_id"]

        default = None
        if cp_id:
            default = next((k for k, v in cp_opts.items() if v == cp_id), None)

        ff_cp = FormField(dlg.body, "Cuenta por Pagar", field_type="combo",
                          values=list(cp_opts.keys()), width=780, default=default)
        ff_cp.pack(pady=6)

        ff_monto = FormField(dlg.body, "Monto ($)",
                             placeholder="0.00", width=780)
        ff_monto.pack(pady=6)

        ff_metodo = FormField(dlg.body, "Metodo", field_type="combo",
                               values=["EFECTIVO", "TRANSFERENCIA"], width=780)
        ff_metodo.pack(pady=6)

        ff_fecha = FormField(dlg.body, "Fecha", placeholder=hoy(), width=780)
        ff_fecha.set(hoy())
        ff_fecha.pack(pady=6)

        ff_ref = FormField(dlg.body, "Referencia",
                           placeholder="TRF-...", width=780)
        ff_ref.pack(pady=6)

        def _save():
            try:
                sel = ff_cp.get()
                cpid = cp_opts.get(sel)
                if not cpid:
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
                    cpid, monto, metodo, ff_fecha.get(),
                    referencia=ff_ref.get() or None,
                    usuario_id=self.user.get("usuario_id", 1),
                )
                dlg.destroy()
                self._load()
                show_toast(self, "Pago registrado correctamente")
            except Exception as e:
                show_toast(dlg, str(e), "error")

        ActionButton(dlg.footer, "Registrar", "success",
                     command=_save, width=160).pack(side="right", padx=6)
        ActionButton(dlg.footer, "Cancelar", "ghost",
                     command=dlg.destroy, width=120).pack(side="right", padx=6)
