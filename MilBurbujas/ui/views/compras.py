# -*- coding: utf-8 -*-
"""
Mil Burbujas UI - Vista de Compras (TX-01 Registrar Compra + TX-08 Anular).
"""
import customtkinter as ctk
from ui.theme import COLORS, FONTS, PADDING
from ui.widgets import (CardFrame, ScrollableTable, ActionButton, FormField,
                         Dialog, show_toast, confirm_dialog, hoy)
from services.compra_service import CompraService
from services.catalogo_service import CatalogoService
from services.proveedor_service import ProveedorService


class ComprasView(ctk.CTkFrame):
    def __init__(self, master, user):
        super().__init__(master, fg_color="transparent")
        self.user = user
        self._compra_svc = CompraService()
        self._cat_svc = CatalogoService()
        self._prov_svc = ProveedorService()
        self._build()

    def _build(self):
        top = ctk.CTkFrame(self, fg_color="transparent")
        top.pack(fill="x", padx=PADDING, pady=(PADDING, 10))
        ctk.CTkLabel(top, text="Compras", font=FONTS["title"],
                     text_color=COLORS["text"]).pack(side="left")
        ActionButton(top, text="+ Nueva Compra", style="success",
                     command=self._dlg_nueva_compra, width=180,
                     height=44).pack(side="right")

        self.tbl = ScrollableTable(self,
            columns=["ID", "# Factura", "Proveedor", "Subtotal", "IVA", "Total", "Tipo Pago", "Estado", "Fecha"],
            col_widths=[45, 120, 220, 80, 70, 90, 100, 100, 100], height=500,
            actions=[
                {"text": "o", "color": COLORS["info"], "hover": "#1565C0",
                 "callback": self._ver_detalle},
                {"text": "X", "color": COLORS["danger"], "hover": "#C62828",
                 "callback": self._confirmar_anular},
            ])
        self.tbl.pack(fill="both", expand=True, padx=PADDING, pady=(0, PADDING))
        self._load()

    def _load(self):
        compras = self._compra_svc.get_completas()
        rows = []
        for c in compras:
            prov_nombre = c.get("proveedor_nombre", "")
            estado_txt = "Registrada" if c["estado"] == "REGISTRADA" else "Anulada"
            rows.append([
                c["compra_id"],
                c.get("numero_factura", ""),
                prov_nombre,
                "${:.2f}".format(c.get("subtotal_sin_iva", 0)),
                "${:.2f}".format(c.get("monto_iva", 0)),
                "${:.2f}".format(c.get("total", 0)),
                c.get("tipo_pago", ""),
                estado_txt,
                c.get("fecha_compra", "")[:10],
            ])
        self.tbl.set_data(rows)

    # ------------------------------------------------------------------
    # Ver detalle de compra
    # ------------------------------------------------------------------
    def _ver_detalle(self, row):
        cid = row[0]
        compra = self._compra_svc.get_por_id(cid)
        if not compra:
            show_toast(self, "Compra no encontrada", "error")
            return
        detalles = self._compra_svc.get_detalles(cid)
        iva_pct = 15

        dlg = Dialog(self, "Factura de Compra", width=1000, height=700)

        # ═══════════════════════════════════════════════════
        # ENCABEZADO PROFESIONAL
        # ═══════════════════════════════════════════════════
        header_card = ctk.CTkFrame(dlg.body, fg_color=COLORS["primary"], corner_radius=12, height=80)
        header_card.pack(fill="x", pady=(0, 12))
        header_card.pack_propagate(False)

        fr_hdr = ctk.CTkFrame(header_card, fg_color="transparent")
        fr_hdr.pack(fill="both", expand=True, padx=20, pady=10)

        # Logo / Nombre empresa
        fr_logo = ctk.CTkFrame(fr_hdr, fg_color="transparent")
        fr_logo.pack(side="left")
        ctk.CTkLabel(fr_logo, text="MilBurbujas", font=("Segoe UI", 22, "bold"),
                     text_color=COLORS["text_light"]).pack(anchor="w")
        ctk.CTkLabel(fr_logo, text="Productos de Belleza, Limpieza y Cosmeticos",
                     font=("Segoe UI", 11), text_color="#F8BBD0").pack(anchor="w")

        # Numero y estado
        fr_num = ctk.CTkFrame(fr_hdr, fg_color="transparent")
        fr_num.pack(side="right")
        estado = compra.get("estado", "")
        estado_txt = "REGISTRADA" if estado == "REGISTRADA" else "ANULADA"
        estado_bg = "#388E3C" if estado == "REGISTRADA" else "#D32F2F"
        ctk.CTkLabel(fr_num, text="COMPRA #{}".format(cid), font=("Segoe UI", 18, "bold"),
                     text_color=COLORS["text_light"]).pack(anchor="e")
        ctk.CTkLabel(fr_num, text=estado_txt, font=("Segoe UI", 12, "bold"),
                     text_color=COLORS["text_light"], fg_color=estado_bg,
                     corner_radius=6, width=110, height=24).pack(anchor="e", pady=(4, 0))

        # ═══════════════════════════════════════════════════
        # DATOS DE LA COMPRA (dos columnas)
        # ═══════════════════════════════════════════════════
        info_card = CardFrame(dlg.body)
        info_card.pack(fill="x", pady=(0, 10))

        fr_cols = ctk.CTkFrame(info_card, fg_color="transparent")
        fr_cols.pack(fill="x", padx=20, pady=12)

        # Columna izquierda
        fr_left = ctk.CTkFrame(fr_cols, fg_color="transparent")
        fr_left.pack(side="left", fill="x", expand=True)
        for lbl, val in [
            ("Factura:", compra.get("numero_factura", "")),
            ("Proveedor:", row[2]),
        ]:
            fr_r = ctk.CTkFrame(fr_left, fg_color="transparent")
            fr_r.pack(fill="x", pady=2)
            ctk.CTkLabel(fr_r, text=lbl, font=("Segoe UI", 12, "bold"),
                         text_color=COLORS["text_sec"], width=90, anchor="e").pack(side="left")
            ctk.CTkLabel(fr_r, text=str(val), font=("Segoe UI", 13),
                         text_color=COLORS["text"], anchor="w").pack(side="left", padx=(8, 0))

        # Columna derecha
        fr_right = ctk.CTkFrame(fr_cols, fg_color="transparent")
        fr_right.pack(side="right")
        for lbl, val in [
            ("Fecha:", str(compra.get("fecha_compra", ""))[:10]),
            ("Tipo Pago:", compra.get("tipo_pago", "")),
        ]:
            fr_r = ctk.CTkFrame(fr_right, fg_color="transparent")
            fr_r.pack(fill="x", pady=2)
            ctk.CTkLabel(fr_r, text=lbl, font=("Segoe UI", 12, "bold"),
                         text_color=COLORS["text_sec"], width=90, anchor="e").pack(side="left")
            ctk.CTkLabel(fr_r, text=str(val), font=("Segoe UI", 13),
                         text_color=COLORS["text"], anchor="w").pack(side="left", padx=(8, 0))

        # ═══════════════════════════════════════════════════
        # LINEA SEPARADORA
        # ═══════════════════════════════════════════════════
        ctk.CTkFrame(dlg.body, fg_color=COLORS["primary"], height=2, corner_radius=0).pack(fill="x", pady=(0, 6))

        # ═══════════════════════════════════════════════════
        # TITULO TABLA
        # ═══════════════════════════════════════════════════
        ctk.CTkLabel(dlg.body, text="  DETALLE DE PRODUCTOS", font=("Segoe UI", 13, "bold"),
                     text_color=COLORS["primary"]).pack(anchor="w", pady=(2, 4))

        # Header tabla
        hdr = ctk.CTkFrame(dlg.body, fg_color=COLORS["primary"], corner_radius=0, height=36)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        for txt, w in [("#", 35), ("Codigo", 110), ("Producto", 230), ("P.U.", 85), ("Cant.", 55),
                       ("Incl. IVA", 70), ("Base", 85), ("IVA $", 70), ("Total", 90)]:
            ctk.CTkLabel(hdr, text=txt, font=("Segoe UI", 12, "bold"), width=w,
                         text_color=COLORS["text_light"], fg_color="transparent",
                         corner_radius=0, height=36, anchor="w", padx=6).pack(side="left")

        # Filas de productos
        items_scroll = ctk.CTkScrollableFrame(dlg.body, height=180,
                                               fg_color=COLORS["bg_card"], corner_radius=0)
        items_scroll.pack(fill="both", expand=True)

        total_items_qty = 0
        for i, d in enumerate(detalles):
            bg = COLORS["bg_card"] if i % 2 == 0 else COLORS["row_alt"]
            fr = ctk.CTkFrame(items_scroll, fg_color=bg, corner_radius=0)
            fr.pack(fill="x", pady=(0, 1))

            prod_nombre = d.get("producto_nombre", "Producto #{}".format(d.get("producto_id", "")))
            prod_codigo = d.get("producto_codigo", "")
            incl_iva = d.get("incluye_iva", 0)
            pu = d.get("precio_unitario", 0)
            qty = d.get("cantidad", 0)
            total_items_qty += int(qty)

            # Recalcular base e IVA
            if incl_iva:
                precio_sin = round(pu / (1 + iva_pct / 100), 4)
                iva_unit = pu - precio_sin
            else:
                precio_sin = pu
                iva_unit = round(pu * iva_pct / 100, 4)

            base_total = round(precio_sin * qty, 2)
            iva_total = round(iva_unit * qty, 2)
            total_item = round(base_total + iva_total, 2)

            incl_txt = "Si" if incl_iva else "No"
            for val, w in [(str(i + 1), 35), (str(prod_codigo)[:12], 110),
                           (str(prod_nombre)[:28], 230),
                           ("${:.2f}".format(pu), 85),
                           (str(int(qty)), 55),
                           (incl_txt, 70),
                           ("${:.2f}".format(base_total), 85),
                           ("${:.2f}".format(iva_total), 70),
                           ("${:.2f}".format(total_item), 90)]:
                ctk.CTkLabel(fr, text=val, font=("Segoe UI", 12), width=w,
                             fg_color="transparent", anchor="w", height=30, padx=6).pack(side="left")

        # ═══════════════════════════════════════════════════
        # RESUMEN / TOTALES (profesional, alineado a la derecha)
        # ═══════════════════════════════════════════════════
        fr_bottom = ctk.CTkFrame(dlg.body, fg_color="transparent")
        fr_bottom.pack(fill="x", pady=(8, 0))

        # Info items a la izquierda
        ctk.CTkLabel(fr_bottom, text="Total items: {} | Productos: {}".format(
            total_items_qty, len(detalles)),
            font=("Segoe UI", 12), text_color=COLORS["text_sec"]).pack(side="left", padx=8)

        # Cuadro de totales a la derecha
        fr_totales = ctk.CTkFrame(fr_bottom, fg_color=COLORS["bg_card"], corner_radius=10,
                                   border_width=2, border_color=COLORS["primary"], width=320)
        fr_totales.pack(side="right", padx=8)
        fr_totales.pack_propagate(False)

        fr_nums = ctk.CTkFrame(fr_totales, fg_color="transparent")
        fr_nums.pack(fill="both", expand=True, padx=16, pady=10)

        subtotal_val = compra.get("subtotal_sin_iva", 0)
        iva_val = compra.get("monto_iva", 0)
        total_val = compra.get("total", 0)

        for lbl, val, fnt, tc in [
            ("Subtotal sin IVA:", "${:.2f}".format(subtotal_val), ("Segoe UI", 13), COLORS["text"]),
            ("IVA (15%):", "${:.2f}".format(iva_val), ("Segoe UI", 13), COLORS["text"]),
        ]:
            fr_t = ctk.CTkFrame(fr_nums, fg_color="transparent")
            fr_t.pack(fill="x", pady=1)
            ctk.CTkLabel(fr_t, text=lbl, font=fnt, text_color=COLORS["text_sec"],
                         anchor="e").pack(side="left", fill="x", expand=True)
            ctk.CTkLabel(fr_t, text=val, font=fnt, text_color=tc,
                         anchor="e", width=100).pack(side="right")

        # Linea separadora
        ctk.CTkFrame(fr_nums, fg_color=COLORS["primary"], height=2).pack(fill="x", pady=4)

        fr_total = ctk.CTkFrame(fr_nums, fg_color="transparent")
        fr_total.pack(fill="x")
        ctk.CTkLabel(fr_total, text="TOTAL:", font=("Segoe UI", 16, "bold"),
                     text_color=COLORS["primary"], anchor="e").pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(fr_total, text="${:.2f}".format(total_val), font=("Segoe UI", 16, "bold"),
                     text_color=COLORS["primary"], anchor="e", width=100).pack(side="right")

        # Observaciones
        obs = compra.get("observaciones", "")
        if obs:
            fr_obs = ctk.CTkFrame(dlg.body, fg_color="transparent")
            fr_obs.pack(fill="x", pady=(6, 0))
            ctk.CTkLabel(fr_obs, text="Observaciones: {}".format(obs),
                         font=("Segoe UI", 11), text_color=COLORS["text_sec"],
                         wraplength=800, justify="left").pack(anchor="w", padx=8)

        ActionButton(dlg.footer, "Cerrar", "ghost", command=dlg.destroy,
                     width=120).pack(side="right", padx=8)

    # ------------------------------------------------------------------
    # Anular compra con confirmacion
    # ------------------------------------------------------------------
    def _confirmar_anular(self, row):
        cid = row[0]
        if "Anulada" in str(row[7]):
            show_toast(self, "Esta compra ya esta anulada", "warning")
            return

        compra = self._compra_svc.get_por_id(cid)
        if not compra:
            show_toast(self, "Compra no encontrada", "error")
            return
        detalles = self._compra_svc.get_detalles(cid)

        dlg = Dialog(self, "Anular Compra #{}".format(cid), width=950, height=620)

        # Aviso
        ctk.CTkLabel(dlg.body, text="Se anulara esta compra y se descontara el stock.",
                     font=("Segoe UI", 15, "bold"), text_color=COLORS["danger"]
                     ).pack(anchor="w", pady=(0, 8))

        # Info cabecera
        info = CardFrame(dlg.body)
        info.pack(fill="x", pady=(0, 8))
        fr_info = ctk.CTkFrame(info, fg_color="transparent")
        fr_info.pack(fill="x", padx=16, pady=10)
        for label, valor in [
            ("# Factura:", compra.get("numero_factura", "")),
            ("Fecha:", str(compra.get("fecha_compra", ""))[:10]),
            ("Proveedor:", row[2]),
            ("Tipo Pago:", compra.get("tipo_pago", "")),
        ]:
            fr_r = ctk.CTkFrame(fr_info, fg_color="transparent")
            fr_r.pack(fill="x", pady=1)
            ctk.CTkLabel(fr_r, text=label, font=FONTS["heading"],
                         text_color=COLORS["text_sec"], width=120, anchor="e").pack(side="left")
            ctk.CTkLabel(fr_r, text=str(valor), font=FONTS["body"],
                         anchor="w").pack(side="left", padx=(8, 0))

        # Tabla productos
        hdr = ctk.CTkFrame(dlg.body, fg_color="transparent")
        hdr.pack(fill="x")
        for txt, w in [("#", 35), ("Producto", 280), ("P.U.", 100), ("Cant", 60),
                       ("IVA", 60), ("Subtotal", 110), ("Total", 110)]:
            ctk.CTkLabel(hdr, text=txt, font=FONTS["heading"], width=w,
                         text_color=COLORS["text_light"], fg_color=COLORS["primary"],
                         corner_radius=0, height=30, anchor="w", padx=6).pack(side="left", padx=(0, 1))

        scr = ctk.CTkScrollableFrame(dlg.body, height=160,
                                      fg_color=COLORS["bg_card"], corner_radius=0)
        scr.pack(fill="both", expand=True)
        for i, d in enumerate(detalles):
            bg = COLORS["bg_card"] if i % 2 == 0 else COLORS["row_alt"]
            fr = ctk.CTkFrame(scr, fg_color=bg, corner_radius=0)
            fr.pack(fill="x", pady=(0, 1))
            pn = d.get("producto_nombre", "Producto #{}".format(d.get("producto_id", "")))
            iva_txt = "Si" if d.get("incluye_iva", 0) else "No"
            sub = d.get("subtotal", 0)
            total_item = d.get("total", sub + d.get("monto_iva", 0))
            for val, w in [(str(i + 1), 35), (str(pn)[:35], 280),
                           ("${:.2f}".format(d.get("precio_unitario", 0)), 100),
                           (str(d.get("cantidad", 0)), 60),
                           (iva_txt, 60),
                           ("${:.2f}".format(sub), 110),
                           ("${:.2f}".format(total_item), 110)]:
                ctk.CTkLabel(fr, text=val, font=FONTS["body"], width=w,
                             fg_color="transparent", anchor="w", height=28, padx=6).pack(side="left")

        # Total
        fr_tot = ctk.CTkFrame(dlg.body, fg_color=COLORS["bg_main"], corner_radius=8,
                               border_width=2, border_color=COLORS["danger"])
        fr_tot.pack(fill="x", pady=(8, 0))
        ctk.CTkLabel(fr_tot, text="TOTAL A ANULAR:  ${:.2f}".format(compra.get("total", 0)),
                     font=("Segoe UI", 18, "bold"), text_color=COLORS["danger"]
                     ).pack(pady=10)

        # Botones
        ActionButton(dlg.footer, "Si, anular compra", "danger",
                     command=lambda: (self._anular(cid), dlg.destroy()),
                     width=180).pack(side="right", padx=8)
        ActionButton(dlg.footer, "Cancelar", "ghost",
                     command=dlg.destroy, width=130).pack(side="right", padx=8)

    def _anular(self, cid):
        try:
            self._compra_svc.anular_compra(cid)
            self._load()
            show_toast(self, "Compra #{} anulada correctamente".format(cid))
        except Exception as e:
            show_toast(self, "Error: {}".format(e), "error")

    def _dlg_nueva_compra(self):
        dlg = Dialog(self, "Nueva Compra", width=1100, height=750)
        self._items_compra = []

        # Cargar productos para busqueda
        prods = self._cat_svc.get_productos_completos()
        self._all_prods_compra = {p["producto_id"]: p for p in prods if p["estado"] == "ACT"}

        # ============================
        # PASO 1: PROVEEDOR Y FACTURA
        # ============================
        paso1 = CardFrame(dlg.body)
        paso1.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(paso1, text="Paso 1 - Datos de la compra",
                     font=FONTS["heading"], text_color=COLORS["primary"]
                     ).pack(anchor="w", padx=PADDING, pady=(12, 8))

        fr_top = ctk.CTkFrame(paso1, fg_color="transparent")
        fr_top.pack(fill="x", padx=PADDING, pady=(0, 6))

        provs = self._prov_svc.get_todos()
        prov_opts = {"{} ({})".format(p["razon_social"], p["ruc_cedula"]): p["proveedor_id"]
                     for p in provs if p["estado"] == "ACT"}
        ff_prov = FormField(fr_top, "Proveedor", field_type="combo",
                            values=list(prov_opts.keys()), width=520, required=True)
        ff_prov.pack(side="left", padx=(0, 16))
        ff_factura = FormField(fr_top, "# Factura", placeholder="FAC-001", width=240, required=True)
        ff_factura.pack(side="left")

        fr_pago = ctk.CTkFrame(paso1, fg_color="transparent")
        fr_pago.pack(fill="x", padx=PADDING, pady=(0, 12))
        ff_tipo = FormField(fr_pago, "Tipo Pago", field_type="combo",
                            values=["CONTADO", "CREDITO"], width=240)
        ff_tipo.pack(side="left", padx=(0, 16))
        ff_plazo = FormField(fr_pago, "Plazo (dias)", placeholder="30", width=180,
                             hint="Solo para credito")
        ff_plazo.pack(side="left", padx=(0, 16))
        ff_fecha = FormField(fr_pago, "Fecha Compra", placeholder=hoy(), width=220)
        ff_fecha.set(hoy())
        ff_fecha.pack(side="left")

        # ============================
        # PASO 2: PRODUCTOS
        # ============================
        paso2 = CardFrame(dlg.body)
        paso2.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(paso2, text="Paso 2 - Agregar productos",
                     font=FONTS["heading"], text_color=COLORS["primary"]
                     ).pack(anchor="w", padx=PADDING, pady=(12, 4))

        ctk.CTkLabel(paso2,
                     text="Escanea o escribe el codigo de barras o nombre. Si ya existe, se suma la cantidad.",
                     font=FONTS.get("form_hint", FONTS["small"]),
                     text_color=COLORS["text_sec"]
                     ).pack(anchor="w", padx=PADDING, pady=(0, 8))

        fr_add = ctk.CTkFrame(paso2, fg_color="transparent")
        fr_add.pack(fill="x", padx=PADDING, pady=(0, 6))

        ff_prod_buscar = ctk.CTkEntry(fr_add,
                                       placeholder_text="Codigo de barras o nombre del producto...",
                                       width=400, height=42, font=FONTS["body"],
                                       corner_radius=10, border_color=COLORS["border"])
        ff_prod_buscar.pack(side="left", padx=(0, 10))

        ff_qty = ctk.CTkEntry(fr_add, placeholder_text="Cant.",
                               width=80, height=42, font=FONTS["body"],
                               corner_radius=10, border_color=COLORS["border"])
        ff_qty.insert(0, "1")
        ff_qty.pack(side="left", padx=(0, 10))

        ff_pu = ctk.CTkEntry(fr_add, placeholder_text="P.U. $",
                              width=100, height=42, font=FONTS["body"],
                              corner_radius=10, border_color=COLORS["border"])
        ff_pu.pack(side="left", padx=(0, 10))

        # IVA combo con label descriptivo
        fr_iva_wrap = ctk.CTkFrame(fr_add, fg_color="transparent")
        fr_iva_wrap.pack(side="left", padx=(0, 10))
        ctk.CTkLabel(fr_iva_wrap, text="¿Incluye IVA?",
                     font=FONTS.get("form_hint", FONTS["tiny"]),
                     text_color=COLORS["text_sec"]).pack(anchor="w")
        ff_iva = ctk.CTkComboBox(fr_iva_wrap, values=["No", "Si"],
                                  width=90, height=36, font=FONTS["body"],
                                  corner_radius=10, border_color=COLORS["border"],
                                  state="readonly")
        ff_iva.set("No")
        ff_iva.pack()

        ff_caducidad = ctk.CTkEntry(fr_add,
                                     placeholder_text="Caducidad (AAAA-MM-DD)",
                                     width=180, height=42, font=FONTS["body"],
                                     corner_radius=10, border_color=COLORS["border"])
        ff_caducidad.pack(side="left", padx=(0, 10))

        lbl_prod_found = ctk.CTkLabel(paso2, text="",
                                       font=FONTS["body"], text_color=COLORS["text_sec"],
                                       height=30)
        lbl_prod_found.pack(anchor="w", padx=PADDING)

        def _buscar_y_agregar():
            q = ff_prod_buscar.get().strip().lower()
            if not q:
                show_toast(dlg, "Escribe un codigo de barras o nombre", "warning")
                return

            found = None
            # Buscar por codigo de barras exacto
            for p in self._all_prods_compra.values():
                cb = (p.get("codigo_barras") or "").lower()
                if cb and cb == q:
                    found = p
                    break
            # Buscar por nombre parcial
            if not found:
                for p in self._all_prods_compra.values():
                    if q in p["nombre"].lower():
                        found = p
                        break

            if not found:
                lbl_prod_found.configure(text="Producto no encontrado",
                                          text_color=COLORS["danger"])
                return

            try:
                qty = int(ff_qty.get() or 1)
            except ValueError:
                show_toast(dlg, "La cantidad debe ser un numero", "warning")
                return
            if qty <= 0:
                show_toast(dlg, "Cantidad debe ser mayor a 0", "warning")
                return

            # Auto-detectar IVA del producto si el usuario no lo cambio
            aplica_iva = found.get("aplica_iva_compra", 1)
            ff_iva.set("Si" if aplica_iva else "No")

            # Auto-fill precio si esta vacio
            pu_text = ff_pu.get().strip()
            if not pu_text:
                ref_price = found.get("precio_referencia_compra", 0) or 0
                if ref_price > 0:
                    pu_text = str(ref_price)
                    ff_pu.delete(0, "end")
                    ff_pu.insert(0, pu_text)

            try:
                pu = float(pu_text or 0)
            except ValueError:
                show_toast(dlg, "El precio debe ser un numero", "warning")
                return

            if pu <= 0:
                show_toast(dlg, "Ingresa un precio unitario mayor a 0", "warning")
                return

            iva_val = 1 if ff_iva.get() == "Si" else 0
            caducidad_val = ff_caducidad.get().strip() or None

            # Si el producto ya esta en la lista, actualizar cantidad/precio/iva
            merged = False
            for it in self._items_compra:
                if it["producto_id"] == found["producto_id"]:
                    it["cantidad"] += qty
                    it["precio_unitario"] = pu
                    it["incluye_iva"] = iva_val
                    if caducidad_val:
                        it["fecha_caducidad_lote"] = caducidad_val
                    merged = True
                    break

            if not merged:
                barras = found.get("codigo_barras") or ""
                self._items_compra.append({
                    "producto_id": found["producto_id"],
                    "nombre": found["nombre"],
                    "codigo_barras": barras,
                    "cantidad": qty,
                    "precio_unitario": pu,
                    "incluye_iva": iva_val,
                    "fecha_caducidad_lote": caducidad_val,
                })

            action = "Sumado" if merged else "Agregado"
            lbl_prod_found.configure(
                text="{}: {} x{} - ${:.2f}".format(action, found["nombre"][:30], qty, pu * qty),
                text_color=COLORS["success"])
            ff_prod_buscar.delete(0, "end")
            ff_qty.delete(0, "end")
            ff_qty.insert(0, "1")
            ff_pu.delete(0, "end")
            ff_caducidad.delete(0, "end")
            ff_prod_buscar.focus()
            _refresh()

        ActionButton(fr_add, "Agregar", "success",
                     command=_buscar_y_agregar, width=100, height=42).pack(side="left")
        ff_prod_buscar.bind("<Return>", lambda e: _buscar_y_agregar())

        # -- Tabla de items con boton eliminar --
        fr_items_container = ctk.CTkFrame(paso2, fg_color="transparent")
        fr_items_container.pack(fill="x", padx=PADDING, pady=(6, 4))

        items_header = ctk.CTkFrame(fr_items_container, fg_color="transparent")
        items_header.pack(fill="x")
        hdr_cols = [("#", 30), ("Producto", 200), ("Caduca", 90), ("Cant", 50), ("P.U.", 80),
                    ("IVA", 45), ("Subtotal", 80), ("IVA $", 65), ("Total", 85), ("", 45)]
        for txt, w in hdr_cols:
            ctk.CTkLabel(items_header, text="  {}".format(txt), font=FONTS["heading"],
                         width=w, text_color=COLORS["text_light"],
                         fg_color=COLORS["primary"], corner_radius=0,
                         height=36, anchor="w", padx=4
                         ).pack(side="left", fill="y", padx=(0, 1))

        items_scroll = ctk.CTkScrollableFrame(fr_items_container, height=160,
                                               fg_color=COLORS["bg_card"],
                                               corner_radius=0)
        items_scroll.pack(fill="x")

        # Totales prominentes
        fr_total = ctk.CTkFrame(paso2, fg_color=COLORS["bg_main"],
                                 corner_radius=10, border_width=2,
                                 border_color=COLORS["primary"])
        fr_total.pack(fill="x", padx=PADDING, pady=(4, 12))
        lbl_subtotal = ctk.CTkLabel(fr_total, text="Subtotal:  $0.00",
                                     font=FONTS["heading"],
                                     text_color=COLORS["text_sec"])
        lbl_subtotal.pack(pady=(8, 0))
        lbl_iva_total = ctk.CTkLabel(fr_total, text="IVA (15%):  $0.00",
                                      font=FONTS["heading"],
                                      text_color=COLORS["text_sec"])
        lbl_iva_total.pack()
        lbl_total = ctk.CTkLabel(fr_total, text="TOTAL:  $0.00",
                                  font=("Segoe UI", 22, "bold"),
                                  text_color=COLORS["primary"])
        lbl_total.pack(pady=(0, 8))

        iva_pct = 15  # IVA Ecuador

        def _refresh():
            for w in items_scroll.winfo_children():
                w.destroy()
            sum_subtotal = 0.0
            sum_iva = 0.0
            for i, it in enumerate(self._items_compra):
                bg = COLORS["bg_card"] if i % 2 == 0 else COLORS["row_alt"]
                row_fr = ctk.CTkFrame(items_scroll, fg_color=bg, corner_radius=0)
                row_fr.pack(fill="x", pady=(0, 1))

                pu = it["precio_unitario"]
                qty = it["cantidad"]
                if it["incluye_iva"]:
                    precio_sin = round(pu / (1 + iva_pct / 100), 4)
                    iva_unit = pu - precio_sin
                else:
                    precio_sin = pu
                    iva_unit = round(pu * iva_pct / 100, 4)

                sub_sin = round(precio_sin * qty, 2)
                iva_item = round(iva_unit * qty, 2)
                total_item = round(sub_sin + iva_item, 2)
                sum_subtotal += sub_sin
                sum_iva += iva_item

                caduc_txt = it.get("fecha_caducidad_lote") or "-"
                vals = [
                    (str(i + 1), 30),
                    (it["nombre"][:24], 200),
                    (caduc_txt[:10], 90),
                    (str(qty), 50),
                    ("${:.2f}".format(pu), 80),
                    ("Si" if it["incluye_iva"] else "No", 45),
                    ("${:.2f}".format(sub_sin), 80),
                    ("${:.2f}".format(iva_item), 65),
                    ("${:.2f}".format(total_item), 85),
                ]
                for val, w in vals:
                    ctk.CTkLabel(row_fr, text="  {}".format(val), font=FONTS["body"],
                                 width=w, fg_color="transparent", corner_radius=0,
                                 anchor="w", height=34, padx=4
                                 ).pack(side="left", fill="y")

                # Boton eliminar
                def _del(idx=i):
                    removed = self._items_compra.pop(idx)
                    lbl_prod_found.configure(
                        text="Quitado: {}".format(removed["nombre"]),
                        text_color=COLORS["warning"])
                    _refresh()

                ctk.CTkButton(row_fr, text="X", width=40, height=28,
                              fg_color=COLORS["danger"], hover_color="#D32F2F",
                              text_color=COLORS["text_light"], corner_radius=4,
                              font=FONTS["small"], command=_del
                              ).pack(side="left", padx=4)

            grand_total = round(sum_subtotal + sum_iva, 2)
            lbl_subtotal.configure(text="Subtotal:  ${:.2f}".format(sum_subtotal))
            lbl_iva_total.configure(text="IVA (15%):  ${:.2f}".format(sum_iva))
            lbl_total.configure(text="TOTAL:  ${:.2f}".format(grand_total))

        # -- BOTONES FOOTER --
        def _save():
            if not self._items_compra:
                show_toast(dlg, "Agrega al menos un producto", "warning")
                return
            try:
                prov_id = prov_opts.get(ff_prov.get())
                if not prov_id:
                    show_toast(dlg, "Selecciona un proveedor", "warning")
                    return
                if not ff_factura.get():
                    show_toast(dlg, "Ingresa el numero de factura", "warning")
                    return

                cab = {
                    "numero_factura": ff_factura.get(),
                    "proveedor_id": prov_id,
                    "fecha_compra": ff_fecha.get(),
                    "tipo_pago": ff_tipo.get(),
                }
                if ff_tipo.get() == "CREDITO":
                    cab["plazo_credito_dias"] = int(ff_plazo.get() or 30)
                items = [{"producto_id": it["producto_id"], "cantidad": it["cantidad"],
                          "precio_unitario": it["precio_unitario"],
                          "incluye_iva": it["incluye_iva"],
                          "fecha_caducidad_lote": it.get("fecha_caducidad_lote")}
                         for it in self._items_compra]
                result = self._compra_svc.registrar_compra(cab, items)
                dlg.destroy()
                self._load()
                show_toast(self, "Compra #{} - ${:.2f}".format(result["compra_id"], result["total"]))
            except Exception as e:
                show_toast(dlg, "Error: {}".format(e), "error")

        ActionButton(dlg.footer, "Registrar Compra", "success",
                     command=_save, width=200).pack(side="right", padx=8)
        ActionButton(dlg.footer, "Cancelar", "ghost",
                     command=dlg.destroy, width=120).pack(side="right", padx=8)
