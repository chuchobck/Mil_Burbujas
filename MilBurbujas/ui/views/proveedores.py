# -*- coding: utf-8 -*-
"""
Mil Burbujas UI — Vista de Proveedores (CRUD).
"""
import customtkinter as ctk
from ui.theme import COLORS, FONTS, PADDING
from ui.widgets import (ScrollableTable, ActionButton, FormField,
                         Dialog, show_toast, SearchBar)
from services.proveedor_service import ProveedorService


class ProveedoresView(ctk.CTkFrame):
    def __init__(self, master, user):
        super().__init__(master, fg_color="transparent")
        self.user = user
        self._svc = ProveedorService()
        self._build()

    def _build(self):
        top = ctk.CTkFrame(self, fg_color="transparent")
        top.pack(fill="x", padx=PADDING, pady=(PADDING, 8))
        ctk.CTkLabel(top, text="🏭  Proveedores", font=FONTS["title"],
                     text_color=COLORS["text"]).pack(side="left")
        ActionButton(top, text="➕ Nuevo Proveedor", style="success",
                     command=self._dlg_prov, width=180).pack(side="right")

        SearchBar(self, "Buscar por razón social o RUC...",
                  on_search=self._buscar).pack(fill="x", padx=PADDING, pady=(0, 8))

        self.tbl = ScrollableTable(self,
            columns=["ID", "RUC/CI", "Razón Social", "Teléfono", "Tipo Crédito", "Estado"],
            col_widths=[50, 140, 340, 140, 140, 100], height=480)
        self.tbl.pack(fill="both", expand=True, padx=PADDING, pady=(0, PADDING))
        self.tbl.on_select(self._on_select)
        self._load()

    def _load(self, filtro=""):
        provs = self._svc.get_todos()
        rows = []
        for p in provs:
            if filtro and filtro.lower() not in f"{p['razon_social']} {p['ruc_cedula']}".lower():
                continue
            rows.append([p["proveedor_id"], p["ruc_cedula"], p["razon_social"],
                         p.get("telefono", ""), p.get("tipo_credito", "CONTADO"), p["estado"]])
        self.tbl.set_data(rows)

    def _buscar(self, q):
        self._load(q)

    def _on_select(self, idx, row):
        self._dlg_prov(row[0])

    def _dlg_prov(self, pid=None):
        is_edit = pid is not None
        title = "✏️ Editar Proveedor" if is_edit else "➕ Nuevo Proveedor"
        dlg = Dialog(self, title, width=900, height=680)
        data = self._svc.get_por_id(pid) if is_edit else {}

        ff = {}
        fields = [
            ("ruc_cedula", "RUC / Cedula", "0991001001"),
            ("razon_social", "Razon Social", "Distribuidora S.A."),
            ("nombre_contacto", "Contacto", "Juan Perez"),
            ("telefono", "Telefono", "0991112233"),
            ("email", "Email", "proveedor@mail.com"),
            ("direccion", "Direccion", "Av. Principal y 1ra"),
            ("dia_visita", "Dia de Visita", "Ej: Lunes, Miercoles"),
        ]
        for key, lbl, ph in fields:
            ff[key] = FormField(dlg.body, lbl, ph, width=800)
            ff[key].pack(pady=4)
            if is_edit:
                ff[key].set(data.get(key, ""))

        ff["tipo_credito"] = FormField(dlg.body, "Tipo Crédito", field_type="combo",
                                        values=["CONTADO", "CREDITO_15", "CREDITO_60", "CREDITO_90"],
                                        width=800)
        ff["tipo_credito"].pack(pady=4)
        if is_edit:
            ff["tipo_credito"].set(data.get("tipo_credito", "CONTADO"))

        ff["frecuencia_pedido"] = FormField(dlg.body, "Frecuencia Pedido", field_type="combo",
                                             values=["SEMANAL", "QUINCENAL", "MENSUAL", "BAJO_PEDIDO"],
                                             width=800)
        ff["frecuencia_pedido"].pack(pady=4)
        if is_edit:
            ff["frecuencia_pedido"].set(data.get("frecuencia_pedido", "SEMANAL"))

        def _save():
            try:
                payload = {k: ff[k].get() for k in ff}
                if is_edit:
                    self._svc.actualizar(pid, payload)
                else:
                    self._svc.crear(payload)
                dlg.destroy()
                self._load()
                show_toast(self, f"Proveedor {'actualizado' if is_edit else 'creado'} ✅")
            except Exception as e:
                show_toast(dlg, str(e), "error")

        ActionButton(dlg.footer, "💾 Guardar", "success", command=_save, width=160).pack(side="right", padx=6)
        if is_edit:
            ActionButton(dlg.footer, "🗑️ Desactivar", "danger",
                         command=lambda: self._desact(pid, dlg), width=140).pack(side="left", padx=6)
        ActionButton(dlg.footer, "Cancelar", "ghost", command=dlg.destroy, width=120).pack(side="right", padx=6)

    def _desact(self, pid, dlg):
        try:
            self._svc.desactivar(pid)
            dlg.destroy()
            self._load()
            show_toast(self, "Proveedor desactivado ✅")
        except Exception as e:
            show_toast(self, str(e), "error")
