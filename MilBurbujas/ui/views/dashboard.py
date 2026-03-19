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
        self._app = self._find_app()
        self._build()

    def _find_app(self):
        """Busca la ventana raíz (MilBurbujasApp) para poder navegar."""
        w = self.master
        while w:
            if hasattr(w, '_navigate'):
                return w
            w = getattr(w, 'master', None)
        return None

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

        # ── Panel de Alertas (scrollable) ──
        alert_card = CardFrame(bottom)
        alert_card.grid(row=0, column=0, sticky="nsew", padx=(0, 8), pady=4)
        ctk.CTkLabel(alert_card, text="⚠️  Alertas", font=FONTS["subtitle"],
                     text_color=COLORS["warning"]).pack(anchor="w", padx=PADDING, pady=(PADDING, 4))
        self.alert_scroll = ctk.CTkScrollableFrame(alert_card, fg_color="transparent")
        self.alert_scroll.pack(fill="both", expand=True, padx=4, pady=(0, PADDING))

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

    # ─── Helpers para crear filas de alerta ───

    def _add_alert_header(self, icon, text, color, nav_key=None):
        """Agrega un encabezado de sección de alerta."""
        row = ctk.CTkFrame(self.alert_scroll, fg_color="transparent")
        row.pack(fill="x", pady=(8, 2))
        lbl = ctk.CTkLabel(row, text=f"{icon} {text}",
                            font=("Segoe UI", 13, "bold"),
                            text_color=color, anchor="w")
        lbl.pack(side="left", fill="x", expand=True)

    def _add_alert_item(self, text, color="#666666"):
        """Agrega una línea de detalle de alerta."""
        lbl = ctk.CTkLabel(self.alert_scroll, text=f"   • {text}",
                            font=("Segoe UI", 12), text_color=color,
                            anchor="w", justify="left")
        lbl.pack(fill="x", padx=8, pady=1)

    def _add_separator(self):
        """Línea separadora entre secciones."""
        sep = ctk.CTkFrame(self.alert_scroll, height=1,
                            fg_color=COLORS.get("border", "#E0E0E0"))
        sep.pack(fill="x", padx=8, pady=4)

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

        # ── Limpiar alertas ──
        for w in self.alert_scroll.winfo_children():
            w.destroy()

        has_alerts = False
        alertas = self._inv.get_alertas()

        # 1. Stock bajo — TODOS los productos
        stock_bajo = alertas.get("stock_bajo", [])
        if stock_bajo:
            has_alerts = True
            self._add_alert_header(
                "🔴", f"STOCK BAJO — {len(stock_bajo)} producto(s)",
                COLORS.get("danger", "#E53935"), nav_key="inventario")
            for p in stock_bajo:
                marca = p.get('marca_nombre') or ''
                marca_txt = f" ({marca})" if marca else ''
                self._add_alert_item(
                    f"{p['nombre']}{marca_txt}: {p['stock_actual']}/{p['stock_minimo']} uds",
                    COLORS.get("danger", "#E53935"))
            self._add_separator()

        # 2. Próximos a caducar — TODOS
        prox_cad = alertas.get("proximos_caducar", [])
        if prox_cad:
            has_alerts = True
            self._add_alert_header(
                "🟡", f"PRÓXIMOS A CADUCAR — {len(prox_cad)} producto(s)",
                COLORS.get("warning", "#FF9800"), nav_key="inventario")
            for p in prox_cad:
                self._add_alert_item(
                    f"{p['nombre']}: caduca {p.get('fecha_caducidad', '?')}",
                    COLORS.get("warning", "#FF9800"))
            self._add_separator()

        # 3. CxC vencidas — TODAS con cliente y monto
        cxc_lista = d.get("detalle_cxc_vencidas", [])
        if cxc_lista:
            has_alerts = True
            total_cxc = sum(c.get('saldo_pendiente', 0) for c in cxc_lista)
            self._add_alert_header(
                "🟠", f"CUENTAS POR COBRAR VENCIDAS — {len(cxc_lista)} (${total_cxc:.2f})",
                COLORS.get("warning", "#FF9800"), nav_key="cobros")
            for c in cxc_lista:
                self._add_alert_item(
                    f"{c.get('cliente_nombre', '?')}: ${c.get('saldo_pendiente', 0):.2f}  "
                    f"(vence: {c.get('fecha_vencimiento', '?')})",
                    "#E65100")
            self._add_separator()

        # 4. CxP vencidas — TODAS con proveedor y monto
        cxp_lista = d.get("detalle_cxp_vencidas", [])
        if cxp_lista:
            has_alerts = True
            total_cxp = sum(c.get('saldo_pendiente', 0) for c in cxp_lista)
            self._add_alert_header(
                "🔴", f"CUENTAS POR PAGAR VENCIDAS — {len(cxp_lista)} (${total_cxp:.2f})",
                COLORS.get("danger", "#E53935"), nav_key="pagos")
            for c in cxp_lista:
                self._add_alert_item(
                    f"{c.get('proveedor_nombre', '?')}: ${c.get('saldo_pendiente', 0):.2f}  "
                    f"(vence: {c.get('fecha_vencimiento', '?')})",
                    COLORS.get("danger", "#E53935"))

        if not has_alerts:
            ctk.CTkLabel(self.alert_scroll, text="✅ Sin alertas pendientes",
                          font=("Segoe UI", 13), text_color=COLORS.get("success", "#43A047"),
                          anchor="w").pack(fill="x", padx=8, pady=20)

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
