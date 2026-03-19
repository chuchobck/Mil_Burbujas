# -*- coding: utf-8 -*-
"""
Mil Burbujas UI - Vista de Ventas (TX-02 Registrar Venta + TX-06 Anular).
Busqueda por codigo de barras o nombre. Diseno horizontal.
"""
import customtkinter as ctk
from ui.theme import COLORS, FONTS, PADDING
from ui.widgets import (CardFrame, ScrollableTable, ActionButton, FormField,
                         Dialog, show_toast, confirm_dialog, hoy, SearchBar)
from services.venta_service import VentaService
from services.catalogo_service import CatalogoService
from services.cliente_service import ClienteService


class VentasView(ctk.CTkFrame):
    def __init__(self, master, user):
        super().__init__(master, fg_color="transparent")
        self.user = user
        self._venta_svc = VentaService()
        self._cat_svc = CatalogoService()
        self._cli_svc = ClienteService()
        self._build()

    def _build(self):
        top = ctk.CTkFrame(self, fg_color="transparent")
        top.pack(fill="x", padx=PADDING, pady=(PADDING, 10))
        ctk.CTkLabel(top, text="Ventas", font=FONTS["title"],
                     text_color=COLORS["text"]).pack(side="left")
        ActionButton(top, text="+ Nueva Venta", style="success",
                     command=self._dlg_nueva_venta, width=180,
                     height=44).pack(side="right")

        self.tbl = ScrollableTable(self,
            columns=["ID", "Comprobante", "Cliente", "Total", "Metodo Pago", "Estado", "Fecha"],
            col_widths=[50, 140, 240, 100, 120, 110, 120], height=500,
            actions=[
                {"text": "o", "color": COLORS["info"], "hover": "#1565C0",
                 "callback": self._ver_detalle},
                {"text": "X", "color": COLORS["danger"], "hover": "#C62828",
                 "callback": self._confirmar_anular},
            ])
        self.tbl.pack(fill="both", expand=True, padx=PADDING, pady=(0, PADDING))
        self._load()

    def _load(self):
        ventas = self._venta_svc.get_completas()
        rows = []
        for v in ventas:
            cli_nombre = v.get("cliente_nombre", "Consumidor Final")
            estado_txt = "Completada" if v["estado"] == "COMPLETADA" else "Anulada"
            rows.append([v["venta_id"], v.get("numero_comprobante", ""),
                         cli_nombre,
                         "${:.2f}".format(v.get("total", 0)), v["metodo_pago"], estado_txt,
                         v.get("fecha_venta", "")[:10]])
        self.tbl.set_data(rows)

    # ------------------------------------------------------------------
    # Ver detalle de venta
    # ------------------------------------------------------------------
    def _ver_detalle(self, row):
        vid = row[0]
        venta = self._venta_svc.get_por_id(vid)
        if not venta:
            show_toast(self, "Venta no encontrada", "error")
            return
        detalles = self._venta_svc.get_detalles(vid)

        dlg = Dialog(self, "Comprobante de Venta", width=950, height=680)

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
        estado = venta.get("estado", "")
        estado_txt = "COMPLETADA" if estado == "COMPLETADA" else "ANULADA"
        estado_bg = "#388E3C" if estado == "COMPLETADA" else "#D32F2F"
        ctk.CTkLabel(fr_num, text="VENTA #{}".format(vid), font=("Segoe UI", 18, "bold"),
                     text_color=COLORS["text_light"]).pack(anchor="e")
        ctk.CTkLabel(fr_num, text=estado_txt, font=("Segoe UI", 12, "bold"),
                     text_color=COLORS["text_light"], fg_color=estado_bg,
                     corner_radius=6, width=120, height=24).pack(anchor="e", pady=(4, 0))

        # ═══════════════════════════════════════════════════
        # DATOS DE LA VENTA (dos columnas)
        # ═══════════════════════════════════════════════════
        info_card = CardFrame(dlg.body)
        info_card.pack(fill="x", pady=(0, 10))

        fr_cols = ctk.CTkFrame(info_card, fg_color="transparent")
        fr_cols.pack(fill="x", padx=20, pady=12)

        # Columna izquierda
        fr_left = ctk.CTkFrame(fr_cols, fg_color="transparent")
        fr_left.pack(side="left", fill="x", expand=True)
        for lbl, val in [
            ("Comprobante:", venta.get("numero_comprobante", "")),
            ("Cliente:", row[2]),
        ]:
            fr_r = ctk.CTkFrame(fr_left, fg_color="transparent")
            fr_r.pack(fill="x", pady=2)
            ctk.CTkLabel(fr_r, text=lbl, font=("Segoe UI", 12, "bold"),
                         text_color=COLORS["text_sec"], width=100, anchor="e").pack(side="left")
            ctk.CTkLabel(fr_r, text=str(val), font=("Segoe UI", 13),
                         text_color=COLORS["text"], anchor="w").pack(side="left", padx=(8, 0))

        # Columna derecha
        fr_right = ctk.CTkFrame(fr_cols, fg_color="transparent")
        fr_right.pack(side="right")
        metodo = venta.get("metodo_pago", "")
        for lbl, val in [
            ("Fecha:", str(venta.get("fecha_venta", ""))[:16]),
            ("Metodo Pago:", metodo),
        ]:
            fr_r = ctk.CTkFrame(fr_right, fg_color="transparent")
            fr_r.pack(fill="x", pady=2)
            ctk.CTkLabel(fr_r, text=lbl, font=("Segoe UI", 12, "bold"),
                         text_color=COLORS["text_sec"], width=100, anchor="e").pack(side="left")
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

        hdr = ctk.CTkFrame(dlg.body, fg_color=COLORS["primary"], corner_radius=0, height=36)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        for txt, w in [("#", 35), ("Producto", 340), ("P.U.", 100), ("Cant.", 60),
                       ("Descuento", 100), ("Subtotal", 120)]:
            ctk.CTkLabel(hdr, text=txt, font=("Segoe UI", 12, "bold"), width=w,
                         text_color=COLORS["text_light"], fg_color="transparent",
                         corner_radius=0, height=36, anchor="w", padx=6).pack(side="left")

        items_scroll = ctk.CTkScrollableFrame(dlg.body, height=180,
                                               fg_color=COLORS["bg_card"], corner_radius=0)
        items_scroll.pack(fill="both", expand=True)

        total_items_qty = 0
        for i, d in enumerate(detalles):
            bg = COLORS["bg_card"] if i % 2 == 0 else COLORS["row_alt"]
            fr = ctk.CTkFrame(items_scroll, fg_color=bg, corner_radius=0)
            fr.pack(fill="x", pady=(0, 1))
            prod_nombre = d.get("producto_nombre", d.get("nombre", "Producto #{}".format(d.get("producto_id", ""))))
            sub = d.get("subtotal", 0)
            desc = d.get("descuento_unitario", 0) * d.get("cantidad", 0)
            qty = d.get("cantidad", 0)
            total_items_qty += int(qty)
            for val, w in [(str(i + 1), 35), (str(prod_nombre)[:42], 340),
                           ("${:.2f}".format(d.get("precio_unitario", 0)), 100),
                           (str(int(qty)), 60),
                           ("${:.2f}".format(desc), 100),
                           ("${:.2f}".format(sub), 120)]:
                ctk.CTkLabel(fr, text=val, font=("Segoe UI", 12), width=w,
                             fg_color="transparent", anchor="w", height=30, padx=6).pack(side="left")

        # ═══════════════════════════════════════════════════
        # RESUMEN / TOTALES
        # ═══════════════════════════════════════════════════
        fr_bottom = ctk.CTkFrame(dlg.body, fg_color="transparent")
        fr_bottom.pack(fill="x", pady=(8, 0))

        # Info items a la izquierda
        fr_info_left = ctk.CTkFrame(fr_bottom, fg_color="transparent")
        fr_info_left.pack(side="left", padx=8)
        ctk.CTkLabel(fr_info_left, text="Total items: {} | Productos: {}".format(
            total_items_qty, len(detalles)),
            font=("Segoe UI", 12), text_color=COLORS["text_sec"]).pack(anchor="w")

        # Mostrar info de pago si es efectivo
        monto_rec = venta.get("monto_recibido")
        cambio_val = venta.get("cambio")
        if metodo == "EFECTIVO" and monto_rec:
            ctk.CTkLabel(fr_info_left, text="Recibido: ${:.2f}".format(monto_rec),
                         font=("Segoe UI", 12), text_color=COLORS["text_sec"]).pack(anchor="w")
            if cambio_val and cambio_val > 0:
                ctk.CTkLabel(fr_info_left, text="Cambio: ${:.2f}".format(cambio_val),
                             font=("Segoe UI", 13, "bold"), text_color=COLORS["success"]).pack(anchor="w")
        elif metodo == "TRANSFERENCIA":
            ref = venta.get("referencia_transferencia", "")
            if ref:
                ctk.CTkLabel(fr_info_left, text="Ref: {}".format(ref),
                             font=("Segoe UI", 12), text_color=COLORS["text_sec"]).pack(anchor="w")
        elif metodo == "CREDITO":
            ctk.CTkLabel(fr_info_left, text="Venta a Credito",
                         font=("Segoe UI", 12, "bold"), text_color=COLORS["warning"]).pack(anchor="w")

        # Cuadro de totales a la derecha
        fr_totales = ctk.CTkFrame(fr_bottom, fg_color=COLORS["bg_card"], corner_radius=10,
                                   border_width=2, border_color=COLORS["primary"], width=300)
        fr_totales.pack(side="right", padx=8)
        fr_totales.pack_propagate(False)

        fr_nums = ctk.CTkFrame(fr_totales, fg_color="transparent")
        fr_nums.pack(fill="both", expand=True, padx=16, pady=10)

        subtotal_val = venta.get("subtotal", 0)
        descuento_val = venta.get("descuento", 0)
        total_val = venta.get("total", 0)

        for lbl, val in [
            ("Subtotal:", "${:.2f}".format(subtotal_val)),
            ("Descuento:", "-${:.2f}".format(descuento_val)),
        ]:
            fr_t = ctk.CTkFrame(fr_nums, fg_color="transparent")
            fr_t.pack(fill="x", pady=1)
            ctk.CTkLabel(fr_t, text=lbl, font=("Segoe UI", 13),
                         text_color=COLORS["text_sec"], anchor="e").pack(side="left", fill="x", expand=True)
            tc = COLORS["danger"] if "Descuento" in lbl and descuento_val > 0 else COLORS["text"]
            ctk.CTkLabel(fr_t, text=val, font=("Segoe UI", 13), text_color=tc,
                         anchor="e", width=100).pack(side="right")

        # Linea separadora
        ctk.CTkFrame(fr_nums, fg_color=COLORS["primary"], height=2).pack(fill="x", pady=4)

        fr_total = ctk.CTkFrame(fr_nums, fg_color="transparent")
        fr_total.pack(fill="x")
        ctk.CTkLabel(fr_total, text="TOTAL:", font=("Segoe UI", 16, "bold"),
                     text_color=COLORS["primary"], anchor="e").pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(fr_total, text="${:.2f}".format(total_val), font=("Segoe UI", 16, "bold"),
                     text_color=COLORS["primary"], anchor="e", width=100).pack(side="right")

        # Pie de factura
        ctk.CTkLabel(dlg.body, text="Gracias por su compra — MilBurbujas",
                     font=("Segoe UI", 11), text_color=COLORS["text_sec"]).pack(pady=(8, 0))

        ActionButton(dlg.footer, "Cerrar", "ghost", command=dlg.destroy,
                     width=120).pack(side="right", padx=8)

    # ------------------------------------------------------------------
    # Anular venta con confirmacion
    # ------------------------------------------------------------------
    def _confirmar_anular(self, row):
        vid = row[0]
        if "Anulada" in str(row[5]):
            show_toast(self, "Esta venta ya esta anulada", "warning")
            return

        venta = self._venta_svc.get_por_id(vid)
        if not venta:
            show_toast(self, "Venta no encontrada", "error")
            return
        detalles = self._venta_svc.get_detalles(vid)

        dlg = Dialog(self, "Anular Venta #{}".format(vid), width=920, height=620)

        # Aviso
        ctk.CTkLabel(dlg.body, text="Se anulara esta venta y se devolvera el stock.",
                     font=("Segoe UI", 15, "bold"), text_color=COLORS["danger"]
                     ).pack(anchor="w", pady=(0, 8))

        # Info cabecera
        info = CardFrame(dlg.body)
        info.pack(fill="x", pady=(0, 8))
        fr_info = ctk.CTkFrame(info, fg_color="transparent")
        fr_info.pack(fill="x", padx=16, pady=10)
        for label, valor in [
            ("Comprobante:", venta.get("numero_comprobante", "")),
            ("Fecha:", str(venta.get("fecha_venta", ""))[:16]),
            ("Cliente:", row[2]),
            ("Metodo:", venta.get("metodo_pago", "")),
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
        for txt, w in [("#", 35), ("Producto", 320), ("P.U.", 100), ("Cant", 60),
                       ("Desc.", 90), ("Subtotal", 110)]:
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
            desc = d.get("descuento_unitario", 0) * d.get("cantidad", 0)
            for val, w in [(str(i + 1), 35), (str(pn)[:40], 320),
                           ("${:.2f}".format(d.get("precio_unitario", 0)), 100),
                           (str(d.get("cantidad", 0)), 60),
                           ("${:.2f}".format(desc), 90),
                           ("${:.2f}".format(d.get("subtotal", 0)), 110)]:
                ctk.CTkLabel(fr, text=val, font=FONTS["body"], width=w,
                             fg_color="transparent", anchor="w", height=28, padx=6).pack(side="left")

        # Total
        fr_tot = ctk.CTkFrame(dlg.body, fg_color=COLORS["bg_main"], corner_radius=8,
                               border_width=2, border_color=COLORS["danger"])
        fr_tot.pack(fill="x", pady=(8, 0))
        ctk.CTkLabel(fr_tot, text="TOTAL A ANULAR:  ${:.2f}".format(venta.get("total", 0)),
                     font=("Segoe UI", 18, "bold"), text_color=COLORS["danger"]
                     ).pack(pady=10)

        # Botones
        ActionButton(dlg.footer, "Si, anular venta", "danger",
                     command=lambda: (self._anular(vid), dlg.destroy()),
                     width=180).pack(side="right", padx=8)
        ActionButton(dlg.footer, "Cancelar", "ghost",
                     command=dlg.destroy, width=130).pack(side="right", padx=8)

    def _anular(self, vid):
        try:
            self._venta_svc.anular_venta(vid)
            self._load()
            show_toast(self, "Venta #{} anulada correctamente".format(vid))
        except Exception as e:
            show_toast(self, "Error: {}".format(e), "error")

    # ------------------------------------------------------------------
    # DIALOGO: NUEVA VENTA - Layout horizontal en una sola pantalla
    # ------------------------------------------------------------------
    def _dlg_nueva_venta(self):
        dlg = Dialog(self, "Registrar Nueva Venta", width=1500, height=720)
        self._items = []
        self._venta_total = 0.0

        # Cargar datos
        clientes = self._cli_svc.get_todos()
        prods = self._cat_svc.get_productos_completos()
        self._all_prods = {p["producto_id"]: p for p in prods
                           if p["estado"] == "ACT" and p["stock_actual"] > 0}

        # ==============================================================
        # FILA 1: PASO 1 - CLIENTE (horizontal compacto)
        # ==============================================================
        paso1 = CardFrame(dlg.body)
        paso1.pack(fill="x", pady=(0, 6))

        fr_cli_row = ctk.CTkFrame(paso1, fg_color="transparent")
        fr_cli_row.pack(fill="x", padx=12, pady=8)

        ctk.CTkLabel(fr_cli_row, text="Paso 1 - Cliente:",
                     font=FONTS["heading"], text_color=COLORS["primary"]
                     ).pack(side="left", padx=(0, 10))

        ff_buscar_cli = ctk.CTkEntry(fr_cli_row, placeholder_text="Cedula o nombre...",
                                      width=280, height=36, font=FONTS["body"],
                                      corner_radius=8, border_color=COLORS["border"])
        ff_buscar_cli.pack(side="left", padx=(0, 6))

        self._cli_seleccionado = {"id": None, "nombre": "Consumidor Final"}

        lbl_cli_info = ctk.CTkLabel(fr_cli_row, text="Consumidor Final",
                                     font=FONTS["body"], text_color=COLORS["text"],
                                     fg_color=COLORS["primary_light"],
                                     corner_radius=6, height=34, width=320, anchor="w", padx=10)
        lbl_cli_info.pack(side="left", padx=(0, 10))

        def _buscar_cliente():
            q = ff_buscar_cli.get().strip().lower()
            if not q:
                self._cli_seleccionado = {"id": None, "nombre": "Consumidor Final"}
                lbl_cli_info.configure(text="Consumidor Final")
                return
            for c in clientes:
                if c["estado"] != "ACT":
                    continue
                nombre = "{} {}".format(c["nombres"], c["apellidos"])
                if q == c["cedula"].lower() or q in nombre.lower():
                    self._cli_seleccionado = {"id": c["cliente_id"], "nombre": nombre}
                    lbl_cli_info.configure(text="{} - {}".format(nombre, c["cedula"]))
                    return
            lbl_cli_info.configure(text="Cliente no encontrado")

        ActionButton(fr_cli_row, "Buscar", "primary", command=_buscar_cliente,
                     width=70, height=36).pack(side="left", padx=(0, 10))
        ff_buscar_cli.bind("<Return>", lambda e: _buscar_cliente())

        # ==============================================================
        # FILA 2: PASO 2 (izq) + PASO 3 (der) - HORIZONTAL
        # ==============================================================
        fr_main = ctk.CTkFrame(dlg.body, fg_color="transparent")
        fr_main.pack(fill="both", expand=True, pady=(0, 4))

        # --------------------------------------------------------------
        # COLUMNA IZQUIERDA: Paso 2 - Agregar productos + Tabla
        # --------------------------------------------------------------
        fr_left = CardFrame(fr_main)
        fr_left.pack(side="left", fill="both", expand=True, padx=(0, 6))

        # Titulo + buscador producto
        fr_prod_top = ctk.CTkFrame(fr_left, fg_color="transparent")
        fr_prod_top.pack(fill="x", padx=10, pady=(8, 4))

        ctk.CTkLabel(fr_prod_top, text="Paso 2 - Productos",
                     font=FONTS["heading"], text_color=COLORS["primary"]
                     ).pack(side="left", padx=(0, 15))

        ff_codigo = ctk.CTkEntry(fr_prod_top, placeholder_text="Codigo de barras o nombre...",
                                  width=400, height=36, font=FONTS["body"],
                                  corner_radius=8, border_color=COLORS["border"])
        ff_codigo.pack(side="left", padx=(0, 6))

        ff_qty = ctk.CTkEntry(fr_prod_top, placeholder_text="Cant", width=60,
                               height=36, font=FONTS["body"], corner_radius=8,
                               border_color=COLORS["border"])
        ff_qty.insert(0, "1")
        ff_qty.pack(side="left", padx=(0, 6))

        lbl_prod_found = ctk.CTkLabel(fr_prod_top, text="", font=FONTS["small"],
                                       text_color=COLORS["text_sec"], width=300)
        lbl_prod_found.pack(side="left", padx=(10, 0))

        def _buscar_y_agregar():
            q = ff_codigo.get().strip().lower()
            if not q:
                show_toast(dlg, "Escribe codigo o nombre", "warning")
                return
            found = None
            for p in self._all_prods.values():
                cb = (p.get("codigo_barras") or "").lower()
                if cb and cb == q:
                    found = p
                    break
            if not found:
                for p in self._all_prods.values():
                    if q in p["nombre"].lower():
                        found = p
                        break
            if not found:
                lbl_prod_found.configure(text="No encontrado", text_color=COLORS["danger"])
                return
            try:
                qty = int(ff_qty.get() or 1)
            except ValueError:
                show_toast(dlg, "Cantidad invalida", "warning")
                return
            if qty <= 0:
                show_toast(dlg, "Cantidad > 0", "warning")
                return
            ya = sum(it["cantidad"] for it in self._items if it["producto_id"] == found["producto_id"])
            if ya + qty > found["stock_actual"]:
                show_toast(dlg, "Stock: {} (ya tienes {})".format(found["stock_actual"], ya), "warning")
                return
            merged = False
            for it in self._items:
                if it["producto_id"] == found["producto_id"]:
                    it["cantidad"] += qty
                    merged = True
                    break
            if not merged:
                self._items.append({
                    "producto_id": found["producto_id"],
                    "nombre": found["nombre"],
                    "codigo_barras": found.get("codigo_barras") or "",
                    "precio": found["precio_venta"],
                    "cantidad": qty
                })
            lbl_prod_found.configure(text="+{} {}".format(qty, found["nombre"][:25]), text_color=COLORS["success"])
            ff_codigo.delete(0, "end")
            ff_qty.delete(0, "end")
            ff_qty.insert(0, "1")
            ff_codigo.focus()
            _refresh_items()

        ActionButton(fr_prod_top, "Agregar", "success", command=_buscar_y_agregar,
                     width=100, height=36).pack(side="left", padx=(0, 4))
        ff_codigo.bind("<Return>", lambda e: _buscar_y_agregar())

        # Tabla de items
        fr_tbl = ctk.CTkFrame(fr_left, fg_color="transparent")
        fr_tbl.pack(fill="both", expand=True, padx=10, pady=(4, 6))

        hdr = ctk.CTkFrame(fr_tbl, fg_color="transparent")
        hdr.pack(fill="x")
        for txt, w in [("#", 30), ("Codigo", 130), ("Producto", 280), ("P.U.", 75),
                       ("Cant", 45), ("Subtot", 85), ("", 45)]:
            ctk.CTkLabel(hdr, text=txt, font=FONTS["heading"], width=w,
                         text_color=COLORS["text_light"], fg_color=COLORS["primary"],
                         corner_radius=0, height=32, anchor="w", padx=4).pack(side="left", padx=(0, 1))

        items_scroll = ctk.CTkScrollableFrame(fr_tbl, height=200, fg_color=COLORS["bg_card"], corner_radius=0)
        items_scroll.pack(fill="both", expand=True)

        # Total
        fr_total = ctk.CTkFrame(fr_left, fg_color=COLORS["bg_main"], corner_radius=8,
                                 border_width=2, border_color=COLORS["primary"])
        fr_total.pack(fill="x", padx=10, pady=(0, 8))
        lbl_total = ctk.CTkLabel(fr_total, text="TOTAL: $0.00",
                                  font=("Segoe UI", 22, "bold"), text_color=COLORS["primary"])
        lbl_total.pack(pady=8)

        # --------------------------------------------------------------
        # COLUMNA DERECHA: Paso 3 - Forma de pago + Cambio
        # --------------------------------------------------------------
        fr_right = CardFrame(fr_main)
        fr_right.pack(side="right", fill="y", padx=(0, 0))
        fr_right.configure(width=360)

        ctk.CTkLabel(fr_right, text="Paso 3 - Pago",
                     font=FONTS["heading"], text_color=COLORS["primary"]
                     ).pack(anchor="w", padx=12, pady=(10, 6))

        ff_metodo = FormField(fr_right, "Forma de pago", field_type="combo",
                               values=["EFECTIVO", "TRANSFERENCIA", "CREDITO"], width=320)
        ff_metodo.pack(padx=12, pady=(0, 4))

        ff_monto = FormField(fr_right, "Monto recibido ($)", placeholder="0.00",
                              width=320, hint="Solo para efectivo")
        ff_monto.pack(padx=12, pady=(0, 4))

        ff_ref = FormField(fr_right, "Ref. transferencia", placeholder="TRF-...",
                            width=320, hint="Solo para transferencia")
        ff_ref.pack(padx=12, pady=(0, 8))

        # Info credito (visible solo cuando se selecciona CREDITO)
        fr_credito_info = ctk.CTkFrame(fr_right, fg_color=COLORS["bg_main"], corner_radius=8,
                                        border_width=2, border_color=COLORS["warning"])
        lbl_credito_info = ctk.CTkLabel(fr_credito_info, text="Venta a credito\nSe generara cuenta por cobrar al cliente.",
                                         font=FONTS["body"], text_color=COLORS["warning"],
                                         justify="left")
        lbl_credito_info.pack(padx=10, pady=10)

        # Calculadora cambio
        fr_cambio = ctk.CTkFrame(fr_right, fg_color=COLORS["bg_main"], corner_radius=8,
                                  border_width=2, border_color=COLORS["success"])
        fr_cambio.pack(fill="x", padx=12, pady=(0, 8))

        ctk.CTkLabel(fr_cambio, text="Calculadora de Cambio", font=FONTS["body"],
                     text_color=COLORS["text_sec"]).pack(anchor="w", padx=10, pady=(6, 2))

        lbl_cambio_det = ctk.CTkLabel(fr_cambio, text="Total: $0 - Recibido: $0",
                                       font=FONTS["small"], text_color=COLORS["text_sec"])
        lbl_cambio_det.pack(anchor="w", padx=10, pady=(0, 2))

        lbl_cambio_res = ctk.CTkLabel(fr_cambio, text="Cambio: --",
                                       font=("Segoe UI", 18, "bold"), text_color=COLORS["success"])
        lbl_cambio_res.pack(anchor="w", padx=10, pady=(0, 8))

        def _upd_cambio(*_):
            try:
                rec = float(ff_monto.get().replace(",", ".").strip() or 0)
            except ValueError:
                rec = 0
            tot = self._venta_total
            chg = rec - self._venta_total
            lbl_cambio_det.configure(text="Total: ${:.2f} - Recibido: ${:.2f}".format(tot, rec))
            if rec <= 0 or tot <= 0:
                lbl_cambio_res.configure(text="Cambio: --", text_color=COLORS["text_sec"])
                fr_cambio.configure(border_color=COLORS["border"])
            elif chg >= 0:
                lbl_cambio_res.configure(text="Cambio: ${:.2f}".format(chg), text_color=COLORS["success"])
                fr_cambio.configure(border_color=COLORS["success"])
            else:
                lbl_cambio_res.configure(text="Falta: ${:.2f}".format(abs(chg)), text_color=COLORS["danger"])
                fr_cambio.configure(border_color=COLORS["danger"])

        if ff_monto.var:
            ff_monto.var.trace_add("write", _upd_cambio)

        # --- Mostrar/ocultar campos segun metodo de pago ---
        def _on_metodo_change(*_):
            metodo = ff_metodo.get()
            if metodo == "EFECTIVO":
                ff_monto.pack(padx=12, pady=(0, 4))
                ff_ref.pack_forget()
                fr_credito_info.pack_forget()
                fr_cambio.pack(fill="x", padx=12, pady=(0, 8))
                _upd_cambio()
            elif metodo == "TRANSFERENCIA":
                ff_monto.pack_forget()
                ff_ref.pack(padx=12, pady=(0, 8))
                fr_credito_info.pack_forget()
                fr_cambio.pack_forget()
            elif metodo == "CREDITO":
                ff_monto.pack_forget()
                ff_ref.pack_forget()
                fr_credito_info.pack(fill="x", padx=12, pady=(0, 8))
                fr_cambio.pack_forget()

        # Vincular el cambio de metodo al combo
        ff_metodo.input.configure(command=_on_metodo_change)
        # Estado inicial: EFECTIVO seleccionado por defecto
        ff_metodo.set("EFECTIVO")
        _on_metodo_change()

        def _refresh_items():
            for w in items_scroll.winfo_children():
                w.destroy()
            for i, it in enumerate(self._items):
                bg = COLORS["bg_card"] if i % 2 == 0 else COLORS["row_alt"]
                row = ctk.CTkFrame(items_scroll, fg_color=bg, corner_radius=0)
                row.pack(fill="x", pady=(0, 1))
                sub = it["precio"] * it["cantidad"]
                for val, w in [(str(i + 1), 30), (it["codigo_barras"][:14], 130),
                               (it["nombre"][:30], 280), ("${:.2f}".format(it["precio"]), 75),
                               (str(it["cantidad"]), 45), ("${:.2f}".format(sub), 85)]:
                    ctk.CTkLabel(row, text=val, font=FONTS["body"], width=w,
                                 fg_color="transparent", anchor="w", height=28, padx=4).pack(side="left")

                def _del(idx=i):
                    self._items.pop(idx)
                    lbl_prod_found.configure(text="Eliminado", text_color=COLORS["warning"])
                    _refresh_items()

                ctk.CTkButton(row, text="X", width=40, height=24, fg_color=COLORS["danger"],
                              hover_color="#D32F2F", text_color=COLORS["text_light"],
                              corner_radius=4, font=FONTS["small"], command=_del).pack(side="left", padx=2)
            self._venta_total = sum(it["precio"] * it["cantidad"] for it in self._items)
            lbl_total.configure(text="TOTAL: ${:.2f}".format(self._venta_total))
            _upd_cambio()

        # ==============================================================
        # FOOTER: Botones
        # ==============================================================
        def _save():
            if not self._items:
                show_toast(dlg, "Agrega productos", "warning")
                return
            try:
                metodo = ff_metodo.get()
                if not metodo:
                    show_toast(dlg, "Selecciona forma de pago", "warning")
                    return
                cli_id = self._cli_seleccionado["id"]
                cab = {"metodo_pago": metodo, "es_credito": 1 if metodo == "CREDITO" else 0}
                if cli_id:
                    cab["cliente_id"] = cli_id
                if metodo == "EFECTIVO":
                    m = ff_monto.get()
                    if not m:
                        show_toast(dlg, "Ingresa monto", "warning")
                        return
                    mv = float(m)
                    if mv < self._venta_total:
                        show_toast(dlg, "Monto < Total", "warning")
                        return
                    cab["monto_recibido"] = mv
                if metodo == "TRANSFERENCIA":
                    ref = ff_ref.get()
                    if not ref:
                        show_toast(dlg, "Ingresa referencia", "warning")
                        return
                    cab["referencia_transferencia"] = ref
                if metodo == "CREDITO" and not cli_id:
                    show_toast(dlg, "Credito requiere cliente", "warning")
                    return
                items = [{"producto_id": it["producto_id"], "cantidad": it["cantidad"]} for it in self._items]
                result = self._venta_svc.registrar_venta(cab, items)
                dlg.destroy()
                self._load()
                chg_txt = ""
                if metodo == "EFECTIVO":
                    chg = cab["monto_recibido"] - result.get("total", 0)
                    if chg > 0:
                        chg_txt = " - Cambio: ${:.2f}".format(chg)
                show_toast(self, "Venta #{} - ${:.2f}{}".format(result["venta_id"], result["total"], chg_txt))
            except Exception as e:
                show_toast(dlg, "Error: {}".format(e), "error")

        ActionButton(dlg.footer, "Registrar Venta", "success", command=_save, width=180).pack(side="right", padx=8)
        ActionButton(dlg.footer, "Cancelar", "ghost", command=dlg.destroy, width=100).pack(side="right", padx=8)
