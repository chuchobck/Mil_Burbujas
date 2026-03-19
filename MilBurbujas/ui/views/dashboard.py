# -*- coding: utf-8 -*-
"""
Mil Burbujas UI — Dashboard (pantalla principal).
"""
import customtkinter as ctk
from ui.theme import COLORS, FONTS, PADDING
from ui.widgets import KPIBox, CardFrame, ScrollableTable
from services.reporte_service import ReporteService
from services.inventario_service import InventarioService


class DashboardView(ctk.CTkFrame):
    def __init__(self, master, user):
        super().__init__(master, fg_color="transparent")
        self.user = user
        self._rep = ReporteService()
        self._inv = InventarioService()
        self._build()

    def _build(self):
        # Título
        top = ctk.CTkFrame(self, fg_color="transparent")
        top.pack(fill="x", padx=PADDING, pady=(PADDING, 8))
        ctk.CTkLabel(top, text=f"📊  Bienvenido(a), {self.user.get('nombre_completo', 'Admin')}",
                     font=FONTS["title"], text_color=COLORS["text"]).pack(side="left")
        ctk.CTkButton(top, text="🔄 Actualizar", width=120, font=FONTS["small"],
                       fg_color=COLORS["info"], hover_color="#1976D2",
                       command=self.refresh).pack(side="right")

        # KPIs
        self.kpi_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.kpi_frame.pack(fill="x", padx=PADDING, pady=8)

        # Alertas + Ventas recientes
        bottom = ctk.CTkFrame(self, fg_color="transparent")
        bottom.pack(fill="both", expand=True, padx=PADDING, pady=(0, PADDING))
        bottom.grid_columnconfigure(0, weight=1)
        bottom.grid_columnconfigure(1, weight=1)

        # Alertas
        alert_card = CardFrame(bottom)
        alert_card.grid(row=0, column=0, sticky="nsew", padx=(0, 8), pady=4)
        ctk.CTkLabel(alert_card, text="⚠️  Alertas", font=FONTS["subtitle"],
                     text_color=COLORS["warning"]).pack(anchor="w", padx=PADDING, pady=(PADDING, 4))
        self.alert_list = ctk.CTkLabel(alert_card, text="Cargando...",
                                        font=FONTS["body"], text_color=COLORS["text_sec"],
                                        anchor="nw", justify="left", wraplength=400)
        self.alert_list.pack(fill="both", expand=True, padx=PADDING, pady=(0, PADDING))

        # Top productos
        top_card = CardFrame(bottom)
        top_card.grid(row=0, column=1, sticky="nsew", padx=(8, 0), pady=4)
        ctk.CTkLabel(top_card, text="🏆  Más vendidos hoy", font=FONTS["subtitle"],
                     text_color=COLORS["primary"]).pack(anchor="w", padx=PADDING, pady=(PADDING, 4))
        self.top_list = ctk.CTkLabel(top_card, text="Cargando...",
                                      font=FONTS["body"], text_color=COLORS["text_sec"],
                                      anchor="nw", justify="left", wraplength=400)
        self.top_list.pack(fill="both", expand=True, padx=PADDING, pady=(0, PADDING))

        self.refresh()

    def refresh(self):
        try:
            d = self._rep.get_dashboard()
        except Exception:
            d = {}

        # Limpiar KPIs
        for w in self.kpi_frame.winfo_children():
            w.destroy()

        kpis = [
            ("Ventas Hoy",   f"${d.get('ventas_hoy', 0):.2f}", COLORS["success"], "💵"),
            ("# Ventas",     d.get("cantidad_ventas", 0), COLORS["info"], "🛒"),
            ("Inventario",   f"${d.get('valor_inventario_costo', 0):.2f}", COLORS["primary"], "📦"),
            ("Productos",    d.get("total_productos", 0), COLORS["accent"], "🏷️"),
            ("CxC Pendiente",f"${d.get('total_por_cobrar', 0):.2f}", COLORS["warning"], "💰"),
            ("CxP Pendiente",f"${d.get('total_por_pagar', 0):.2f}", COLORS["danger"], "💳"),
        ]
        for i, (titulo, valor, color, icono) in enumerate(kpis):
            box = KPIBox(self.kpi_frame, titulo, valor, color, icono)
            box.pack(side="left", fill="x", expand=True, padx=4)

        # Alertas
        alertas = self._inv.get_alertas()
        lines = []
        if alertas.get("total_stock_bajo", 0) > 0:
            lines.append(f"🔴 {alertas['total_stock_bajo']} producto(s) con stock bajo")
            for p in alertas.get("stock_bajo", [])[:5]:
                lines.append(f"   • {p['nombre']}: {p['stock_actual']}/{p['stock_minimo']}")
        if alertas.get("total_proximos_caducar", 0) > 0:
            lines.append(f"🟡 {alertas['total_proximos_caducar']} producto(s) próximos a caducar")
        cxc_v = d.get("cuentas_cobrar_vencidas", 0)
        if cxc_v > 0:
            lines.append(f"🟠 {cxc_v} cuenta(s) por cobrar vencidas")
        cxp_v = d.get("cuentas_pagar_vencidas", 0)
        if cxp_v > 0:
            lines.append(f"🔴 {cxp_v} cuenta(s) por pagar vencidas")
        self.alert_list.configure(text="\n".join(lines) if lines else "✅ Sin alertas pendientes")

        # Top vendidos
        try:
            from datetime import date
            hoy = date.today().isoformat()
            rv = self._rep.reporte_ventas_periodo(hoy, hoy)
            top_prods = rv.get("productos_mas_vendidos", [])[:5]
            if top_prods:
                lines2 = [f"{i+1}. {p.get('nombre', '')} — {p.get('cantidad_vendida', 0)} uds"
                          for i, p in enumerate(top_prods)]
                self.top_list.configure(text="\n".join(lines2))
            else:
                self.top_list.configure(text="No hay ventas registradas hoy")
        except Exception:
            self.top_list.configure(text="No hay datos de ventas hoy")
