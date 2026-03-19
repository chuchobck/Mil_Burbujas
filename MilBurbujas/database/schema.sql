-- ============================================
-- Mil Burbujas - ESQUEMA DE BASE DE DATOS
-- Sistema de Gestión para Tienda de Productos
-- de Belleza, Limpieza y Cosméticos
-- Motor: SQLite 3
-- 26 tablas | 35 relaciones | 3FN
-- ============================================

PRAGMA foreign_keys = ON;
PRAGMA journal_mode = WAL;
PRAGMA encoding = 'UTF-8';

-- =============================================
-- MÓDULO CORE / SEGURIDAD
-- =============================================

CREATE TABLE IF NOT EXISTS usuario (
    usuario_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre_completo TEXT    NOT NULL,
    email           TEXT    NOT NULL UNIQUE,
    contrasena_hash TEXT    NOT NULL,
    rol             TEXT    NOT NULL DEFAULT 'ADMIN' CHECK (rol IN ('ADMIN', 'CAJERO', 'OPERADOR')),
    estado          TEXT    NOT NULL DEFAULT 'ACT'   CHECK (estado IN ('ACT', 'INA')),
    fecha_creacion  TEXT    NOT NULL DEFAULT (datetime('now', 'localtime')),
    ultimo_acceso   TEXT
);

CREATE TABLE IF NOT EXISTS configuracion (
    config_id          INTEGER PRIMARY KEY AUTOINCREMENT,
    clave              TEXT    NOT NULL UNIQUE,
    valor              TEXT    NOT NULL,
    descripcion        TEXT,
    tipo_dato          TEXT    NOT NULL CHECK (tipo_dato IN ('STRING', 'NUMERIC', 'BOOLEAN', 'DATE')),
    fecha_modificacion TEXT    NOT NULL DEFAULT (datetime('now', 'localtime'))
);

CREATE TABLE IF NOT EXISTS auditoria (
    auditoria_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id     INTEGER NOT NULL,
    tabla_afectada TEXT    NOT NULL,
    operacion      TEXT    NOT NULL CHECK (operacion IN ('INSERT', 'UPDATE', 'DELETE')),
    registro_id    TEXT    NOT NULL,
    datos_anteriores TEXT,
    datos_nuevos     TEXT,
    ip_local       TEXT,
    fecha_hora     TEXT    NOT NULL DEFAULT (datetime('now', 'localtime')),
    FOREIGN KEY (usuario_id) REFERENCES usuario (usuario_id)
);

-- =============================================
-- MÓDULO CATÁLOGO
-- =============================================

CREATE TABLE IF NOT EXISTS categoria (
    categoria_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    categoria_padre_id INTEGER,
    nombre             TEXT    NOT NULL UNIQUE,
    descripcion        TEXT,
    nivel              INTEGER NOT NULL DEFAULT 0,
    estado             TEXT    NOT NULL DEFAULT 'ACT' CHECK (estado IN ('ACT', 'INA')),
    fecha_creacion     TEXT    NOT NULL DEFAULT (datetime('now', 'localtime')),
    fecha_modificacion TEXT,
    FOREIGN KEY (categoria_padre_id) REFERENCES categoria (categoria_id)
);

CREATE TABLE IF NOT EXISTS marca (
    marca_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre         TEXT    NOT NULL UNIQUE,
    descripcion    TEXT,
    estado         TEXT    NOT NULL DEFAULT 'ACT' CHECK (estado IN ('ACT', 'INA')),
    fecha_creacion TEXT    NOT NULL DEFAULT (datetime('now', 'localtime'))
);

CREATE TABLE IF NOT EXISTS linea_producto (
    linea_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    marca_id       INTEGER NOT NULL,
    nombre         TEXT    NOT NULL,
    descripcion    TEXT,
    estado         TEXT    NOT NULL DEFAULT 'ACT' CHECK (estado IN ('ACT', 'INA')),
    fecha_creacion TEXT    NOT NULL DEFAULT (datetime('now', 'localtime')),
    FOREIGN KEY (marca_id) REFERENCES marca (marca_id),
    UNIQUE (marca_id, nombre)
);

CREATE TABLE IF NOT EXISTS unidad_medida (
    unidad_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre      TEXT    NOT NULL UNIQUE,
    abreviatura TEXT    NOT NULL UNIQUE,
    tipo        TEXT    NOT NULL CHECK (tipo IN ('CONTEO', 'PESO', 'VOLUMEN')),
    estado      TEXT    NOT NULL DEFAULT 'ACT' CHECK (estado IN ('ACT', 'INA'))
);

CREATE TABLE IF NOT EXISTS producto (
    producto_id            INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo_barras          TEXT    NOT NULL UNIQUE,
    nombre                 TEXT    NOT NULL,
    descripcion            TEXT,
    categoria_id           INTEGER NOT NULL,
    marca_id               INTEGER,
    linea_id               INTEGER,
    unidad_id              INTEGER NOT NULL,
    precio_referencia_compra REAL  DEFAULT 0.00,
    precio_venta           REAL    NOT NULL CHECK (precio_venta >= 0),
    precio_venta_minimo    REAL    DEFAULT 0.00,
    stock_actual           INTEGER NOT NULL DEFAULT 0 CHECK (stock_actual >= 0),
    stock_minimo           INTEGER NOT NULL DEFAULT 4,
    stock_maximo           INTEGER,
    fecha_caducidad        TEXT,
    dias_alerta_caducidad  INTEGER DEFAULT 180,
    aplica_iva_compra      INTEGER NOT NULL DEFAULT 1 CHECK (aplica_iva_compra IN (0, 1)),
    estado                 TEXT    NOT NULL DEFAULT 'ACT' CHECK (estado IN ('ACT', 'INA')),
    fecha_creacion         TEXT    NOT NULL DEFAULT (datetime('now', 'localtime')),
    fecha_modificacion     TEXT,
    FOREIGN KEY (categoria_id) REFERENCES categoria (categoria_id),
    FOREIGN KEY (marca_id)     REFERENCES marca (marca_id),
    FOREIGN KEY (linea_id)     REFERENCES linea_producto (linea_id),
    FOREIGN KEY (unidad_id)    REFERENCES unidad_medida (unidad_id)
);

-- =============================================
-- MÓDULO PROVEEDORES
-- =============================================

CREATE TABLE IF NOT EXISTS proveedor (
    proveedor_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    ruc_cedula         TEXT    NOT NULL UNIQUE,
    razon_social       TEXT    NOT NULL,
    nombre_contacto    TEXT,
    telefono           TEXT,
    whatsapp           TEXT,
    email              TEXT,
    direccion          TEXT,
    tipo_credito       TEXT    NOT NULL DEFAULT 'CONTADO' CHECK (tipo_credito IN ('CONTADO', 'CREDITO_15', 'CREDITO_60', 'CREDITO_90')),
    plazo_credito_dias INTEGER DEFAULT 0,
    frecuencia_pedido  TEXT    CHECK (frecuencia_pedido IN ('SEMANAL', 'QUINCENAL', 'MENSUAL', 'BAJO_PEDIDO')),
    dia_visita         TEXT,
    observaciones      TEXT,
    estado             TEXT    NOT NULL DEFAULT 'ACT' CHECK (estado IN ('ACT', 'INA')),
    fecha_creacion     TEXT    NOT NULL DEFAULT (datetime('now', 'localtime')),
    fecha_modificacion TEXT
);

CREATE TABLE IF NOT EXISTS proveedor_producto (
    proveedor_producto_id INTEGER PRIMARY KEY AUTOINCREMENT,
    proveedor_id          INTEGER NOT NULL,
    producto_id           INTEGER NOT NULL,
    precio_compra         REAL    NOT NULL CHECK (precio_compra >= 0),
    precio_compra_con_iva REAL,
    incluye_iva           INTEGER NOT NULL DEFAULT 1 CHECK (incluye_iva IN (0, 1)),
    es_proveedor_principal INTEGER NOT NULL DEFAULT 0 CHECK (es_proveedor_principal IN (0, 1)),
    fecha_ultimo_precio   TEXT    NOT NULL DEFAULT (datetime('now', 'localtime')),
    estado                TEXT    NOT NULL DEFAULT 'ACT' CHECK (estado IN ('ACT', 'INA')),
    FOREIGN KEY (proveedor_id) REFERENCES proveedor (proveedor_id),
    FOREIGN KEY (producto_id)  REFERENCES producto (producto_id),
    UNIQUE (proveedor_id, producto_id)
);

CREATE TABLE IF NOT EXISTS precio_referencia (
    precio_ref_id  INTEGER PRIMARY KEY AUTOINCREMENT,
    producto_id    INTEGER NOT NULL,
    origen         TEXT    NOT NULL CHECK (origen IN ('SUPERMERCADO', 'HIPERMERCADO', 'TIENDA', 'ONLINE')),
    nombre_comercio TEXT   NOT NULL,
    precio         REAL    NOT NULL CHECK (precio >= 0),
    fecha_consulta TEXT    NOT NULL,
    observaciones  TEXT,
    FOREIGN KEY (producto_id) REFERENCES producto (producto_id)
);

-- =============================================
-- MÓDULO CLIENTES
-- =============================================

CREATE TABLE IF NOT EXISTS cliente (
    cliente_id        INTEGER PRIMARY KEY AUTOINCREMENT,
    cedula            TEXT    NOT NULL UNIQUE,
    nombres           TEXT    NOT NULL,
    apellidos         TEXT    NOT NULL,
    telefono          TEXT,
    direccion         TEXT,
    habilitado_credito INTEGER NOT NULL DEFAULT 0 CHECK (habilitado_credito IN (0, 1)),
    limite_credito    REAL    DEFAULT 0.00,
    saldo_pendiente   REAL    NOT NULL DEFAULT 0.00,
    frecuencia_pago   TEXT    CHECK (frecuencia_pago IN ('QUINCENAL', 'MENSUAL', 'FIN_DE_MES')),
    observaciones     TEXT,
    estado            TEXT    NOT NULL DEFAULT 'ACT' CHECK (estado IN ('ACT', 'INA')),
    fecha_creacion    TEXT    NOT NULL DEFAULT (datetime('now', 'localtime')),
    fecha_modificacion TEXT
);

-- =============================================
-- MÓDULO COMPRAS
-- =============================================

CREATE TABLE IF NOT EXISTS compra (
    compra_id         INTEGER PRIMARY KEY AUTOINCREMENT,
    numero_factura    TEXT    NOT NULL,
    proveedor_id      INTEGER NOT NULL,
    usuario_id        INTEGER NOT NULL,
    fecha_compra      TEXT    NOT NULL,
    fecha_recepcion   TEXT,
    subtotal_sin_iva  REAL    NOT NULL DEFAULT 0.00,
    monto_iva         REAL    NOT NULL DEFAULT 0.00,
    total             REAL    NOT NULL CHECK (total >= 0),
    tipo_pago         TEXT    NOT NULL CHECK (tipo_pago IN ('CONTADO', 'CREDITO')),
    plazo_credito_dias INTEGER DEFAULT 0,
    estado            TEXT    NOT NULL DEFAULT 'REGISTRADA' CHECK (estado IN ('REGISTRADA', 'RECIBIDA', 'ANULADA')),
    observaciones     TEXT,
    fecha_creacion    TEXT    NOT NULL DEFAULT (datetime('now', 'localtime')),
    FOREIGN KEY (proveedor_id) REFERENCES proveedor (proveedor_id),
    FOREIGN KEY (usuario_id)   REFERENCES usuario (usuario_id),
    UNIQUE (numero_factura, proveedor_id)
);

CREATE TABLE IF NOT EXISTS compra_detalle (
    compra_detalle_id  INTEGER PRIMARY KEY AUTOINCREMENT,
    compra_id          INTEGER NOT NULL,
    producto_id        INTEGER NOT NULL,
    cantidad           REAL    NOT NULL CHECK (cantidad > 0),
    precio_unitario    REAL    NOT NULL CHECK (precio_unitario >= 0),
    incluye_iva        INTEGER NOT NULL DEFAULT 1 CHECK (incluye_iva IN (0, 1)),
    precio_sin_iva     REAL    NOT NULL CHECK (precio_sin_iva >= 0),
    subtotal           REAL    NOT NULL CHECK (subtotal >= 0),
    fecha_caducidad_lote TEXT,
    FOREIGN KEY (compra_id)   REFERENCES compra (compra_id),
    FOREIGN KEY (producto_id) REFERENCES producto (producto_id)
);

-- =============================================
-- MÓDULO VENTAS / POS
-- =============================================

CREATE TABLE IF NOT EXISTS venta (
    venta_id                INTEGER PRIMARY KEY AUTOINCREMENT,
    numero_comprobante      TEXT    NOT NULL UNIQUE,
    cliente_id              INTEGER,
    usuario_id              INTEGER NOT NULL,
    fecha_venta             TEXT    NOT NULL DEFAULT (datetime('now', 'localtime')),
    subtotal                REAL    NOT NULL DEFAULT 0.00,
    descuento               REAL    NOT NULL DEFAULT 0.00,
    total                   REAL    NOT NULL CHECK (total >= 0),
    metodo_pago             TEXT    NOT NULL CHECK (metodo_pago IN ('EFECTIVO', 'TRANSFERENCIA', 'CREDITO', 'MIXTO')),
    monto_recibido          REAL,
    cambio                  REAL,
    referencia_transferencia TEXT,
    es_credito              INTEGER NOT NULL DEFAULT 0 CHECK (es_credito IN (0, 1)),
    comprobante_emitido     INTEGER NOT NULL DEFAULT 0 CHECK (comprobante_emitido IN (0, 1)),
    estado                  TEXT    NOT NULL DEFAULT 'COMPLETADA' CHECK (estado IN ('COMPLETADA', 'ANULADA')),
    observaciones           TEXT,
    fecha_creacion          TEXT    NOT NULL DEFAULT (datetime('now', 'localtime')),
    FOREIGN KEY (cliente_id) REFERENCES cliente (cliente_id),
    FOREIGN KEY (usuario_id) REFERENCES usuario (usuario_id)
);

CREATE TABLE IF NOT EXISTS venta_detalle (
    venta_detalle_id  INTEGER PRIMARY KEY AUTOINCREMENT,
    venta_id          INTEGER NOT NULL,
    producto_id       INTEGER NOT NULL,
    promocion_id      INTEGER,
    cantidad          REAL    NOT NULL CHECK (cantidad > 0),
    precio_unitario   REAL    NOT NULL CHECK (precio_unitario >= 0),
    precio_original   REAL    NOT NULL CHECK (precio_original >= 0),
    descuento_unitario REAL   NOT NULL DEFAULT 0.00,
    subtotal          REAL    NOT NULL CHECK (subtotal >= 0),
    FOREIGN KEY (venta_id)    REFERENCES venta (venta_id),
    FOREIGN KEY (producto_id) REFERENCES producto (producto_id),
    FOREIGN KEY (promocion_id) REFERENCES promocion (promocion_id)
);

-- =============================================
-- MÓDULO CUENTAS POR COBRAR
-- =============================================

CREATE TABLE IF NOT EXISTS cuenta_cobrar (
    cuenta_cobrar_id INTEGER PRIMARY KEY AUTOINCREMENT,
    numero_cuenta    TEXT    NOT NULL UNIQUE,
    cliente_id       INTEGER NOT NULL,
    venta_id         INTEGER NOT NULL UNIQUE,
    monto_original   REAL    NOT NULL CHECK (monto_original > 0),
    saldo_pendiente  REAL    NOT NULL CHECK (saldo_pendiente >= 0),
    fecha_emision    TEXT    NOT NULL,
    fecha_vencimiento TEXT   NOT NULL,
    estado_pago      TEXT    NOT NULL DEFAULT 'PENDIENTE' CHECK (estado_pago IN ('PENDIENTE', 'PARCIAL', 'PAGADO', 'VENCIDO')),
    estado           TEXT    NOT NULL DEFAULT 'ACT' CHECK (estado IN ('ACT', 'INA')),
    observaciones    TEXT,
    fecha_creacion   TEXT    NOT NULL DEFAULT (datetime('now', 'localtime')),
    FOREIGN KEY (cliente_id) REFERENCES cliente (cliente_id),
    FOREIGN KEY (venta_id)   REFERENCES venta (venta_id)
);

CREATE TABLE IF NOT EXISTS pago_cliente (
    pago_cliente_id          INTEGER PRIMARY KEY AUTOINCREMENT,
    cuenta_cobrar_id         INTEGER NOT NULL,
    usuario_id               INTEGER NOT NULL,
    monto_pago               REAL    NOT NULL CHECK (monto_pago > 0),
    metodo_pago              TEXT    NOT NULL CHECK (metodo_pago IN ('EFECTIVO', 'TRANSFERENCIA')),
    referencia_transferencia TEXT,
    fecha_pago               TEXT    NOT NULL,
    observaciones            TEXT,
    estado                   TEXT    NOT NULL DEFAULT 'ACT' CHECK (estado IN ('ACT', 'INA')),
    fecha_creacion           TEXT    NOT NULL DEFAULT (datetime('now', 'localtime')),
    FOREIGN KEY (cuenta_cobrar_id) REFERENCES cuenta_cobrar (cuenta_cobrar_id),
    FOREIGN KEY (usuario_id)       REFERENCES usuario (usuario_id)
);

-- =============================================
-- MÓDULO CUENTAS POR PAGAR
-- =============================================

CREATE TABLE IF NOT EXISTS cuenta_pagar (
    cuenta_pagar_id  INTEGER PRIMARY KEY AUTOINCREMENT,
    numero_cuenta    TEXT    NOT NULL UNIQUE,
    proveedor_id     INTEGER NOT NULL,
    compra_id        INTEGER NOT NULL UNIQUE,
    monto_original   REAL    NOT NULL CHECK (monto_original > 0),
    saldo_pendiente  REAL    NOT NULL CHECK (saldo_pendiente >= 0),
    fecha_emision    TEXT    NOT NULL,
    fecha_vencimiento TEXT   NOT NULL,
    estado_pago      TEXT    NOT NULL DEFAULT 'PENDIENTE' CHECK (estado_pago IN ('PENDIENTE', 'PARCIAL', 'PAGADO', 'VENCIDO')),
    estado           TEXT    NOT NULL DEFAULT 'ACT' CHECK (estado IN ('ACT', 'INA')),
    observaciones    TEXT,
    fecha_creacion   TEXT    NOT NULL DEFAULT (datetime('now', 'localtime')),
    FOREIGN KEY (proveedor_id) REFERENCES proveedor (proveedor_id),
    FOREIGN KEY (compra_id)    REFERENCES compra (compra_id)
);

CREATE TABLE IF NOT EXISTS pago_proveedor (
    pago_proveedor_id        INTEGER PRIMARY KEY AUTOINCREMENT,
    cuenta_pagar_id          INTEGER NOT NULL,
    usuario_id               INTEGER NOT NULL,
    monto_pago               REAL    NOT NULL CHECK (monto_pago > 0),
    metodo_pago              TEXT    NOT NULL CHECK (metodo_pago IN ('EFECTIVO', 'TRANSFERENCIA')),
    referencia_transferencia TEXT,
    fecha_pago               TEXT    NOT NULL,
    observaciones            TEXT,
    estado                   TEXT    NOT NULL DEFAULT 'ACT' CHECK (estado IN ('ACT', 'INA')),
    fecha_creacion           TEXT    NOT NULL DEFAULT (datetime('now', 'localtime')),
    FOREIGN KEY (cuenta_pagar_id) REFERENCES cuenta_pagar (cuenta_pagar_id),
    FOREIGN KEY (usuario_id)      REFERENCES usuario (usuario_id)
);

-- =============================================
-- MÓDULO AJUSTES DE INVENTARIO
-- =============================================

CREATE TABLE IF NOT EXISTS ajuste_inventario (
    ajuste_id         INTEGER PRIMARY KEY AUTOINCREMENT,
    numero_ajuste     TEXT    NOT NULL UNIQUE,
    producto_id       INTEGER NOT NULL,
    usuario_id        INTEGER NOT NULL,
    tipo_ajuste       TEXT    NOT NULL CHECK (tipo_ajuste IN ('CONSUMO_PERSONAL', 'DANIO', 'CADUCIDAD', 'MERMA', 'DEVOLUCION_CAMBIO', 'ENTRADA_MANUAL', 'CORRECCION')),
    cantidad          REAL    NOT NULL,
    motivo            TEXT    NOT NULL,
    producto_cambio_id INTEGER,
    observaciones     TEXT,
    estado            TEXT    NOT NULL DEFAULT 'ACT' CHECK (estado IN ('ACT', 'INA')),
    fecha_creacion    TEXT    NOT NULL DEFAULT (datetime('now', 'localtime')),
    FOREIGN KEY (producto_id)       REFERENCES producto (producto_id),
    FOREIGN KEY (usuario_id)        REFERENCES usuario (usuario_id),
    FOREIGN KEY (producto_cambio_id) REFERENCES producto (producto_id)
);

CREATE TABLE IF NOT EXISTS movimiento_inventario (
    movimiento_id    INTEGER PRIMARY KEY AUTOINCREMENT,
    producto_id      INTEGER NOT NULL,
    tipo_movimiento  TEXT    NOT NULL CHECK (tipo_movimiento IN ('ENTRADA', 'SALIDA')),
    origen           TEXT    NOT NULL CHECK (origen IN ('COMPRA', 'VENTA', 'AJUSTE', 'DEVOLUCION', 'ANULACION')),
    documento_id     INTEGER NOT NULL,
    cantidad         REAL    NOT NULL CHECK (cantidad > 0),
    stock_anterior   INTEGER NOT NULL,
    stock_posterior  INTEGER NOT NULL,
    fecha_movimiento TEXT    NOT NULL DEFAULT (datetime('now', 'localtime')),
    FOREIGN KEY (producto_id) REFERENCES producto (producto_id)
);

-- =============================================
-- MÓDULO PROMOCIONES
-- =============================================

CREATE TABLE IF NOT EXISTS promocion (
    promocion_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre             TEXT    NOT NULL UNIQUE,
    descripcion        TEXT,
    tipo_promocion     TEXT    NOT NULL CHECK (tipo_promocion IN ('DESCUENTO_PRECIO', 'KIT_REGALO', 'PORCENTAJE')),
    descuento_porcentaje REAL,
    precio_promocional   REAL,
    fecha_inicio       TEXT    NOT NULL,
    fecha_fin          TEXT    NOT NULL,
    activa             INTEGER NOT NULL DEFAULT 1 CHECK (activa IN (0, 1)),
    estado             TEXT    NOT NULL DEFAULT 'ACT' CHECK (estado IN ('ACT', 'INA')),
    fecha_creacion     TEXT    NOT NULL DEFAULT (datetime('now', 'localtime')),
    fecha_modificacion TEXT
);

CREATE TABLE IF NOT EXISTS promocion_producto (
    promo_producto_id    INTEGER PRIMARY KEY AUTOINCREMENT,
    promocion_id         INTEGER NOT NULL,
    producto_id          INTEGER NOT NULL,
    cantidad_en_kit      REAL    NOT NULL DEFAULT 1.0,
    precio_individual_kit REAL,
    FOREIGN KEY (promocion_id) REFERENCES promocion (promocion_id),
    FOREIGN KEY (producto_id)  REFERENCES producto (producto_id),
    UNIQUE (promocion_id, producto_id)
);

-- =============================================
-- MÓDULO FINANCIERO
-- =============================================

CREATE TABLE IF NOT EXISTS gasto_operativo (
    gasto_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id     INTEGER NOT NULL,
    tipo_gasto     TEXT    NOT NULL CHECK (tipo_gasto IN ('ARRIENDO', 'SERVICIOS', 'TRANSPORTE', 'ALIMENTACION', 'OTROS')),
    descripcion    TEXT    NOT NULL,
    monto          REAL    NOT NULL CHECK (monto > 0),
    fecha_gasto    TEXT    NOT NULL,
    metodo_pago    TEXT    NOT NULL CHECK (metodo_pago IN ('EFECTIVO', 'TRANSFERENCIA')),
    comprobante    TEXT,
    estado         TEXT    NOT NULL DEFAULT 'ACT' CHECK (estado IN ('ACT', 'INA')),
    fecha_creacion TEXT    NOT NULL DEFAULT (datetime('now', 'localtime')),
    FOREIGN KEY (usuario_id) REFERENCES usuario (usuario_id)
);

CREATE TABLE IF NOT EXISTS cierre_caja (
    cierre_id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id                 INTEGER NOT NULL,
    fecha_cierre               TEXT    NOT NULL UNIQUE,
    total_ventas_efectivo      REAL    NOT NULL DEFAULT 0.00,
    total_ventas_transferencia REAL    NOT NULL DEFAULT 0.00,
    total_ventas_credito       REAL    NOT NULL DEFAULT 0.00,
    total_compras              REAL    NOT NULL DEFAULT 0.00,
    total_gastos               REAL    NOT NULL DEFAULT 0.00,
    efectivo_esperado          REAL    NOT NULL DEFAULT 0.00,
    efectivo_real              REAL    NOT NULL DEFAULT 0.00,
    diferencia                 REAL    NOT NULL DEFAULT 0.00,
    observaciones              TEXT,
    estado                     TEXT    NOT NULL DEFAULT 'CERRADO' CHECK (estado IN ('CERRADO', 'ANULADO')),
    fecha_creacion             TEXT    NOT NULL DEFAULT (datetime('now', 'localtime')),
    FOREIGN KEY (usuario_id) REFERENCES usuario (usuario_id)
);

-- =============================================
-- ÍNDICES ADICIONALES PARA RENDIMIENTO
-- =============================================

-- Producto
CREATE INDEX IF NOT EXISTS idx_producto_categoria   ON producto (categoria_id);
CREATE INDEX IF NOT EXISTS idx_producto_marca        ON producto (marca_id);
CREATE INDEX IF NOT EXISTS idx_producto_estado_stock ON producto (estado, stock_actual);
CREATE INDEX IF NOT EXISTS idx_producto_caducidad    ON producto (fecha_caducidad);

-- Compras
CREATE INDEX IF NOT EXISTS idx_compra_proveedor_fecha ON compra (proveedor_id, fecha_compra);

-- Ventas
CREATE INDEX IF NOT EXISTS idx_venta_fecha    ON venta (fecha_venta);
CREATE INDEX IF NOT EXISTS idx_venta_cliente  ON venta (cliente_id);

-- Cuentas por cobrar
CREATE INDEX IF NOT EXISTS idx_cc_cliente_estado ON cuenta_cobrar (cliente_id, estado_pago);
CREATE INDEX IF NOT EXISTS idx_cc_vencimiento   ON cuenta_cobrar (fecha_vencimiento);

-- Cuentas por pagar
CREATE INDEX IF NOT EXISTS idx_cp_proveedor_estado ON cuenta_pagar (proveedor_id, estado_pago);
CREATE INDEX IF NOT EXISTS idx_cp_vencimiento      ON cuenta_pagar (fecha_vencimiento);

-- Movimientos inventario
CREATE INDEX IF NOT EXISTS idx_mov_producto_fecha ON movimiento_inventario (producto_id, fecha_movimiento);

-- Proveedor-Producto
CREATE INDEX IF NOT EXISTS idx_pp_producto ON proveedor_producto (producto_id);

-- Auditoría
CREATE INDEX IF NOT EXISTS idx_aud_tabla_fecha ON auditoria (tabla_afectada, fecha_hora);

-- =============================================
-- DATOS INICIALES: Ver se