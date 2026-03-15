# 🫧 Mil Burbujas — Sistema de Gestión Integral para Tienda

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/SQLite-3-07405E?logo=sqlite&logoColor=white" />
  <img src="https://img.shields.io/badge/CustomTkinter-UI-blueviolet" />
  <img src="https://img.shields.io/badge/Arquitectura-3%20Capas-orange" />
  <img src="https://img.shields.io/badge/M%C3%B3dulos-15%2B-brightgreen" />
  <img src="https://img.shields.io/badge/Licencia-MIT-green" />
  <img src="https://img.shields.io/badge/Estado-Producci%C3%B3n-brightgreen" />
</p>

<p align="center">
  <b>Sistema POS + ERP ligero para tiendas de productos de belleza, limpieza y cosméticos.</b><br/>
  Punto de venta, inventario inteligente, auditoría de stock, abastecimiento, reportería financiera<br/>
  y más — todo en una app de escritorio sin necesidad de servidor.
</p>

---

## ✨ Características Principales

### 💼 Operaciones Comerciales

| Módulo | Descripción |
|--------|-------------|
| 🛒 **Ventas (POS)** | Registro rápido con lector de barras, cálculo automático de IVA 15%, impresión de comprobantes RISE |
| 📦 **Compras** | Ingreso de mercadería con actualización automática de inventario y relación proveedor-producto |
| 💳 **Cobros** | Gestión de cuentas por cobrar, abonos parciales, historial de pagos por cliente |
| 💰 **Pagos** | Control de cuentas por pagar a proveedores con seguimiento de vencimientos |
| 🧾 **Gastos** | Registro de gastos operativos categorizados |
| 🔒 **Cierre de Caja** | Cierre diario con cuadre automático efectivo vs sistema |

### 📦 Gestión de Inventario y Catálogo

| Módulo | Descripción |
|--------|-------------|
| 🏷️ **Catálogo** | Productos, categorías jerárquicas, marcas y líneas con filtros inteligentes |
| 📋 **Inventario** | Stock en tiempo real, alertas de mínimo, ajustes manuales y movimientos trazables |
| 🚚 **Abastecimiento** | Panel de reposición: productos bajo stock + proveedor principal + precio de compra. Gestión de proveedores por producto |
| 📝 **Auditoría de Stock** | Conteo físico por categoría o global, escaneo con código de barras, ajuste automático de diferencias, historial de discrepancias |

### 📊 Inteligencia y Control

| Módulo | Descripción |
|--------|-------------|
| 📊 **Dashboard** | KPIs en tiempo real: ventas del día, stock, cobros pendientes, caja |
| 📈 **Reportes** | 8 reportes: ventas, compras, inventario, financieros, rentabilidad y más |
| 👤 **Usuarios** | Roles Admin / Cajero con autenticación SHA-256 y permisos por módulo |
| 🏭 **Proveedores** | Directorio completo con productos asociados e historial de precios |
| 👥 **Clientes** | CRUD con historial de compras, créditos y datos de contacto |

---

## � Módulos Destacados

### 🚚 Abastecimiento — Reposición Inteligente

Panel unificado que responde la pregunta: **"¿Qué necesito comprar, a quién y a qué precio?"**

- **Tab Reposición:** Muestra productos con stock bajo mínimo + proveedor principal + último precio de compra + valor estimado de reposición
- **Tab Proveedores x Producto:** Asigna múltiples proveedores por producto con precios y prioridad

```
┌─ Reposición ──────────────────────────────────────────┐
│  KPIs: 87 productos bajo stock | $2,340 valor estimado│
│                                                        │
│  Producto          Stock  Mín  Proveedor     Precio   │
│  Shampoo Sedal 400ml  2    5   Dist. Unilever  $3.20  │
│  Jabón Protex 3pk      0    3   Dist. Colgate   $4.50  │
│  Cloro Ajax 1L          1    5   La Fabril        $1.80  │
└────────────────────────────────────────────────────────┘
```

### 📝 Auditoría de Stock — Conteo Físico Profesional

Sistema completo de **conteo físico** para detectar merma, pérdida o errores de inventario:

1. **Crear conteo** → por categoría específica o inventario completo
2. **Escanear productos** → código de barras + cantidad real, con progreso en tiempo real
3. **Finalizar** → el sistema calcula diferencias y opcionalmente **ajusta el stock automáticamente**

```
Flujo:  Crear Sesión → Escanear → Revisar Diferencias → Finalizar + Auto-ajuste
                                                              │
                                         ┌────────────────────┤
                                         │  Shampoo X         │
                                         │  Sistema: 20       │
                                         │  Físico:  17       │
                                         │  Dif: -3 ⚠️        │
                                         │  → Ajuste auto -3  │
                                         └─────────────────────┘
```

- **Historial:** Consulta conteos anteriores con detalle producto por producto
- **Discrepancias:** Análisis por categoría — identifica áreas con más pérdida recurrente

---

## �🖥️ Capturas de Pantalla

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
├── config.py               # Configuración global (IVA, rutas, estados)
├── database/
│   ├── connection.py       # Singleton SQLite con WAL + transacciones
│   ├── schema.sql          # Esquema completo (29 tablas)
│   ├── seed_data.sql       # Datos iniciales (categorías, marcas, líneas)
│   └── backup.py           # Respaldo y restauración a USB/carpeta
├── models/                 # Capa DAO — Data Access Objects
│   ├── base_model.py       # CRUD genérico reutilizable (insert, update, delete, query)
│   ├── producto.py         # Producto con stock, precios, códigos de barra
│   ├── venta.py / venta_detalle.py
│   ├── compra.py / compra_detalle.py
│   ├── conteo_fisico.py    # Sesiones de conteo de inventario
│   ├── conteo_fisico_detalle.py  # Líneas de conteo por producto
│   └── ... (22 modelos)
├── services/               # Lógica de negocio + validaciones
│   ├── venta_service.py    # Facturación, anulación, cálculo IVA
│   ├── inventario_service.py  # Movimientos, ajustes, alertas stock
│   ├── auditoria_stock_service.py  # Conteo físico + auto-ajuste
│   ├── reporte_service.py  # 8 reportes financieros y operativos
│   └── ... (14 servicios)
├── ui/                     # Interfaz gráfica — CustomTkinter
│   ├── app.py              # Ventana principal + sidebar + navegación por roles
│   ├── login.py            # Autenticación con hash SHA-256
│   ├── theme.py            # Sistema de temas: colores, fuentes, menú, permisos
│   ├── widgets.py          # Componentes: ScrollableTable, KPIBox, Dialog, FormField...
│   └── views/              # 15 vistas del sistema
│       ├── dashboard.py
│       ├── ventas.py
│       ├── compras.py
│       ├── catalogo.py     # Productos, categorías, marcas, líneas
│       ├── abastecimiento.py  # Reposición + Proveedores x Producto
│       ├── auditoria_stock.py # Conteo físico + Historial + Discrepancias
│       ├── inventario.py
│       └── ... (8 más)
├── tests/                  # Suite completa de pruebas (7 archivos)
│   ├── test_fase1_database.py     # Conexión, schema, CRUD
│   ├── test_fase2_services.py     # Lógica de negocio
│   ├── test_fase3_runner.py       # Runner completo
│   ├── test_integracion.py        # Flujos end-to-end
│   ├── test_reglas_negocio.py     # IVA, RISE, stock mínimo
│   ├── test_casos_borde.py        # Edge cases
│   └── test_frontend_e2e.py       # UI smoke tests
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

- **Motor:** SQLite 3 con WAL mode (escrituras concurrentes sin bloqueo)
- **29 tablas** con foreign keys, constraints, índices y checks
- **Transacciones ACID** con context manager para operaciones críticas
- **Respaldo automático** a USB o carpeta externa
- **Auditoría completa:** cada INSERT/UPDATE/DELETE queda registrado con usuario, timestamp y datos antes/después
- **Secuencias automáticas:** numeración de ventas (VTA-000001), compras (CMP-000001), conteos (CF-000001) etc.

### Tablas principales

```
usuario, producto, categoria, marca, linea_producto, unidad_medida,
venta, venta_detalle, compra, compra_detalle, cliente, proveedor,
proveedor_producto, movimiento_inventario, ajuste_inventario,
conteo_fisico, conteo_fisico_detalle, cuenta_cobrar, cuenta_pagar,
pago_cliente, pago_proveedor, gasto_operativo, cierre_caja,
promocion, promocion_producto, precio_referencia, configuracion, auditoria
```

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

## 🔧 Stack Técnico

| Tecnología | Uso | Detalle |
|-----------|-----|---------|
| **Python 3.10+** | Lenguaje principal | Type hints, f-strings, context managers |
| **CustomTkinter** | Interfaz gráfica | UI moderna sobre Tkinter, temas personalizados |
| **SQLite 3** | Base de datos | WAL mode, foreign keys, generated columns |
| **hashlib/SHA-256** | Seguridad | Hashing de contraseñas con salt |
| **Mermaid** | Documentación | Diagramas ER versionados en el repo |

### Patrones de diseño aplicados

- **Singleton** — `DatabaseConnection` garantiza una sola conexión
- **DAO (Data Access Object)** — `BaseModel` con CRUD genérico heredable
- **Service Layer** — Toda la lógica de negocio aislada de la UI
- **Observer** — `StringVar.trace_add` para filtros reactivos en ComboBox
- **Transaction Script** — Operaciones complejas (ventas, conteos) dentro de `with db.transaction()`

---

## 📝 Reglas de Negocio Implementadas

- **IVA Ecuador 15%** calculado automáticamente en ventas y compras
- **RISE:** Comprobante obligatorio para montos > $3.00
- **Stock mínimo configurable** por producto con alertas automáticas
- **Caducidad:** Control con 6 meses de anticipación
- **Créditos:** Cuentas por cobrar/pagar con abonos parciales y saldos
- **Cierre de caja:** Cuadre diario efectivo vs sistema con diferencia calculada
- **Anulación con reversión:** Anular ventas/compras revierte inventario automáticamente
- **Conteo físico:** Auto-ajuste de stock al finalizar auditoría
- **Proveedor principal:** Se actualiza automáticamente al registrar compras
- **Precios de referencia:** Historial de precios de compra por proveedor

---

## 🤝 Contribuciones

¡Las contribuciones son bienvenidas! Si deseas mejorar Mil Burbujas:

1. Haz fork del repositorio
2. Crea una rama para tu feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -m 'feat: agrega nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request

### Ideas para contribuir

- [ ] Exportación de reportes a PDF/Excel
- [ ] Integración con impresoras térmicas de tickets
- [ ] Sincronización multi-sucursal
- [ ] Dashboard con gráficas (matplotlib/plotly)
- [ ] Módulo de fidelización / puntos de cliente

---

## 📄 Licencia

Este proyecto está bajo la licencia MIT. Ver el archivo `LICENSE` para más detalles.

---

<p align="center">
  Hecho con ❤️ por <a href="https://github.com/chuchobck">chuchobck</a><br/>
  <b>🫧 Mil Burbujas</b> — Gestión inteligente para tu negocio<br/><br/>
  <i>⭐ Si te resulta útil, dale una estrella al repo — ayuda mucho.</i>
</p>
