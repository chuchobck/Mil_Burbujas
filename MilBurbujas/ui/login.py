# -*- coding: utf-8 -*-
"""
Mil Burbujas UI — Pantalla de Login.
"""
import customtkinter as ctk
from ui.theme import COLORS, FONTS, PADDING
from ui.widgets import ActionButton, show_toast
from services.usuario_service import UsuarioService


class LoginFrame(ctk.CTkFrame):
    """Pantalla de inicio de sesión a pantalla completa."""

    def __init__(self, master, on_login_success):
        super().__init__(master, fg_color=COLORS["bg_main"])
        self._on_login = on_login_success
        self._usr_svc = UsuarioService()
        self._build()

    def _build(self):
        # Centrar contenido
        center = ctk.CTkFrame(self, fg_color=COLORS["bg_card"],
                               corner_radius=16, width=420, height=480,
                               border_width=1, border_color=COLORS["border"])
        center.place(relx=0.5, rely=0.5, anchor="center")
        center.pack_propagate(False)

        # Logo / título
        ctk.CTkLabel(center, text="🫧", font=("Segoe UI", 52)).pack(pady=(36, 0))
        ctk.CTkLabel(center, text="MilBurbujas", font=("Segoe UI", 28, "bold"),
                     text_color=COLORS["primary"]).pack(pady=(4, 0))
        ctk.CTkLabel(center, text="Mil Burbujas — Sistema de Gestión",
                     font=FONTS["small"], text_color=COLORS["text_sec"]).pack(pady=(2, 28))

        # Email
        ctk.CTkLabel(center, text="Correo electrónico", font=FONTS["small"],
                     text_color=COLORS["text_sec"]).pack(anchor="w", padx=40)
        self.email = ctk.CTkEntry(center, placeholder_text="admin@milburbujas.local",
                                   width=320, height=42, font=FONTS["body"])
        self.email.pack(padx=40, pady=(2, 12))

        # Contraseña
        ctk.CTkLabel(center, text="Contraseña", font=FONTS["small"],
                     text_color=COLORS["text_sec"]).pack(anchor="w", padx=40)
        self.password = ctk.CTkEntry(center, placeholder_text="••••••",
                                      width=320, height=42, font=FONTS["body"],
                                      show="•")
        self.password.pack(padx=40, pady=(2, 24))

        # Botón
        ActionButton(center, text="Ingresar", style="primary",
                     command=self._do_login, width=320, height=44).pack(padx=40)

        # Mensaje de error
        self.error_lbl = ctk.CTkLabel(center, text="", font=FONTS["small"],
                                       text_color=COLORS["danger"])
        self.error_lbl.pack(pady=(12, 0))

        # Binds
        self.password.bind("<Return>", lambda e: self._do_login())
        self.email.bind("<Return>", lambda e: self.password.focus())

        # Focus
        self.email.focus()

    def _do_login(self):
        email = self.email.get().strip()
        pwd = self.password.get().strip()
        if not email or not pwd:
            self.error_lbl.configure(text="Ingrese correo y contraseña")
            return

        user = self._usr_svc.autenticar(email, pwd)
        if user:
            self._on_login(user)
        else:
            self.error_lbl.configure(text="❌ Credenciales inválidas")
            self.password.delete(0, "end")
