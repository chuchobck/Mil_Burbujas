# -*- coding: utf-8 -*-
"""
Mil Burbujas - Verificación completa de la Fase 1 (Base de Datos)
Ejecuta pruebas de:
  1. Creación de schema (26 tablas)
  2. Seed data (datos iniciales)
  3. CRUD en cada modelo
  4. Transacciones atómicas (las 8 TX definidas)
  5. Foreign keys y constraints
  6. Integridad referencial
"""
import os
import sys

# El test está en MilBurbujas/tests/, necesitamos agregar MilBurbujas/ al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import DB_DIR
from database.connection import DatabaseConnection

# Importar TODOS los modelos
from models.usuario import UsuarioModel
from models.configuracion import ConfiguracionModel
from models.auditoria import AuditoriaModel
from models.categoria import CategoriaModel
from models.marca import MarcaModel
from models.linea_producto import LineaProductoModel
from models.unidad_medida import UnidadMedidaModel
from models.producto import ProductoModel
from models.proveedor import ProveedorModel
from models.proveedor_producto import ProveedorProductoModel
from models.precio_referencia import PrecioReferenciaModel
from models.cliente import ClienteModel
from models.compra import CompraModel
from models.compra_detalle import CompraDetalleModel
from models.venta import VentaModel
from models.venta_detalle import VentaDetalleModel
from models.cuenta_cobrar import CuentaCobrarModel
from models.pago_cliente import PagoClienteModel
from models.cuenta_pagar import CuentaPagarModel
from models.pago_proveedor import PagoProveedorModel
from models.ajuste_inventario import AjusteInventarioModel
from models.movimiento_inventario import MovimientoInventarioModel
from models.promocion import PromocionModel
from models.promocion_producto import PromocionProductoModel
from models.gasto_operativo import GastoOperativoModel
from models.cierre_caja import CierreCajaModel


# Contadores globales
passed = 0
failed = 0
total = 0


def test(nombre: str, condicion: bool, detalle: str = ""):
    """Evalúa un test y reporta resultado."""
    global passed, failed, total
    total += 1
    if condicion:
        passed += 1
        print(f"  ✅ {nombre}")
    else:
        failed += 1
        print(f"  ❌ {nombre} → {detalle}")


def limpiar_db_test():
    """Elimina la BD de prueba para empezar limpio."""
    test_db = os.path.join(DB_DIR, "milburbujas.db")
    if os.path.exists(test_db):
        # Cerrar conexión existente
        db = DatabaseConnection()
        db.close()
        DatabaseConnection._instance = None
        DatabaseConnection._connection = None
        os.remove(test_db)
        print("[INFO] BD de prueba anterior eliminada.")


def test_01_creacion_schema():
    """Test 1: Creación del schema completo."""
    print("\n" + "=" * 60)
    print("TEST 1: CREACIÓN DEL SCHEMA (26 tablas)")
    print("=" * 60)

    db = DatabaseConnection()
    result = db.init_database()
    test("Schema creado sin errores", result)

    count = db.get_table_count()
    test(f"Total de tablas = 26", count == 26, f"Encontradas: {count}")

    tablas_esperadas = [
        "ajuste_inventario", "auditoria", "categoria", "cierre_caja",
        "cliente", "compra", "compra_detalle", "configuracion",
        "cuenta_cobrar", "cuenta_pagar", "gasto_operativo",
        "linea_producto", "marca", "movimiento_inventario",
        "pago_cliente", "pago_proveedor", "precio_referencia",
        "producto", "promocion", "promocion_producto", "proveedor",
        "proveedor_producto", "unidad_medida", "usuario", "venta",
        "venta_detalle"
    ]
    tablas_reales = sorted(db.get_tables())
    test("Todas las tablas esperadas existen",
         tablas_reales == tablas_esperadas,
         f"Diferencias: {set(tablas_esperadas) - set(tablas_reales)}")


def test_02_seed_data():
    """Test 2: Datos iniciales cargados."""
    print("\n" + "=" * 60)
    print("TEST 2: SEED DATA (datos iniciales)")
    print("=" * 60)

    usuario = UsuarioModel()
    config = ConfiguracionModel()
    unidad = UnidadMedidaModel()
    categoria = CategoriaModel()
    marca = MarcaModel()

    # Usuario admin
    admin = usuario.get_by_email("admin@milburbujas.local")
    test("Usuario admin existe", admin is not None)
    test("Usuario admin rol ADMIN", admin and admin["rol"] == "ADMIN")

    # Configuración
    iva = config.get_valor("IVA_PORCENTAJE")
    test("Config IVA_PORCENTAJE = 15", iva == "15", f"Valor: {iva}")

    monto_min = config.get_valor("MONTO_MIN_COMPROBANTE")
    test("Config MONTO_MIN_COMPROBANTE = 3.00", monto_min == "3.00")

    total_configs = config.count()
    test(f"Total configs >= 14", total_configs >= 14, f"Encontradas: {total_configs}")

    # Unidades de medida
    total_unidades = unidad.count()
    test(f"Unidades de medida = 15", total_unidades == 15, f"Encontradas: {total_unidades}")

    un = unidad.get_by_abreviatura("UN")
    test("Unidad 'UN' existe", un is not None)

    # Categorías
    total_cat = categoria.count()
    test(f"Categorías >= 12", total_cat >= 12, f"Encontradas: {total_cat}")

    raices = categoria.get_raices()
    test(f"Categorías raíz >= 11", len(raices) >= 11, f"Encontradas: {len(raices)}")

    # Marcas (se crean manualmente, el seed no incluye marcas)
    total_marcas = marca.count()
    test(f"Marcas >= 0 (se crean manualmente)", total_marcas >= 0, f"Encontradas: {total_marcas}")


def test_03_crud_modelos():
    """Test 3: CRUD en modelos principales."""
    print("\n" + "=" * 60)
    print("TEST 3: CRUD EN MODELOS")
    print("=" * 60)

    # ── Categoría ──
    cat_model = CategoriaModel()
    cat_id = cat_model.insert({
        "nombre": "Test Categoría CRUD",
        "descripcion": "Categoría de prueba",
        "nivel": 0
    })
    test("Categoría INSERT", cat_id > 0)

    cat = cat_model.get_by_id(cat_id)
    test("Categoría READ", cat is not None and cat["nombre"] == "Test Categoría CRUD")

    cat_model.update(cat_id, {"descripcion": "Modificada"})
    cat = cat_model.get_by_id(cat_id)
    test("Categoría UPDATE", cat["descripcion"] == "Modificada")

    cat_model.deactivate(cat_id)
    cat = cat_model.get_by_id(cat_id)
    test("Categoría DELETE lógico", cat["estado"] == "INA")

    # ── Marca ──
    marca_model = MarcaModel()
    marca_id = marca_model.insert({"nombre": "Test Marca CRUD", "descripcion": "Prueba"})
    test("Marca INSERT", marca_id > 0)

    # ── Línea de Producto ──
    linea_model = LineaProductoModel()
    linea_id = linea_model.insert({
        "marca_id": marca_id,
        "nombre": "Test Línea CRUD",
        "descripcion": "Prueba"
    })
    test("Línea Producto INSERT", linea_id > 0)

    # ── Producto ──
    prod_model = ProductoModel()
    unidad = UnidadMedidaModel().get_by_abreviatura("UN")
    cat_activa = CategoriaModel().get_raices()[0]

    prod_id = prod_model.insert({
        "codigo_barras": "TEST-001",
        "nombre": "Champú Test",
        "categoria_id": cat_activa["categoria_id"],
        "marca_id": marca_id,
        "linea_id": linea_id,
        "unidad_id": unidad["unidad_id"],
        "precio_referencia_compra": 3.50,
        "precio_venta": 5.95,
        "precio_venta_minimo": 4.00,
        "stock_actual": 20,
        "stock_minimo": 5,
        "stock_maximo": 50,
        "aplica_iva_compra": 1,
    })
    test("Producto INSERT", prod_id > 0)

    prod = prod_model.get_by_codigo_barras("TEST-001")
    test("Producto READ por código", prod is not None and prod["precio_venta"] == 5.95)

    # ── Proveedor ──
    prov_model = ProveedorModel()
    prov_id = prov_model.insert({
        "ruc_cedula": "1712345678",
        "razon_social": "Proveedor Test CRUD",
        "tipo_credito": "CREDITO_60",
        "plazo_credito_dias": 60,
        "frecuencia_pedido": "QUINCENAL",
    })
    test("Proveedor INSERT", prov_id > 0)

    # ── Proveedor-Producto ──
    pp_model = ProveedorProductoModel()
    pp_id = pp_model.insert({
        "proveedor_id": prov_id,
        "producto_id": prod_id,
        "precio_compra": 3.50,
        "precio_compra_con_iva": 4.03,
        "incluye_iva": 1,
        "es_proveedor_principal": 1,
    })
    test("Proveedor-Producto INSERT (N:M)", pp_id > 0)

    ppal = pp_model.get_proveedor_principal(prod_id)
    test("Proveedor principal de producto", ppal is not None)

    # ── Cliente ──
    cli_model = ClienteModel()
    cli_id = cli_model.insert({
        "cedula": "1798765432",
        "nombres": "María",
        "apellidos": "Pérez Test",
        "telefono": "0991234567",
        "habilitado_credito": 1,
        "limite_credito": 50.00,
        "saldo_pendiente": 0.00,
        "frecuencia_pago": "QUINCENAL",
    })
    test("Cliente INSERT", cli_id > 0)

    cli = cli_model.get_by_cedula("1798765432")
    test("Cliente READ por cédula", cli is not None)

    # ── Precio Referencia ──
    pr_model = PrecioReferenciaModel()
    pr_id = pr_model.insert({
        "producto_id": prod_id,
        "origen": "SUPERMERCADO",
        "nombre_comercio": "Hipermarket",
        "precio": 6.50,
        "fecha_consulta": "2026-03-01",
    })
    test("Precio Referencia INSERT", pr_id > 0)

    # ── Gasto Operativo ──
    gasto_model = GastoOperativoModel()
    gasto_id = gasto_model.insert({
        "usuario_id": 1,
        "tipo_gasto": "ARRIENDO",
        "descripcion": "Arriendo mes de marzo",
        "monto": 200.00,
        "fecha_gasto": "2026-03-01",
        "metodo_pago": "EFECTIVO",
    })
    test("Gasto Operativo INSERT", gasto_id > 0)

    print(f"\n  📦 IDs generados: cat={cat_id}, marca={marca_id}, prod={prod_id}, prov={prov_id}, cli={cli_id}")


def test_04_transaccion_compra():
    """Test 4: TX-01 Registrar Compra (transacción atómica)."""
    print("\n" + "=" * 60)
    print("TEST 4: TRANSACCIÓN - REGISTRAR COMPRA (TX-01)")
    print("=" * 60)

    db = DatabaseConnection()
    prod_model = ProductoModel()
    compra_model = CompraModel()
    detalle_model = CompraDetalleModel()
    mov_model = MovimientoInventarioModel()
    cp_model = CuentaPagarModel()

    # Obtener producto de prueba
    prod = prod_model.get_by_codigo_barras("TEST-001")
    stock_antes = prod["stock_actual"]
    prov = ProveedorModel().get_by_ruc("1712345678")

    try:
        with db.transaction():
            # 1. Cabecera de compra
            compra_id = compra_model.insert_in_transaction({
                "numero_factura": "FAC-TEST-001",
                "proveedor_id": prov["proveedor_id"],
                "usuario_id": 1,
                "fecha_compra": "2026-03-10",
                "subtotal_sin_iva": 35.00,
                "monto_iva": 5.25,
                "total": 40.25,
                "tipo_pago": "CREDITO",
                "plazo_credito_dias": 60,
            })

            # 2. Detalle
            detalle_model.insert_in_transaction({
                "compra_id": compra_id,
                "producto_id": prod["producto_id"],
                "cantidad": 10,
                "precio_unitario": 4.03,
                "incluye_iva": 1,
                "precio_sin_iva": 3.50,
                "subtotal": 35.00,
                "fecha_caducidad_lote": "2027-06-15",
            })

            # 3. Actualizar stock
            nuevo_stock = stock_antes + 10
            prod_model.actualizar_stock(prod["producto_id"], nuevo_stock)

            # 4. Movimiento de inventario
            mov_model.registrar(
                producto_id=prod["producto_id"],
                tipo="ENTRADA", origen="COMPRA",
                documento_id=compra_id,
                cantidad=10,
                stock_anterior=stock_antes,
                stock_posterior=nuevo_stock
            )

            # 5. Cuenta por pagar (es crédito)
            cp_model.insert_in_transaction({
                "numero_cuenta": "CP-TEST-001",
                "proveedor_id": prov["proveedor_id"],
                "compra_id": compra_id,
                "monto_original": 40.25,
                "saldo_pendiente": 40.25,
                "fecha_emision": "2026-03-10",
                "fecha_vencimiento": "2026-05-09",
                "estado_pago": "PENDIENTE",
            })

        # Verificar fuera de transacción
        prod_despues = prod_model.get_by_id(prod["producto_id"])
        test("TX Compra: stock actualizado", prod_despues["stock_actual"] == stock_antes + 10,
             f"Esperado {stock_antes + 10}, real {prod_despues['stock_actual']}")

        compra = compra_model.get_by_id(compra_id)
        test("TX Compra: cabecera creada", compra is not None)

        detalles = detalle_model.get_by_compra(compra_id)
        test("TX Compra: detalle creado", len(detalles) == 1)

        movs = mov_model.get_by_documento("COMPRA", compra_id)
        test("TX Compra: movimiento registrado", len(movs) == 1)

        cp = cp_model.get_by_compra(compra_id)
        test("TX Compra: cuenta por pagar creada", cp is not None and cp["saldo_pendiente"] == 40.25)

    except Exception as e:
        test("TX Compra: ejecutada sin error", False, str(e))


def test_05_transaccion_venta():
    """Test 5: TX-02 Registrar Venta (transacción atómica)."""
    print("\n" + "=" * 60)
    print("TEST 5: TRANSACCIÓN - REGISTRAR VENTA (TX-02)")
    print("=" * 60)

    db = DatabaseConnection()
    prod_model = ProductoModel()
    venta_model = VentaModel()
    vd_model = VentaDetalleModel()
    mov_model = MovimientoInventarioModel()
    cc_model = CuentaCobrarModel()
    cli_model = ClienteModel()

    prod = prod_model.get_by_codigo_barras("TEST-001")
    stock_antes = prod["stock_actual"]
    cli = cli_model.get_by_cedula("1798765432")

    try:
        with db.transaction():
            # 1. Cabecera de venta (fiado)
            venta_id = venta_model.insert_in_transaction({
                "numero_comprobante": "NV-TEST-001",
                "cliente_id": cli["cliente_id"],
                "usuario_id": 1,
                "subtotal": 11.90,
                "descuento": 0.00,
                "total": 11.90,
                "metodo_pago": "CREDITO",
                "es_credito": 1,
                "comprobante_emitido": 1,  # > $3.00
            })

            # 2. Detalle
            vd_model.insert_in_transaction({
                "venta_id": venta_id,
                "producto_id": prod["producto_id"],
                "cantidad": 2,
                "precio_unitario": 5.95,
                "precio_original": 5.95,
                "descuento_unitario": 0.00,
                "subtotal": 11.90,
            })

            # 3. Descontar stock
            nuevo_stock = stock_antes - 2
            prod_model.actualizar_stock(prod["producto_id"], nuevo_stock)

            # 4. Movimiento
            mov_model.registrar(
                producto_id=prod["producto_id"],
                tipo="SALIDA", origen="VENTA",
                documento_id=venta_id,
                cantidad=2,
                stock_anterior=stock_antes,
                stock_posterior=nuevo_stock
            )

            # 5. Cuenta por cobrar (fiado)
            cc_model.insert_in_transaction({
                "numero_cuenta": "CC-TEST-001",
                "cliente_id": cli["cliente_id"],
                "venta_id": venta_id,
                "monto_original": 11.90,
                "saldo_pendiente": 11.90,
                "fecha_emision": "2026-03-10",
                "fecha_vencimiento": "2026-03-25",
                "estado_pago": "PENDIENTE",
            })

            # 6. Actualizar saldo del cliente
            nuevo_saldo = cli["saldo_pendiente"] + 11.90
            cli_model.actualizar_saldo(cli["cliente_id"], nuevo_saldo)

        # Verificar
        prod_despues = prod_model.get_by_id(prod["producto_id"])
        test("TX Venta: stock descontado", prod_despues["stock_actual"] == stock_antes - 2)

        venta = venta_model.get_by_id(venta_id)
        test("TX Venta: cabecera creada", venta is not None and venta["total"] == 11.90)

        cc = cc_model.get_by_venta(venta_id)
        test("TX Venta: cuenta por cobrar creada", cc is not None)

        cli_despues = cli_model.get_by_id(cli["cliente_id"])
        test("TX Venta: saldo cliente actualizado", cli_despues["saldo_pendiente"] == 11.90)

    except Exception as e:
        test("TX Venta: ejecutada sin error", False, str(e))


def test_06_transaccion_pago_cliente():
    """Test 6: TX-03 Registrar Pago de Cliente."""
    print("\n" + "=" * 60)
    print("TEST 6: TRANSACCIÓN - PAGO DE CLIENTE (TX-03)")
    print("=" * 60)

    db = DatabaseConnection()
    cc_model = CuentaCobrarModel()
    pago_model = PagoClienteModel()
    cli_model = ClienteModel()

    cli = cli_model.get_by_cedula("1798765432")
    cuentas = cc_model.get_pendientes_por_cliente(cli["cliente_id"])
    cuenta = cuentas[0] if cuentas else None

    try:
        with db.transaction():
            # Pago parcial de $5.00
            pago_model.insert_in_transaction({
                "cuenta_cobrar_id": cuenta["cuenta_cobrar_id"],
                "usuario_id": 1,
                "monto_pago": 5.00,
                "metodo_pago": "EFECTIVO",
                "fecha_pago": "2026-03-15",
            })

            nuevo_saldo_cuenta = cuenta["saldo_pendiente"] - 5.00
            cc_model.update_in_transaction(cuenta["cuenta_cobrar_id"], {
                "saldo_pendiente": nuevo_saldo_cuenta,
                "estado_pago": "PARCIAL" if nuevo_saldo_cuenta > 0 else "PAGADO",
            })

            cli_model.actualizar_saldo(cli["cliente_id"], cli["saldo_pendiente"] - 5.00)

        cc_despues = cc_model.get_by_id(cuenta["cuenta_cobrar_id"])
        test("TX Pago Cliente: saldo cuenta reducido", cc_despues["saldo_pendiente"] == 6.90,
             f"Esperado 6.90, real {cc_despues['saldo_pendiente']}")
        test("TX Pago Cliente: estado PARCIAL", cc_despues["estado_pago"] == "PARCIAL")

        cli_despues = cli_model.get_by_id(cli["cliente_id"])
        test("TX Pago Cliente: saldo cliente reducido", cli_despues["saldo_pendiente"] == 6.90)

    except Exception as e:
        test("TX Pago Cliente: ejecutada sin error", False, str(e))


def test_07_transaccion_pago_proveedor():
    """Test 7: TX-04 Registrar Pago a Proveedor."""
    print("\n" + "=" * 60)
    print("TEST 7: TRANSACCIÓN - PAGO A PROVEEDOR (TX-04)")
    print("=" * 60)

    db = DatabaseConnection()
    cp_model = CuentaPagarModel()
    pago_model = PagoProveedorModel()

    cp = cp_model.get_one_by_field("numero_cuenta", "CP-TEST-001")

    try:
        with db.transaction():
            pago_model.insert_in_transaction({
                "cuenta_pagar_id": cp["cuenta_pagar_id"],
                "usuario_id": 1,
                "monto_pago": 20.00,
                "metodo_pago": "EFECTIVO",
                "fecha_pago": "2026-03-17",
            })

            nuevo_saldo = cp["saldo_pendiente"] - 20.00
            cp_model.update_in_transaction(cp["cuenta_pagar_id"], {
                "saldo_pendiente": nuevo_saldo,
                "estado_pago": "PARCIAL",
            })

        cp_despues = cp_model.get_by_id(cp["cuenta_pagar_id"])
        test("TX Pago Proveedor: saldo reducido", cp_despues["saldo_pendiente"] == 20.25,
             f"Esperado 20.25, real {cp_despues['saldo_pendiente']}")
        test("TX Pago Proveedor: estado PARCIAL", cp_despues["estado_pago"] == "PARCIAL")

    except Exception as e:
        test("TX Pago Proveedor: ejecutada sin error", False, str(e))


def test_08_transaccion_ajuste():
    """Test 8: TX-05 Ajuste de Inventario."""
    print("\n" + "=" * 60)
    print("TEST 8: TRANSACCIÓN - AJUSTE DE INVENTARIO (TX-05)")
    print("=" * 60)

    db = DatabaseConnection()
    prod_model = ProductoModel()
    ajuste_model = AjusteInventarioModel()
    mov_model = MovimientoInventarioModel()

    prod = prod_model.get_by_codigo_barras("TEST-001")
    stock_antes = prod["stock_actual"]

    try:
        with db.transaction():
            # Consumo personal: -1 unidad
            ajuste_id = ajuste_model.insert_in_transaction({
                "numero_ajuste": "AJ-TEST-001",
                "producto_id": prod["producto_id"],
                "usuario_id": 1,
                "tipo_ajuste": "CONSUMO_PERSONAL",
                "cantidad": -1,
                "motivo": "Uso personal de la propietaria",
            })

            nuevo_stock = stock_antes - 1
            prod_model.actualizar_stock(prod["producto_id"], nuevo_stock)

            mov_model.registrar(
                producto_id=prod["producto_id"],
                tipo="SALIDA", origen="AJUSTE",
                documento_id=ajuste_id,
                cantidad=1,
                stock_anterior=stock_antes,
                stock_posterior=nuevo_stock
            )

        prod_despues = prod_model.get_by_id(prod["producto_id"])
        test("TX Ajuste: stock reducido por consumo personal",
             prod_despues["stock_actual"] == stock_antes - 1)

        movs = mov_model.get_by_documento("AJUSTE", ajuste_id)
        test("TX Ajuste: movimiento registrado", len(movs) == 1)

    except Exception as e:
        test("TX Ajuste: ejecutada sin error", False, str(e))


def test_09_rollback():
    """Test 9: Verificar que el ROLLBACK funciona."""
    print("\n" + "=" * 60)
    print("TEST 9: ROLLBACK EN TRANSACCIONES")
    print("=" * 60)

    db = DatabaseConnection()
    prod_model = ProductoModel()
    prod = prod_model.get_by_codigo_barras("TEST-001")
    stock_antes = prod["stock_actual"]

    try:
        with db.transaction():
            prod_model.actualizar_stock(prod["producto_id"], stock_antes - 100)
            # Forzar error: insertar venta con FK inválido
            db.execute_in_transaction(
                "INSERT INTO venta_detalle (venta_id, producto_id, cantidad, precio_unitario, precio_original, subtotal) VALUES (99999, 99999, 1, 1, 1, 1)"
            )
    except Exception:
        pass  # Se espera el error

    # Verificar que el stock NO cambió (rollback)
    prod_despues = prod_model.get_by_id(prod["producto_id"])
    test("ROLLBACK: stock no cambió tras error",
         prod_despues["stock_actual"] == stock_antes,
         f"Esperado {stock_antes}, real {prod_despues['stock_actual']}")


def test_10_constraints():
    """Test 10: Verificar constraints y FK."""
    print("\n" + "=" * 60)
    print("TEST 10: CONSTRAINTS Y FOREIGN KEYS")
    print("=" * 60)

    db = DatabaseConnection()
    prod_model = ProductoModel()

    # UK: código duplicado
    try:
        prod_model.insert({
            "codigo_barras": "TEST-001",  # duplicado
            "nombre": "Duplicado",
            "categoria_id": 1, "unidad_id": 1,
            "precio_venta": 1.00,
        })
        test("UK: código duplicado rechazado", False, "No lanzó excepción")
    except Exception:
        test("UK: código duplicado rechazado", True)

    # CHECK: precio negativo
    try:
        prod_model.insert({
            "codigo_barras": "TEST-NEG",
            "nombre": "Precio Negativo",
            "categoria_id": 1, "unidad_id": 1,
            "precio_venta": -5.00,
        })
        test("CHECK: precio negativo rechazado", False, "No lanzó excepción")
    except Exception:
        test("CHECK: precio negativo rechazado", True)

    # CHECK: estado inválido
    try:
        db.execute(
            "INSERT INTO marca (nombre, estado) VALUES ('Test Bad Estado', 'MALO')"
        )
        test("CHECK: estado inválido rechazado", False, "No lanzó excepción")
    except Exception:
        test("CHECK: estado inválido rechazado", True)

    # FK: categoría inexistente
    try:
        prod_model.insert({
            "codigo_barras": "TEST-FK",
            "nombre": "FK Inválida",
            "categoria_id": 99999,  # no existe
            "unidad_id": 1,
            "precio_venta": 1.00,
        })
        test("FK: categoría inexistente rechazada", False, "No lanzó excepción")
    except Exception:
        test("FK: categoría inexistente rechazada", True)


def test_11_consultas_especificas():
    """Test 11: Consultas específicas de negocio."""
    print("\n" + "=" * 60)
    print("TEST 11: CONSULTAS ESPECÍFICAS DE NEGOCIO")
    print("=" * 60)

    # Stock bajo
    prod_model = ProductoModel()
    stock_bajo = prod_model.get_stock_bajo()
    test("Consulta stock bajo ejecuta OK", isinstance(stock_bajo, list))

    # Valor inventario
    valor = prod_model.get_valor_inventario()
    test("Consulta valor inventario ejecuta OK", valor is not None)

    # Productos completos
    completos = prod_model.get_completo()
    test("Consulta productos completos ejecuta OK", len(completos) >= 1)

    # Búsqueda
    resultados = prod_model.buscar("Champú")
    test("Búsqueda de producto funciona", len(resultados) >= 1)

    # Comparativo precios
    pr_model = PrecioReferenciaModel()
    comparativo = pr_model.get_comparativo(completos[0]["producto_id"])
    test("Comparativo de precios ejecuta OK", isinstance(comparativo, list))

    # Cuentas vencidas
    cc_model = CuentaCobrarModel()
    vencidas = cc_model.get_vencidas()
    test("Consulta cuentas vencidas ejecuta OK", isinstance(vencidas, list))

    cp_model = CuentaPagarModel()
    total_deuda = cp_model.get_total_pendiente()
    test("Total deuda proveedores calculado", total_deuda > 0, f"Total: {total_deuda}")

    # Totales del día
    venta_model = VentaModel()
    totales = venta_model.get_totales_dia()
    test("Totales del día ejecuta OK", totales is not None)

    # Proveedor con saldo
    prov_model = ProveedorModel()
    provs = prov_model.get_con_saldo_pendiente()
    test("Proveedores con saldo ejecuta OK", isinstance(provs, list))


def main():
    """Ejecuta todos los tests."""
    global passed, failed, total

    print("\n" + "🔧" * 30)
    print("  Mil Burbujas - VERIFICACIÓN FASE 1 (BASE DE DATOS)")
    print("🔧" * 30)

    limpiar_db_test()

    test_01_creacion_schema()
    test_02_seed_data()
    test_03_crud_modelos()
    test_04_transaccion_compra()
    test_05_transaccion_venta()
    test_06_transaccion_pago_cliente()
    test_07_transaccion_pago_proveedor()
    test_08_transaccion_ajuste()
    test_09_rollback()
    test_10_constraints()
    test_11_consultas_especificas()

    # Resumen
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE VERIFICACIÓN")
    print("=" * 60)
    print(f"  Total de tests:  {total}")
    print(f"  ✅ Pasaron:       {passed}")
    print(f"  ❌ Fallaron:      {failed}")
    print(f"  Porcentaje:      {(passed / total * 100) if total > 0 else 0:.1f}%")

    if failed == 0:
        print("\n  🎉 FASE 1 COMPLETADA - BASE DE DATOS CONGELADA")
        print("  👉 Puedes proceder a la FASE 2 (Servicios)")
    else:
        print(f"\n  ⚠️  Hay {failed} test(s) fallido(s). Revisar antes de continuar.")

    print("=" * 60)

    # Cerrar conexión
    DatabaseConnection().close()
    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
