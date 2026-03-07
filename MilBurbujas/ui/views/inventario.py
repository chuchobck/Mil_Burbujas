# -*- coding: utf-8 -*-
"""
Mil Burbujas UI — Vista de Inventario (ajustes + alertas).
"""
import customtkinter as ctk
from ui.theme import COLORS, FONTS, PADDING
from ui.widgets import (CardFrame, ScrollableTable, ActionButton, FormField,
                         Dialog, show_toast, SearchBar, KPIBox)
from services.inventario_service import InventarioService
from services.catalogo_service import CatalogoService


class InventarioView(ctk.CTkFrame):
    def __init__(self, master, user):
        super().__init__(master, fg_color="transparent")
        self.user = user
        self._inv = InventarioService()
        self._cat = CatalogoService()
        self._build()

    def _build(self):
        top = ctk.CTkFrame(self, fg_color="transparent")
        top.pack(fill="x", padx=PADDING, pady=(PADDING, 8))
        ctk.CTkLabel(top, text="📋  Inventario", font=FONTS["title"],
                     text_color=COLORS["text"]).pack(side="left")
        ActionButton(top, text="➕ Ajuste Manual", style="warning",
                     command=self._dlg_ajuste, width=160).pack(side="right")

        # Alertas KPI
        self.alert_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.alert_frame.pack(fill="x", padx=PADDING, pady=4)

        # Tabs
        tabs = ctk.CTkTabview(self, fg_color=COLORS["bg_card"],
                               segmented_button_selected_color=COLORS["primary"],
                               segmented_button_selected_hover_color=COLORS["primary_dark"])
        tabs.pack(fill="both", expand=True, padx=PADDING, pady=(0, PADDING))

        tab_stock = tabs.add("Stock Actual")
        tab_movs = tabs.add("Movimientos")
        tab_alertas = tabs.add("Alertas")

        # Stock
        SearchBar(tab_stock, "Buscar producto...",
                  on_search=self._buscar).pack(fill="x", padx=PADDING, pady=8)
        self.tbl_stock = ScrollableTable(tab_stock,
            columns=["ID", "Cod.Barras", "Nombre", "Stock", "Min", "Max", "Estado"],
            col_widths=[45, 130, 340, 80, 70, 70, 100], height=400)
        self.tbl_stock.pack(fill="both", expand=True, padx=PADDING)

        # Movimientos
        self.tbl_movs = ScrollableTable(tab_movs,
            columns=["Fecha", "Producto", "Tipo", "Origen", "Cantidad", "Stock Res."],
            col_widths=[120, 300, 100, 140, 90, 100], height=440)
        self.tbl_movs.pack(fill="both", expand=True, padx=PADDING, pady=PADDING)

        # Alertas
        self.lbl_alertas = ctk.CTkLabel(tab_alertas, text="", font=FONTS["body"],
                                         anchor="nw", justify="left", wraplength=600)
        self.lbl_alertas.pack(fill="both", padx=PADDING, pady=PADDING)

        self._load()

    def _load(self, filtro=""):
        prods = self._cat.get_productos_completos()
        rows = []
        for p in prods:
            if filtro and filtro.lower() not in f"{p['nombre']} {p.get('codigo_barras', '')}".lower():
                continue
            rows.append([p["producto_id"], p.get("codigo_barras", ""), p["nombre"],
                         p["stock_actual"], p.get("stock_minimo", 0),
                         p.get("stock_maximo", 0), p["estado"]])
        self.tbl_stock.set_data(rows)

        # Movimientos recientes
        movs = self._inv.get_ajustes()
        rows_m = []
        for m in movs:
            rows_m.append([m.get("fecha_ajuste", m.get("fecha_movimiento", ""))[:16],
                           m.get("producto_nombre", m.get("producto_id", "")),
                           m.get("tipo_ajuste", m.get("tipo_movimiento", "")),
                           m.get("observacion", ""),
                           m.get("cantidad", 0), m.get("stock_resultante", "")])
        self.tbl_movs.set_data(rows_m)

        # Alertas
        alertas = self._inv.get_alertas()
        lines = []
        sb = alertas.get("stock_bajo", [])
        if sb:
            lines.append(f"{'─' * 50}")
            lines.append(f"🔴  STOCK BAJO  ({len(sb)} productos)")
            lines.append(f"{'─' * 50}")
            for p in sb:
                codigo = p.get('codigo_barras', '')
                marca = p.get('marca_nombre', '')
                cat = p.get('categoria_nombre', '')
                info = f"[{codigo}]" if codigo else ''
                extra = ' · '.join(x for x in [marca, cat] if x)
                lines.append(f"  • {p['nombre']} {info}")
                if extra:
                    lines.append(f"    {extra}")
                lines.append(f"    Stock: {p['stock_actual']} uds  |  Mín: {p['stock_minimo']}  |  Máx: {p.get('stock_maximo', '?')}")
                lines.append("")

        pc = alertas.get("proximos_caducar", [])
        if pc:
            lines.append(f"{'─' * 50}")
            lines.append(f"🟡  PRÓXIMOS A CADUCAR  ({len(pc)} productos)")
            lines.append(f"{'─' * 50}")
            for p in pc:
                codigo = p.get('codigo_barras', '')
                info = f"[{codigo}]" if codigo else ''
                lines.append(f"  • {p['nombre']} {info}")
                lines.append(f"    Caduca: {p.get('fecha_caducidad', '?')}  |  Stock: {p.get('stock_actual', '?')} uds")
                lines.append("")

        if not sb and not pc:
            lines.append("✅ Sin alertas de inventario")

        self.lbl_alertas.configure(text="\n".join(lines))

        # KPIs
        for w in self.alert_frame.winfo_children():
            w.destroy()
        KPIBox(self.alert_frame, "Stock Bajo", alertas.get("total_stock_bajo", 0),
               COLORS["danger"], "🔴").pack(side="left", fill="x", expand=True, padx=4)
        KPIBox(self.alert_frame, "Próx. Caducar", alertas.get("total_proximos_caducar", 0),
               COLORS["warning"], "🟡").pack(side="left", fill="x", expand=True, padx=4)
        KPIBox(self.alert_frame, "Total Productos", len(prods),
               COLORS["info"], "📦").pack(side="left", fill="x", expand=True, padx=4)

    def _buscar(self, q):
        self._load(q)

    def _dlg_ajuste(self):
        dlg = Dialog(self, "Ajuste de Inventario", width=900, height=560)
        prods = self._cat.get_productos_completos()
        prods_act = {p["producto_id"]: p for p in prods if p["estado"] == "ACT"}

        ctk.CTkLabel(dlg.body, text="Producto", font=FONTS["form_label"],
                     text_color=COLORS["text_sec"]).pack(anchor="w", padx=8)
        ff_prod_buscar = ctk.CTkEntry(dlg.body,
                                       placeholder_text="Codigo de barras o nombre del producto...",
                                       width=800, height=42, font=FONTS["body"],
                                       corner_radius=10, border_color=COLORS["border"])
        ff_prod_buscar.pack(pady=(0, 4), padx=8)

        lbl_prod_info = ctk.CTkLabel(dlg.body, text="", font=FONTS["body"],
                                      text_color=COLORS["text_sec"], height=28)
        lbl_prod_info.pack(anchor="w", padx=8)

        _sel_prod = {"id": None}

        def _buscar_prod(event=None):
            q = ff_prod_buscar.get().strip().lower()
            if not q:
                lbl_prod_info.configure(text="", text_color=COLORS["text_sec"])
                _sel_prod["id"] = None
                return
            found = None
            for p in prods_act.values():
                cb = (p.get("codigo_barras") or "").lower()
                if cb and cb == q:
                    found = p
                    break
            if not found:
                for p in prods_act.values():
                    if q in p["nombre"].lower():
                        found = p
                        break
            if found:
                _sel_prod["id"] = found["producto_id"]
                lbl_prod_info.configure(
                    text="{} - {} (Stock: {})".format(
                        found.get("codigo_barras", "S/C"), found["nombre"], found["stock_actual"]),
                    text_color=COLORS["success"])
            else:
                _sel_prod["id"] = None
                lbl_prod_info.configure(text="Producto no encontrado",
                                         text_color=COLORS["danger"])

        ff_prod_buscar.bind("<Return>", _buscar_prod)
        ff_prod_buscar.bind("<FocusOut>", _buscar_prod)

        ff_tipo = FormField(dlg.body, "Tipo Ajuste", field_type="combo",
                            values=["CONSUMO_PERSONAL", "DANIO", "CADUCIDAD",
                                    "MERMA", "ENTRADA_MANUAL", "CORRECCION"], width=800)
        ff_tipo.pack(pady=6)
        ff_qty = FormField(dlg.body, "Cantidad (+entrada / -salida)", placeholder="-1", width=800)
        ff_qty.pack(pady=6)
        ff_obs = FormField(dlg.body, "Observacion", placeholder="Motivo del ajuste", width=800)
        ff_obs.pack(pady=6)

        def _save():
            try:
                pid = _sel_prod["id"]
                if not pid:
                    show_toast(dlg, "Busca y selecciona un producto primero", "warning")
                    return
                self._inv.registrar_ajuste(pid, ff_tipo.get(),
                                           int(ff_qty.get() or 0), ff_obs.get())
                dlg.destroy()
                self._load()
                show_toast(self, "Ajuste registrado")
            except Exception as e:
                show_toast(dlg, str(e), "error")

        ActionButton(dlg.footer, "Registrar", "success", command=_save, width=160).pack(side="right", padx=6)
        ActionButton(dlg.footer, "Cancelar", "ghost", command=dlg.destroy, width=120).pack(side="right", padx=6)
