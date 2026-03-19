# 🫧 Mil Burbujas — Sistema de Gestión para Tienda

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/SQLite-3-07405E?logo=sqlite&logoColor=white" />
  <img src="https://img.shields.io/badge/CustomTkinter-UI-blueviolet" />
  <img src="https://img.shields.io/badge/Licencia-MIT-green" />
  <img src="https://img.shields.io/badge/Estado-Producci%C3%B3n-brightgreen" />
</p>

<p align="center">
  <b>Sistema POS completo para tiendas de productos de belleza, limpieza y cosméticos.</b><br/>
  Desarrollado en Python con interfaz gráfica moderna, base de datos local y reportería integrada.
</p>

---

## ✨ Características Principales

| Módulo | Descripción |
|--------|-------------|
| 🛒 **Ventas** | Registro rápido de ventas, cálculo automático de IVA, impresión de comprobantes |
| 📦 **Compras** | Ingreso de mercadería con actualización automática de inventario |
| 📋 **Catálogo** | Gestión de productos, categorías, marcas y líneas |
| 👥 **Clientes** | CRUD completo con historial de compras y créditos |
| 🏭 **Proveedores** | Directorio de proveedores con productos asociados |
| 📊 **Inventario** | Control de stock, alertas de mínimo, ajustes y movimientos |
| 💳 **Cobros** | Gestión de cuentas por cobrar y pagos de clientes |
| 💰 **Pagos** | Control de cuentas por pagar a proveedores |
| 🧾 **Gastos** | Registro de gastos operativos del negocio |
| 🔒 **Cierre de Caja** | Cierre diario con cuadre automático |
| 📈 **Reportes** | 8 reportes completos: ventas, compras, inventario, financieros y más |
| 👤 **Usuarios** | Sistema de roles (Admin / Cajero) con autenticación segura |

---

## 🖥️ Capturas de Pantalla

> *Interfaz moderna con CustomTkinter, sidebar de navegación y diseño responsivo.*

```
┌─────────────┬─────────────────────────────────────┐
│  🫧          │  Dashboard                          │
│  Mil Burbujas│  ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐  │
│             │  │Ventas│ │Stock│ │Cobros│ │Caja │  │
│  📊 Dashboard│  │$2,450│ │ 847 │ │ $320│ │$1.2k│  │
│  🛒 Ventas  │  └─────┘ └─────┘ └─────┘ └─────┘  │
│  📦 Compras │                                     │
│  📋 Catálogo│  Ventas Recientes                   │
│  👥 Clientes│  ─────────────────────────           │
│  🏭 Proveed.│  #001  María López     $45.50       │
│  📊 Inventar│  #002  Carlos Ruiz     $23.80       │
│  💳 Cobros  │  #003  Ana García      $67.20       │
│  📈 Reportes│                                     │
└─────────────┴─────────────────────────────────────┘
```

---

## 🚀 Instalación Rápida

### Requisitos
- **Python 3.10+**
- **pip** (gestor de paquetes)

### Pasos

```bash
# 1. Clonar el repositorio
git clone https://github.com/chuchobck/Mil_Burbujas.git
cd Mil_Burbujas

# 2. Crear entorno virtual (recomendado)
python -m venv .venv
.venv\Scripts\activate      # Windows
# source .venv/bin/activate  # Linux/Mac

# 3. Instalar dependencias
pip install -r MilBurbujas/requirements.txt

# 4. Ejecutar la aplicación
cd MilBurbujas
python main.py
```

> **Primera ejecución:** La base de datos se crea automáticamente con datos iniciales.

### Credenciales por defecto

| Rol | Email | Contraseña |
|-----|-------|-----------|
| Admin | `admin@milburbujas.local` | `admin123` |
| Cajero | `cajero@milburbujas.local` | `cajero123` |

---

## 🏗️ Arquitectura del Proyecto

```
MilBurbujas/
├── main.py                 # Punto de entrada
├── config.py               # Configuración global
├── database/
│   ├── connection.py       # Singleton SQLite con transacciones
│   ├── schema.sql          # Esquema completo (25+ tablas)
│   ├── seed_data.sql       # Datos iniciales
│   └── backup.py           # Respaldo y restauración
├── models/                 # Capa DAO (Data Access Objects)
│   ├── base_model.py       # CRUD genérico reutilizable
│   ├── producto.py
│   ├── venta.py
│   └── ... (20+ modelos)
├── services/               # Lógica de negocio
│   ├── venta_service.py
│   ├── inventario_service.py
│   ├── reporte_service.py
│   └── ... (13 servicios)
├── ui/                     # Interfaz gráfica (CustomTkinter)
│   ├── app.py              # Ventana principal + navegación
│   ├── login.py            # Pantalla de autenticación
│   ├── theme.py            # Sistema de temas y colores
│   ├── widgets.py          # Componentes reutilizables
│   └── views/              # 12 vistas del sistema
├── tests/                  # Suite completa de pruebas
│   ├── test_fase1_database.py
│   ├── test_fase2_services.py
│   ├── test_fase3_runner.py
│   └── ... (7 archivos de test)
└── assets/                 # Fuentes, íconos, imágenes
```

### Patrón de Diseño: **3 Capas**

```
┌──────────────────────┐
│   UI (CustomTkinter)  │  ← Interfaz gráfica
├──────────────────────┤
│   Services            │  ← Lógica de negocio + validaciones
├──────────────────────┤
│   Models (DAO)        │  ← Acceso a datos SQLite
└──────────────────────┘
```

---

## 📊 Base de Datos

- **Motor:** SQLite 3 (sin servidor, portable)
- **25+ tablas** con relaciones completas
- **Respaldo automático** a USB o carpeta externa
- **Auditoría** completa de todas las operaciones

Ver el [Modelo ER completo](MilBurbujas_Modelo_ER.mermaid) en formato Mermaid.

---

## 🧪 Testing

```bash
cd MilBurbujas

# Ejecutar toda la suite de pruebas
python -m tests.test_fase3_runner

# Tests por fase
python -m tests.test_fase1_database    # Base de datos
python -m tests.test_fase2_services    # Servicios
python -m tests.test_integracion       # Integración
python -m tests.test_casos_borde       # Edge cases
python -m tests.test_reglas_negocio    # Reglas de negocio
python -m tests.test_frontend_e2e      # End-to-End
```

---

## 🔧 Tecnologías

| Tecnología | Uso |
|-----------|-----|
| **Python 3.10+** | Lenguaje principal |
| **CustomTkinter** | Interfaz gráfica moderna |
| **SQLite 3** | Base de datos local |
| **hashlib/SHA-256** | Seguridad de contraseñas |
| **Mermaid** | Diagramas ER |

---

## 📝 Reglas de Negocio Implementadas

- IVA Ecuador 15% calculado automáticamente
- Comprobante obligatorio para montos > $3.00 (RISE)
- Alertas de stock mínimo configurables
- Control de caducidad de productos (6 meses anticipación)
- Sistema de créditos con cuentas por cobrar/pagar
- Cierre de caja diario con cuadre automático
- Anulación de ventas y compras con reversión de inventario

---

## 🤝 Contribuciones

¡Las contribuciones son bienvenidas! Si deseas mejorar Mil Burbujas:

1. Haz fork del repositorio
2. Crea una rama para tu feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -m 'Agrega nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request

---

## 📄 Licencia

Este proyecto está bajo la licencia MIT. Ver el archivo `LICENSE` para más detalles.

---

<p align="center">
  Hecho con ❤️ por <a href="https://github.com/chuchobck">chuchobck</a><br/>
  <b>🫧 Mil Burbujas</b> — Gestión inteligente para tu negocio
</p>
