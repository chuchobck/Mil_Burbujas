# -*- coding: utf-8 -*-
"""
Mil Burbujas UI — Reportes (RPT-01 ~ RPT-08).
"""
import customtkinter as ctk
from ui.theme import COLORS, FONTS, PADDING
from ui.widgets import (ScrollableTable, ActionButton, FormField,
                         CardFrame, KPIBox, show_toast, hoy)
from services.reporte_service import ReporteService


class ReportesView(ctk.CTkFrame):
    def __init__(self, master, user):
        super().__init__(master, fg_color="transparent")
        self.user = user
        self._svc = ReporteService()
        self._build()

    def _build(self):
        top = ctk.CTkFrame(self, fg_color="transparent")
        top.pack(fill="x", padx=PADDING, pady=(PADDING, 8))
        ctk.CTkLabel(top, text="📊  Reportes", font=FONTS["title"],
                     text_color=COLORS["text"]).pack(side="left")

        # — Rango de fechas —
        rng = ctk.CTkFrame(self, fg_color="transparent")
        rng.pack(fill="x", padx=PADDING, pady=(0, 8))
        ctk.CTkLabel(rng, text="Desde:", font=FONTS["body"]).pack(side="left", padx=(0, 4))
        self.ff_desde = FormField(rng, "", placeholder="YYYY-MM-DD", width=130)
        self.ff_desde.set(hoy()[:8] + "01")
        self.ff_desde.pack(side="left", padx=(0, 12))
        ctk.CTkLabel(rng, text="Hasta:", font=FONTS["body"]).pack(side="left", padx=(0, 4))
        self.ff_hasta = FormField(rng, "", placeholder="YYYY-MM-DD", width=130)
        self.ff_hasta.set(hoy())
        self.ff_hasta.pack(side="left", padx=(0, 12))
        ActionButton(rng, text="🔄 Actualizar", style="primary", width=130,
                     command=self._refresh).pack(side="left", padx=4)

        # — KPIs resumen —
        kf = ctk.CTkFrame(self, fg_color="transparent")
        kf.pack(fill="x", padx=PADDING, pady=(0, 8))
        self.kpi_v = KPIBox(kf, "Ventas", "$0", COLORS["success"])
        self.kpi_c = KPIBox(kf, "Compras", "$0", COLORS["danger"])
        self.kpi_g = KPIBox(kf, "Gastos", "$0", COLORS["warning"])
        self.kpi_u = KPIBox(kf, "Utilidad", "$0", COLORS["primary"])
        for i, k in enumerate([self.kpi_v, self.kpi_c, self.kpi_g, self.kpi_u]):
            k.grid(row=0, column=i, padx=6, pady=4, sticky="nsew")
            kf.columnconfigure(i, weight=1)

        # — Tabs de detalle —
        self.tabs = ctk.CTkTabview(self, fg_color=COLORS["bg_main"],
                                    segmented_button_fg_color=COLORS["bg_card"],
                                    segmented_button_selected_color=COLORS["primary"])
        self.tabs.pack(fill="both", expand=True, padx=PADDING, pady=(0, PADDING))

        for name in ["Ventas", "Compras", "Gastos", "Inventario", "CxC", "CxP"]:
            self.tabs.add(name)

        self.tbl_ventas = ScrollableTable(self.tabs.tab("Ventas"),
            columns=["ID", "Fecha", "Cliente", "Total", "Método Pago", "Estado"],
            col_widths=[50, 120, 300, 110, 140, 120], height=320)
        self.tbl_ventas.pack(fill="both", expand=True, padx=PADDING, pady=6)

        self.tbl_compras = ScrollableTable(self.tabs.tab("Compras"),
            columns=["ID", "Fecha", "Proveedor", "Total", "Tipo Pago", "Estado"],
            col_widths=[50, 120, 300, 110, 140, 120], height=320)
        self.tbl_compras.pack(fill="both", expand=True, padx=PADDING, pady=6)

        self.tbl_gastos = ScrollableTable(self.tabs.tab("Gastos"),
            columns=["ID", "Tipo", "Descripción", "Monto", "Método Pago", "Fecha"],
            col_widths=[50, 160, 320, 110, 140, 120], height=320)
        self.tbl_gastos.pack(fill="both", expand=True, padx=PADDING, pady=6)

        self.tbl_inv = ScrollableTable(self.tabs.tab("Inventario"),
            columns=["Producto", "Stock", "Costo U.", "Precio V.", "Valor Stock"],
            col_widths=[380, 80, 120, 120, 140], height=320)
        self.tbl_inv.pack(fill="both", expand=True, padx=PADDING, pady=6)

        self.tbl_cxc = ScrollableTable(self.tabs.tab("CxC"),
            columns=["ID", "Cliente", "Original", "Saldo", "Estado", "Vencimiento"],
            col_widths=[50, 300, 120, 120, 120, 140], height=320)
        self.tbl_cxc.pack(fill="both", expand=True, padx=PADDING, pady=6)

        self.tbl_cxp = ScrollableTable(self.tabs.tab("CxP"),
            columns=["ID", "Proveedor", "Original", "Saldo", "Estado", "Vencimiento"],
            col_widths=[50, 300, 120, 120, 120, 140], height=320)
        self.tbl_cxp.pack(fill="both", expand=True, padx=PADDING, pady=6)

        self._refresh()

    def _refresh(self):
        d = self.ff_desde.get()
        h = self.ff_hasta.get()

        # Utilidad (resumen financiero)
        try:
            rpt = self._svc.reporte_utilidad_periodo(d, h)
            self.kpi_v.set_value(f"${rpt.get('total_ventas', 0):.2f}")
            self.kpi_c.set_value(f"${rpt.get('total_compras', 0):.2f}")
            self.kpi_g.set_value(f"${rpt.get('total_gastos', 0):.2f}")
            self.kpi_u.set_value(f"${rpt.get('utilidad_neta', 0):.2f}")
        except Exception:
            pass

        # Ventas
        try:
            rv = self._svc.reporte_ventas_periodo(d, h)
            ventas = rv.get("ventas", [])
            rows_v = [[v.get("venta_id"), v.get("fecha_venta", ""),
                       v.get("cliente_nombre", ""), f"${v.get('total', 0):.2f}",
                       v.get("metodo_pago", ""), v.get("estado", "")] for v in ventas]
            self.tbl_ventas.set_data(rows_v)
        except Exception:
            pass

        # Compras
        try:
            rc = self._svc.reporte_compras_periodo(d, h)
            compras = rc.get("compras", [])
            rows_c = [[c.get("compra_id"), c.get("fecha_compra", ""),
                       c.get("proveedor_nombre", ""), f"${c.get('total', 0):.2f}",
                       c.get("tipo_pago", ""), c.get("estado", "")] for c in compras]
            self.tbl_compras.set_data(rows_c)
        except Exception:
            pass

        # Gastos
        try:
            rg = self._svc.reporte_gastos_periodo(d, h)
            gastos = rg.get("gastos", [])
            rows_g = [[g.get("gasto_id"), g.get("tipo_gasto", ""),
                       g.get("descripcion", ""), f"${g.get('monto', 0):.2f}",
                       g.get("metodo_pago", ""), g.get("fecha_gasto", "")] for g in gastos]
            self.tbl_gastos.set_data(rows_g)
        except Exception:
            pass

        # Inventario
        try:
            ri_data = self._svc.reporte_inventario()
            stock_bajo = ri_data.get("stock_bajo", [])
            rows_i = [[p.get("nombre", ""), p.get("stock_actual", 0),
                       f"${p.get('precio_compra', p.get('precio_referencia_compra', 0)):.2f}",
                       f"${p.get('precio_venta', 0):.2f}",
                       f"${p.get('stock_actual', 0) * p.get('precio_venta', 0):.2f}"]
                      for p in stock_bajo]
            self.tbl_inv.set_data(rows_i)
        except Exception:
            pass

        # CxC
        try:
            rxc_data = self._svc.reporte_cuentas_cobrar()
            cxc = rxc_data.get("cuentas", [])
            rows_xc = [[x.get("cuenta_cobrar_id"), x.get("cliente_nombre", ""),
                        f"${x.get('monto_original', 0):.2f}", f"${x.get('saldo_pendiente', 0):.2f}",
                        x.get("estado_pago", ""), x.get("fecha_vencimiento", "")] for x in cxc]
            self.tbl_cxc.set_data(rows_xc)
        except Exception:
            pass

        # CxP
        try:
            rxp_data = self._svc.reporte_cuentas_pagar()
            cxp = rxp_data.get("cuentas", [])
            rows_xp = [[x.get("cuenta_pagar_id"), x.get("proveedor_nombre", ""),
                        f"${x.get('monto_original', 0):.2f}", f"${x.get('saldo_pendiente', 0):.2f}",
                        x.get("estado_pago", ""), x.get("fecha_vencimiento", "")] for x in cxp]
            self.tbl_cxp.set_data(rows_xp)
        except Exception:
            pass
