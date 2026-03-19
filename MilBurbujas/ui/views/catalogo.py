# -*- coding: utf-8 -*-
"""
Mil Burbujas UI - Vista de Catalogo (Productos, Categorias, Marcas, Lineas).
"""
import customtkinter as ctk
from ui.theme import COLORS, FONTS, PADDING
from ui.widgets import (CardFrame, ScrollableTable, ActionButton, FormField,
                         SearchBar, Dialog, show_toast, confirm_dialog)
from services.catalogo_service import CatalogoService


class CatalogoView(ctk.CTkFrame):
    def __init__(self, master, user):
        super().__init__(master, fg_color="transparent")
        self.user = user
        self._svc = CatalogoService()
        self._build()

    def _build(self):
        tabs = ctk.CTkTabview(self, fg_color=COLORS["bg_card"],
                               segmented_button_selected_color=COLORS["primary"],
                               segmented_button_selected_hover_color=COLORS["primary_dark"])
        tabs.pack(fill="both", expand=True, padx=PADDING, pady=PADDING)

        self.tab_prod = tabs.add("Productos")
        self.tab_cat = tabs.add("Categorias")
        self.tab_marca = tabs.add("Marcas")
        self.tab_linea = tabs.add("Lineas")

        self._build_productos(self.tab_prod)
        self._build_categorias(self.tab_cat)
        self._build_marcas(self.tab_marca)
        self._build_lineas(self.tab_linea)

    # ============================
    # PRODUCTOS
    # ============================
    def _build_productos(self, parent):
        top = ctk.CTkFrame(parent, fg_color="transparent")
        top.pack(fill="x", padx=PADDING, pady=(PADDING, 8))
        SearchBar(top, "Buscar por nombre o codigo de barras...",
                  on_search=self._buscar_prod).pack(side="left")
        ActionButton(top, text="+ Nuevo Producto", style="success",
                     command=self._dlg_producto, width=180, height=42).pack(side="right")

        self.tbl_prod = ScrollableTable(parent,
            columns=["ID", "Cod. Barras", "Nombre", "PV", "PVMin", "Stock", "Estado"],
            col_widths=[45, 160, 320, 90, 90, 70, 90], height=460)
        self.tbl_prod.pack(fill="both", expand=True, padx=PADDING, pady=(0, PADDING))
        self.tbl_prod.on_select(self._on_prod_select)
        self._load_productos()

    def _load_productos(self, filtro=""):
        prods = self._svc.get_productos_completos()
        rows = []
        for p in prods:
            if filtro:
                f_lower = filtro.lower()
                searchable = (p["nombre"] + (p.get("codigo_barras") or "")).lower()
                if f_lower not in searchable:
                    continue
            barras = p.get("codigo_barras") or ""
            rows.append([p["producto_id"], barras, p["nombre"],
                         "${:.2f}".format(p["precio_venta"]),
                         "${:.2f}".format(p.get("precio_venta_minimo", 0) or 0),
                         p["stock_actual"], p["estado"]])
        self.tbl_prod.set_data(rows)

    def _buscar_prod(self, q):
        self._load_productos(q)

    def _on_prod_select(self, idx, row):
        self._dlg_producto(prod_id=row[0])

    def _dlg_producto(self, prod_id=None):
        is_edit = prod_id is not None
        title = "Editar Producto" if is_edit else "Nuevo Producto"
        dlg = Dialog(self, title, width=900, height=880)

        cats = self._svc.get_todas_categorias()
        cat_opts = {c["nombre"]: c["categoria_id"] for c in cats}
        unds = self._svc.get_unidades()
        und_opts = {"{} ({})".format(u["nombre"], u.get("abreviatura", "")): u["unidad_id"] for u in unds}
        marcas = self._svc.get_marcas()
        marca_opts = {"(Sin marca)": None}
        marca_opts.update({m["nombre"]: m["marca_id"] for m in marcas})
        linea_opts = {"(Sin linea)": None}

        data = self._svc.get_producto(prod_id) if is_edit else {}

        # -- Informacion basica --
        ctk.CTkLabel(dlg.body, text="Informacion basica",
                     font=FONTS["heading"], text_color=COLORS["primary"]
                     ).pack(anchor="w", pady=(8, 4))

        ff = {}
        ff["codigo_barras"] = FormField(dlg.body, "Codigo de Barras", placeholder="Dejar vacio para auto-generar (INT-000001)",
                                         width=800, required=False,
                                         hint="Si no tiene codigo de barras, se genera uno automatico")
        ff["codigo_barras"].pack(pady=3)
        ff["nombre"] = FormField(dlg.body, "Nombre", placeholder="Nombre del producto",
                                  width=800, required=True)
        ff["nombre"].pack(pady=3)
        ff["descripcion"] = FormField(dlg.body, "Descripcion", placeholder="Descripcion opcional",
                                       width=800)
        ff["descripcion"].pack(pady=3)
        ff["categoria"] = FormField(dlg.body, "Categoria", field_type="combo",
                                     values=list(cat_opts.keys()), width=800, required=True)
        ff["categoria"].pack(pady=3)
        ff["marca"] = FormField(dlg.body, "Marca", field_type="combo",
                                 values=list(marca_opts.keys()), width=800,
                                 hint="Opcional — selecciona la marca del producto")
        ff["marca"].pack(pady=3)
        ff["linea"] = FormField(dlg.body, "Linea", field_type="combo",
                                 values=list(linea_opts.keys()), width=800,
                                 hint="Opcional — gama dentro de la marca (ej: Anticaida)")
        ff["linea"].pack(pady=3)

        def _on_marca_change(*_args):
            """Actualiza las lineas disponibles al cambiar la marca."""
            marca_sel = marca_opts.get(ff["marca"].get())
            new_lineas = {"(Sin linea)": None}
            if marca_sel:
                lineas = self._svc.get_lineas_por_marca(marca_sel)
                new_lineas.update({l["nombre"]: l["linea_id"] for l in lineas})
            ff["linea"].input.configure(values=list(new_lineas.keys()))
            ff["linea"].set("(Sin linea)")
            linea_opts.clear()
            linea_opts.update(new_lineas)

        ff["marca"].input.configure(command=_on_marca_change)

        ff["unidad"] = FormField(dlg.body, "Unidad", field_type="combo",
                                  values=list(und_opts.keys()), width=800, required=True)
        ff["unidad"].pack(pady=3)

        # -- Precios --
        ctk.CTkLabel(dlg.body, text="Precios",
                     font=FONTS["heading"], text_color=COLORS["primary"]
                     ).pack(anchor="w", pady=(12, 4))

        ff["precio_referencia_compra"] = FormField(dlg.body, "Costo de Compra ($)",
                                                       placeholder="0.00", width=800,
                                                       hint="Precio al que compras el producto")
        ff["precio_referencia_compra"].pack(pady=3)

        ff["precio_venta"] = FormField(dlg.body, "Precio de Venta ($)",
                                        placeholder="0.00", width=800, required=True,
                                        hint="Precio al que vendes al cliente")
        ff["precio_venta"].pack(pady=3)

        # Precio minimo: auto-calculado, NO editable
        lbl_min_frame = ctk.CTkFrame(dlg.body, fg_color="transparent")
        lbl_min_frame.pack(fill="x", pady=(3, 0))
        ctk.CTkLabel(lbl_min_frame, text="  Precio Minimo ($)  (automatico: costo + {}% margen)".format(
                     int(self._svc._get_margen_default())),
                     font=FONTS.get("form_label", FONTS["small"]),
                     text_color=COLORS["text_sec"]).pack(anchor="w")
        pvm_var = ctk.StringVar(value="$0.00")
        pvm_display = ctk.CTkEntry(dlg.body, textvariable=pvm_var, width=800,
                                    height=38, font=FONTS["body"],
                                    corner_radius=8, border_color=COLORS["border"],
                                    state="disabled",
                                    fg_color=COLORS.get("bg_hover", "#f0f0f0"))
        pvm_display.pack(pady=(0, 3))

        def _recalc_pvm(*_args):
            """Recalcula precio minimo al cambiar costo de compra."""
            try:
                costo = float(ff["precio_referencia_compra"].get() or 0)
            except ValueError:
                costo = 0
            pvm = self._svc.calcular_precio_minimo(costo)
            pvm_var.set("${:.2f}".format(pvm))

        # Vincular recalculo al cambio del campo costo
        ff["precio_referencia_compra"].var.trace_add("write", _recalc_pvm)

        # -- Stock --
        ctk.CTkLabel(dlg.body, text="Inventario",
                     font=FONTS["heading"], text_color=COLORS["primary"]
                     ).pack(anchor="w", pady=(12, 4))

        for key, label, ph in [("stock_actual", "Stock Actual", "0"),
                                ("stock_minimo", "Stock Minimo", "5"),
                                ("stock_maximo", "Stock Maximo", "500")]:
            ff[key] = FormField(dlg.body, label, placeholder=ph, width=800)
            ff[key].pack(pady=3)

        if is_edit:
            ff["codigo_barras"].set(data.get("codigo_barras", ""))
            ff["nombre"].set(data.get("nombre", ""))
            ff["descripcion"].set(data.get("descripcion", "") or "")
            for name, cid in cat_opts.items():
                if cid == data.get("categoria_id"):
                    ff["categoria"].set(name)
            # Marca
            marca_edit = data.get("marca_id")
            if marca_edit:
                for name, mid in marca_opts.items():
                    if mid == marca_edit:
                        ff["marca"].set(name)
                        _on_marca_change()  # cargar lineas de esa marca
                        break
                # Linea
                linea_edit = data.get("linea_id")
                if linea_edit:
                    for name, lid in linea_opts.items():
                        if lid == linea_edit:
                            ff["linea"].set(name)
                            break
            for name, uid in und_opts.items():
                if uid == data.get("unidad_id"):
                    ff["unidad"].set(name)
            ff["precio_referencia_compra"].set(data.get("precio_referencia_compra", 0))
            ff["precio_venta"].set(data.get("precio_venta", 0))
            # precio_venta_minimo se recalcula automaticamente via trace
            ff["stock_actual"].set(data.get("stock_actual", 0))
            ff["stock_minimo"].set(data.get("stock_minimo", 5))
            ff["stock_maximo"].set(data.get("stock_maximo", 500))

        def _save():
            try:
                marca_sel = marca_opts.get(ff["marca"].get())
                linea_sel = linea_opts.get(ff["linea"].get())
                payload = {
                    "codigo_barras": ff["codigo_barras"].get(),
                    "nombre": ff["nombre"].get(),
                    "descripcion": ff["descripcion"].get() or None,
                    "categoria_id": cat_opts.get(ff["categoria"].get()),
                    "marca_id": marca_sel,
                    "linea_id": linea_sel,
                    "unidad_id": und_opts.get(ff["unidad"].get()),
                    "precio_venta": float(ff["precio_venta"].get() or 0),
                    "precio_referencia_compra": float(ff["precio_referencia_compra"].get() or 0),
                    "stock_actual": int(ff["stock_actual"].get() or 0),
                    "stock_minimo": int(ff["stock_minimo"].get() or 5),
                    "stock_maximo": int(ff["stock_maximo"].get() or 500),
                    "aplica_iva_compra": 1,
                }
                if not payload["nombre"]:
                    show_toast(dlg, "El nombre es obligatorio", "warning")
                    return
                if is_edit:
                    self._svc.actualizar_producto(prod_id, payload)
                else:
                    self._svc.crear_producto(payload)
                dlg.destroy()
                self._load_productos()
                action = "actualizado" if is_edit else "creado"
                show_toast(self, "Producto {}".format(action))
            except Exception as e:
                show_toast(dlg, str(e), "error")

        ActionButton(dlg.footer, "Guardar", "success", command=_save).pack(side="right", padx=4)
        if is_edit:
            ActionButton(dlg.footer, "Desactivar", "danger",
                         command=lambda: self._desactivar_prod(prod_id, dlg)).pack(side="left", padx=4)
        ActionButton(dlg.footer, "Cancelar", "ghost", command=dlg.destroy).pack(side="right", padx=4)

    def _desactivar_prod(self, pid, dlg):
        try:
            self._svc.desactivar_producto(pid)
            dlg.destroy()
            self._load_productos()
            show_toast(self, "Producto desactivado")
        except Exception as e:
            show_toast(self, str(e), "error")

    # ============================
    # CATEGORIAS
    # ============================
    def _build_categorias(self, parent):
        top = ctk.CTkFrame(parent, fg_color="transparent")
        top.pack(fill="x", padx=PADDING, pady=(PADDING, 8))
        ctk.CTkLabel(top, text="Categorias de productos",
                     font=FONTS["heading"], text_color=COLORS["text"]).pack(side="left")
        ActionButton(top, text="+ Nueva Categoria", style="success",
                     command=self._dlg_categoria, width=180, height=42).pack(side="right")
        self.tbl_cat = ScrollableTable(parent,
            columns=["ID", "Nombre", "Tipo", "Estado"],
            col_widths=[60, 500, 120, 120], height=440)
        self.tbl_cat.pack(fill="both", expand=True, padx=PADDING, pady=(0, PADDING))
        self._load_categorias()

    def _load_categorias(self):
        cats = self._svc.get_todas_categorias()
        rows = []
        for c in cats:
            tipo = "Principal" if c.get("nivel", 0) == 0 else "Subcategoria"
            rows.append([c["categoria_id"], c["nombre"], tipo, c.get("estado", "ACT")])
        self.tbl_cat.set_data(rows)

    def _dlg_categoria(self):
        dlg = Dialog(self, "Nueva Categoria", width=900, height=300)

        fr_row = ctk.CTkFrame(dlg.body, fg_color="transparent")
        fr_row.pack(fill="x", padx=12, pady=(20, 8))

        ctk.CTkLabel(fr_row, text="Nombre:", font=FONTS["body"],
                     text_color=COLORS["text"]).pack(side="left", padx=(0, 6))
        ff_n = ctk.CTkEntry(fr_row, placeholder_text="Ej: Cremas, Shampoos, Limpieza...",
                             width=400, height=38, font=FONTS["body"],
                             corner_radius=8, border_color=COLORS["border"])
        ff_n.pack(side="left", padx=(0, 20))

        ctk.CTkLabel(fr_row, text="Tipo:", font=FONTS["body"],
                     text_color=COLORS["text"]).pack(side="left", padx=(0, 6))
        ff_tipo = ctk.CTkComboBox(fr_row, values=["Principal", "Subcategoria"],
                                   width=200, height=38, font=FONTS["body"],
                                   corner_radius=8, border_color=COLORS["border"],
                                   state="readonly")
        ff_tipo.set("Principal")
        ff_tipo.pack(side="left", padx=(0, 10))

        ctk.CTkLabel(dlg.body,
                     text="Principal = categorias generales (Belleza, Limpieza, Cosmeticos)\n"
                          "Subcategoria = divisiones dentro de una principal (Cremas, Shampoos)",
                     font=FONTS.get("form_hint", FONTS["small"]),
                     text_color=COLORS["text_sec"], justify="left"
                     ).pack(anchor="w", padx=20, pady=(4, 10))

        def _save():
            try:
                nombre = ff_n.get().strip()
                if not nombre:
                    show_toast(dlg, "Escribe un nombre", "warning")
                    return
                lvl = 0 if ff_tipo.get() == "Principal" else 1
                self._svc.crear_categoria({"nombre": nombre, "nivel": lvl})
                dlg.destroy()
                self._load_categorias()
                show_toast(self, "Categoria creada")
            except Exception as e:
                show_toast(self, str(e), "error")
        ActionButton(dlg.footer, "Guardar", "success", command=_save, width=160).pack(side="right", padx=6)
        ActionButton(dlg.footer, "Cancelar", "ghost", command=dlg.destroy, width=120).pack(side="right", padx=6)

    # ============================
    # MARCAS
    # ============================
    def _build_marcas(self, parent):
        top = ctk.CTkFrame(parent, fg_color="transparent")
        top.pack(fill="x", padx=PADDING, pady=(PADDING, 8))
        ctk.CTkLabel(top, text="Marcas registradas",
                     font=FONTS["heading"], text_color=COLORS["text"]).pack(side="left")
        ActionButton(top, text="+ Nueva Marca", style="success",
                     command=self._dlg_marca, width=180, height=42).pack(side="right")
        self.tbl_marca = ScrollableTable(parent,
            columns=["ID", "Nombre", "Descripcion", "Estado"],
            col_widths=[60, 300, 380, 120], height=440)
        self.tbl_marca.pack(fill="both", expand=True, padx=PADDING, pady=(0, PADDING))
        self._load_marcas()

    def _load_marcas(self):
        marcas = self._svc.get_marcas()
        rows = [[m["marca_id"], m["nombre"], m.get("descripcion", ""), m.get("estado", "ACT")] for m in marcas]
        self.tbl_marca.set_data(rows)

    def _dlg_marca(self):
        dlg = Dialog(self, "Nueva Marca", width=820, height=340)
        ff_n = FormField(dlg.body, "Nombre", "Ej: L'Oreal", width=720, required=True)
        ff_n.pack(pady=8)
        ff_d = FormField(dlg.body, "Descripcion", "Opcional", width=720)
        ff_d.pack(pady=8)

        def _save():
            try:
                self._svc.crear_marca({"nombre": ff_n.get(), "descripcion": ff_d.get()})
                dlg.destroy()
                self._load_marcas()
                show_toast(self, "Marca creada")
            except Exception as e:
                show_toast(self, str(e), "error")
        ActionButton(dlg.footer, "Guardar", "success", command=_save, width=160).pack(side="right", padx=6)
        ActionButton(dlg.footer, "Cancelar", "ghost", command=dlg.destroy, width=120).pack(side="right", padx=6)

    # ============================
    # LINEAS
    # ============================
    def _build_lineas(self, parent):
        top = ctk.CTkFrame(parent, fg_color="transparent")
        top.pack(fill="x", padx=PADDING, pady=(PADDING, 8))
        ctk.CTkLabel(top, text="Lineas de productos",
                     font=FONTS["heading"], text_color=COLORS["text"]).pack(side="left")
        ActionButton(top, text="+ Nueva Linea", style="success",
                     command=self._dlg_linea, width=180, height=42).pack(side="right")
        self.tbl_linea = ScrollableTable(parent,
            columns=["ID", "Nombre", "Marca", "Estado"],
            col_widths=[60, 350, 320, 120], height=440)
        self.tbl_linea.pack(fill="both", expand=True, padx=PADDING, pady=(0, PADDING))
        self._load_lineas()

    def _load_lineas(self):
        lineas = self._svc.get_lineas()
        rows = [[l["linea_id"], l["nombre"], l.get("marca_nombre", ""), l.get("estado", "ACT")] for l in lineas]
        self.tbl_linea.set_data(rows)

    def _dlg_linea(self):
        dlg = Dialog(self, "Nueva Linea", width=820, height=360)
        marcas = self._svc.get_marcas()
        marca_opts = {m["nombre"]: m["marca_id"] for m in marcas}
        ff_m = FormField(dlg.body, "Marca", field_type="combo",
                         values=list(marca_opts.keys()), width=720, required=True)
        ff_m.pack(pady=8)
        ff_n = FormField(dlg.body, "Nombre Linea", "Ej: Elvive", width=720, required=True)
        ff_n.pack(pady=8)

        def _save():
            try:
                mid = marca_opts.get(ff_m.get())
                self._svc.crear_linea({"marca_id": mid, "nombre": ff_n.get()})
                dlg.destroy()
                self._load_lineas()
                show_toast(self, "Linea creada")
            except Exception as e:
                show_toast(self, str(e), "error")
        ActionButton(dlg.footer, "Guardar", "success", command=_save, width=160).pack(side="right", padx=6)
        ActionButton(dlg.footer, "Cancelar", "ghost", command=dlg.destroy, width=120).pack(side="right", padx=6)
