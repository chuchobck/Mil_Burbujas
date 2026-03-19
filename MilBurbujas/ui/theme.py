# -*- coding: utf-8 -*-
"""
Mil Burbujas UI — Constantes de tema y helpers visuales para CustomTkinter.
"""

# ═══════════════════════════════════════════
# PALETA DE COLORES
# ═══════════════════════════════════════════
COLORS = {
    "primary":      "#E91E63",   # Rosa fuerte (marca MilBurbujas)
    "primary_dark": "#C2185B",
    "primary_light":"#F8BBD0",
    "accent":       "#FF4081",
    "bg_dark":      "#1A1A2E",   # Sidebar
    "bg_main":      "#F5F5F5",   # Fondo general
    "bg_card":      "#FFFFFF",   # Cards
    "text":         "#212121",
    "text_sec":     "#757575",
    "text_light":   "#FFFFFF",
    "success":      "#4CAF50",
    "warning":      "#FF9800",
    "danger":       "#F44336",
    "info":         "#2196F3",
    "border":       "#E0E0E0",
    "hover":        "#FCE4EC",
    "row_alt":      "#FAFAFA",
}

# ═══════════════════════════════════════════
# FUENTES  (familia, tamaño, peso)
# ═══════════════════════════════════════════
FONTS = {
    "title":    ("Segoe UI", 24, "bold"),
    "subtitle": ("Segoe UI", 18, "bold"),
    "heading":  ("Segoe UI", 15, "bold"),
    "body":     ("Segoe UI", 14),
    "small":    ("Segoe UI", 12),
    "tiny":     ("Segoe UI", 11),
    "mono":     ("Consolas", 13),
    "btn":      ("Segoe UI", 14, "bold"),
    "nav":      ("Segoe UI", 14),
    "nav_active": ("Segoe UI", 14, "bold"),
    "kpi_value":  ("Segoe UI", 30, "bold"),
    "kpi_label":  ("Segoe UI", 12),
    "form_label": ("Segoe UI", 13, "bold"),
    "form_hint":  ("Segoe UI", 11),
}

# ═══════════════════════════════════════════
# DIMENSIONES
# ═══════════════════════════════════════════
SIDEBAR_WIDTH = 230
TOPBAR_HEIGHT = 60
PADDING = 18
CARD_RADIUS = 14
BTN_RADIUS = 10
INPUT_HEIGHT = 42

# ═══════════════════════════════════════════
# ICONOS (emoji como placeholder universal)
# ═══════════════════════════════════════════
ICONS = {
    "dashboard":  "📊",
    "ventas":     "🛒",
    "compras":    "📦",
    "catalogo":   "🏷️",
    "clientes":   "👥",
    "proveedores":"🏭",
    "inventario": "📋",
    "cobros":     "💰",
    "pagos":      "💳",
    "gastos":     "💸",
    "cierre":     "🔐",
    "reportes":   "📈",
    "config":     "⚙️",
    "logout":     "🚪",
    "add":        "➕",
    "edit":       "✏️",
    "delete":     "🗑️",
    "search":     "🔍",
    "save":       "💾",
    "cancel":     "❌",
    "check":      "✅",
    "warn":       "⚠️",
    "info":       "ℹ️",
    "user":       "👤",
    "money":      "💵",
    "refresh":    "🔄",
}

# Menú lateral — (clave, icono, label)
MENU_ITEMS = [
    ("dashboard",   "📊", "Dashboard"),
    ("ventas",      "🛒", "Ventas"),
    ("compras",     "📦", "Compras"),
    ("catalogo",    "🏷️", "Catálogo"),
    ("clientes",    "👥", "Clientes"),
    ("proveedores", "🏭", "Proveedores"),
    ("inventario",  "📋", "Inventario"),
    ("cobros",      "💰", "Cobros"),
    ("pagos",       "💳", "Pagos"),
    ("gastos",      "💸", "Gastos"),
    ("cierre",      "🔐", "Cierre Caja"),
    ("reportes",    "📈", "Reportes"),
]

# Modulos permitidos por rol (ADMIN ve todo)
ROL_MENUS = {
    "CAJERO": {"ventas", "cobros"},
}
