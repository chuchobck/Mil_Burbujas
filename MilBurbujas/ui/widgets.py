# -*- coding: utf-8 -*-
"""
Mil Burbujas UI — Widgets reutilizables para toda la aplicación.
"""
import customtkinter as ctk
from ui.theme import COLORS, FONTS, CARD_RADIUS, BTN_RADIUS, INPUT_HEIGHT, PADDING, SIDEBAR_WIDTH
from datetime import date


# ═══════════════════════════════════════════
# CARD FRAME (contenedor con sombra)
# ═══════════════════════════════════════════
class CardFrame(ctk.CTkFrame):
    def __init__(self, master, **kw):
        kw.setdefault("fg_color", COLORS["bg_card"])
        kw.setdefault("corner_radius", CARD_RADIUS)
        kw.setdefault("border_width", 1)
        kw.setdefault("border_color", COLORS["border"])
        super().__init__(master, **kw)


# ═══════════════════════════════════════════
# KPI BOX
# ═══════════════════════════════════════════
class KPIBox(CardFrame):
    def __init__(self, master, titulo, valor, color=None, icono="", **kw):
        super().__init__(master, **kw)
        self._color = color or COLORS["primary"]
        top = ctk.CTkFrame(self, fg_color="transparent")
        top.pack(fill="x", padx=PADDING, pady=(PADDING, 4))
        ctk.CTkLabel(top, text=icono, font=("Segoe UI", 20)).pack(side="left")
        ctk.CTkLabel(top, text=titulo, font=FONTS["kpi_label"],
                     text_color=COLORS["text_sec"]).pack(side="left", padx=6)

        self._lbl = ctk.CTkLabel(self, text=str(valor),
                                  font=FONTS["kpi_value"],
                                  text_color=self._color)
        self._lbl.pack(padx=PADDING, pady=(0, PADDING), anchor="w")

    def set_value(self, v):
        self._lbl.configure(text=str(v))


# ═══════════════════════════════════════════
# ACTION BUTTON (botón estilizado)
# ═══════════════════════════════════════════
class ActionButton(ctk.CTkButton):
    STYLES = {
        "primary": (COLORS["primary"], COLORS["primary_dark"], COLORS["text_light"]),
        "success": (COLORS["success"], "#388E3C", COLORS["text_light"]),
        "danger":  (COLORS["danger"],  "#D32F2F", COLORS["text_light"]),
        "warning": (COLORS["warning"], "#F57C00", COLORS["text"]),
        "info":    (COLORS["info"],    "#1976D2", COLORS["text_light"]),
        "ghost":   ("transparent", COLORS["hover"], COLORS["primary"]),
    }

    def __init__(self, master, text="", style="primary", icon="", **kw):
        fg, hover, tc = self.STYLES.get(style, self.STYLES["primary"])
        label = f"{icon} {text}".strip() if icon else text
        kw.setdefault("corner_radius", BTN_RADIUS)
        kw.setdefault("height", INPUT_HEIGHT)
        kw.setdefault("font", FONTS["btn"])
        super().__init__(master, text=label, fg_color=fg,
                         hover_color=hover, text_color=tc, **kw)


# ═══════════════════════════════════════════
# FORM FIELD (label + input en bloque)
# ═══════════════════════════════════════════
class FormField(ctk.CTkFrame):
    def __init__(self, master, label, placeholder="", width=None,
                 field_type="entry", values=None, default=None,
                 hint="", required=False, **kw):
        super().__init__(master, fg_color="transparent", **kw)
        # Etiqueta con indicador de obligatorio
        lbl_text = f"  {label}" + ("  *" if required else "")
        ctk.CTkLabel(self, text=lbl_text,
                     font=FONTS.get("form_label", FONTS["small"]),
                     text_color=COLORS["text"]).pack(anchor="w", pady=(2, 0))

        # Hint / ayuda debajo del label
        if hint:
            ctk.CTkLabel(self, text=f"  💡 {hint}",
                         font=FONTS.get("form_hint", FONTS["tiny"]),
                         text_color=COLORS["text_sec"]).pack(anchor="w")

        w = width or 320
        if field_type == "combo":
            self.var = ctk.StringVar(value=default or "")
            self.input = ctk.CTkComboBox(self, values=values or [],
                                          variable=self.var, width=w,
                                          height=INPUT_HEIGHT, font=FONTS["body"],
                                          state="readonly",
                                          corner_radius=BTN_RADIUS,
                                          border_color=COLORS["border"],
                                          button_color=COLORS["primary"],
                                          dropdown_font=FONTS["body"])
        elif field_type == "textbox":
            self.input = ctk.CTkTextbox(self, width=w, height=90, font=FONTS["body"],
                                         corner_radius=BTN_RADIUS,
                                         border_color=COLORS["border"], border_width=1)
            self.var = None
        else:
            self.var = ctk.StringVar(value=default or "")
            show = "•" if field_type == "password" else ""
            self.input = ctk.CTkEntry(self, placeholder_text=placeholder,
                                       textvariable=self.var, width=w,
                                       height=INPUT_HEIGHT, font=FONTS["body"],
                                       show=show, corner_radius=BTN_RADIUS,
                                       border_color=COLORS["border"])
        self.input.pack(pady=(3, 2))

    def get(self):
        if self.var:
            return self.var.get().strip()
        return self.input.get("1.0", "end").strip()

    def set(self, val):
        if self.var:
            self.var.set(str(val))
        else:
            self.input.delete("1.0", "end")
            self.input.insert("1.0", str(val))

    def clear(self):
        if self.var:
            self.var.set("")
        else:
            self.input.delete("1.0", "end")


# ═══════════════════════════════════════════
# SCROLLABLE TABLE (tabla básica con scroll)
# ═══════════════════════════════════════════
class ScrollableTable(ctk.CTkScrollableFrame):
    """Tabla simple basada en Labels dentro de un grid — se expande al ancho disponible.

    Soporta columnas de accion opcionales con botones a la derecha.
    actions = [{"text": "icono", "color": "#hex", "callback": fn(row_data)}, ...]
    """

    def __init__(self, master, columns, col_widths=None, height=400,
                 actions=None, **kw):
        super().__init__(master, height=height, fg_color=COLORS["bg_card"],
                         corner_radius=CARD_RADIUS, **kw)
        self.columns = columns
        self.col_widths = col_widths or [120] * len(columns)
        self._rows_data = []
        self._selected_row = None
        self._on_select = None
        self._actions = actions or []
        # Permitir que las columnas se expandan proporcionalmente
        total_cols = len(columns) + len(self._actions)
        for j in range(len(columns)):
            self.grid_columnconfigure(j, weight=self.col_widths[j], minsize=self.col_widths[j])
        for k in range(len(self._actions)):
            self.grid_columnconfigure(len(columns) + k, weight=0, minsize=44)
        self._draw_header()

    def _draw_header(self):
        for j, col in enumerate(self.columns):
            lbl = ctk.CTkLabel(self, text=f"  {col}", font=FONTS["heading"],
                               width=self.col_widths[j],
                               text_color=COLORS["text_light"],
                               fg_color=COLORS["primary"],
                               corner_radius=0, height=40, anchor="w", padx=8)
            lbl.grid(row=0, column=j, sticky="nsew", padx=(0, 1))
        for k, act in enumerate(self._actions):
            lbl = ctk.CTkLabel(self, text="", font=FONTS["heading"],
                               width=44,
                               text_color=COLORS["text_light"],
                               fg_color=COLORS["primary"],
                               corner_radius=0, height=40)
            lbl.grid(row=0, column=len(self.columns) + k, sticky="nsew", padx=(0, 1))

    def set_data(self, rows: list[list]):
        """rows = [[col1, col2, ...], ...]"""
        for widget in self.winfo_children():
            info = widget.grid_info()
            if info and int(info.get("row", 0)) > 0:
                widget.destroy()
        self._rows_data = rows
        for i, row in enumerate(rows, start=1):
            bg = COLORS["bg_card"] if i % 2 == 0 else COLORS["row_alt"]
            for j, val in enumerate(row):
                lbl = ctk.CTkLabel(self, text=f"  {val}" if val is not None else "",
                                   font=FONTS["body"], width=self.col_widths[j],
                                   fg_color=bg, corner_radius=0, anchor="w",
                                   height=36, padx=6)
                lbl.grid(row=i, column=j, sticky="nsew", padx=(0, 1), pady=(0, 1))
                lbl.bind("<Button-1>", lambda e, r=i-1: self._click_row(r))
            # Action buttons
            for k, act in enumerate(self._actions):
                btn = ctk.CTkButton(
                    self, text=act.get("text", "?"), width=40, height=30,
                    fg_color=act.get("color", COLORS["primary"]),
                    hover_color=act.get("hover", "#555555"),
                    text_color=COLORS["text_light"],
                    corner_radius=4, font=("Segoe UI", 14),
                    command=lambda r=row, cb=act["callback"]: cb(r),
                )
                btn.grid(row=i, column=len(self.columns) + k, padx=2, pady=2)

    def _click_row(self, idx):
        self._selected_row = idx
        if self._on_select:
            self._on_select(idx, self._rows_data[idx])

    def on_select(self, callback):
        self._on_select = callback

    def get_selected(self):
        if self._selected_row is not None and self._selected_row < len(self._rows_data):
            return self._rows_data[self._selected_row]
        return None


# ═══════════════════════════════════════════
# SEARCH BAR
# ═══════════════════════════════════════════
class SearchBar(ctk.CTkFrame):
    def __init__(self, master, placeholder="Buscar...", on_search=None, **kw):
        super().__init__(master, fg_color="transparent", **kw)
        self.var = ctk.StringVar()
        self.entry = ctk.CTkEntry(self, placeholder_text=placeholder,
                                   textvariable=self.var, width=400,
                                   height=INPUT_HEIGHT, font=FONTS["body"],
                                   corner_radius=BTN_RADIUS,
                                   border_color=COLORS["border"])
        self.entry.pack(side="left", padx=(0, 10))
        ActionButton(self, text="🔍 Buscar", style="primary",
                     command=lambda: on_search(self.var.get()) if on_search else None,
                     width=120, height=INPUT_HEIGHT).pack(side="left", padx=(0, 6))
        ActionButton(self, text="❌ Limpiar", style="ghost",
                     command=lambda: (self.var.set(""), on_search("") if on_search else None),
                     width=100, height=INPUT_HEIGHT).pack(side="left")
        if on_search:
            self.entry.bind("<Return>", lambda e: on_search(self.var.get()))


# ═══════════════════════════════════════════
# DIALOG (ventana modal simple)
# ═══════════════════════════════════════════
class Dialog(ctk.CTkToplevel):
    def __init__(self, master, title="", width=550, height=580):
        super().__init__(master)
        self.title(title)
        self.geometry(f"{width}x{height}")
        self.resizable(False, False)
        self.configure(fg_color=COLORS["bg_main"])

        # Centrar en pantalla
        self.update_idletasks()
        x = (self.winfo_screenwidth() - width) // 2
        y = (self.winfo_screenheight() - height) // 2
        self.geometry(f"{width}x{height}+{x}+{y}")

        self.grab_set()
        self.focus_force()

        # Header con barra de color
        hdr_bar = ctk.CTkFrame(self, fg_color=COLORS["primary"], height=5,
                                corner_radius=0)
        hdr_bar.pack(fill="x")

        self.header = ctk.CTkLabel(self, text=title, font=FONTS["subtitle"],
                                    text_color=COLORS["primary"])
        self.header.pack(pady=(PADDING, 12))

        self.body = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.body.pack(fill="both", expand=True, padx=PADDING + 4, pady=(0, 10))

        self.footer = ctk.CTkFrame(self, fg_color="transparent", height=60)
        self.footer.pack(fill="x", padx=PADDING + 4, pady=(0, PADDING))


# ═══════════════════════════════════════════
# TOAST (mensaje temporal)
# ═══════════════════════════════════════════
def show_toast(master, message, kind="success", duration=3000):
    """Muestra un mensaje temporal en la parte superior."""
    colors = {"success": COLORS["success"], "error": COLORS["danger"],
              "warning": COLORS["warning"], "info": COLORS["info"]}
    color = colors.get(kind, COLORS["info"])
    toast = ctk.CTkLabel(master, text=f"  {message}  ", font=FONTS["body"],
                          fg_color=color, text_color=COLORS["text_light"],
                          corner_radius=8, height=40)
    toast.place(relx=0.5, rely=0.02, anchor="n")
    master.after(duration, toast.destroy)


def confirm_dialog(master, title, message, on_confirm):
    """Dialogo de confirmacion si/no - centrado y claro."""
    dlg = Dialog(master, title=title, width=520, height=320)
    ctk.CTkLabel(dlg.body, text=message, font=FONTS["body"],
                 wraplength=440, justify="left").pack(pady=20, expand=True)
    ActionButton(dlg.footer, text="Si, confirmar", style="success",
                 command=lambda: (on_confirm(), dlg.destroy()),
                 width=160).pack(side="right", padx=8)
    ActionButton(dlg.footer, text="No, cancelar", style="ghost",
                 command=dlg.destroy, width=140).pack(side="right", padx=8)


def hoy():
    return date.today().isoformat()
