# -*- coding: utf-8 -*-
"""
Mil Burbujas UI — Vista de Clientes (CRUD).
- Formulario intuitivo: al CREAR solo pide datos básicos.
- Los campos de crédito solo aparecen al EDITAR (cuando el cliente ya existe).
"""
import customtkinter as ctk
from ui.theme import COLORS, FONTS, PADDING
from ui.widgets import (ScrollableTable, ActionButton, FormField,
                         Dialog, show_toast, SearchBar, CardFrame)
from services.cliente_service import ClienteService


class ClientesView(ctk.CTkFrame):
    def __init__(self, master, user):
        super().__init__(master, fg_color="transparent")
        self.user = user
        self._svc = ClienteService()
        self._build()

    # ──────────────────────── CONSTRUIR ────────────────────────
    def _build(self):
        # Barra superior
        top = ctk.CTkFrame(self, fg_color="transparent")
        top.pack(fill="x", padx=PADDING, pady=(PADDING, 10))

        ctk.CTkLabel(top, text="👥  Clientes", font=FONTS["title"],
                     text_color=COLORS["text"]).pack(side="left")

        ActionButton(top, text="➕ Nuevo Cliente", style="success",
                     command=self._dlg_nuevo_cliente, width=180,
                     height=42).pack(side="right")

        # Barra de búsqueda
        SearchBar(self, "Buscar por nombre o cédula...",
                  on_search=self._buscar).pack(fill="x", padx=PADDING, pady=(0, 10))

        # Tabla de clientes
        self.tbl = ScrollableTable(self,
            columns=["ID", "Cédula", "Nombre Completo", "Teléfono",
                     "Crédito", "Límite", "Saldo", "Estado"],
            col_widths=[45, 120, 260, 130, 80, 110, 110, 100], height=480)
        self.tbl.pack(fill="both", expand=True, padx=PADDING, pady=(0, 6))
        self.tbl.on_select(self._on_select)

        # Hint
        ctk.CTkLabel(self, text="💡 Haz clic en un cliente para editarlo",
                     font=FONTS.get("form_hint", FONTS["tiny"]),
                     text_color=COLORS["text_sec"]).pack(pady=(0, 8))
        self._load()

    # ──────────────────────── CARGAR DATOS ─────────────────────
    def _load(self, filtro=""):
        clientes = self._svc.get_todos()
        rows = []
        for c in clientes:
            nombre_full = f"{c['nombres']} {c['apellidos']}"
            if filtro and filtro.lower() not in f"{nombre_full} {c['cedula']}".lower():
                continue
            credito_txt = "✅ Sí" if c.get("habilitado_credito") else "❌ No"
            estado_txt = "🟢 Activo" if c["estado"] == "ACT" else "🔴 Inactivo"
            rows.append([
                c["cliente_id"], c["cedula"], nombre_full,
                c.get("telefono", "—"),
                credito_txt,
                f"${c.get('limite_credito', 0):.2f}",
                f"${c.get('saldo_pendiente', 0):.2f}",
                estado_txt
            ])
        self.tbl.set_data(rows)

    def _buscar(self, q):
        self._load(q)

    def _on_select(self, idx, row):
        self._dlg_editar_cliente(row[0])

    # ═══════════════════════════════════════════════════════════
    # DIÁLOGO: NUEVO CLIENTE (solo datos básicos, sin crédito)
    # ═══════════════════════════════════════════════════════════
    def _dlg_nuevo_cliente(self):
        dlg = Dialog(self, "➕ Registrar Nuevo Cliente", width=900, height=560)

        # Mensaje informativo
        info = ctk.CTkFrame(dlg.body, fg_color=COLORS["primary_light"],
                             corner_radius=10)
        info.pack(fill="x", pady=(0, 12))
        ctk.CTkLabel(info, text="📝 Ingresa los datos del nuevo cliente.\n"
                     "Solo necesitas cédula y nombre para empezar.",
                     font=FONTS.get("form_hint", FONTS["small"]),
                     text_color=COLORS["text"], wraplength=780,
                     justify="left").pack(padx=12, pady=10)

        ff = {}
        ff["cedula"] = FormField(dlg.body, "Cédula / RUC", "Ej: 0901234567",
                                  width=800, required=True,
                                  hint="Número de cédula de 10 dígitos o RUC de 13")
        ff["cedula"].pack(pady=5)

        ff["nombres"] = FormField(dlg.body, "Nombres", "Ej: María José",
                                   width=800, required=True)
        ff["nombres"].pack(pady=5)

        ff["apellidos"] = FormField(dlg.body, "Apellidos", "Ej: López Torres",
                                     width=800, required=True)
        ff["apellidos"].pack(pady=5)

        ff["telefono"] = FormField(dlg.body, "Telefono", "Ej: 0991234567",
                                    width=800,
                                    hint="Opcional — para contactar al cliente")
        ff["telefono"].pack(pady=5)

        ff["direccion"] = FormField(dlg.body, "Dirección", "Ej: Av. Principal y Calle 2",
                                     width=800,
                                     hint="Opcional — dirección de referencia")
        ff["direccion"].pack(pady=5)

        def _guardar():
            cedula = ff["cedula"].get()
            nombres = ff["nombres"].get()
            apellidos = ff["apellidos"].get()

            if not cedula:
                show_toast(dlg, "⚠️ La cédula es obligatoria", "warning")
                return
            if not nombres:
                show_toast(dlg, "⚠️ El nombre es obligatorio", "warning")
                return
            if not apellidos:
                show_toast(dlg, "⚠️ El apellido es obligatorio", "warning")
                return

            try:
                payload = {
                    "cedula": cedula,
                    "nombres": nombres,
                    "apellidos": apellidos,
                    "telefono": ff["telefono"].get(),
                    "direccion": ff["direccion"].get(),
                    "habilitado_credito": 0,
                    "limite_credito": 400,
                    "saldo_pendiente": 0,
                    "frecuencia_pago": "MENSUAL",
                }
                self._svc.crear(payload)
                dlg.destroy()
                self._load()
                show_toast(self, f"✅ Cliente {nombres} {apellidos} registrado correctamente")
            except Exception as e:
                show_toast(dlg, f"❌ {e}", "error")

        ActionButton(dlg.footer, "💾 Registrar Cliente", "success",
                     command=_guardar, width=200).pack(side="right", padx=6)
        ActionButton(dlg.footer, "Cancelar", "ghost",
                     command=dlg.destroy).pack(side="right", padx=6)

    # ═══════════════════════════════════════════════════════════
    # DIÁLOGO: EDITAR CLIENTE (aquí SÍ aparece crédito)
    # ═══════════════════════════════════════════════════════════
    def _dlg_editar_cliente(self, cid):
        data = self._svc.get_por_id(cid)
        if not data:
            show_toast(self, "Cliente no encontrado", "error")
            return

        nombre_full = f"{data['nombres']} {data['apellidos']}"
        dlg = Dialog(self, "Editar: {}".format(nombre_full), width=920, height=780)

        ff = {}

        # ── SECCIÓN: Datos personales ──
        sec1 = ctk.CTkLabel(dlg.body, text="📋 Datos Personales",
                              font=FONTS["heading"], text_color=COLORS["primary"])
        sec1.pack(anchor="w", pady=(0, 6))

        ff["cedula"] = FormField(dlg.body, "Cédula / RUC", width=820, required=True)
        ff["cedula"].pack(pady=4)
        ff["cedula"].set(data.get("cedula", ""))

        ff["nombres"] = FormField(dlg.body, "Nombres", width=820, required=True)
        ff["nombres"].pack(pady=4)
        ff["nombres"].set(data.get("nombres", ""))

        ff["apellidos"] = FormField(dlg.body, "Apellidos", width=820, required=True)
        ff["apellidos"].pack(pady=4)
        ff["apellidos"].set(data.get("apellidos", ""))

        ff["telefono"] = FormField(dlg.body, "Telefono", width=820)
        ff["telefono"].pack(pady=4)
        ff["telefono"].set(data.get("telefono", ""))

        ff["direccion"] = FormField(dlg.body, "Dirección", width=820)
        ff["direccion"].pack(pady=4)
        ff["direccion"].set(data.get("direccion", ""))

        # ── SEPARADOR ──
        sep = ctk.CTkFrame(dlg.body, fg_color=COLORS["border"], height=2)
        sep.pack(fill="x", pady=12)

        # ── SECCIÓN: Crédito (solo edición) ──
        sec2 = ctk.CTkLabel(dlg.body, text="💳 Configuración de Crédito",
                              font=FONTS["heading"], text_color=COLORS["primary"])
        sec2.pack(anchor="w", pady=(0, 6))

        ctk.CTkLabel(dlg.body,
                     text="💡 Habilita el crédito solo si el cliente ya tiene\n"
                          "    historial de compras y confías en su pago.",
                     font=FONTS.get("form_hint", FONTS["small"]),
                     text_color=COLORS["text_sec"],
                     justify="left").pack(anchor="w", pady=(0, 8))

        ff["habilitado_credito"] = FormField(
            dlg.body, "¿Permitir compras a crédito?",
            field_type="combo", values=["No", "Sí"], width=820,
            hint="Selecciona 'Sí' solo si quieres que este cliente compre a crédito")
        ff["habilitado_credito"].pack(pady=4)
        ff["habilitado_credito"].set("Sí" if data.get("habilitado_credito") else "No")

        ff["limite_credito"] = FormField(
            dlg.body, "Límite de crédito ($)", "Ej: 100.00", width=820,
            hint="Monto máximo que puede deber el cliente")
        ff["limite_credito"].pack(pady=4)
        ff["limite_credito"].set(data.get("limite_credito", 0))

        ff["frecuencia_pago"] = FormField(
            dlg.body, "¿Cada cuánto paga?",
            field_type="combo",
            values=["QUINCENAL", "MENSUAL", "FIN_DE_MES"], width=820,
            hint="Con qué frecuencia el cliente acostumbra pagar")
        ff["frecuencia_pago"].pack(pady=4)
        ff["frecuencia_pago"].set(data.get("frecuencia_pago", "MENSUAL"))

        # Info de saldo actual
        saldo = data.get("saldo_pendiente", 0)
        if saldo > 0:
            saldo_frame = ctk.CTkFrame(dlg.body, fg_color=COLORS["warning"],
                                        corner_radius=8)
            saldo_frame.pack(fill="x", pady=8)
            ctk.CTkLabel(saldo_frame,
                         text=f"⚠️ Este cliente tiene un saldo pendiente de ${saldo:.2f}",
                         font=FONTS["body"], text_color=COLORS["text"],
                         ).pack(padx=12, pady=8)

        def _guardar():
            nombres = ff["nombres"].get()
            apellidos = ff["apellidos"].get()
            if not ff["cedula"].get() or not nombres or not apellidos:
                show_toast(dlg, "⚠️ Cédula, nombres y apellidos son obligatorios", "warning")
                return
            try:
                payload = {
                    "cedula": ff["cedula"].get(),
                    "nombres": nombres,
                    "apellidos": apellidos,
                    "telefono": ff["telefono"].get(),
                    "direccion": ff["direccion"].get(),
                    "habilitado_credito": 1 if ff["habilitado_credito"].get() == "Sí" else 0,
                    "limite_credito": float(ff["limite_credito"].get() or 400),
                    "frecuencia_pago": ff["frecuencia_pago"].get() or "MENSUAL",
                    "saldo_pendiente": saldo,
                }
                self._svc.actualizar(cid, payload)
                dlg.destroy()
                self._load()
                show_toast(self, f"✅ Cliente {nombres} {apellidos} actualizado")
            except Exception as e:
                show_toast(dlg, f"❌ {e}", "error")

        ActionButton(dlg.footer, "💾 Guardar Cambios", "success",
                     command=_guardar, width=200).pack(side="right", padx=6)

        if saldo == 0:
            ActionButton(dlg.footer, "🗑️ Desactivar", "danger",
                         command=lambda: self._desact(cid, dlg),
                         width=140).pack(side="left", padx=6)

        ActionButton(dlg.footer, "Cancelar", "ghost",
                     command=dlg.destroy).pack(side="right", padx=6)

    # ──────────────────────── DESACTIVAR ───────────────────────
    def _desact(self, cid, dlg):
        try:
            self._svc.desactivar(cid)
            dlg.destroy()
            self._load()
            show_toast(self, "✅ Cliente desactivado")
        except Exception as e:
            show_toast(self, f"❌ {e}", "error")
