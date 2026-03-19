# -*- coding: utf-8 -*-
"""
Mil Burbujas UI - Cierre de Caja (TX-07).
Muestra KPIs de ventas, compras, gastos, cobros y efectivo esperado.
"""
import customtkinter as ctk
from ui.theme import COLORS, FONTS, PADDING
from ui.widgets import (ScrollableTable, ActionButton, FormField,
                         CardFrame, KPIBox, Dialog, show_toast, hoy)
from services.cierre_caja_service import CierreCajaService


class CierreCajaView(ctk.CTkFrame):
    def __init__(self, master, user):
        super().__init__(master, fg_color="transparent")
        self.user = user
        self._svc = CierreCajaService()
        self._preview = None
        self._build()

    def _build(self):
        top = ctk.CTkFrame(self, fg_color="transparent")
        top.pack(fill="x", padx=PADDING, pady=(PADDING, 8))
        ctk.CTkLabel(top, text="Cierre de Caja", font=FONTS["title"],
                     text_color=COLORS["text"]).pack(side="left")
        ActionButton(top, text="Preparar Cierre", style="primary",
                     command=self._preparar, width=170).pack(side="right", padx=(0, 8))

        # -- KPIs del cierre preparado --
        self.kpi_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.kpi_frame.pack(fill="x", padx=PADDING, pady=(0, 8))
        self.kpi_ventas = KPIBox(self.kpi_frame, "Ventas Efectivo", "$0.00", COLORS["success"])
        self.kpi_ventas.grid(row=0, column=0, padx=6, pady=6, sticky="nsew")
        self.kpi_transfer = KPIBox(self.kpi_frame, "Ventas Transfer.", "$0.00", COLORS["info"])
        self.kpi_transfer.grid(row=0, column=1, padx=6, pady=6, sticky="nsew")
        self.kpi_compras = KPIBox(self.kpi_frame, "Compras Contado", "$0.00", COLORS["danger"])
        self.kpi_compras.grid(row=0, column=2, padx=6, pady=6, sticky="nsew")
        self.kpi_gastos = KPIBox(self.kpi_frame, "Gastos", "$0.00", COLORS["warning"])
        self.kpi_gastos.grid(row=0, column=3, padx=6, pady=6, sticky="nsew")
        self.kpi_cobros = KPIBox(self.kpi_frame, "Cobros Fiados", "$0.00", "#6C63FF")
        self.kpi_cobros.grid(row=0, column=4, padx=6, pady=6, sticky="nsew")
        self.kpi_esperado = KPIBox(self.kpi_frame, "Esperado Caja", "$0.00", COLORS["primary"])
        self.kpi_esperado.grid(row=0, column=5, padx=6, pady=6, sticky="nsew")
        for c in range(6):
            self.kpi_frame.columnconfigure(c, weight=1)

        # -- Historial de cierres --
        ctk.CTkLabel(self, text="Historial de Cierres", font=FONTS["heading"],
                     text_color=COLORS["text"]).pack(anchor="w", padx=PADDING, pady=(8, 4))
        self.tbl = ScrollableTable(self,
            columns=["ID", "Fecha", "Esperado", "Real", "Diferencia", "Observaciones"],
            col_widths=[50, 120, 120, 120, 120, 380], height=340)
        self.tbl.pack(fill="both", expand=True, padx=PADDING, pady=(0, PADDING))
        self._load_hist()

    def _load_hist(self):
        cierres = self._svc.get_ultimos(20)
        rows = []
        for c in cierres:
            rows.append([c["cierre_id"], c["fecha_cierre"],
                         "${:.2f}".format(c["efectivo_esperado"]),
                         "${:.2f}".format(c["efectivo_real"]),
                         "${:.2f}".format(c["diferencia"]),
                         c.get("observaciones", "")])
        self.tbl.set_data(rows)

    def _preparar(self):
        try:
            if self._svc.existe_cierre(hoy()):
                show_toast(self, "Ya existe cierre para hoy", "warning")
                return
            p = self._svc.preparar_cierre(hoy())
            self._preview = p
            # Actualizar KPIs con las claves CORRECTAS del servicio
            self.kpi_ventas.set_value("${:.2f}".format(p.get("total_ventas_efectivo", 0)))
            self.kpi_transfer.set_value("${:.2f}".format(p.get("total_ventas_transferencia", 0)))
            self.kpi_compras.set_value("${:.2f}".format(p.get("total_compras", 0)))
            self.kpi_gastos.set_value("${:.2f}".format(p.get("total_gastos", 0)))
            self.kpi_cobros.set_value("${:.2f}".format(p.get("cobros_efectivo", 0)))
            self.kpi_esperado.set_value("${:.2f}".format(p.get("efectivo_esperado", 0)))
            self._dlg_cerrar(p)
        except Exception as e:
            show_toast(self, str(e), "error")

    def _dlg_cerrar(self, p):
        dlg = Dialog(self, "Cerrar Caja", width=880, height=520)

        # Resumen
        info = ctk.CTkFrame(dlg.body, fg_color=COLORS["bg_main"], corner_radius=8)
        info.pack(fill="x", padx=12, pady=(8, 10))

        lines = [
            ("Ventas Efectivo:", "${:.2f}".format(p.get("total_ventas_efectivo", 0))),
            ("Ventas Transferencia:", "${:.2f}".format(p.get("total_ventas_transferencia", 0))),
            ("Ventas Credito:", "${:.2f}".format(p.get("total_ventas_credito", 0))),
            ("Cobros de Fiados:", "${:.2f}".format(p.get("cobros_efectivo", 0))),
            ("Compras Contado:", "${:.2f}".format(p.get("total_compras", 0))),
            ("Gastos:", "${:.2f}".format(p.get("total_gastos", 0))),
        ]
        for label, valor in lines:
            row = ctk.CTkFrame(info, fg_color="transparent")
            row.pack(fill="x", padx=12, pady=2)
            ctk.CTkLabel(row, text=label, font=FONTS["body"],
                         text_color=COLORS["text"], width=220, anchor="w").pack(side="left")
            ctk.CTkLabel(row, text=valor, font=FONTS["body"],
                         text_color=COLORS["primary"]).pack(side="left")

        # Esperado destacado
        ctk.CTkLabel(dlg.body, text="Efectivo esperado: ${:.2f}".format(p.get("efectivo_esperado", 0)),
                     font=("Segoe UI", 18, "bold"), text_color=COLORS["primary"]).pack(pady=(4, 8))

        ff_real = FormField(dlg.body, "Efectivo Real ($)", placeholder="0.00", width=780)
        ff_real.pack(pady=6)
        ff_obs = FormField(dlg.body, "Observaciones", field_type="textbox", width=780)
        ff_obs.pack(pady=6)

        def _cerrar():
            try:
                self._svc.cerrar_caja(
                    efectivo_real=float(ff_real.get() or 0),
                    fecha=hoy(),
                    observaciones=ff_obs.get(),
                    usuario_id=self.user["usuario_id"])
                dlg.destroy()
                self._load_hist()
                self._preview = None
                show_toast(self, "Caja cerrada correctamente")
            except Exception as e:
                show_toast(dlg, str(e), "error")

        ActionButton(dlg.footer, "Cerrar Caja", "danger", command=_cerrar, width=160).pack(side="right", padx=6)
        ActionButton(dlg.footer, "Cancelar", "ghost", command=dlg.destroy, width=120).pack(side="right", padx=6)
