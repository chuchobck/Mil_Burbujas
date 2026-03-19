# -*- coding: utf-8 -*-
"""
Mil Burbujas — Ventana principal con sidebar, topbar y área de contenido.
"""
import customtkinter as ctk
from config import APP_TITLE
from ui.theme import COLORS, FONTS, SIDEBAR_WIDTH, TOPBAR_HEIGHT, PADDING, MENU_ITEMS, ROL_MENUS
from ui.widgets import ActionButton
from ui.login import LoginFrame
from ui.views import (DashboardView, CatalogoView, VentasView, ComprasView,
                       ClientesView, ProveedoresView, InventarioView,
                       CobrosView, PagosView, GastosView, CierreCajaView,
                       ReportesView)


VIEW_MAP = {
    "dashboard":   DashboardView,
    "ventas":      VentasView,
    "compras":     ComprasView,
    "catalogo":    CatalogoView,
    "clientes":    ClientesView,
    "proveedores": ProveedoresView,
    "inventario":  InventarioView,
    "cobros":      CobrosView,
    "pagos":       PagosView,
    "gastos":      GastosView,
    "cierre":      CierreCajaView,
    "reportes":    ReportesView,
}


class MilBurbujasApp(ctk.CTk):
    """Ventana principal de la aplicación Mil Burbujas."""

    def __init__(self):
        super().__init__()
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        self.title(APP_TITLE)
        self.geometry("1366x768")
        self.minsize(1100, 650)
        self.state("zoomed")  # Maximizar en Windows

        self._user = None
        self._current_key = None
        self._current_view = None
        self._nav_btns: dict[str, ctk.CTkButton] = {}

        # Mostrar login primero
        self._show_login()

    # ──────────────────── LOGIN ────────────────────
    def _show_login(self):
        self._clear_root()
        self._login = LoginFrame(self, on_login_success=self._on_login)
        self._login.pack(fill="both", expand=True)

    def _on_login(self, user: dict):
        self._user = user
        self._login.destroy()
        self._build_shell()
        # Navegar al primer modulo permitido segun rol
        rol = user.get("rol", "ADMIN")
        allowed = ROL_MENUS.get(rol)
        if allowed:
            first = next((k for k, _, _ in MENU_ITEMS if k in allowed), "ventas")
        else:
            first = "dashboard"
        self._navigate(first)

    # ──────────────────── SHELL ─────────────────────
    def _build_shell(self):
        # ---------- SIDEBAR ----------
        self.sidebar = ctk.CTkFrame(self, width=SIDEBAR_WIDTH,
                                     fg_color=COLORS["bg_dark"], corner_radius=0)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # Logo
        logo = ctk.CTkFrame(self.sidebar, fg_color="transparent", height=70)
        logo.pack(fill="x")
        logo.pack_propagate(False)
        ctk.CTkLabel(logo, text="🫧 MilBurbujas",
                     font=("Segoe UI", 17, "bold"),
                     text_color=COLORS["primary_light"]).pack(expand=True)

        # Menú (filtrado por rol)
        menu_frame = ctk.CTkScrollableFrame(self.sidebar, fg_color="transparent")
        menu_frame.pack(fill="both", expand=True, padx=6, pady=4)

        rol = self._user.get("rol", "ADMIN")
        allowed = ROL_MENUS.get(rol)  # None = todo permitido (ADMIN)
        items = [m for m in MENU_ITEMS if allowed is None or m[0] in allowed]

        for key, icon, label in items:
            btn = ctk.CTkButton(
                menu_frame, text=f" {icon}  {label}",
                font=FONTS["nav"], anchor="w",
                fg_color="transparent",
                hover_color=COLORS["primary_dark"],
                text_color=COLORS["text_light"],
                height=40, corner_radius=8,
                command=lambda k=key: self._navigate(k))
            btn.pack(fill="x", pady=1)
            self._nav_btns[key] = btn

        # Logout al fondo
        bottom = ctk.CTkFrame(self.sidebar, fg_color="transparent", height=60)
        bottom.pack(fill="x", side="bottom", padx=6, pady=8)
        ctk.CTkButton(bottom, text="🚪  Cerrar sesión",
                      font=FONTS["nav"], anchor="w",
                      fg_color="transparent", hover_color=COLORS["danger"],
                      text_color="#EF9A9A", height=38, corner_radius=8,
                      command=self._logout).pack(fill="x")

        # ---------- COLUMNA DERECHA ----------
        right = ctk.CTkFrame(self, fg_color=COLORS["bg_main"], corner_radius=0)
        right.pack(side="right", fill="both", expand=True)

        # Topbar
        topbar = ctk.CTkFrame(right, height=TOPBAR_HEIGHT,
                               fg_color=COLORS["bg_card"], corner_radius=0,
                               border_width=0)
        topbar.pack(fill="x")
        topbar.pack_propagate(False)

        nombre = self._user.get("nombre_completo", "Admin")
        rol = self._user.get("rol", "")
        ctk.CTkLabel(topbar, text=f"👤  {nombre}  |  {rol}",
                     font=FONTS["body"],
                     text_color=COLORS["text_sec"]).pack(side="right", padx=PADDING)

        self._lbl_section = ctk.CTkLabel(topbar, text="Dashboard",
                                          font=FONTS["subtitle"],
                                          text_color=COLORS["text"])
        self._lbl_section.pack(side="left", padx=PADDING)

        # Área de contenido
        self._content_area = ctk.CTkFrame(right, fg_color=COLORS["bg_main"],
                                           corner_radius=0)
        self._content_area.pack(fill="both", expand=True)

    # ──────────────────── NAVEGACIÓN ───────────────
    def _navigate(self, key: str):
        if key == self._current_key:
            return

        # Quitar highlight anterior
        if self._current_key and self._current_key in self._nav_btns:
            self._nav_btns[self._current_key].configure(
                fg_color="transparent", font=FONTS["nav"])

        # Highlight nuevo
        if key in self._nav_btns:
            self._nav_btns[key].configure(
                fg_color=COLORS["primary"], font=FONTS["nav_active"])

        self._current_key = key

        # Buscar label
        label = next((lbl for k, _, lbl in MENU_ITEMS if k == key), key)
        self._lbl_section.configure(text=label)

        # Destruir vista anterior
        if self._current_view:
            self._current_view.destroy()

        # Crear nueva vista
        view_cls = VIEW_MAP.get(key)
        if view_cls:
            self._current_view = view_cls(self._content_area, user=self._user)
            self._current_view.pack(fill="both", expand=True)
        else:
            lbl = ctk.CTkLabel(self._content_area, text=f"Vista «{key}» en desarrollo",
                               font=FONTS["title"], text_color=COLORS["text_sec"])
            lbl.pack(expand=True)
            self._current_view = lbl

    # ──────────────────── LOGOUT ───────────────────
    def _logout(self):
        self._user = None
        self._current_key = None
        self._current_view = None
        self._nav_btns.clear()
        self._show_login()

    # ──────────────────── HELPERS ──────────────────
    def _clear_root(self):
        for w in self.winfo_children():
            w.destroy()
