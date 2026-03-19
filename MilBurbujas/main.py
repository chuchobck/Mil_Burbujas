# -*- coding: utf-8 -*-
"""
Mil Burbujas - Punto de entrada del sistema.
Inicializa la base de datos y lanza la aplicacion CustomTkinter.
"""
import os
import sys

# Asegurar que el directorio del proyecto este en el path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import APP_TITLE, DB_PATH
from database.connection import DatabaseConnection


def init_app():
    """Inicializa la base de datos si no existe."""
    db = DatabaseConnection()

    if not os.path.exists(DB_PATH):
        print("[INFO] Primera ejecucion. Creando base de datos...")
        db.init_database()
        print("[OK] Base de datos creada en: {}".format(DB_PATH))
    else:
        tablas = db.get_table_count()
        print("[OK] Base de datos existente. Tablas: {}".format(tablas))

    db.close()


def main():
    """Funcion principal - lanza la interfaz grafica."""
    print("=" * 50)
    print("  {}".format(APP_TITLE))
    print("=" * 50)

    init_app()

    from ui.app import MilBurbujasApp
    app = MilBurbujasApp()
    app.mainloop()


if __name__ == "__main__":
    main()
