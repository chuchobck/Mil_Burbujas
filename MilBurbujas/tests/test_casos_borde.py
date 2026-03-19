# -*- coding: utf-8 -*-
"""
Mil Burbujas - Fase 3 · Test 2/3: CASOS BORDE (Edge Cases)
Pruebas de condiciones límite, valores extremos, datos inválidos
y situaciones inusuales que podrían romper la aplicación.
"""
import os, sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import DB_DIR
from database.connection import DatabaseConnection

from services.usuario_service import UsuarioService
from services.catalogo_service import CatalogoService
from services.proveedor_service import ProveedorService
from services.cliente_service import ClienteService
from services.compra_service import CompraService
from services.venta_service import VentaService
from services.cobro_service import CobroService
from services.pago_service import PagoService
from services.inventario_service import InventarioService
from services.cierre_caja_service import CierreCajaService
from services.gasto_service import GastoService
from services.reporte_service import ReporteService

from models.producto import ProductoModel
from models.cliente import ClienteModel

passed = 0
failed = 0
total = 0


def test(nombre, condicion, detalle=""):
    global passed, failed, total
    total += 1
    if condicion:
        passed += 1
        print(f"  ✅ {nombre}")
    else:
        failed += 1
        print(f"  ❌ {nombre} → {detalle}")


def espera_error(fn, nombre, tipo_error=ValueError):
    """Ejecuta fn, espera que lance tipo_error."""
    try:
        fn()
        test(nombre, False, "No lanzó excepción")
    except tipo_error:
        test(nombre, True)
    except Exception as e:
        test(nombre, False, f"Error inesperado: {type(e).__name__}: {e}")


def limpiar_db():
    db_path = os.path.join(DB_DIR, "milburbujas.db")
    if os.path.exists(db_path):
        db = DatabaseConnection()
        db.close()
        DatabaseConnection._instance = None
        DatabaseConnection._connection = None
        os.remove(db_path)
    db = DatabaseConnection()
    db.init_database()


def crear_producto_test(cat_svc, codigo, nombre, precio_venta=5.00, stock=20):
    """Helper rápido para crear un producto."""
    cats = cat_svc.get_categorias_raiz()
    unds = cat_svc.get_unidades()
    return cat_svc.crear_producto({
        "codigo_barras": codigo, "nombre": nombre,
        "categoria_id": cats[0]["categoria_id"],
        "unidad_id": unds[0]["unidad_id"],
        "precio_venta": precio_venta,
        "precio_venta_minimo": round(precio_venta * 0.7, 2),
        "stock_actual": stock,
        "stock_minimo": 2, "stock_maximo": 500,
        "aplica_iva_compra": 1,
    })


# ══════════════════════════════════════════════════════════════════
# GRUPO 1: VALORES NUMÉRICOS EXTREMOS
# ══════════════════════════════════════════════════════════════════

def test_01_valores_extremos():
    print("\n" + "=" * 60)
    print("GRUPO 1: VALORES NUMÉRICOS EXTREMOS")
    print("=" * 60)

    cat_svc = CatalogoService()

    # Precio = 0 (debería permitirse para productos de regalo/muestra)
    p_cero = cat_svc.crear_producto({
        "codigo_barras": "BORDE-01", "nombre": "Muestra Gratis",
        "categoria_id": cat_svc.get_categorias_raiz()[0]["categoria_id"],
        "unidad_id": cat_svc.get_unidades()[0]["unidad_id"],
        "precio_venta": 0.00, "stock_actual": 10,
        "stock_minimo": 0, "stock_maximo": 100,
    })
    test("Producto precio $0 permitido", p_cero is not None)

    # Precio negativo (debe rechazar)
    espera_error(
        lambda: cat_svc.crear_producto({
            "codigo_barras": "BORDE-02", "nombre": "Bad",
            "categoria_id": cat_svc.get_categorias_raiz()[0]["categoria_id"],
            "unidad_id": cat_svc.get_unidades()[0]["unidad_id"],
            "precio_venta": -5.00,
        }),
        "Precio negativo rechazado"
    )

    # Precio muy alto
    p_caro = crear_producto_test(cat_svc, "BORDE-03", "Perfume Exclusivo", 9999.99, 5)
    test("Producto precio $9999.99", p_caro["precio_venta"] == 9999.99)

    # Stock = 0 (producto sin stock)
    p_sin_stock = crear_producto_test(cat_svc, "BORDE-04", "Agotado", 10.00, 0)
    test("Producto stock=0 creado", p_sin_stock["stock_actual"] == 0)

    # Intentar vender producto sin stock
    venta_svc = VentaService()
    espera_error(
        lambda: venta_svc.registrar_venta(
            cabecera={"metodo_pago": "EFECTIVO", "monto_recibido": 100, "es_credito": 0},
            items=[{"producto_id": p_sin_stock["producto_id"], "cantidad": 1}]
        ),
        "Venta con stock=0 rechazada"
    )

    # ── Precisión decimal ──
    cat_svc2 = CatalogoService()

    # Precio con muchos decimales
    p_dec = crear_producto_test(cat_svc2, "BORDE-05", "Decimal Test", 3.33, 100)
    v_svc = VentaService()
    v = v_svc.registrar_venta(
        cabecera={"metodo_pago": "EFECTIVO", "monto_recibido": 20, "es_credito": 0},
        items=[{"producto_id": p_dec["producto_id"], "cantidad": 3}]
    )
    # 3.33 * 3 = 9.99
    test("Precisión decimal 3.33*3=9.99", v["total"] == 9.99, f"Real: {v['total']}")

    # Cambio con decimales: 20 - 9.99 = 10.01
    test("Cambio decimal correcto", v["cambio"] == 10.01, f"Real: {v['cambio']}")

    return p_cero, p_sin_stock


# ══════════════════════════════════════════════════════════════════
# GRUPO 2: VALIDACIONES DE DUPLICADOS
# ══════════════════════════════════════════════════════════════════

def test_02_duplicados():
    print("\n" + "=" * 60)
    print("GRUPO 2: VALIDACIONES DE DUPLICADOS")
    print("=" * 60)

    cat_svc = CatalogoService()
    cli_svc = ClienteService()
    prov_svc = ProveedorService()
    usr_svc = UsuarioService()

    # ── Categoría duplicada ──
    cat_svc.crear_categoria({"nombre": "Duplicada Test", "nivel": 0})
    espera_error(
        lambda: cat_svc.crear_categoria({"nombre": "Duplicada Test", "nivel": 0}),
        "Categoría duplicada rechazada"
    )

    # ── Marca duplicada ──
    cat_svc.crear_marca({"nombre": "Marca Dup Test"})
    espera_error(
        lambda: cat_svc.crear_marca({"nombre": "Marca Dup Test"}),
        "Marca duplicada rechazada"
    )

    # ── Producto código duplicado ──
    crear_producto_test(cat_svc, "DUP-001", "Original")
    espera_error(
        lambda: crear_producto_test(cat_svc, "DUP-001", "Copia"),
        "Código producto duplicado rechazado"
    )

    # ── Cliente cédula duplicada ──
    cli_svc.crear({"cedula": "9999999999", "nombres": "Original", "apellidos": "Test"})
    espera_error(
        lambda: cli_svc.crear({"cedula": "9999999999", "nombres": "Copia", "apellidos": "Test"}),
        "Cédula cliente duplicada rechazada"
    )

    # ── Proveedor RUC duplicado ──
    prov_svc.crear({"ruc_cedula": "8888888888", "razon_social": "Prov Original"})
    espera_error(
        lambda: prov_svc.crear({"ruc_cedula": "8888888888", "razon_social": "Prov Copia"}),
        "RUC proveedor duplicado rechazado"
    )

    # ── Usuario email duplicado ──
    usr_svc.crear({"nombre_completo": "User Test", "email": "dup@test.com", "contrasena": "test123"})
    espera_error(
        lambda: usr_svc.crear({"nombre_completo": "User Dup", "email": "dup@test.com", "contrasena": "test123"}),
        "Email usuario duplicado rechazado"
    )


# ══════════════════════════════════════════════════════════════════
# GRUPO 3: OPERACIONES CON CRÉDITO LÍMITE
# ══════════════════════════════════════════════════════════════════

def test_03_credito_limites():
    print("\n" + "=" * 60)
    print("GRUPO 3: OPERACIONES CON CRÉDITO AL LÍMITE")
    print("=" * 60)

    cat_svc = CatalogoService()
    cli_svc = ClienteService()
    venta_svc = VentaService()
    cobro_svc = CobroService()

    # Producto de $10
    prod = crear_producto_test(cat_svc, "CRED-001", "Producto Crédito", 10.00, 100)

    # Cliente con límite exacto $20
    cli = cli_svc.crear({
        "cedula": "1111111111", "nombres": "Límite", "apellidos": "Justo",
        "habilitado_credito": 1, "limite_credito": 20.00, "saldo_pendiente": 0.00,
    })

    # Venta exacta al límite ($20)
    v1 = venta_svc.registrar_venta(
        cabecera={"cliente_id": cli["cliente_id"], "metodo_pago": "CREDITO", "es_credito": 1},
        items=[{"producto_id": prod["producto_id"], "cantidad": 2}]
    )
    test("Crédito exacto al límite ($20/$20)", v1["total"] == 20.00)

    cli_post = ClienteModel().get_by_id(cli["cliente_id"])
    test("Saldo = límite ($20)", cli_post["saldo_pendiente"] == 20.00)

    # Intentar otra venta a crédito ($10 más, excede)
    espera_error(
        lambda: venta_svc.registrar_venta(
            cabecera={"cliente_id": cli["cliente_id"], "metodo_pago": "CREDITO", "es_credito": 1},
            items=[{"producto_id": prod["producto_id"], "cantidad": 1}]
        ),
        "Crédito agotado rechazado"
    )

    # Pagar $10, ahora tiene $10 disponible
    from models.cuenta_cobrar import CuentaCobrarModel
    cc = CuentaCobrarModel().get_by_venta(v1["venta_id"])
    cobro_svc.registrar_pago(cc["cuenta_cobrar_id"], 10.00, "EFECTIVO", "2026-03-15")

    cli_post2 = ClienteModel().get_by_id(cli["cliente_id"])
    test("Después de pagar $10, saldo = $10", cli_post2["saldo_pendiente"] == 10.00)

    # Ahora sí puede comprar exactamente $10 más
    v2 = venta_svc.registrar_venta(
        cabecera={"cliente_id": cli["cliente_id"], "metodo_pago": "CREDITO", "es_credito": 1},
        items=[{"producto_id": prod["producto_id"], "cantidad": 1}]
    )
    test("Crédito renovado OK ($10)", v2["total"] == 10.00)

    cli_post3 = ClienteModel().get_by_id(cli["cliente_id"])
    test("Saldo nuevamente en límite ($20)", cli_post3["saldo_pendiente"] == 20.00)

    # Cliente sin habilitación de crédito
    cli_no = cli_svc.crear({
        "cedula": "2222222222", "nombres": "Sin", "apellidos": "Crédito",
        "habilitado_credito": 0, "limite_credito": 100.00,
    })
    espera_error(
        lambda: venta_svc.registrar_venta(
            cabecera={"cliente_id": cli_no["cliente_id"], "metodo_pago": "CREDITO", "es_credito": 1},
            items=[{"producto_id": prod["producto_id"], "cantidad": 1}]
        ),
        "Sin crédito habilitado rechazado"
    )


# ══════════════════════════════════════════════════════════════════
# GRUPO 4: COBROS Y PAGOS BORDE
# ══════════════════════════════════════════════════════════════════

def test_04_pagos_borde():
    print("\n" + "=" * 60)
    print("GRUPO 4: COBROS Y PAGOS — CASOS BORDE")
    print("=" * 60)

    cobro_svc = CobroService()
    pago_svc = PagoService()

    # ── Monto cero ──
    espera_error(
        lambda: cobro_svc.registrar_pago(1, 0.00, "EFECTIVO", "2026-03-15"),
        "Cobro monto $0 rechazado"
    )

    # ── Monto negativo ──
    espera_error(
        lambda: cobro_svc.registrar_pago(1, -5.00, "EFECTIVO", "2026-03-15"),
        "Cobro monto negativo rechazado"
    )

    # ── Cuenta inexistente ──
    espera_error(
        lambda: cobro_svc.registrar_pago(99999, 1.00, "EFECTIVO", "2026-03-15"),
        "Cobro cuenta inexistente rechazado"
    )

    # ── Pago proveedor monto cero ──
    espera_error(
        lambda: pago_svc.registrar_pago(1, 0.00, "EFECTIVO", "2026-03-15"),
        "Pago proveedor $0 rechazado"
    )


# ══════════════════════════════════════════════════════════════════
# GRUPO 5: INVENTARIO EXTREMO
# ══════════════════════════════════════════════════════════════════

def test_05_inventario_extremo():
    print("\n" + "=" * 60)
    print("GRUPO 5: INVENTARIO — EXTREMOS")
    print("=" * 60)

    cat_svc = CatalogoService()
    inv_svc = InventarioService()
    prod_model = ProductoModel()

    # Producto con stock = 1
    prod = crear_producto_test(cat_svc, "INV-BORDE-01", "Último Stock", 10.00, 1)

    # Sacar exactamente todo el stock
    inv_svc.registrar_ajuste(prod["producto_id"], "CONSUMO_PERSONAL", -1,
                             "Último del stock")
    p = prod_model.get_by_id(prod["producto_id"])
    test("Stock llega a exactamente 0", p["stock_actual"] == 0)

    # Intentar sacar una más
    espera_error(
        lambda: inv_svc.registrar_ajuste(prod["producto_id"], "MERMA", -1, "No hay"),
        "Ajuste -1 con stock=0 rechazado"
    )

    # Entrada manual a stock 0
    inv_svc.registrar_ajuste(prod["producto_id"], "ENTRADA_MANUAL", 100,
                             "Reposición masiva")
    p = prod_model.get_by_id(prod["producto_id"])
    test("Reposición masiva OK (0→100)", p["stock_actual"] == 100)

    # Producto inexistente
    espera_error(
        lambda: inv_svc.registrar_ajuste(99999, "MERMA", -1, "No existe"),
        "Ajuste producto inexistente rechazado"
    )

    # Cantidad cero
    espera_error(
        lambda: inv_svc.registrar_ajuste(prod["producto_id"], "CORRECCION", 0, "Cero"),
        "Ajuste cantidad=0 rechazado"
    )


# ══════════════════════════════════════════════════════════════════
# GRUPO 6: COMPRAS — VALIDACIONES
# ══════════════════════════════════════════════════════════════════

def test_06_compras_validaciones():
    print("\n" + "=" * 60)
    print("GRUPO 6: COMPRAS — VALIDACIONES ESTRICTAS")
    print("=" * 60)

    compra_svc = CompraService()
    cat_svc = CatalogoService()
    prov_svc = ProveedorService()

    prov = prov_svc.crear({"ruc_cedula": "0501010101", "razon_social": "Prov Borde Test"})
    prod = crear_producto_test(cat_svc, "COMP-BORDE-01", "Para compra borde", 10.00, 50)

    # ── Sin ítems ──
    espera_error(
        lambda: compra_svc.registrar_compra(
            cabecera={"numero_factura": "BORDE-X01", "proveedor_id": prov["proveedor_id"],
                      "fecha_compra": "2026-03-10", "tipo_pago": "CONTADO"},
            items=[]
        ),
        "Compra sin ítems rechazada"
    )

    # ── Cantidad = 0 ──
    espera_error(
        lambda: compra_svc.registrar_compra(
            cabecera={"numero_factura": "BORDE-X02", "proveedor_id": prov["proveedor_id"],
                      "fecha_compra": "2026-03-10", "tipo_pago": "CONTADO"},
            items=[{"producto_id": prod["producto_id"], "cantidad": 0, "precio_unitario": 5.0, "incluye_iva": 0}]
        ),
        "Compra cantidad=0 rechazada"
    )

    # ── Proveedor inactivo ──
    prov2 = prov_svc.crear({"ruc_cedula": "0502020202", "razon_social": "Prov Inactivo"})
    prov_svc.desactivar(prov2["proveedor_id"])
    espera_error(
        lambda: compra_svc.registrar_compra(
            cabecera={"numero_factura": "BORDE-X03", "proveedor_id": prov2["proveedor_id"],
                      "fecha_compra": "2026-03-10", "tipo_pago": "CONTADO"},
            items=[{"producto_id": prod["producto_id"], "cantidad": 1, "precio_unitario": 5.0, "incluye_iva": 0}]
        ),
        "Compra a proveedor inactivo rechazada"
    )

    # ── Producto inexistente ──
    espera_error(
        lambda: compra_svc.registrar_compra(
            cabecera={"numero_factura": "BORDE-X04", "proveedor_id": prov["proveedor_id"],
                      "fecha_compra": "2026-03-10", "tipo_pago": "CONTADO"},
            items=[{"producto_id": 99999, "cantidad": 5, "precio_unitario": 5.0, "incluye_iva": 0}]
        ),
        "Compra producto inexistente rechazada"
    )


# ══════════════════════════════════════════════════════════════════
# GRUPO 7: VENTAS — VALIDACIONES ESTRICTAS
# ══════════════════════════════════════════════════════════════════

def test_07_ventas_validaciones():
    print("\n" + "=" * 60)
    print("GRUPO 7: VENTAS — VALIDACIONES ESTRICTAS")
    print("=" * 60)

    cat_svc = CatalogoService()
    venta_svc = VentaService()

    prod = crear_producto_test(cat_svc, "VENTA-BORDE-01", "Para venta borde", 10.00, 5)

    # ── Sin ítems ──
    espera_error(
        lambda: venta_svc.registrar_venta(
            cabecera={"metodo_pago": "EFECTIVO", "monto_recibido": 100, "es_credito": 0},
            items=[]
        ),
        "Venta sin ítems rechazada"
    )

    # ── Cantidad <= 0 ──
    espera_error(
        lambda: venta_svc.registrar_venta(
            cabecera={"metodo_pago": "EFECTIVO", "monto_recibido": 100, "es_credito": 0},
            items=[{"producto_id": prod["producto_id"], "cantidad": -1}]
        ),
        "Venta cantidad negativa rechazada"
    )

    # ── Monto recibido insuficiente ──
    espera_error(
        lambda: venta_svc.registrar_venta(
            cabecera={"metodo_pago": "EFECTIVO", "monto_recibido": 1.00, "es_credito": 0},
            items=[{"producto_id": prod["producto_id"], "cantidad": 2}]  # $20
        ),
        "Pago insuficiente rechazado"
    )

    # ── Crédito sin cliente_id ──
    espera_error(
        lambda: venta_svc.registrar_venta(
            cabecera={"metodo_pago": "CREDITO", "es_credito": 1},
            items=[{"producto_id": prod["producto_id"], "cantidad": 1}]
        ),
        "Crédito sin cliente rechazado"
    )

    # ── Venta que agota exactamente el stock ──
    v = venta_svc.registrar_venta(
        cabecera={"metodo_pago": "EFECTIVO", "monto_recibido": 100, "es_credito": 0},
        items=[{"producto_id": prod["producto_id"], "cantidad": 5}]
    )
    test("Venta agota stock exacto (5/5)", v is not None)

    p_post = ProductoModel().get_by_id(prod["producto_id"])
    test("Stock quedó en 0", p_post["stock_actual"] == 0)

    # Siguiente venta ya no puede
    espera_error(
        lambda: venta_svc.registrar_venta(
            cabecera={"metodo_pago": "EFECTIVO", "monto_recibido": 100, "es_credito": 0},
            items=[{"producto_id": prod["producto_id"], "cantidad": 1}]
        ),
        "Venta post-agotamiento rechazada"
    )


# ══════════════════════════════════════════════════════════════════
# GRUPO 8: USUARIOS — SEGURIDAD
# ══════════════════════════════════════════════════════════════════

def test_08_usuarios_seguridad():
    print("\n" + "=" * 60)
    print("GRUPO 8: USUARIOS — SEGURIDAD Y AUTENTICACIÓN")
    print("=" * 60)

    usr_svc = UsuarioService()

    # ── Crear usuario ──
    u = usr_svc.crear({
        "nombre_completo": "Test Borde",
        "email": "borde@test.com",
        "contrasena": "segura123",
        "rol": "OPERADOR",
    })
    test("Crear usuario borde", u is not None)

    # ── Auth correcta ──
    auth = usr_svc.autenticar("borde@test.com", "segura123")
    test("Auth correcta", auth is not None)

    # ── Auth email inexistente ──
    auth2 = usr_svc.autenticar("noexiste@test.com", "segura123")
    test("Auth email inexistente → None", auth2 is None)

    # ── Auth contraseña vacía ──
    auth3 = usr_svc.autenticar("borde@test.com", "")
    test("Auth contraseña vacía → None", auth3 is None)

    # ── Cambiar contraseña con actual incorrecta ──
    espera_error(
        lambda: usr_svc.cambiar_contrasena(u["usuario_id"], "mala", "nueva123"),
        "Cambio con contraseña incorrecta rechazado"
    )

    # ── Contraseña muy corta ──
    espera_error(
        lambda: usr_svc.cambiar_contrasena(u["usuario_id"], "segura123", "123"),
        "Contraseña < 6 chars rechazada"
    )

    # ── Desactivar y no puede autenticar ──
    usr_svc.desactivar(u["usuario_id"])
    auth4 = usr_svc.autenticar("borde@test.com", "segura123")
    test("Usuario inactivo no puede auth", auth4 is None)


# ══════════════════════════════════════════════════════════════════
# GRUPO 9: CARACTERES ESPECIALES Y TEXTO
# ══════════════════════════════════════════════════════════════════

def test_09_caracteres_especiales():
    print("\n" + "=" * 60)
    print("GRUPO 9: CARACTERES ESPECIALES EN DATOS")
    print("=" * 60)

    cat_svc = CatalogoService()
    cli_svc = ClienteService()

    # ── Tildes y ñ en nombres ──
    cat = cat_svc.crear_categoria({"nombre": "Higiene Niños/Bebés", "nivel": 0})
    test("Categoría con ñ y tildes", cat["nombre"] == "Higiene Niños/Bebés")

    marca = cat_svc.crear_marca({"nombre": "L'Oréal París™"})
    test("Marca con apóstrofe y ™", marca["nombre"] == "L'Oréal París™")

    # ── Cliente con apellido compuesto ──
    cli = cli_svc.crear({
        "cedula": "5555555555",
        "nombres": "María José",
        "apellidos": "De la Cruz O'Brien",
        "telefono": "+593 99-111-2233",
    })
    test("Cliente apellido con apóstrofe", cli["apellidos"] == "De la Cruz O'Brien")

    # ── Producto con descripción larga ──
    prod = crear_producto_test(cat_svc, "CHAR-001",
                               "Crema Hidratante Corporal con Vitamina E & Aloe Vera (200ml) – Edición Especial",
                               15.00, 20)
    test("Producto nombre largo con &, –, ()", prod is not None)


# ══════════════════════════════════════════════════════════════════
# GRUPO 10: DESACTIVACIÓN CON DEPENDENCIAS
# ══════════════════════════════════════════════════════════════════

def test_10_desactivacion_dependencias():
    print("\n" + "=" * 60)
    print("GRUPO 10: DESACTIVACIÓN CON DEPENDENCIAS")
    print("=" * 60)

    cat_svc = CatalogoService()
    cli_svc = ClienteService()
    prov_svc = ProveedorService()
    venta_svc = VentaService()

    # ── Cliente con saldo pendiente no se puede desactivar ──
    prod = crear_producto_test(cat_svc, "DEP-001", "Prod Dependencia", 10.00, 50)
    cli = cli_svc.crear({
        "cedula": "6666666666", "nombres": "Con", "apellidos": "Deuda",
        "habilitado_credito": 1, "limite_credito": 100.00, "saldo_pendiente": 0.00,
    })
    venta_svc.registrar_venta(
        cabecera={"cliente_id": cli["cliente_id"], "metodo_pago": "CREDITO", "es_credito": 1},
        items=[{"producto_id": prod["producto_id"], "cantidad": 1}]
    )
    espera_error(
        lambda: cli_svc.desactivar(cli["cliente_id"]),
        "Desactivar cliente con deuda rechazado"
    )

    # ── Cliente sin deuda sí se puede ──
    cli2 = cli_svc.crear({"cedula": "7777777777", "nombres": "Sin", "apellidos": "Deuda"})
    result = cli_svc.desactivar(cli2["cliente_id"])
    test("Desactivar cliente sin deuda OK", result)

    # ── Proveedor con cuentas pendientes ──
    prov = prov_svc.crear({"ruc_cedula": "3333333333", "razon_social": "Prov con Deuda"})
    CompraService().registrar_compra(
        cabecera={
            "numero_factura": "DEP-COMP-01", "proveedor_id": prov["proveedor_id"],
            "fecha_compra": "2026-03-10", "tipo_pago": "CREDITO", "plazo_credito_dias": 30,
        },
        items=[{"producto_id": prod["producto_id"], "cantidad": 5,
                "precio_unitario": 5.0, "incluye_iva": 0}]
    )
    espera_error(
        lambda: prov_svc.desactivar(prov["proveedor_id"]),
        "Desactivar proveedor con deuda rechazado"
    )

    # ── Proveedor sin deuda ──
    prov2 = prov_svc.crear({"ruc_cedula": "4444444444", "razon_social": "Prov sin Deuda"})
    result2 = prov_svc.desactivar(prov2["proveedor_id"])
    test("Desactivar proveedor sin deuda OK", result2)


# ══════════════════════════════════════════════════════════════════
# GRUPO 11: REPORTES EN PERÍODO VACÍO
# ══════════════════════════════════════════════════════════════════

def test_11_reportes_vacios():
    print("\n" + "=" * 60)
    print("GRUPO 11: REPORTES EN PERÍODO VACÍO")
    print("=" * 60)

    rep_svc = ReporteService()

    # Período futuro sin datos
    rv = rep_svc.reporte_ventas_periodo("2030-01-01", "2030-12-31")
    test("Reporte ventas vacío sin error", rv is not None)
    test("Total ventas vacío = 0", rv["total_ventas"] == 0)
    test("Cantidad ventas vacío = 0", rv["cantidad_ventas"] == 0)

    rc = rep_svc.reporte_compras_periodo("2030-01-01", "2030-12-31")
    test("Reporte compras vacío sin error", rc["total_compras"] == 0)

    rg = rep_svc.reporte_gastos_periodo("2030-01-01", "2030-12-31")
    test("Reporte gastos vacío sin error", rg["total_gastos"] == 0)

    ru = rep_svc.reporte_utilidad_periodo("2030-01-01", "2030-12-31")
    test("Utilidad período vacío = 0", ru["utilidad_neta"] == 0)
    test("Margen vacío = 0 (no div/0)", ru["margen_bruto"] == 0)


# ══════════════════════════════════════════════════════════════════
# GRUPO 12: GASTOS — VALIDACIONES
# ══════════════════════════════════════════════════════════════════

def test_12_gastos_validaciones():
    print("\n" + "=" * 60)
    print("GRUPO 12: GASTOS — VALIDACIONES")
    print("=" * 60)

    gasto_svc = GastoService()

    # Monto cero
    espera_error(
        lambda: gasto_svc.registrar({"tipo_gasto": "OTROS", "descripcion": "Bad",
                                      "monto": 0, "fecha_gasto": "2026-03-10",
                                      "metodo_pago": "EFECTIVO"}),
        "Gasto $0 rechazado"
    )

    # Monto negativo
    espera_error(
        lambda: gasto_svc.registrar({"tipo_gasto": "OTROS", "descripcion": "Bad",
                                      "monto": -10, "fecha_gasto": "2026-03-10",
                                      "metodo_pago": "EFECTIVO"}),
        "Gasto negativo rechazado"
    )

    # Gasto válido
    g = gasto_svc.registrar({"tipo_gasto": "ARRIENDO", "descripcion": "Arriendo local",
                              "monto": 250.00, "fecha_gasto": "2026-03-01",
                              "metodo_pago": "TRANSFERENCIA"})
    test("Gasto válido registrado", g["monto"] == 250.00)


# ══════════════════════════════════════════════════════════════════
# GRUPO 13: CIERRE DE CAJA DUPLICADO
# ══════════════════════════════════════════════════════════════════

def test_13_cierre_duplicado():
    print("\n" + "=" * 60)
    print("GRUPO 13: CIERRE DE CAJA — DUPLICADOS")
    print("=" * 60)

    cierre_svc = CierreCajaService()
    fecha = "2026-05-01"

    # Primer cierre
    preview = cierre_svc.preparar_cierre(fecha)
    cierre_svc.cerrar_caja(preview["efectivo_esperado"], fecha=fecha)
    test("Primer cierre OK", True)

    # Segundo cierre mismo día
    espera_error(
        lambda: cierre_svc.cerrar_caja(0, fecha=fecha),
        "Cierre duplicado rechazado"
    )

    # Verificar que existe
    test("Existe cierre para esa fecha", cierre_svc.existe_cierre(fecha))


# ══════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════

def main():
    global passed, failed, total

    print("\n" + "🔬" * 30)
    print("  Mil Burbujas - FASE 3 · CASOS BORDE")
    print("🔬" * 30)

    limpiar_db()

    test_01_valores_extremos()
    test_02_duplicados()
    test_03_credito_limites()
    test_04_pagos_borde()
    test_05_inventario_extremo()
    test_06_compras_validaciones()
    test_07_ventas_validaciones()
    test_08_usuarios_seguridad()
    test_09_caracteres_especiales()
    test_10_desactivacion_dependencias()
    test_11_reportes_vacios()
    test_12_gastos_validaciones()
    test_13_cierre_duplicado()

    print("\n" + "=" * 60)
    print("📊 RESUMEN CASOS BORDE")
    print("=" * 60)
    print(f"  Total: {total}  ✅ {passed}  ❌ {failed}  ({passed/total*100:.1f}%)")
    if failed == 0:
        print("  🎉 CASOS BORDE — Sin errores")
    else:
        print(f"  ⚠️  {failed} fallo(s) requieren revisión")
    print("=" * 60)

    DatabaseConnection().close()
    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
