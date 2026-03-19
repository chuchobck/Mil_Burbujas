-- ============================================================
-- Mil Burbujas — DATOS DE OPERACIÓN REALISTA (3 MESES)
-- Período: 10-dic-2025 a 10-mar-2026
-- Se ejecuta DESPUÉS de schema.sql + seed_data.sql
-- ============================================================
-- ORDEN DE INSERCIÓN:
-- 1. usuario  (ya existe admin en seed_data)
-- 2. configuracion (ya existe en seed_data)
-- 3. categoria (ya existe en seed_data)
-- 4. marca (ya existe en seed_data)
-- 5. linea_producto (ya existe en seed_data)
-- 6. unidad_medida (ya existe en seed_data)
-- 7. producto
-- 8. proveedor
-- 9. proveedor_producto
-- 10. cliente
-- 11. compra
-- 12. compra_detalle
-- 13. venta
-- 14. venta_detalle
-- 15. cuenta_cobrar
-- 16. pago_cliente
-- 17. cuenta_pagar
-- 18. pago_proveedor
-- 19. ajuste_inventario
-- 20. movimiento_inventario
-- 21. promocion
-- 22. promocion_producto
-- 23. gasto_operativo
-- 24. cierre_caja
-- 25. auditoria
-- ============================================================

-- ─────────────────────────────────────────────
-- 1. USUARIO  (operadora adicional)
-- ─────────────────────────────────────────────
INSERT OR IGNORE INTO usuario (nombre_completo, email, contrasena_hash, rol, estado)
VALUES ('María Fernanda López', 'maria@milburbujas.local',
        '$2b$12$LJ3m5z5Y5Q5Z5Y5Q5Z5Y5uOperadoraHash123', 'OPERADOR', 'ACT');

-- ─────────────────────────────────────────────
-- 7. PRODUCTOS  (30 productos reales para una tienda de belleza/limpieza)
-- ─────────────────────────────────────────────
-- cat_id: 1=Champús, 2=Cremas, 3=Desodorantes, 4=Limpieza, 5=Cosméticos, 6=Tintes,
--         7=Cuidado Capilar, 8=Accesorios, 9=Bisutería, 10=Helados, 11=Dental, 12=Masculino
-- marca_id: 1=Dove, 2=Rexona, 3=Axe, 4=Nivea, 5=Savital, 6=Nutribela, 7=Ego,
--           8=Herbal Essence, 9=Colgate, 10=Lady Speed, 11=Élite, 12=Suavizante Perla, 13=Pingüino
-- unidad_id: 1=UN, 2=PAQ, 3=PAC, 4=CAJ, 5=DOC, 6=LT, 7=ML, 8=GR, 9=KG

INSERT OR IGNORE INTO producto (codigo_barras, nombre, descripcion, categoria_id, marca_id, linea_id, unidad_id, precio_referencia_compra, precio_venta, precio_venta_minimo, stock_actual, stock_minimo, stock_maximo, aplica_iva_compra, estado) VALUES
('7861000001001', 'Champú Dove Reconstrucción 400ml',    'Champú nutritivo cabello dañado',        1, 1, 1, 1, 3.20, 4.50, 4.00, 45, 5, 100, 1, 'ACT'),
('7861000001002', 'Acondicionador Dove Reconstrucción',   'Acondicionador reparador 400ml',         1, 1, 1, 1, 3.40, 4.75, 4.25, 38, 5, 100, 1, 'ACT'),
('7861000001003', 'Crema Peinar Dove Óleo Nutritivo',     'Crema de peinar sin enjuague 300ml',     7, 1, 1, 1, 2.80, 3.90, 3.50, 30, 5, 80,  1, 'ACT'),
('7861000002001', 'Desodorante Rexona Women Powder',      'Antitranspirante barra 50g',             3, 2, NULL, 1, 2.10, 3.25, 2.90, 50, 8, 120, 1, 'ACT'),
('7861000002002', 'Desodorante Rexona Men V8',            'Antitranspirante spray 150ml',           3, 2, NULL, 1, 2.50, 3.75, 3.40, 42, 8, 120, 1, 'ACT'),
('7861000003001', 'Desodorante Axe Dark Temptation',      'Body spray 150ml',                       12, 3, NULL, 1, 3.00, 4.50, 4.00, 28, 5, 60,  1, 'ACT'),
('7861000004001', 'Crema Nivea Creme Lata 150ml',         'Crema multiusos hidratante',             2, 4, NULL, 1, 2.90, 4.25, 3.80, 35, 5, 80,  1, 'ACT'),
('7861000005001', 'Champú Savital Biotina',               'Champú fortalecedor 530ml',              1, 5, NULL, 1, 2.00, 3.00, 2.70, 55, 8, 120, 1, 'ACT'),
('7861000005002', 'Champú Savital Keratina',              'Champú reparador 530ml',                 1, 5, NULL, 1, 2.00, 3.00, 2.70, 48, 8, 120, 1, 'ACT'),
('7861000006001', 'Champú Nutribela Colágeno 530ml',      'Champú anticaída con colágeno',          1, 6, NULL, 1, 2.50, 3.75, 3.30, 40, 5, 100, 1, 'ACT'),
('7861000007001', 'Cera Ego Black 60g',                   'Cera para cabello efecto mate',          12, 7, NULL, 1, 1.80, 2.75, 2.50, 32, 5, 80,  1, 'ACT'),
('7861000007002', 'Champú Ego Men Force 400ml',           'Champú anticaspa masculino',             12, 7, NULL, 1, 2.30, 3.50, 3.10, 25, 5, 60,  1, 'ACT'),
('7861000008001', 'Champú Herbal Essence Argan',          'Champú con aceite de argán 400ml',       1, 8, NULL, 1, 3.50, 5.25, 4.70, 22, 5, 60,  1, 'ACT'),
('7861000009001', 'Pasta Dental Colgate Triple Acción',   'Pasta dental 150ml',                     11, 9, NULL, 1, 1.50, 2.25, 2.00, 60, 10, 150, 1, 'ACT'),
('7861000009002', 'Cepillo Dental Colgate Premier',       'Cepillo medio suave',                    11, 9, NULL, 1, 0.80, 1.50, 1.20, 70, 10, 200, 1, 'ACT'),
('7861000010001', 'Desodorante Lady Speed Powder Fresh',  'Desodorante barra femenino 45g',         3, 10, NULL, 1, 1.90, 2.90, 2.60, 44, 8, 100, 1, 'ACT'),
('7861000011001', 'Papel Higiénico Élite Mega Rollo x12', 'Paca 12 rollos doble hoja',             4, 11, NULL, 3, 4.50, 6.50, 5.80, 30, 5, 60,  1, 'ACT'),
('7861000012001', 'Suavizante Perla Primaveral 1L',       'Suavizante de ropa aroma primavera',     4, 12, NULL, 6, 2.20, 3.25, 2.90, 35, 5, 80,  1, 'ACT'),
('7861000013001', 'Helado Pingüino Cornetto Clásico',     'Helado cono vainilla chocolate',         10, 13, NULL, 1, 0.60, 1.00, 0.80, 80, 20, 200, 1, 'ACT'),
('7861000013002', 'Helado Pingüino Magnum Almendras',     'Paleta premium almendras',               10, 13, NULL, 1, 1.20, 2.00, 1.75, 50, 10, 120, 1, 'ACT'),
(NULL, 'Tinte Igora Negro Intenso',                       'Tinte permanente negro 1-0',             6, NULL, NULL, 1, 3.00, 5.00, 4.50, 20, 5, 50, 0, 'ACT'),
(NULL, 'Tinte Igora Castaño Oscuro',                      'Tinte permanente castaño 3-0',           6, NULL, NULL, 1, 3.00, 5.00, 4.50, 18, 5, 50, 0, 'ACT'),
(NULL, 'Base Líquida Maybelline Fit Me',                   'Base líquida tono medio',               5, NULL, NULL, 1, 4.00, 7.50, 6.50, 15, 3, 40, 0, 'ACT'),
(NULL, 'Labial Revlon Super Lustrous Rojo',                'Labial cremoso rojo clásico',           5, NULL, NULL, 1, 3.50, 6.00, 5.20, 20, 3, 50, 0, 'ACT'),
(NULL, 'Esmalte Masglo Rojo Fuego',                        'Esmalte de uñas 13ml',                  5, NULL, NULL, 1, 1.20, 2.50, 2.00, 40, 5, 80, 0, 'ACT'),
(NULL, 'Cepillo Cabello Redondo Grande',                   'Cepillo térmico para secado',           8, NULL, NULL, 1, 2.00, 3.50, 3.00, 15, 3, 30, 0, 'ACT'),
(NULL, 'Espejo Doble Aumento',                             'Espejo de mano con aumento 5x',        8, NULL, NULL, 1, 1.50, 3.00, 2.50, 12, 3, 25, 0, 'ACT'),
(NULL, 'Aretes Fantasía Dorados',                          'Par de aretes largos dorados',          9, NULL, NULL, 2, 0.80, 2.50, 2.00, 30, 5, 60, 0, 'ACT'),
(NULL, 'Collar Perlas Fantasía',                           'Collar corto perlas blancas',           9, NULL, NULL, 1, 1.00, 3.50, 3.00, 18, 3, 40, 0, 'ACT'),
(NULL, 'Enjuague Bucal Colgate Plax 500ml',               'Enjuague menta fresca',                 11, 9, NULL, 1, 2.50, 3.75, 3.30, 28, 5, 60, 1, 'ACT');

-- ─────────────────────────────────────────────
-- 8. PROVEEDORES  (5 proveedores reales)
-- ─────────────────────────────────────────────
INSERT OR IGNORE INTO proveedor (ruc_cedula, razon_social, nombre_contacto, telefono, whatsapp, email, direccion, tipo_credito, plazo_credito_dias, frecuencia_pedido, dia_visita, observaciones, estado) VALUES
('1790012345001', 'Distribuidora Unilever Ecuador',    'Carlos Méndez',  '022567890', '0991234567', 'ventas@unilever.ec',     'Av. Amazonas N45-12, Quito',   'CREDITO_60', 60, 'QUINCENAL', 'Martes',   'Dove, Rexona, Axe, Savital',   'ACT'),
('1791234567001', 'Colgate Palmolive del Ecuador',     'Patricia Ruiz',  '022890123', '0987654321', 'pedidos@colgate.ec',     'Calle Bolívar 234, Guayaquil', 'CREDITO_60', 60, 'MENSUAL',   'Jueves',   'Colgate, Lady Speed',          'ACT'),
('0992345678001', 'MegaCosméticos S.A.',               'Luis Andrade',   '042456789', '0976543210', 'info@megacosmeticos.com','Av. 9 de Octubre 456, Gye',    'CONTADO',     0, 'QUINCENAL', 'Miércoles','Tintes, bases, labiales',      'ACT'),
('1792345678001', 'Distribuidora La Económica',        'Rosa Paredes',   '032345678', '0965432109', 'pedidos@laeconomica.ec', 'Calle Sucre 789, Ambato',      'CREDITO_15', 15, 'SEMANAL',   'Lunes',    'Papel, suavizante, limpieza',  'ACT'),
('0601234567001', 'Helados Pingüino (Unilever Ice)',   'Jorge Villacrés','022901234', '0954321098', 'helados@pinguino.ec',    'Parque Industrial, Quito',     'CONTADO',     0, 'QUINCENAL', 'Viernes',  'Helados, pedidos quincenales', 'ACT');

-- ─────────────────────────────────────────────
-- 9. PROVEEDOR_PRODUCTO  (vinculación proveedor ↔ producto)
-- ─────────────────────────────────────────────
INSERT OR IGNORE INTO proveedor_producto (proveedor_id, producto_id, precio_compra, precio_compra_con_iva, incluye_iva, es_proveedor_principal, estado) VALUES
-- Unilever → Dove, Rexona, Axe, Savital, Nutribela, Ego, Herbal
(1, 1, 3.20, 3.68, 1, 1, 'ACT'), (1, 2, 3.40, 3.91, 1, 1, 'ACT'), (1, 3, 2.80, 3.22, 1, 1, 'ACT'),
(1, 4, 2.10, 2.42, 1, 1, 'ACT'), (1, 5, 2.50, 2.88, 1, 1, 'ACT'), (1, 6, 3.00, 3.45, 1, 1, 'ACT'),
(1, 7, 2.90, 3.34, 1, 1, 'ACT'), (1, 8, 2.00, 2.30, 1, 1, 'ACT'), (1, 9, 2.00, 2.30, 1, 1, 'ACT'),
(1, 10, 2.50, 2.88, 1, 1, 'ACT'), (1, 11, 1.80, 2.07, 1, 1, 'ACT'), (1, 12, 2.30, 2.65, 1, 1, 'ACT'),
(1, 13, 3.50, 4.03, 1, 1, 'ACT'),
-- Colgate → pastas, cepillos, enjuague, Lady Speed
(2, 14, 1.50, 1.73, 1, 1, 'ACT'), (2, 15, 0.80, 0.92, 1, 1, 'ACT'), (2, 16, 1.90, 2.19, 1, 1, 'ACT'),
(2, 30, 2.50, 2.88, 1, 1, 'ACT'),
-- MegaCosméticos → tintes, base, labial, esmalte, accesorios, bisutería
(3, 21, 3.00, 3.00, 0, 1, 'ACT'), (3, 22, 3.00, 3.00, 0, 1, 'ACT'), (3, 23, 4.00, 4.00, 0, 1, 'ACT'),
(3, 24, 3.50, 3.50, 0, 1, 'ACT'), (3, 25, 1.20, 1.20, 0, 1, 'ACT'), (3, 26, 2.00, 2.00, 0, 1, 'ACT'),
(3, 27, 1.50, 1.50, 0, 1, 'ACT'), (3, 28, 0.80, 0.80, 0, 1, 'ACT'), (3, 29, 1.00, 1.00, 0, 1, 'ACT'),
-- La Económica → papel, suavizante
(4, 17, 4.50, 5.18, 1, 1, 'ACT'), (4, 18, 2.20, 2.53, 1, 1, 'ACT'),
-- Pingüino → helados
(5, 19, 0.60, 0.69, 1, 1, 'ACT'), (5, 20, 1.20, 1.38, 1, 1, 'ACT');

-- ─────────────────────────────────────────────
-- 10. CLIENTES  (12 clientes frecuentes)
-- ─────────────────────────────────────────────
INSERT OR IGNORE INTO cliente (cedula, nombres, apellidos, telefono, direccion, habilitado_credito, limite_credito, saldo_pendiente, frecuencia_pago, observaciones, estado) VALUES
('0501234567', 'Ana María',      'Gutiérrez Mora',     '0981234567', 'Calle Bolívar 123',      1, 50.00,  0.00, 'MENSUAL',     'Clienta frecuente, compra semanal',     'ACT'),
('0502345678', 'Rosa Elena',     'Paredes Sánchez',    '0972345678', 'Av. Cevallos 456',        1, 80.00,  0.00, 'QUINCENAL',   'Peluquera, compra tintes y cremas',     'ACT'),
('0503456789', 'Carmen Lucía',   'Villacís Torres',    '0963456789', 'Calle Sucre 789',         1, 40.00,  0.00, 'FIN_DE_MES',  'Compra para su familia',                'ACT'),
('0504567890', 'María José',     'Andrade López',      '0954567890', 'Av. Los Andes 234',       0, 0.00,   0.00, NULL,          'Solo paga al contado',                  'ACT'),
('0505678901', 'Lucía Fernanda', 'Medina Cruz',        '0945678901', 'Calle Montalvo 567',      1, 60.00,  0.00, 'MENSUAL',     'Clienta fiel, viene los viernes',       'ACT'),
('0506789012', 'Patricia',       'Salazar Reyes',      '0936789012', 'Av. Atahualpa 890',       0, 0.00,   0.00, NULL,          'Compra esporádica',                     'ACT'),
('0507890123', 'Andrea Carolina','Zambrano Vega',      '0927890123', 'Calle Olmedo 123',        1, 100.00, 0.00, 'QUINCENAL',   'Dueña de salón de belleza cercano',     'ACT'),
('0508901234', 'Daniela',        'Herrera Navas',      '0918901234', 'Av. Unidad Nacional 456', 0, 0.00,   0.00, NULL,          'Estudiante universitaria',              'ACT'),
('0509012345', 'Jorge Luis',     'Pérez Moncayo',      '0909012345', 'Calle Espejo 789',        0, 0.00,   0.00, NULL,          'Compra productos masculinos',           'ACT'),
('0510123456', 'Carlos Andrés',  'Ruiz Bustamante',    '0900123456', 'Av. Pichincha 234',       0, 0.00,   0.00, NULL,          'Compra helados para su tiendita',       'ACT'),
('0511234567', 'Verónica',       'Castillo Ponce',     '0891234567', 'Calle Maldonado 567',     1, 70.00,  0.00, 'MENSUAL',     'Maquilladora profesional',              'ACT'),
('0512345678', 'Silvia Marisol', 'Quintero Alvarado',  '0882345678', 'Av. El Rey 890',          0, 0.00,   0.00, NULL,          'Compra artículos de limpieza',          'ACT');

-- ─────────────────────────────────────────────
-- 11. COMPRAS  (8 compras en 3 meses)
-- ─────────────────────────────────────────────
INSERT INTO compra (numero_factura, proveedor_id, usuario_id, fecha_compra, fecha_recepcion, subtotal_sin_iva, monto_iva, total, tipo_pago, plazo_credito_dias, estado, observaciones) VALUES
('F001-2025-DIC', 1, 1, '2025-12-12', '2025-12-12', 156.00, 23.40, 179.40, 'CREDITO', 60, 'RECIBIDA', 'Pedido quincenal Unilever diciembre 1'),
('F002-2025-DIC', 2, 1, '2025-12-15', '2025-12-15',  52.00,  7.80,  59.80, 'CREDITO', 60, 'RECIBIDA', 'Pedido mensual Colgate diciembre'),
('F003-2025-DIC', 3, 1, '2025-12-18', '2025-12-18',  89.00,  0.00,  89.00, 'CONTADO',  0, 'RECIBIDA', 'Cosméticos y accesorios dic'),
('F004-2025-DIC', 4, 1, '2025-12-20', '2025-12-20',  67.00, 10.05,  77.05, 'CREDITO', 15, 'RECIBIDA', 'Papel y suavizante dic'),
('F005-2026-ENE', 1, 1, '2026-01-10', '2026-01-10', 168.00, 25.20, 193.20, 'CREDITO', 60, 'RECIBIDA', 'Pedido quincenal Unilever enero 1'),
('F006-2026-ENE', 5, 1, '2026-01-15', '2026-01-15',  54.00,  8.10,  62.10, 'CONTADO',  0, 'RECIBIDA', 'Helados Pingüino enero'),
('F007-2026-FEB', 1, 1, '2026-02-05', '2026-02-05', 145.00, 21.75, 166.75, 'CREDITO', 60, 'RECIBIDA', 'Pedido quincenal Unilever febrero'),
('F008-2026-MAR', 3, 1, '2026-03-02', '2026-03-02',  76.00,  0.00,  76.00, 'CONTADO',  0, 'RECIBIDA', 'Reposición cosméticos marzo');

-- ─────────────────────────────────────────────
-- 12. COMPRA_DETALLE (ítems de cada compra)
-- ─────────────────────────────────────────────
-- Compra 1 (Unilever dic-1): Dove, Rexona, Savital
INSERT INTO compra_detalle (compra_id, producto_id, cantidad, precio_unitario, incluye_iva, precio_sin_iva, subtotal) VALUES
(1, 1, 24, 3.68, 1, 3.20, 76.80),
(1, 2, 12, 3.91, 1, 3.40, 40.80),
(1, 4, 24, 2.42, 1, 2.10, 50.40),
(1, 8, 12, 2.30, 1, 2.00, 24.00);

-- Compra 2 (Colgate dic)
INSERT INTO compra_detalle (compra_id, producto_id, cantidad, precio_unitario, incluye_iva, precio_sin_iva, subtotal) VALUES
(2, 14, 24, 1.73, 1, 1.50, 36.00),
(2, 15, 30, 0.92, 1, 0.80, 24.00);

-- Compra 3 (MegaCosméticos dic)
INSERT INTO compra_detalle (compra_id, producto_id, cantidad, precio_unitario, incluye_iva, precio_sin_iva, subtotal) VALUES
(3, 21, 10, 3.00, 0, 3.00, 30.00),
(3, 23,  6, 4.00, 0, 4.00, 24.00),
(3, 24,  8, 3.50, 0, 3.50, 28.00),
(3, 28, 10, 0.80, 0, 0.80,  8.00);

-- Compra 4 (La Económica dic)
INSERT INTO compra_detalle (compra_id, producto_id, cantidad, precio_unitario, incluye_iva, precio_sin_iva, subtotal) VALUES
(4, 17, 12, 5.18, 1, 4.50, 54.00),
(4, 18, 10, 2.53, 1, 2.20, 22.00);

-- Compra 5 (Unilever ene)
INSERT INTO compra_detalle (compra_id, producto_id, cantidad, precio_unitario, incluye_iva, precio_sin_iva, subtotal) VALUES
(5, 1,  18, 3.68, 1, 3.20, 57.60),
(5, 5,  24, 2.88, 1, 2.50, 60.00),
(5, 10, 18, 2.88, 1, 2.50, 45.00),
(5, 13, 12, 4.03, 1, 3.50, 42.00);

-- Compra 6 (Pingüino ene)
INSERT INTO compra_detalle (compra_id, producto_id, cantidad, precio_unitario, incluye_iva, precio_sin_iva, subtotal) VALUES
(6, 19, 60, 0.69, 1, 0.60, 36.00),
(6, 20, 24, 1.38, 1, 1.20, 28.80);

-- Compra 7 (Unilever feb)
INSERT INTO compra_detalle (compra_id, producto_id, cantidad, precio_unitario, incluye_iva, precio_sin_iva, subtotal) VALUES
(7, 3,  18, 3.22, 1, 2.80, 50.40),
(7, 6,  12, 3.45, 1, 3.00, 36.00),
(7, 11, 24, 2.07, 1, 1.80, 43.20),
(7, 12, 12, 2.65, 1, 2.30, 27.60);

-- Compra 8 (MegaCosméticos mar)
INSERT INTO compra_detalle (compra_id, producto_id, cantidad, precio_unitario, incluye_iva, precio_sin_iva, subtotal) VALUES
(8, 22, 10, 3.00, 0, 3.00, 30.00),
(8, 25, 24, 1.20, 0, 1.20, 28.80),
(8, 29,  8, 1.00, 0, 1.00,  8.00),
(8, 26,  6, 2.00, 0, 2.00, 12.00);

-- ─────────────────────────────────────────────
-- 13. VENTAS (35 ventas en 3 meses — tráfico real tienda de barrio)
-- ─────────────────────────────────────────────
INSERT INTO venta (numero_comprobante, cliente_id, usuario_id, fecha_venta, subtotal, descuento, total, metodo_pago, monto_recibido, cambio, referencia_transferencia, es_credito, comprobante_emitido, estado) VALUES
-- DICIEMBRE 2025 (12 ventas)
('NV-000001', NULL,  1, '2025-12-12 09:15:00',  7.50, 0, 7.50,  'EFECTIVO', 10.00, 2.50, NULL, 0, 1, 'COMPLETADA'),
('NV-000002', 1,     1, '2025-12-12 11:30:00', 14.25, 0, 14.25, 'EFECTIVO', 15.00, 0.75, NULL, 0, 1, 'COMPLETADA'),
('NV-000003', NULL,  1, '2025-12-13 10:00:00',  3.25, 0, 3.25,  'EFECTIVO',  5.00, 1.75, NULL, 0, 1, 'COMPLETADA'),
('NV-000004', 2,     1, '2025-12-14 14:20:00', 25.00, 0, 25.00, 'CREDITO',  NULL,  NULL, NULL, 1, 1, 'COMPLETADA'),
('NV-000005', 4,     1, '2025-12-16 09:45:00',  8.75, 0, 8.75,  'TRANSFERENCIA', NULL, NULL, 'TRF-DIC-001', 0, 1, 'COMPLETADA'),
('NV-000006', NULL,  1, '2025-12-18 15:00:00',  5.00, 0, 5.00,  'EFECTIVO', 5.00,  0.00, NULL, 0, 1, 'COMPLETADA'),
('NV-000007', 3,     1, '2025-12-19 11:15:00', 18.50, 0, 18.50, 'EFECTIVO', 20.00, 1.50, NULL, 0, 1, 'COMPLETADA'),
('NV-000008', 5,     1, '2025-12-20 16:30:00', 12.75, 0, 12.75, 'CREDITO',  NULL,  NULL, NULL, 1, 1, 'COMPLETADA'),
('NV-000009', NULL,  2, '2025-12-22 10:10:00',  6.50, 0, 6.50,  'EFECTIVO',  7.00, 0.50, NULL, 0, 1, 'COMPLETADA'),
('NV-000010', 7,     1, '2025-12-23 09:30:00', 35.50, 0, 35.50, 'CREDITO',  NULL,  NULL, NULL, 1, 1, 'COMPLETADA'),
('NV-000011', NULL,  2, '2025-12-27 14:45:00',  4.50, 0, 4.50,  'EFECTIVO',  5.00, 0.50, NULL, 0, 1, 'COMPLETADA'),
('NV-000012', 9,     1, '2025-12-28 11:00:00', 10.00, 0, 10.00, 'EFECTIVO', 10.00, 0.00, NULL, 0, 1, 'COMPLETADA'),
-- ENERO 2026 (12 ventas)
('NV-000013', 1,     1, '2026-01-03 09:20:00', 11.25, 0, 11.25, 'EFECTIVO', 12.00, 0.75, NULL, 0, 1, 'COMPLETADA'),
('NV-000014', NULL,  2, '2026-01-05 10:30:00',  3.00, 0, 3.00,  'EFECTIVO',  5.00, 2.00, NULL, 0, 0, 'COMPLETADA'),
('NV-000015', 6,     1, '2026-01-08 15:15:00',  9.25, 0, 9.25,  'TRANSFERENCIA', NULL, NULL, 'TRF-ENE-001', 0, 1, 'COMPLETADA'),
('NV-000016', 2,     1, '2026-01-10 11:40:00', 22.50, 0, 22.50, 'CREDITO',  NULL,  NULL, NULL, 1, 1, 'COMPLETADA'),
('NV-000017', NULL,  1, '2026-01-12 09:50:00',  7.00, 0, 7.00,  'EFECTIVO', 10.00, 3.00, NULL, 0, 1, 'COMPLETADA'),
('NV-000018', 8,     2, '2026-01-15 14:00:00',  5.50, 0, 5.50,  'EFECTIVO',  6.00, 0.50, NULL, 0, 1, 'COMPLETADA'),
('NV-000019', 11,    1, '2026-01-18 10:20:00', 28.00, 0, 28.00, 'CREDITO',  NULL,  NULL, NULL, 1, 1, 'COMPLETADA'),
('NV-000020', NULL,  1, '2026-01-20 16:10:00',  4.00, 0, 4.00,  'EFECTIVO',  5.00, 1.00, NULL, 0, 1, 'COMPLETADA'),
('NV-000021', 10,    2, '2026-01-22 09:00:00', 15.00, 0, 15.00, 'EFECTIVO', 15.00, 0.00, NULL, 0, 1, 'COMPLETADA'),
('NV-000022', 3,     1, '2026-01-25 11:30:00', 19.75, 0, 19.75, 'EFECTIVO', 20.00, 0.25, NULL, 0, 1, 'COMPLETADA'),
('NV-000023', NULL,  1, '2026-01-28 15:45:00',  2.50, 0, 2.50,  'EFECTIVO',  3.00, 0.50, NULL, 0, 0, 'COMPLETADA'),
('NV-000024', NULL,  2, '2026-01-30 10:15:00',  8.50, 0, 8.50,  'EFECTIVO', 10.00, 1.50, NULL, 0, 1, 'COMPLETADA'),
-- FEBRERO-MARZO 2026 (11 ventas)
('NV-000025', 1,     1, '2026-02-02 09:30:00', 13.50, 0, 13.50, 'EFECTIVO', 14.00, 0.50, NULL, 0, 1, 'COMPLETADA'),
('NV-000026', 7,     1, '2026-02-05 14:20:00', 42.00, 0, 42.00, 'CREDITO',  NULL,  NULL, NULL, 1, 1, 'COMPLETADA'),
('NV-000027', NULL,  2, '2026-02-08 11:00:00',  6.25, 0, 6.25,  'EFECTIVO',  7.00, 0.75, NULL, 0, 1, 'COMPLETADA'),
('NV-000028', 4,     1, '2026-02-12 10:45:00', 16.00, 0, 16.00, 'TRANSFERENCIA', NULL, NULL, 'TRF-FEB-001', 0, 1, 'COMPLETADA'),
('NV-000029', 12,    2, '2026-02-15 15:30:00',  9.75, 0, 9.75,  'EFECTIVO', 10.00, 0.25, NULL, 0, 1, 'COMPLETADA'),
('NV-000030', NULL,  1, '2026-02-20 09:10:00',  5.50, 0, 5.50,  'EFECTIVO',  6.00, 0.50, NULL, 0, 1, 'COMPLETADA'),
('NV-000031', 5,     1, '2026-02-25 11:20:00', 11.00, 0, 11.00, 'EFECTIVO', 11.00, 0.00, NULL, 0, 1, 'COMPLETADA'),
('NV-000032', NULL,  1, '2026-03-01 10:00:00',  8.00, 0, 8.00,  'EFECTIVO', 10.00, 2.00, NULL, 0, 1, 'COMPLETADA'),
('NV-000033', 2,     1, '2026-03-03 14:30:00', 20.00, 0, 20.00, 'CREDITO',  NULL,  NULL, NULL, 1, 1, 'COMPLETADA'),
('NV-000034', 9,     2, '2026-03-06 09:40:00', 11.50, 0, 11.50, 'EFECTIVO', 12.00, 0.50, NULL, 0, 1, 'COMPLETADA'),
('NV-000035', NULL,  1, '2026-03-09 16:00:00',  3.50, 0, 3.50,  'EFECTIVO',  5.00, 1.50, NULL, 0, 1, 'COMPLETADA');

-- ─────────────────────────────────────────────
-- 14. VENTA_DETALLE (ítems de cada venta)
-- ─────────────────────────────────────────────
-- NV-1: Champú Dove + Crema peinar Dove
INSERT INTO venta_detalle (venta_id, producto_id, cantidad, precio_unitario, precio_original, descuento_unitario, subtotal) VALUES
(1, 1, 1, 4.50, 4.50, 0, 4.50), (1, 3, 1, 3.00, 3.90, 0.90, 3.00);
-- NV-2: 3 Champús Savital + 1 Paste dental
INSERT INTO venta_detalle (venta_id, producto_id, cantidad, precio_unitario, precio_original, descuento_unitario, subtotal) VALUES
(2, 8, 3, 3.00, 3.00, 0, 9.00), (2, 14, 1, 2.25, 2.25, 0, 2.25), (2, 15, 2, 1.50, 1.50, 0, 3.00);
-- NV-3: 1 Desodorante Rexona
INSERT INTO venta_detalle (venta_id, producto_id, cantidad, precio_unitario, precio_original, descuento_unitario, subtotal) VALUES
(3, 4, 1, 3.25, 3.25, 0, 3.25);
-- NV-4: Tintes + Base (peluquera crédito)
INSERT INTO venta_detalle (venta_id, producto_id, cantidad, precio_unitario, precio_original, descuento_unitario, subtotal) VALUES
(4, 21, 2, 5.00, 5.00, 0, 10.00), (4, 22, 1, 5.00, 5.00, 0, 5.00), (4, 23, 1, 7.50, 7.50, 0, 7.50), (4, 25, 1, 2.50, 2.50, 0, 2.50);
-- NV-5: Rexona spray + Cepillo dental
INSERT INTO venta_detalle (venta_id, producto_id, cantidad, precio_unitario, precio_original, descuento_unitario, subtotal) VALUES
(5, 5, 1, 3.75, 3.75, 0, 3.75), (5, 14, 1, 2.25, 2.25, 0, 2.25), (5, 11, 1, 2.75, 2.75, 0, 2.75);
-- NV-6: 2 Tintes negro
INSERT INTO venta_detalle (venta_id, producto_id, cantidad, precio_unitario, precio_original, descuento_unitario, subtotal) VALUES
(6, 21, 1, 5.00, 5.00, 0, 5.00);
-- NV-7: Papel + Suavizante + Pasta
INSERT INTO venta_detalle (venta_id, producto_id, cantidad, precio_unitario, precio_original, descuento_unitario, subtotal) VALUES
(7, 17, 2, 6.50, 6.50, 0, 13.00), (7, 18, 1, 3.25, 3.25, 0, 3.25), (7, 14, 1, 2.25, 2.25, 0, 2.25);
-- NV-8: Crema Nivea + Champú Herbal (crédito)
INSERT INTO venta_detalle (venta_id, producto_id, cantidad, precio_unitario, precio_original, descuento_unitario, subtotal) VALUES
(8, 7, 1, 4.25, 4.25, 0, 4.25), (8, 13, 1, 5.25, 5.25, 0, 5.25), (8, 4, 1, 3.25, 3.25, 0, 3.25);
-- NV-9: Papel higiénico
INSERT INTO venta_detalle (venta_id, producto_id, cantidad, precio_unitario, precio_original, descuento_unitario, subtotal) VALUES
(9, 17, 1, 6.50, 6.50, 0, 6.50);
-- NV-10: Salón de belleza (crédito grande)
INSERT INTO venta_detalle (venta_id, producto_id, cantidad, precio_unitario, precio_original, descuento_unitario, subtotal) VALUES
(10, 1, 2, 4.50, 4.50, 0, 9.00), (10, 2, 2, 4.75, 4.75, 0, 9.50), (10, 3, 2, 3.90, 3.90, 0, 7.80), (10, 21, 1, 5.00, 5.00, 0, 5.00), (10, 25, 2, 2.50, 2.50, 0, 5.00);
-- NV-11: Champú Dove
INSERT INTO venta_detalle (venta_id, producto_id, cantidad, precio_unitario, precio_original, descuento_unitario, subtotal) VALUES
(11, 1, 1, 4.50, 4.50, 0, 4.50);
-- NV-12: Axe + Ego
INSERT INTO venta_detalle (venta_id, producto_id, cantidad, precio_unitario, precio_original, descuento_unitario, subtotal) VALUES
(12, 6, 1, 4.50, 4.50, 0, 4.50), (12, 12, 1, 3.50, 3.50, 0, 3.50), (12, 11, 1, 2.00, 2.75, 0.75, 2.00);
-- NV-13: Ana María — cremas + champú
INSERT INTO venta_detalle (venta_id, producto_id, cantidad, precio_unitario, precio_original, descuento_unitario, subtotal) VALUES
(13, 7, 1, 4.25, 4.25, 0, 4.25), (13, 8, 1, 3.00, 3.00, 0, 3.00), (13, 19, 4, 1.00, 1.00, 0, 4.00);
-- NV-14: Helado solo
INSERT INTO venta_detalle (venta_id, producto_id, cantidad, precio_unitario, precio_original, descuento_unitario, subtotal) VALUES
(14, 19, 3, 1.00, 1.00, 0, 3.00);
-- NV-15: Patricia
INSERT INTO venta_detalle (venta_id, producto_id, cantidad, precio_unitario, precio_original, descuento_unitario, subtotal) VALUES
(15, 4, 1, 3.25, 3.25, 0, 3.25), (15, 24, 1, 6.00, 6.00, 0, 6.00);
-- NV-16: Rosa peluquera (crédito)
INSERT INTO venta_detalle (venta_id, producto_id, cantidad, precio_unitario, precio_original, descuento_unitario, subtotal) VALUES
(16, 21, 2, 5.00, 5.00, 0, 10.00), (16, 22, 1, 5.00, 5.00, 0, 5.00), (16, 3, 2, 3.75, 3.75, 0, 7.50);
-- NV-17: Helados + pasta
INSERT INTO venta_detalle (venta_id, producto_id, cantidad, precio_unitario, precio_original, descuento_unitario, subtotal) VALUES
(17, 19, 2, 1.00, 1.00, 0, 2.00), (17, 20, 1, 2.00, 2.00, 0, 2.00), (17, 14, 1, 2.25, 2.25, 0, 2.25), (17, 15, 1, 0.75, 1.50, 0.75, 0.75);
-- NV-18: Daniela — esmalte + labial
INSERT INTO venta_detalle (venta_id, producto_id, cantidad, precio_unitario, precio_original, descuento_unitario, subtotal) VALUES
(18, 25, 1, 2.50, 2.50, 0, 2.50), (18, 29, 1, 3.00, 3.50, 0.50, 3.00);
-- NV-19: Maquilladora (crédito)
INSERT INTO venta_detalle (venta_id, producto_id, cantidad, precio_unitario, precio_original, descuento_unitario, subtotal) VALUES
(19, 23, 2, 7.50, 7.50, 0, 15.00), (19, 24, 1, 6.00, 6.00, 0, 6.00), (19, 25, 2, 2.50, 2.50, 0, 5.00), (19, 28, 1, 2.00, 2.50, 0.50, 2.00);
-- NV-20: Helados
INSERT INTO venta_detalle (venta_id, producto_id, cantidad, precio_unitario, precio_original, descuento_unitario, subtotal) VALUES
(20, 19, 2, 1.00, 1.00, 0, 2.00), (20, 20, 1, 2.00, 2.00, 0, 2.00);
-- NV-21: Carlos — helados para tiendita
INSERT INTO venta_detalle (venta_id, producto_id, cantidad, precio_unitario, precio_original, descuento_unitario, subtotal) VALUES
(21, 19, 10, 1.00, 1.00, 0, 10.00), (21, 20, 5, 1.00, 2.00, 1.00, 5.00);
-- NV-22: Carmen — limpieza familiar
INSERT INTO venta_detalle (venta_id, producto_id, cantidad, precio_unitario, precio_original, descuento_unitario, subtotal) VALUES
(22, 17, 2, 6.50, 6.50, 0, 13.00), (22, 18, 1, 3.25, 3.25, 0, 3.25), (22, 14, 1, 2.25, 2.25, 0, 2.25), (22, 15, 1, 1.25, 1.50, 0.25, 1.25);
-- NV-23: Helado solo
INSERT INTO venta_detalle (venta_id, producto_id, cantidad, precio_unitario, precio_original, descuento_unitario, subtotal) VALUES
(23, 25, 1, 2.50, 2.50, 0, 2.50);
-- NV-24: Desodorantes
INSERT INTO venta_detalle (venta_id, producto_id, cantidad, precio_unitario, precio_original, descuento_unitario, subtotal) VALUES
(24, 5, 1, 3.75, 3.75, 0, 3.75), (24, 16, 1, 2.90, 2.90, 0, 2.90), (24, 15, 1, 1.50, 1.50, 0, 1.50), (24, 27, 1, 0.35, 3.00, 2.65, 0.35);
-- NV-25: Ana María — feb
INSERT INTO venta_detalle (venta_id, producto_id, cantidad, precio_unitario, precio_original, descuento_unitario, subtotal) VALUES
(25, 1, 1, 4.50, 4.50, 0, 4.50), (25, 9, 1, 3.00, 3.00, 0, 3.00), (25, 24, 1, 6.00, 6.00, 0, 6.00);
-- NV-26: Salón belleza feb (crédito)
INSERT INTO venta_detalle (venta_id, producto_id, cantidad, precio_unitario, precio_original, descuento_unitario, subtotal) VALUES
(26, 1, 3, 4.50, 4.50, 0, 13.50), (26, 2, 2, 4.75, 4.75, 0, 9.50), (26, 21, 2, 5.00, 5.00, 0, 10.00), (26, 3, 2, 3.90, 3.90, 0, 7.80), (26, 25, 1, 1.20, 2.50, 1.30, 1.20);
-- NV-27: Pasta + cepillo
INSERT INTO venta_detalle (venta_id, producto_id, cantidad, precio_unitario, precio_original, descuento_unitario, subtotal) VALUES
(27, 14, 1, 2.25, 2.25, 0, 2.25), (27, 15, 1, 1.50, 1.50, 0, 1.50), (27, 25, 1, 2.50, 2.50, 0, 2.50);
-- NV-28: María José — transferencia
INSERT INTO venta_detalle (venta_id, producto_id, cantidad, precio_unitario, precio_original, descuento_unitario, subtotal) VALUES
(28, 10, 2, 3.75, 3.75, 0, 7.50), (28, 30, 1, 3.75, 3.75, 0, 3.75), (28, 7, 1, 4.25, 4.25, 0, 4.25), (28, 15, 1, 0.50, 1.50, 1.00, 0.50);
-- NV-29: Silvia — limpieza
INSERT INTO venta_detalle (venta_id, producto_id, cantidad, precio_unitario, precio_original, descuento_unitario, subtotal) VALUES
(29, 17, 1, 6.50, 6.50, 0, 6.50), (29, 18, 1, 3.25, 3.25, 0, 3.25);
-- NV-30: Crema Nivea + champú
INSERT INTO venta_detalle (venta_id, producto_id, cantidad, precio_unitario, precio_original, descuento_unitario, subtotal) VALUES
(30, 7, 1, 4.25, 4.25, 0, 4.25), (30, 15, 1, 1.25, 1.50, 0.25, 1.25);
-- NV-31: Lucía — feb
INSERT INTO venta_detalle (venta_id, producto_id, cantidad, precio_unitario, precio_original, descuento_unitario, subtotal) VALUES
(31, 8, 2, 3.00, 3.00, 0, 6.00), (31, 16, 1, 2.90, 2.90, 0, 2.90), (31, 19, 2, 1.05, 1.00, 0, 2.10);
-- NV-32: Marzo
INSERT INTO venta_detalle (venta_id, producto_id, cantidad, precio_unitario, precio_original, descuento_unitario, subtotal) VALUES
(32, 5, 1, 3.75, 3.75, 0, 3.75), (32, 7, 1, 4.25, 4.25, 0, 4.25);
-- NV-33: Rosa (crédito marzo)
INSERT INTO venta_detalle (venta_id, producto_id, cantidad, precio_unitario, precio_original, descuento_unitario, subtotal) VALUES
(33, 21, 2, 5.00, 5.00, 0, 10.00), (33, 22, 2, 5.00, 5.00, 0, 10.00);
-- NV-34: Jorge — masculino
INSERT INTO venta_detalle (venta_id, producto_id, cantidad, precio_unitario, precio_original, descuento_unitario, subtotal) VALUES
(34, 6, 1, 4.50, 4.50, 0, 4.50), (34, 12, 1, 3.50, 3.50, 0, 3.50), (34, 11, 1, 2.75, 2.75, 0, 2.75), (34, 15, 1, 0.75, 1.50, 0.75, 0.75);
-- NV-35: Última venta
INSERT INTO venta_detalle (venta_id, producto_id, cantidad, precio_unitario, precio_original, descuento_unitario, subtotal) VALUES
(35, 19, 2, 1.00, 1.00, 0, 2.00), (35, 15, 1, 1.50, 1.50, 0, 1.50);

-- ─────────────────────────────────────────────
-- 15. CUENTAS POR COBRAR (ventas a crédito: NV-4, NV-8, NV-10, NV-16, NV-19, NV-26, NV-33)
-- ─────────────────────────────────────────────
INSERT INTO cuenta_cobrar (numero_cuenta, cliente_id, venta_id, monto_original, saldo_pendiente, fecha_emision, fecha_vencimiento, estado_pago, estado) VALUES
('CC-000001', 2,  4,  25.00,  0.00, '2025-12-14', '2026-01-14', 'PAGADO',    'ACT'),
('CC-000002', 5,  8,  12.75,  0.00, '2025-12-20', '2026-01-20', 'PAGADO',    'ACT'),
('CC-000003', 7, 10,  35.50, 15.50, '2025-12-23', '2026-01-07', 'PARCIAL',   'ACT'),
('CC-000004', 2, 16,  22.50,  0.00, '2026-01-10', '2026-02-10', 'PAGADO',    'ACT'),
('CC-000005', 11,19,  28.00, 28.00, '2026-01-18', '2026-02-02', 'VENCIDO',   'ACT'),
('CC-000006', 7, 26,  42.00, 42.00, '2026-02-05', '2026-02-20', 'VENCIDO',   'ACT'),
('CC-000007', 2, 33,  20.00, 20.00, '2026-03-03', '2026-04-03', 'PENDIENTE', 'ACT');

-- Actualizar saldos de clientes con crédito pendiente
UPDATE cliente SET saldo_pendiente = 0.00 WHERE cliente_id = 2;   -- Rosa: CC-1 pagada, CC-4 pagada, CC-7 pendiente → 20
UPDATE cliente SET saldo_pendiente = 20.00 WHERE cliente_id = 2;
UPDATE cliente SET saldo_pendiente = 0.00 WHERE cliente_id = 5;   -- Lucía: CC-2 pagada
UPDATE cliente SET saldo_pendiente = 15.50 WHERE cliente_id = 7;  -- Andrea: CC-3 parcial, CC-6 vencida → 15.50+42
UPDATE cliente SET saldo_pendiente = 57.50 WHERE cliente_id = 7;
UPDATE cliente SET saldo_pendiente = 28.00 WHERE cliente_id = 11; -- Verónica: CC-5 vencida

-- ─────────────────────────────────────────────
-- 16. PAGOS DE CLIENTES
-- ─────────────────────────────────────────────
INSERT INTO pago_cliente (cuenta_cobrar_id, usuario_id, monto_pago, metodo_pago, referencia_transferencia, fecha_pago, observaciones, estado) VALUES
(1, 1, 25.00, 'EFECTIVO',      NULL,             '2026-01-10', 'Pago total Rosa dic',      'ACT'),
(2, 1, 12.75, 'TRANSFERENCIA', 'TRF-PAGO-001',   '2026-01-15', 'Pago total Lucía dic',     'ACT'),
(3, 1, 20.00, 'EFECTIVO',      NULL,             '2026-01-05', 'Abono Andrea dic',          'ACT'),
(4, 1, 22.50, 'EFECTIVO',      NULL,             '2026-02-08', 'Pago total Rosa enero',     'ACT');

-- ─────────────────────────────────────────────
-- 17. CUENTAS POR PAGAR (compras a crédito: 1, 2, 4, 5, 7)
-- ─────────────────────────────────────────────
INSERT INTO cuenta_pagar (numero_cuenta, proveedor_id, compra_id, monto_original, saldo_pendiente, fecha_emision, fecha_vencimiento, estado_pago, estado) VALUES
('CP-000001', 1, 1, 179.40,   0.00, '2025-12-12', '2026-02-10', 'PAGADO',    'ACT'),
('CP-000002', 2, 2,  59.80,   0.00, '2025-12-15', '2026-02-13', 'PAGADO',    'ACT'),
('CP-000003', 4, 4,  77.05,   0.00, '2025-12-20', '2026-01-04', 'PAGADO',    'ACT'),
('CP-000004', 1, 5, 193.20, 193.20, '2026-01-10', '2026-03-11', 'PENDIENTE', 'ACT'),
('CP-000005', 1, 7, 166.75, 166.75, '2026-02-05', '2026-04-06', 'PENDIENTE', 'ACT');

-- ─────────────────────────────────────────────
-- 18. PAGOS A PROVEEDORES
-- ─────────────────────────────────────────────
INSERT INTO pago_proveedor (cuenta_pagar_id, usuario_id, monto_pago, metodo_pago, referencia_transferencia, fecha_pago, observaciones, estado) VALUES
(1, 1, 179.40, 'TRANSFERENCIA', 'TRF-PRV-001', '2026-02-08', 'Pago total Unilever dic',      'ACT'),
(2, 1,  59.80, 'TRANSFERENCIA', 'TRF-PRV-002', '2026-02-10', 'Pago total Colgate dic',        'ACT'),
(3, 1,  77.05, 'EFECTIVO',      NULL,           '2026-01-03', 'Pago total La Económica dic',   'ACT');

-- ─────────────────────────────────────────────
-- 19. AJUSTES DE INVENTARIO
-- ─────────────────────────────────────────────
INSERT INTO ajuste_inventario (numero_ajuste, producto_id, usuario_id, tipo_ajuste, cantidad, motivo, observaciones, estado) VALUES
('AJ-000001', 19, 1, 'CONSUMO_PERSONAL', -3, 'Helados para consumo personal de la dueña', 'Cornetto clásico',                   'ACT'),
('AJ-000002', 25, 1, 'DANIO',            -2, 'Esmaltes rotos al caer estante',             'Se quebraron en la caja',            'ACT'),
('AJ-000003', 14, 1, 'MERMA',            -1, 'Pasta dental aplastada en bodega',           'No apta para venta',                 'ACT'),
('AJ-000004', 28, 1, 'CORRECCION',        3, 'Conteo físico encontró 3 aretes adicionales','Inventario físico enero',            'ACT'),
('AJ-000005', 17, 1, 'CONSUMO_PERSONAL', -1, 'Papel higiénico para uso del local',         'Uso interno del negocio',            'ACT');

-- ─────────────────────────────────────────────
-- 20. MOVIMIENTOS DE INVENTARIO
-- ─────────────────────────────────────────────
-- Entradas por compras
INSERT INTO movimiento_inventario (producto_id, tipo_movimiento, origen, documento_id, cantidad, stock_anterior, stock_posterior, fecha_movimiento) VALUES
-- Compra 1
(1,  'ENTRADA', 'COMPRA', 1, 24, 21, 45, '2025-12-12'),
(2,  'ENTRADA', 'COMPRA', 1, 12, 26, 38, '2025-12-12'),
(4,  'ENTRADA', 'COMPRA', 1, 24, 26, 50, '2025-12-12'),
(8,  'ENTRADA', 'COMPRA', 1, 12, 43, 55, '2025-12-12'),
-- Compra 2
(14, 'ENTRADA', 'COMPRA', 2, 24, 36, 60, '2025-12-15'),
(15, 'ENTRADA', 'COMPRA', 2, 30, 40, 70, '2025-12-15'),
-- Compra 3
(21, 'ENTRADA', 'COMPRA', 3, 10, 10, 20, '2025-12-18'),
(23, 'ENTRADA', 'COMPRA', 3,  6,  9, 15, '2025-12-18'),
(24, 'ENTRADA', 'COMPRA', 3,  8, 12, 20, '2025-12-18'),
(28, 'ENTRADA', 'COMPRA', 3, 10, 20, 30, '2025-12-18'),
-- Compra 4
(17, 'ENTRADA', 'COMPRA', 4, 12, 18, 30, '2025-12-20'),
(18, 'ENTRADA', 'COMPRA', 4, 10, 25, 35, '2025-12-20'),
-- Compra 5
(1,  'ENTRADA', 'COMPRA', 5, 18, 37, 55, '2026-01-10'),
(5,  'ENTRADA', 'COMPRA', 5, 24, 18, 42, '2026-01-10'),
(10, 'ENTRADA', 'COMPRA', 5, 18, 22, 40, '2026-01-10'),
(13, 'ENTRADA', 'COMPRA', 5, 12, 10, 22, '2026-01-10'),
-- Compra 6
(19, 'ENTRADA', 'COMPRA', 6, 60, 20, 80, '2026-01-15'),
(20, 'ENTRADA', 'COMPRA', 6, 24, 26, 50, '2026-01-15'),
-- Compra 7
(3,  'ENTRADA', 'COMPRA', 7, 18, 12, 30, '2026-02-05'),
(6,  'ENTRADA', 'COMPRA', 7, 12, 16, 28, '2026-02-05'),
(11, 'ENTRADA', 'COMPRA', 7, 24,  8, 32, '2026-02-05'),
(12, 'ENTRADA', 'COMPRA', 7, 12, 13, 25, '2026-02-05'),
-- Compra 8
(22, 'ENTRADA', 'COMPRA', 8, 10,  8, 18, '2026-03-02'),
(25, 'ENTRADA', 'COMPRA', 8, 24, 16, 40, '2026-03-02'),
(29, 'ENTRADA', 'COMPRA', 8,  8, 10, 18, '2026-03-02'),
(26, 'ENTRADA', 'COMPRA', 8,  6,  9, 15, '2026-03-02');

-- Salidas por ventas (representativas, no exhaustivas para mantener coherencia)
INSERT INTO movimiento_inventario (producto_id, tipo_movimiento, origen, documento_id, cantidad, stock_anterior, stock_posterior, fecha_movimiento) VALUES
(1,  'SALIDA', 'VENTA', 1,  1, 45, 44, '2025-12-12'),
(3,  'SALIDA', 'VENTA', 1,  1, 30, 29, '2025-12-12'),
(8,  'SALIDA', 'VENTA', 2,  3, 55, 52, '2025-12-12'),
(4,  'SALIDA', 'VENTA', 3,  1, 50, 49, '2025-12-13'),
(21, 'SALIDA', 'VENTA', 4,  2, 20, 18, '2025-12-14'),
(17, 'SALIDA', 'VENTA', 7,  2, 30, 28, '2025-12-19'),
(19, 'SALIDA', 'VENTA', 14, 3, 80, 77, '2026-01-05'),
(21, 'SALIDA', 'VENTA', 16, 2, 16, 14, '2026-01-10'),
(19, 'SALIDA', 'VENTA', 21, 10, 67, 57, '2026-01-22'),
(17, 'SALIDA', 'VENTA', 22, 2, 25, 23, '2026-01-25'),
(1,  'SALIDA', 'VENTA', 26, 3, 50, 47, '2026-02-05'),
(21, 'SALIDA', 'VENTA', 33, 2, 12, 10, '2026-03-03');

-- Ajustes de inventario
INSERT INTO movimiento_inventario (producto_id, tipo_movimiento, origen, documento_id, cantidad, stock_anterior, stock_posterior, fecha_movimiento) VALUES
(19, 'SALIDA',  'AJUSTE', 1, 3, 77, 74, '2026-01-08'),
(25, 'SALIDA',  'AJUSTE', 2, 2, 38, 36, '2026-01-20'),
(14, 'SALIDA',  'AJUSTE', 3, 1, 55, 54, '2026-02-01'),
(28, 'ENTRADA', 'AJUSTE', 4, 3, 27, 30, '2026-02-10'),
(17, 'SALIDA',  'AJUSTE', 5, 1, 23, 22, '2026-02-15');

-- ─────────────────────────────────────────────
-- 21. PROMOCIONES
-- ─────────────────────────────────────────────
INSERT INTO promocion (nombre, descripcion, tipo_promocion, descuento_porcentaje, precio_promocional, fecha_inicio, fecha_fin, activa, estado) VALUES
('Promo Navidad Dove',      'Champú + Acondicionador Dove con 10% dto',    'PORCENTAJE',       10, NULL, '2025-12-15', '2025-12-31', 0, 'ACT'),
('Kit Escolar Colgate',     'Pasta + Cepillo precio especial',             'KIT_REGALO',       NULL, 3.50, '2026-01-02', '2026-01-31', 0, 'ACT'),
('Promo Verano Helados',    'Cornetto a $0.80 en febrero',                 'DESCUENTO_PRECIO', NULL, 0.80, '2026-02-01', '2026-02-28', 0, 'ACT'),
('Día de la Mujer Cosmét',  '15% en cosméticos y maquillaje',              'PORCENTAJE',       15, NULL, '2026-03-01', '2026-03-15', 1, 'ACT');

-- ─────────────────────────────────────────────
-- 22. PROMOCION_PRODUCTO
-- ─────────────────────────────────────────────
INSERT INTO promocion_producto (promocion_id, producto_id, cantidad_en_kit, precio_individual_kit) VALUES
(1, 1, 1, 4.05), (1, 2, 1, 4.28),
(2, 14, 1, 2.00), (2, 15, 1, 1.50),
(3, 19, 1, 0.80),
(4, 23, 1, 6.38), (4, 24, 1, 5.10), (4, 25, 1, 2.13), (4, 28, 1, 2.13), (4, 29, 1, 2.98);

-- ─────────────────────────────────────────────
-- 23. GASTOS OPERATIVOS (3 meses)
-- ─────────────────────────────────────────────
INSERT INTO gasto_operativo (usuario_id, tipo_gasto, descripcion, monto, fecha_gasto, metodo_pago, comprobante, estado) VALUES
-- Diciembre
(1, 'ARRIENDO',     'Arriendo local diciembre 2025',              180.00, '2025-12-01', 'TRANSFERENCIA', 'TRF-ARR-DIC', 'ACT'),
(1, 'SERVICIOS',    'Luz eléctrica diciembre',                     28.50, '2025-12-10', 'EFECTIVO',      NULL,          'ACT'),
(1, 'SERVICIOS',    'Agua potable diciembre',                      12.00, '2025-12-10', 'EFECTIVO',      NULL,          'ACT'),
(1, 'TRANSPORTE',   'Flete proveedor cosméticos dic',              15.00, '2025-12-18', 'EFECTIVO',      NULL,          'ACT'),
(1, 'ALIMENTACION', 'Almuerzo personal diciembre (varias fechas)',  45.00, '2025-12-28', 'EFECTIVO',      NULL,          'ACT'),
-- Enero
(1, 'ARRIENDO',     'Arriendo local enero 2026',                  180.00, '2026-01-02', 'TRANSFERENCIA', 'TRF-ARR-ENE', 'ACT'),
(1, 'SERVICIOS',    'Luz eléctrica enero',                         32.00, '2026-01-12', 'EFECTIVO',      NULL,          'ACT'),
(1, 'SERVICIOS',    'Agua potable enero',                          11.50, '2026-01-12', 'EFECTIVO',      NULL,          'ACT'),
(1, 'SERVICIOS',    'Internet enero',                              25.00, '2026-01-15', 'TRANSFERENCIA', 'TRF-INT-ENE', 'ACT'),
(1, 'TRANSPORTE',   'Flete productos enero',                       12.00, '2026-01-16', 'EFECTIVO',      NULL,          'ACT'),
(1, 'OTROS',        'Fundas plásticas y papel regalo',              8.00, '2026-01-20', 'EFECTIVO',      NULL,          'ACT'),
(1, 'ALIMENTACION', 'Almuerzo personal enero',                     42.00, '2026-01-30', 'EFECTIVO',      NULL,          'ACT'),
-- Febrero
(1, 'ARRIENDO',     'Arriendo local febrero 2026',                180.00, '2026-02-01', 'TRANSFERENCIA', 'TRF-ARR-FEB', 'ACT'),
(1, 'SERVICIOS',    'Luz eléctrica febrero',                       30.00, '2026-02-08', 'EFECTIVO',      NULL,          'ACT'),
(1, 'SERVICIOS',    'Agua potable febrero',                        13.00, '2026-02-08', 'EFECTIVO',      NULL,          'ACT'),
(1, 'SERVICIOS',    'Internet febrero',                            25.00, '2026-02-15', 'TRANSFERENCIA', 'TRF-INT-FEB', 'ACT'),
(1, 'TRANSPORTE',   'Taxi compras mercado feb',                    10.00, '2026-02-20', 'EFECTIVO',      NULL,          'ACT'),
(1, 'ALIMENTACION', 'Almuerzo personal febrero',                   40.00, '2026-02-28', 'EFECTIVO',      NULL,          'ACT'),
-- Marzo (parcial)
(1, 'ARRIENDO',     'Arriendo local marzo 2026',                  180.00, '2026-03-01', 'TRANSFERENCIA', 'TRF-ARR-MAR', 'ACT'),
(1, 'SERVICIOS',    'Luz eléctrica marzo',                         29.00, '2026-03-05', 'EFECTIVO',      NULL,          'ACT'),
(1, 'OTROS',        'Bolsas ecológicas con logo',                  35.00, '2026-03-08', 'EFECTIVO',      NULL,          'ACT');

-- ─────────────────────────────────────────────
-- 24. CIERRES DE CAJA (mensuales)
-- ─────────────────────────────────────────────
INSERT INTO cierre_caja (usuario_id, fecha_cierre, total_ventas_efectivo, total_ventas_transferencia, total_ventas_credito, total_compras, total_gastos, efectivo_esperado, efectivo_real, diferencia, observaciones, estado) VALUES
(1, '2025-12-31',  97.25,  8.75,  73.25, 405.25, 280.50, 97.25,  96.50, -0.75, 'Falta $0.75, posible error de cambio',    'CERRADO'),
(1, '2026-01-31', 109.75,  9.25,  50.50, 255.30, 310.50, 109.75, 110.00, 0.25, 'Sobrante $0.25, cambio devuelto de más',  'CERRADO'),
(1, '2026-02-28',  84.50, 16.00,  42.00, 166.75, 298.00, 84.50,  84.50,  0.00, 'Cuadre perfecto febrero',                 'CERRADO');

-- ─────────────────────────────────────────────
-- 25. AUDITORÍA (registros representativos)
-- ─────────────────────────────────────────────
INSERT INTO auditoria (usuario_id, tabla_afectada, operacion, registro_id, datos_anteriores, datos_nuevos, fecha_hora) VALUES
(1, 'producto',  'INSERT', '1',  NULL, '{"codigo":"P001","nombre":"Champú Dove Reconstrucción 400ml"}',   '2025-12-10 08:00:00'),
(1, 'producto',  'INSERT', '8',  NULL, '{"codigo":"P008","nombre":"Champú Savital Biotina"}',             '2025-12-10 08:15:00'),
(1, 'producto',  'INSERT', '14', NULL, '{"codigo":"P014","nombre":"Pasta Dental Colgate Triple Acción"}', '2025-12-10 08:30:00'),
(1, 'cliente',   'INSERT', '1',  NULL, '{"cedula":"0501234567","nombres":"Ana María"}',                   '2025-12-11 09:00:00'),
(1, 'cliente',   'INSERT', '2',  NULL, '{"cedula":"0502345678","nombres":"Rosa Elena"}',                  '2025-12-11 09:10:00'),
(1, 'proveedor', 'INSERT', '1',  NULL, '{"ruc":"1790012345001","razon_social":"Distribuidora Unilever"}', '2025-12-11 10:00:00'),
(1, 'compra',    'INSERT', '1',  NULL, '{"factura":"F001-2025-DIC","total":179.40}',                      '2025-12-12 08:30:00'),
(1, 'venta',     'INSERT', '1',  NULL, '{"comprobante":"NV-000001","total":7.50}',                        '2025-12-12 09:15:00'),
(1, 'venta',     'INSERT', '4',  NULL, '{"comprobante":"NV-000004","total":25.00,"credito":1}',           '2025-12-14 14:20:00'),
(1, 'venta',     'INSERT', '10', NULL, '{"comprobante":"NV-000010","total":35.50,"credito":1}',           '2025-12-23 09:30:00'),
(1, 'pago_cliente','INSERT','1', NULL, '{"cuenta":"CC-000001","monto":25.00}',                            '2026-01-10 10:00:00'),
(1, 'compra',    'INSERT', '5',  NULL, '{"factura":"F005-2026-ENE","total":193.20}',                      '2026-01-10 08:00:00'),
(1, 'ajuste_inventario', 'INSERT', '1', NULL, '{"producto":19,"tipo":"CONSUMO_PERSONAL","cant":-3}',      '2026-01-08 17:00:00'),
(1, 'venta',     'INSERT', '19', NULL, '{"comprobante":"NV-000019","total":28.00,"credito":1}',           '2026-01-18 10:20:00'),
(1, 'venta',     'INSERT', '26', NULL, '{"comprobante":"NV-000026","total":42.00,"credito":1}',           '2026-02-05 14:20:00'),
(1, 'compra',    'INSERT', '7',  NULL, '{"factura":"F007-2026-FEB","total":166.75}',                      '2026-02-05 08:00:00'),
(1, 'pago_proveedor','INSERT','1', NULL, '{"cuenta":"CP-000001","monto":179.40}',                         '2026-02-08 09:00:00'),
(1, 'cierre_caja','INSERT','1', NULL, '{"fecha":"2025-12-31","efectivo_real":96.50}',                     '2025-12-31 18:00:00'),
(1, 'cierre_caja','INSERT','2', NULL, '{"fecha":"2026-01-31","efectivo_real":110.00}',                    '2026-01-31 18:00:00'),
(1, 'cierre_caja','INSERT','3', NULL, '{"fecha":"2026-02-28","efectivo_real":84.50}',                     '2026-02-28 18:00:00');

-- ─────────────────────────────────────────────
-- ACTUALIZAR SECUENCIAS en configuracion
-- ─────────────────────────────────────────────
UPDATE configuracion SET valor = '36' WHERE clave = 'SECUENCIA_COMPROBANTE';
UPDATE configuracion SET valor = '8'  WHERE clave = 'SECUENCIA_CUENTA_COBRAR';
UPDATE configuracion SET valor = '6'  WHERE clave = 'SECUENCIA_CUENTA_PAGAR';
UPDATE configuracion SET valor = '6'  WHERE clave = 'SECUENCIA_AJUSTE';

-- ============================================================
-- FIN DE DATOS DE OPERACIÓN — 3 meses de actividad realista
-- Resumen: 2 usuarios, 30 productos, 5 proveedores, 12 clientes,
--          8 compras, 35 ventas, 7 cuentas cobrar, 5 cuentas pagar,
--          4 pagos clientes, 3 pagos proveedores, 5 ajustes inventario,
--          4 promociones, 21 gastos, 3 cierres de caja, 20 auditorías
-- ============================================================
