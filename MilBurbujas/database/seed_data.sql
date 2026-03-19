-- ============================================
-- Mil Burbujas - DATOS INICIALES (SEED)
-- Se ejecuta DESPUÉS de schema.sql
-- Actualizado: 2026-03-13 — Catálogo definitivo
-- ============================================

-- ===== USUARIOS =====
-- Admin: admin@milburbujas.local / admin123
INSERT OR IGNORE INTO usuario (nombre_completo, email, contrasena_hash, rol, estado)
VALUES ('Propietaria', 'admin@milburbujas.local', '$2b$12$LJ3m5z5Y5Q5Z5Y5Q5Z5Y5uDefaultHashParaCambiar', 'ADMIN', 'ACT');

-- Cajero: cajero@milburbujas.local / cajero123
INSERT OR IGNORE INTO usuario (nombre_completo, email, contrasena_hash, rol, estado)
VALUES ('Cajero', 'cajero@milburbujas.local', '1ed4353e845e2e537e017c0fac3a0d402d231809b7989e90da15191c1148a93f', 'CAJERO', 'ACT');

-- ===== CONFIGURACIÓN DEL SISTEMA =====
INSERT OR IGNORE INTO configuracion (clave, valor, descripcion, tipo_dato) VALUES
('IVA_PORCENTAJE',           '15',          'Porcentaje de IVA Ecuador',                    'NUMERIC'),
('MONTO_MIN_COMPROBANTE',    '3.00',        'Monto mínimo para emitir comprobante RISE',    'NUMERIC'),
('DIAS_ALERTA_CADUCIDAD',    '180',         'Días antes de caducidad para alertar',         'NUMERIC'),
('STOCK_MINIMO_DEFAULT',     '5',           'Stock mínimo por defecto para alertas',        'NUMERIC'),
('NOMBRE_NEGOCIO',           'MilBurbujas', 'Nombre comercial de la tienda',                'STRING'),
('RUC_NEGOCIO',              '',            'RUC del negocio para comprobantes',             'STRING'),
('DIRECCION_NEGOCIO',        '',            'Dirección del negocio',                         'STRING'),
('TELEFONO_NEGOCIO',         '',            'Teléfono del negocio',                          'STRING'),
('MONEDA_SIMBOLO',           '$',           'Símbolo de moneda (dólar USD)',                 'STRING'),
('SECUENCIA_COMPROBANTE',    '1',           'Último número de comprobante emitido',          'NUMERIC'),
('SECUENCIA_CUENTA_COBRAR',  '1',           'Último número de cuenta por cobrar',            'NUMERIC'),
('SECUENCIA_CUENTA_PAGAR',   '1',           'Último número de cuenta por pagar',             'NUMERIC'),
('SECUENCIA_AJUSTE',         '1',           'Último número de ajuste de inventario',         'NUMERIC'),
('MARGEN_GANANCIA_DEFAULT',  '23',          'Margen de ganancia por defecto (%)',            'NUMERIC');

-- ===== UNIDADES DE MEDIDA =====
INSERT OR IGNORE INTO unidad_medida (nombre, abreviatura, tipo) VALUES
('Unidad',      'UN',  'CONTEO'),
('Paquete',     'PAQ', 'CONTEO'),
('Paca',        'PAC', 'CONTEO'),
('Caja',        'CAJ', 'CONTEO'),
('Docena',      'DOC', 'CONTEO'),
('Litro',       'LT',  'VOLUMEN'),
('Mililitro',   'ML',  'VOLUMEN'),
('Gramo',       'GR',  'PESO'),
('Kilogramo',   'KG',  'PESO'),
('Sachet',      'SCH', 'CONTEO'),
('Sobre',       'SBR', 'CONTEO'),
('Rollo',       'ROL', 'CONTEO'),
('Frasco',      'FRA', 'CONTEO'),
('Tarro',       'TAR', 'CONTEO'),
('Tubo',        'TUB', 'CONTEO');

-- =============================================
-- 11 CATEGORÍAS PRINCIPALES (Nivel 0)
-- =============================================
INSERT OR IGNORE INTO categoria (nombre, descripcion, nivel) VALUES
('Higiene Personal',      'Jabón corporal, desodorantes, protector solar, cremas, aceites, barberas',         0),
('Cuidado Capilar',       'Shampoo, acondicionador, cremas de peinar, tratamientos, tintes, matizantes',      0),
('Cuidado Bucal',         'Pasta dental, cepillos, enjuague bucal, hilo dental',                              0),
('Maquillaje',            'Base, labiales, rímel, sombras, delineadores, esmaltes, pestañas postizas',        0),
('Accesorios de Belleza', 'Peinillas, cepillos, vinchas, diademas, rulos, espejos, bolsos, brochas',         0),
('Higiene Femenina',      'Toallas higiénicas en paquete, sachet y protectores diarios',                      0),
('Cuidado del Bebé',      'Aceites, talco y toallitas húmedas para bebé',                                     0),
('Limpieza del Hogar',    'Detergente, suavizante, lavavajillas, cloro, ambientales, guantes',                0),
('Papel y Desechables',   'Papel higiénico, servilletas, pañuelos, fundas, algodón, cotonetes',               0),
('Snacks y Alimentos',    'Helados y chicles — único rubro alimenticio',                                      0),
('Artículos Varios',      'Baterías, frascos vacíos y otros artículos diversos',                               0);

-- =============================================
-- SUBCATEGORÍAS (Nivel 1)
-- =============================================

-- ── 1. HIGIENE PERSONAL ──
INSERT OR IGNORE INTO categoria (nombre, descripcion, nivel, categoria_padre_id)
SELECT 'Jabón corporal', 'Jabones corporales en barra y líquido', 1, categoria_id
FROM categoria WHERE nombre = 'Higiene Personal';

INSERT OR IGNORE INTO categoria (nombre, descripcion, nivel, categoria_padre_id)
SELECT 'Desodorantes', 'Desodorantes en barra, roll-on y aerosol', 1, categoria_id
FROM categoria WHERE nombre = 'Higiene Personal';

INSERT OR IGNORE INTO categoria (nombre, descripcion, nivel, categoria_padre_id)
SELECT 'Talco corporal', 'Talco para cuerpo y pies', 1, categoria_id
FROM categoria WHERE nombre = 'Higiene Personal';

INSERT OR IGNORE INTO categoria (nombre, descripcion, nivel, categoria_padre_id)
SELECT 'Protector solar', 'Protectores solares de diferentes FPS', 1, categoria_id
FROM categoria WHERE nombre = 'Higiene Personal';

INSERT OR IGNORE INTO categoria (nombre, descripcion, nivel, categoria_padre_id)
SELECT 'Gel antibacterial', 'Gel antibacterial en frasco y sachet', 1, categoria_id
FROM categoria WHERE nombre = 'Higiene Personal';

INSERT OR IGNORE INTO categoria (nombre, descripcion, nivel, categoria_padre_id)
SELECT 'Alcohol', 'Alcohol antiséptico en diferentes presentaciones', 1, categoria_id
FROM categoria WHERE nombre = 'Higiene Personal';

INSERT OR IGNORE INTO categoria (nombre, descripcion, nivel, categoria_padre_id)
SELECT 'Cremas corporales', 'Cremas hidratantes para cuerpo', 1, categoria_id
FROM categoria WHERE nombre = 'Higiene Personal';

INSERT OR IGNORE INTO categoria (nombre, descripcion, nivel, categoria_padre_id)
SELECT 'Cremas para manos', 'Cremas hidratantes para manos', 1, categoria_id
FROM categoria WHERE nombre = 'Higiene Personal';

INSERT OR IGNORE INTO categoria (nombre, descripcion, nivel, categoria_padre_id)
SELECT 'Aceites corporales', 'Aceites corporales: Johnson, coco, ricino', 1, categoria_id
FROM categoria WHERE nombre = 'Higiene Personal';

INSERT OR IGNORE INTO categoria (nombre, descripcion, nivel, categoria_padre_id)
SELECT 'Mascarillas faciales', 'Mascarillas faciales desechables', 1, categoria_id
FROM categoria WHERE nombre = 'Higiene Personal';

INSERT OR IGNORE INTO categoria (nombre, descripcion, nivel, categoria_padre_id)
SELECT 'Afeitadoras / Barberas', 'Barberas de doble y triple hoja', 1, categoria_id
FROM categoria WHERE nombre = 'Higiene Personal';

-- ── 2. CUIDADO CAPILAR ──
INSERT OR IGNORE INTO categoria (nombre, descripcion, nivel, categoria_padre_id)
SELECT 'Shampoo', 'Shampoo para diferentes tipos de cabello', 1, categoria_id
FROM categoria WHERE nombre = 'Cuidado Capilar';

INSERT OR IGNORE INTO categoria (nombre, descripcion, nivel, categoria_padre_id)
SELECT 'Acondicionador', 'Acondicionador para diferentes tipos de cabello', 1, categoria_id
FROM categoria WHERE nombre = 'Cuidado Capilar';

INSERT OR IGNORE INTO categoria (nombre, descripcion, nivel, categoria_padre_id)
SELECT 'Cremas de peinar', 'Cremas de peinar de diferentes marcas', 1, categoria_id
FROM categoria WHERE nombre = 'Cuidado Capilar';

INSERT OR IGNORE INTO categoria (nombre, descripcion, nivel, categoria_padre_id)
SELECT 'Tratamientos capilares', 'Tratamientos en frasco para cabello', 1, categoria_id
FROM categoria WHERE nombre = 'Cuidado Capilar';

INSERT OR IGNORE INTO categoria (nombre, descripcion, nivel, categoria_padre_id)
SELECT 'Sachet de tratamiento', 'Tratamientos capilares en sachet individual', 1, categoria_id
FROM categoria WHERE nombre = 'Cuidado Capilar';

INSERT OR IGNORE INTO categoria (nombre, descripcion, nivel, categoria_padre_id)
SELECT 'Matizantes', 'Matizantes para cabello', 1, categoria_id
FROM categoria WHERE nombre = 'Cuidado Capilar';

INSERT OR IGNORE INTO categoria (nombre, descripcion, nivel, categoria_padre_id)
SELECT 'Tintes', 'Tintes de cabello en diferentes colores y marcas', 1, categoria_id
FROM categoria WHERE nombre = 'Cuidado Capilar';

INSERT OR IGNORE INTO categoria (nombre, descripcion, nivel, categoria_padre_id)
SELECT 'Gel fijador', 'Gel fijador y spray para cabello', 1, categoria_id
FROM categoria WHERE nombre = 'Cuidado Capilar';

INSERT OR IGNORE INTO categoria (nombre, descripcion, nivel, categoria_padre_id)
SELECT 'Aceites capilares', 'Aceites para cabello: coco, argán, ricino', 1, categoria_id
FROM categoria WHERE nombre = 'Cuidado Capilar';

INSERT OR IGNORE INTO categoria (nombre, descripcion, nivel, categoria_padre_id)
SELECT 'Protector térmico', 'Protectores de calor para cabello', 1, categoria_id
FROM categoria WHERE nombre = 'Cuidado Capilar';

-- ── 3. CUIDADO BUCAL ──
INSERT OR IGNORE INTO categoria (nombre, descripcion, nivel, categoria_padre_id)
SELECT 'Pasta dental', 'Pastas dentales de diferentes marcas', 1, categoria_id
FROM categoria WHERE nombre = 'Cuidado Bucal';

INSERT OR IGNORE INTO categoria (nombre, descripcion, nivel, categoria_padre_id)
SELECT 'Cepillo dental', 'Cepillos dentales de diferentes marcas', 1, categoria_id
FROM categoria WHERE nombre = 'Cuidado Bucal';

INSERT OR IGNORE INTO categoria (nombre, descripcion, nivel, categoria_padre_id)
SELECT 'Enjuague bucal', 'Enjuagues bucales de diferentes marcas', 1, categoria_id
FROM categoria WHERE nombre = 'Cuidado Bucal';

INSERT OR IGNORE INTO categoria (nombre, descripcion, nivel, categoria_padre_id)
SELECT 'Hilo dental', 'Hilo dental de diferentes marcas', 1, categoria_id
FROM categoria WHERE nombre = 'Cuidado Bucal';

-- ── 4. MAQUILLAJE ──
INSERT OR IGNORE INTO categoria (nombre, descripcion, nivel, categoria_padre_id)
SELECT 'Base líquida', 'Maquillaje base en presentación líquida', 1, categoria_id
FROM categoria WHERE nombre = 'Maquillaje';

INSERT OR IGNORE INTO categoria (nombre, descripcion, nivel, categoria_padre_id)
SELECT 'Base en crema', 'Maquillaje base en presentación crema', 1, categoria_id
FROM categoria WHERE nombre = 'Maquillaje';

INSERT OR IGNORE INTO categoria (nombre, descripcion, nivel, categoria_padre_id)
SELECT 'Base en polvo', 'Maquillaje base en polvo compacto', 1, categoria_id
FROM categoria WHERE nombre = 'Maquillaje';

INSERT OR IGNORE INTO categoria (nombre, descripcion, nivel, categoria_padre_id)
SELECT 'Labiales', 'Labiales en diferentes colores y marcas', 1, categoria_id
FROM categoria WHERE nombre = 'Maquillaje';

INSERT OR IGNORE INTO categoria (nombre, descripcion, nivel, categoria_padre_id)
SELECT 'Rímel', 'Rímel / máscara de pestañas', 1, categoria_id
FROM categoria WHERE nombre = 'Maquillaje';

INSERT OR IGNORE INTO categoria (nombre, descripcion, nivel, categoria_padre_id)
SELECT 'Sombras', 'Sombras de ojos en diferentes colores', 1, categoria_id
FROM categoria WHERE nombre = 'Maquillaje';

INSERT OR IGNORE INTO categoria (nombre, descripcion, nivel, categoria_padre_id)
SELECT 'Delineadores', 'Delineadores de ojos y lápiz de ojos', 1, categoria_id
FROM categoria WHERE nombre = 'Maquillaje';

INSERT OR IGNORE INTO categoria (nombre, descripcion, nivel, categoria_padre_id)
SELECT 'Esmaltes', 'Esmaltes de uñas en variedad de colores', 1, categoria_id
FROM categoria WHERE nombre = 'Maquillaje';

INSERT OR IGNORE INTO categoria (nombre, descripcion, nivel, categoria_padre_id)
SELECT 'Quita esmalte', 'Quita esmalte / acetona', 1, categoria_id
FROM categoria WHERE nombre = 'Maquillaje';

INSERT OR IGNORE INTO categoria (nombre, descripcion, nivel, categoria_padre_id)
SELECT 'Pestañas postizas', 'Pestañas postizas individuales y en tira', 1, categoria_id
FROM categoria WHERE nombre = 'Maquillaje';

INSERT OR IGNORE INTO categoria (nombre, descripcion, nivel, categoria_padre_id)
SELECT 'Maquillaje compacto', 'Maquillaje compacto y polvos sueltos', 1, categoria_id
FROM categoria WHERE nombre = 'Maquillaje';

-- ── 5. ACCESORIOS DE BELLEZA ──
INSERT OR IGNORE INTO categoria (nombre, descripcion, nivel, categoria_padre_id)
SELECT 'Accesorios para uñas', 'Limas, decoraciones, tips para uñas', 1, categoria_id
FROM categoria WHERE nombre = 'Accesorios de Belleza';

INSERT OR IGNORE INTO categoria (nombre, descripcion, nivel, categoria_padre_id)
SELECT 'Alicates', 'Alicates para uñas y cutículas', 1, categoria_id
FROM categoria WHERE nombre = 'Accesorios de Belleza';

INSERT OR IGNORE INTO categoria (nombre, descripcion, nivel, categoria_padre_id)
SELECT 'Pinzas', 'Pinzas para cejas y depilación', 1, categoria_id
FROM categoria WHERE nombre = 'Accesorios de Belleza';

INSERT OR IGNORE INTO categoria (nombre, descripcion, nivel, categoria_padre_id)
SELECT 'Peinillas', 'Peinillas de diferente tipo', 1, categoria_id
FROM categoria WHERE nombre = 'Accesorios de Belleza';

INSERT OR IGNORE INTO categoria (nombre, descripcion, nivel, categoria_padre_id)
SELECT 'Cepillos', 'Cepillos para cabello', 1, categoria_id
FROM categoria WHERE nombre = 'Accesorios de Belleza';

INSERT OR IGNORE INTO categoria (nombre, descripcion, nivel, categoria_padre_id)
SELECT 'Rulos', 'Rulos de diferentes tamaños', 1, categoria_id
FROM categoria WHERE nombre = 'Accesorios de Belleza';

INSERT OR IGNORE INTO categoria (nombre, descripcion, nivel, categoria_padre_id)
SELECT 'Diademas', 'Diademas para cabello', 1, categoria_id
FROM categoria WHERE nombre = 'Accesorios de Belleza';

INSERT OR IGNORE INTO categoria (nombre, descripcion, nivel, categoria_padre_id)
SELECT 'Vinchas', 'Vinchas y sujetadores para cabello', 1, categoria_id
FROM categoria WHERE nombre = 'Accesorios de Belleza';

INSERT OR IGNORE INTO categoria (nombre, descripcion, nivel, categoria_padre_id)
SELECT 'Gorro de baño', 'Gorros de baño impermeables', 1, categoria_id
FROM categoria WHERE nombre = 'Accesorios de Belleza';

INSERT OR IGNORE INTO categoria (nombre, descripcion, nivel, categoria_padre_id)
SELECT 'Rizadores de pestañas', 'Rizadores / encrespadores de pestañas', 1, categoria_id
FROM categoria WHERE nombre = 'Accesorios de Belleza';

INSERT OR IGNORE INTO categoria (nombre, descripcion, nivel, categoria_padre_id)
SELECT 'Espejos', 'Espejos de mano y de bolso', 1, categoria_id
FROM categoria WHERE nombre = 'Accesorios de Belleza';

INSERT OR IGNORE INTO categoria (nombre, descripcion, nivel, categoria_padre_id)
SELECT 'Cosmetiqueros', 'Estuches y cosmetiqueros para maquillaje', 1, categoria_id
FROM categoria WHERE nombre = 'Accesorios de Belleza';

INSERT OR IGNORE INTO categoria (nombre, descripcion, nivel, categoria_padre_id)
SELECT 'Bolsos', 'Bolsos y carteras', 1, categoria_id
FROM categoria WHERE nombre = 'Accesorios de Belleza';

INSERT OR IGNORE INTO categoria (nombre, descripcion, nivel, categoria_padre_id)
SELECT 'Medias nylon', 'Medias, nylon, medias invisibles', 1, categoria_id
FROM categoria WHERE nombre = 'Accesorios de Belleza';

INSERT OR IGNORE INTO categoria (nombre, descripcion, nivel, categoria_padre_id)
SELECT 'Accesorios para maquillaje', 'Brochas, esponjas, aplicadores', 1, categoria_id
FROM categoria WHERE nombre = 'Accesorios de Belleza';

-- ── 6. HIGIENE FEMENINA ──
INSERT OR IGNORE INTO categoria (nombre, descripcion, nivel, categoria_padre_id)
SELECT 'Toallas higiénicas', 'Toallas higiénicas en paquete de diferentes marcas', 1, categoria_id
FROM categoria WHERE nombre = 'Higiene Femenina';

INSERT OR IGNORE INTO categoria (nombre, descripcion, nivel, categoria_padre_id)
SELECT 'Toallas higiénicas en sachet', 'Toallas higiénicas individuales en sachet', 1, categoria_id
FROM categoria WHERE nombre = 'Higiene Femenina';

INSERT OR IGNORE INTO categoria (nombre, descripcion, nivel, categoria_padre_id)
SELECT 'Protectores diarios', 'Protectores diarios femeninos', 1, categoria_id
FROM categoria WHERE nombre = 'Higiene Femenina';

-- ── 7. CUIDADO DEL BEBÉ ──
INSERT OR IGNORE INTO categoria (nombre, descripcion, nivel, categoria_padre_id)
SELECT 'Aceites para bebé', 'Aceites suaves para piel de bebé', 1, categoria_id
FROM categoria WHERE nombre = 'Cuidado del Bebé';

INSERT OR IGNORE INTO categoria (nombre, descripcion, nivel, categoria_padre_id)
SELECT 'Talco para bebé', 'Talco para bebé', 1, categoria_id
FROM categoria WHERE nombre = 'Cuidado del Bebé';

INSERT OR IGNORE INTO categoria (nombre, descripcion, nivel, categoria_padre_id)
SELECT 'Toallitas húmedas', 'Toallitas húmedas para bebé', 1, categoria_id
FROM categoria WHERE nombre = 'Cuidado del Bebé';

-- ── 8. LIMPIEZA DEL HOGAR ──
INSERT OR IGNORE INTO categoria (nombre, descripcion, nivel, categoria_padre_id)
SELECT 'Detergente en polvo', 'Detergente y jabón en polvo para ropa', 1, categoria_id
FROM categoria WHERE nombre = 'Limpieza del Hogar';

INSERT OR IGNORE INTO categoria (nombre, descripcion, nivel, categoria_padre_id)
SELECT 'Detergente líquido', 'Detergente líquido para ropa', 1, categoria_id
FROM categoria WHERE nombre = 'Limpieza del Hogar';

INSERT OR IGNORE INTO categoria (nombre, descripcion, nivel, categoria_padre_id)
SELECT 'Suavizante', 'Suavizantes de ropa', 1, categoria_id
FROM categoria WHERE nombre = 'Limpieza del Hogar';

INSERT OR IGNORE INTO categoria (nombre, descripcion, nivel, categoria_padre_id)
SELECT 'Lava platos', 'Jabón y detergente para lavar platos', 1, categoria_id
FROM categoria WHERE nombre = 'Limpieza del Hogar';

INSERT OR IGNORE INTO categoria (nombre, descripcion, nivel, categoria_padre_id)
SELECT 'Limpiapisos', 'Productos para limpiar y desinfectar pisos', 1, categoria_id
FROM categoria WHERE nombre = 'Limpieza del Hogar';

INSERT OR IGNORE INTO categoria (nombre, descripcion, nivel, categoria_padre_id)
SELECT 'Cloro', 'Cloro y lejía', 1, categoria_id
FROM categoria WHERE nombre = 'Limpieza del Hogar';

INSERT OR IGNORE INTO categoria (nombre, descripcion, nivel, categoria_padre_id)
SELECT 'Javol líquido', 'Javol líquido desinfectante', 1, categoria_id
FROM categoria WHERE nombre = 'Limpieza del Hogar';

INSERT OR IGNORE INTO categoria (nombre, descripcion, nivel, categoria_padre_id)
SELECT 'Ambientadores', 'Ambientales en pastilla, aerosol y líquido', 1, categoria_id
FROM categoria WHERE nombre = 'Limpieza del Hogar';

INSERT OR IGNORE INTO categoria (nombre, descripcion, nivel, categoria_padre_id)
SELECT 'Guantes de limpieza', 'Guantes de látex y nitrilo para limpieza', 1, categoria_id
FROM categoria WHERE nombre = 'Limpieza del Hogar';

INSERT OR IGNORE INTO categoria (nombre, descripcion, nivel, categoria_padre_id)
SELECT 'Jabón en barra para lavar', 'Jabón en barra para lavado de ropa', 1, categoria_id
FROM categoria WHERE nombre = 'Limpieza del Hogar';

INSERT OR IGNORE INTO categoria (nombre, descripcion, nivel, categoria_padre_id)
SELECT 'Atomizadores', 'Atomizadores y frascos con spray', 1, categoria_id
FROM categoria WHERE nombre = 'Limpieza del Hogar';

-- ── 9. PAPEL Y DESECHABLES ──
INSERT OR IGNORE INTO categoria (nombre, descripcion, nivel, categoria_padre_id)
SELECT 'Papel higiénico', 'Papel higiénico de diferentes marcas', 1, categoria_id
FROM categoria WHERE nombre = 'Papel y Desechables';

INSERT OR IGNORE INTO categoria (nombre, descripcion, nivel, categoria_padre_id)
SELECT 'Papel higiénico industrial', 'Rollos grandes de papel higiénico industrial', 1, categoria_id
FROM categoria WHERE nombre = 'Papel y Desechables';

INSERT OR IGNORE INTO categoria (nombre, descripcion, nivel, categoria_padre_id)
SELECT 'Servilletas', 'Servilletas de mesa', 1, categoria_id
FROM categoria WHERE nombre = 'Papel y Desechables';

INSERT OR IGNORE INTO categoria (nombre, descripcion, nivel, categoria_padre_id)
SELECT 'Pañuelos', 'Pañuelos desechables para gripe', 1, categoria_id
FROM categoria WHERE nombre = 'Papel y Desechables';

INSERT OR IGNORE INTO categoria (nombre, descripcion, nivel, categoria_padre_id)
SELECT 'Fundas de basura', 'Fundas de basura de diferentes tamaños', 1, categoria_id
FROM categoria WHERE nombre = 'Papel y Desechables';

INSERT OR IGNORE INTO categoria (nombre, descripcion, nivel, categoria_padre_id)
SELECT 'Algodón', 'Algodón en bolsa y rollos', 1, categoria_id
FROM categoria WHERE nombre = 'Papel y Desechables';

INSERT OR IGNORE INTO categoria (nombre, descripcion, nivel, categoria_padre_id)
SELECT 'Cotonetes', 'Hisopos / cotonetes de algodón', 1, categoria_id
FROM categoria WHERE nombre = 'Papel y Desechables';

INSERT OR IGNORE INTO categoria (nombre, descripcion, nivel, categoria_padre_id)
SELECT 'Toallas reutilizables de cocina', 'Toallas absorbentes reutilizables', 1, categoria_id
FROM categoria WHERE nombre = 'Papel y Desechables';

-- ── 10. SNACKS Y ALIMENTOS ──
INSERT OR IGNORE INTO categoria (nombre, descripcion, nivel, categoria_padre_id)
SELECT 'Helados', 'Helados de diferentes marcas y sabores', 1, categoria_id
FROM categoria WHERE nombre = 'Snacks y Alimentos';

INSERT OR IGNORE INTO categoria (nombre, descripcion, nivel, categoria_padre_id)
SELECT 'Chicles', 'Chicles y golosinas', 1, categoria_id
FROM categoria WHERE nombre = 'Snacks y Alimentos';

-- ── 11. ARTÍCULOS VARIOS ──
INSERT OR IGNORE INTO categoria (nombre, descripcion, nivel, categoria_padre_id)
SELECT 'Baterías AA', 'Pilas doble A', 1, categoria_id
FROM categoria WHERE nombre = 'Artículos Varios';

INSERT OR IGNORE INTO categoria (nombre, descripcion, nivel, categoria_padre_id)
SELECT 'Baterías AAA', 'Pilas triple A', 1, categoria_id
FROM categoria WHERE nombre = 'Artículos Varios';

INSERT OR IGNORE INTO categoria (nombre, descripcion, nivel, categoria_padre_id)
SELECT 'Frascos vacíos', 'Frascos y envases vacíos para reventa', 1, categoria_id
FROM categoria WHERE nombre = 'Artículos Varios';
