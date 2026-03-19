# -*- coding: utf-8 -*-
"""
Mil Burbujas - Verificación completa de la Fase 2 (Servicios / Lógica de Negocio)
Ejecuta pruebas de las 8 transacciones (TX-01 a TX-08) + CRUD + validaciones.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import DB_DIR
from database.connection import DatabaseConnection

# Servicios
from services.auditoria_service import AuditoriaService
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

# Modelos (para verificaciones directas)
from models.producto import ProductoModel
from models.cliente import ClienteModel
from models.proveedor import ProveedorModel
from models.cuenta_cobrar import CuentaCobrarModel
from models.cuenta_pagar import CuentaPagarModel
from models.movimiento_inventario import MovimientoInventarioModel

# Contadores
passed = 0
failed = 0
total = 0


def test(nombre: str, condicion: bool, detalle: str = ""):
    global passed, failed, total
    total += 1
    if condicion:
        passed += 1
        print(f"  ✅ {nombre}")
    else:
        failed += 1
        print(f"  ❌ {nombre} → {detalle}")


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


# ══════════════════════════════════════════════════
# TEST 1: CRUD CATÁLOGO VÍA SERVICIO
# ══════════════════════════════════════════════════

def test_01_catalogo():
    print("\n" + "=" * 60)
    print("TEST 1: SERVICIO DE CATÁLOGO (CRUD)")
    print("=" * 60)

    svc = CatalogoService()

    # Categoría
    cat = svc.crear_categoria({"nombre": "SVC Test Cat", "descripcion": "Test", "nivel": 0})
    test("Crear categoría vía servicio", cat is not None and cat["nombre"] == "SVC Test Cat")

    cat = svc.actualizar_categoria(cat["categoria_id"], {"descripcion": "Actualizada"})
    test("Actualizar categoría", cat["descripcion"] == "Actualizada")

    # Marca
    marca = svc.crear_marca({"nombre": "SVC Test Marca", "descripcion": "Test"})
    test("Crear marca", marca is not None)

    # Duplicado
    try:
        svc.crear_marca({"nombre": "SVC Test Marca"})
        test("Marca duplicada rechazada", False)
    except ValueError:
        test("Marca duplicada rechazada", True)

    # Línea
    linea = svc.crear_linea({"marca_id": marca["marca_id"], "nombre": "SVC Línea", "descripcion": "Test"})
    test("Crear línea de producto", linea is not None)

    # Producto
    unidades = svc.get_unidades()
    categorias = svc.get_categorias_raiz()

    producto = svc.crear_producto({
        "codigo_barras": "SVC-PROD-001",
        "nombre": "Champú Servicio Test",
        "categoria_id": categorias[0]["categoria_id"],
        "marca_id": marca["marca_id"],
        "linea_id": linea["linea_id"],
        "unidad_id": unidades[0]["unidad_id"],
        "precio_referencia_compra": 3.00,
        "precio_venta": 5.50,
        "precio_venta_minimo": 4.00,
        "stock_actual": 30,
        "stock_minimo": 5,
        "stock_maximo": 100,
        "aplica_iva_compra": 1,
    })
    test("Crear producto", producto is not None and producto["stock_actual"] == 30)

    # Precio negativo
    try:
        svc.crear_producto({
            "codigo_barras": "SVC-BAD", "nombre": "Bad",
            "categoria_id": categorias[0]["categoria_id"],
            "unidad_id": unidades[0]["unidad_id"],
            "precio_venta": -1.00,
        })
        test("Precio negativo rechazado", False)
    except ValueError:
        test("Precio negativo rechazado", True)

    # Cálculos
    con_iva = svc.calcular_precio_con_iva(10.00)
    test("Cálculo precio con IVA (10 → 11.50)", con_iva == 11.50)

    margen = svc.calcular_margen(3.00, 5.50)
    test("Cálculo margen ganancia", margen > 80)

    sugerido = svc.sugerir_precio_venta(3.00, 30)
    test("Precio sugerido (costo 3 + 30%)", sugerido == 3.90)

    return producto, marca


# ══════════════════════════════════════════════════
# TEST 2: PROVEEDORES VÍA SERVICIO
# ══════════════════════════════════════════════════

def test_02_proveedor(producto):
    print("\n" + "=" * 60)
    print("TEST 2: SERVICIO DE PROVEEDORES")
    print("=" * 60)

    svc = ProveedorService()

    prov = svc.crear({
        "ruc_cedula": "0990001111",
        "razon_social": "Distribuidora SVC Test",
        "tipo_credito": "CREDITO_60",
        "plazo_credito_dias": 60,
        "frecuencia_pedido": "QUINCENAL",
    })
    test("Crear proveedor", prov is not None)

    # Duplicado
    try:
        svc.crear({"ruc_cedula": "0990001111", "razon_social": "Dup"})
        test("RUC duplicado rechazado", False)
    except ValueError:
        test("RUC duplicado rechazado", True)

    # Asignar producto
    pp = svc.asignar_producto({
        "proveedor_id": prov["proveedor_id"],
        "producto_id": producto["producto_id"],
        "precio_compra": 3.00,
        "precio_compra_con_iva": 3.45,
        "incluye_iva": 1,
        "es_proveedor_principal": 1,
    })
    test("Asignar producto a proveedor", pp is not None)

    ppal = svc.get_proveedor_principal(producto["producto_id"])
    test("Obtener proveedor principal", ppal is not None)

    # Precio referencia
    pr = svc.registrar_precio_referencia({
        "producto_id": producto["producto_id"],
        "origen": "SUPERMERCADO",
        "nombre_comercio": "Mi Comisariato",
        "precio": 6.50,
        "fecha_consulta": "2026-03-01",
    })
    test("Registrar precio referencia", pr is not None)

    comp = svc.get_comparativo_precios(producto["producto_id"])
    test("Comparativo de precios", len(comp) >= 2)

    return prov


# ══════════════════════════════════════════════════
# TEST 3: CLIENTES VÍA SERVICIO
# ══════════════════════════════════════════════════

def test_03_cliente():
    print("\n" + "=" * 60)
    print("TEST 3: SERVICIO DE CLIENTES")
    print("=" * 60)

    svc = ClienteService()

    cli = svc.crear({
        "cedula": "1700001111",
        "nombres": "Ana",
        "apellidos": "Gómez Test",
        "telefono": "0991112222",
        "habilitado_credito": 1,
        "limite_credito": 50.00,
        "saldo_pendiente": 0.00,
        "frecuencia_pago": "QUINCENAL",
    })
    test("Crear cliente", cli is not None)

    puede, msg = svc.puede_recibir_credito(cli["cliente_id"], 30.00)
    test("Validar crédito disponible OK", puede)

    puede2, msg2 = svc.puede_recibir_credito(cli["cliente_id"], 60.00)
    test("Validar crédito insuficiente", not puede2)

    # Sin crédito habilitado
    cli2 = svc.crear({
        "cedula": "1700002222", "nombres": "Pedro", "apellidos": "Sin Crédito",
        "habilitado_credito": 0,
    })
    puede3, _ = svc.puede_recibir_credito(cli2["cliente_id"], 5.00)
    test("Cliente sin crédito rechazado", not puede3)

    return cli


# ══════════════════════════════════════════════════
# TEST 4: TX-01 REGISTRAR COMPRA (SERVICIO)
# ══════════════════════════════════════════════════

def test_04_compra(producto, proveedor):
    print("\n" + "=" * 60)
    print("TEST 4: TX-01 REGISTRAR COMPRA (SERVICIO)")
    print("=" * 60)

    svc = CompraService()
    prod_model = ProductoModel()

    stock_antes = prod_model.get_by_id(producto["producto_id"])["stock_actual"]

    compra = svc.registrar_compra(
        cabecera={
            "numero_factura": "FAC-SVC-001",
            "proveedor_id": proveedor["proveedor_id"],
            "fecha_compra": "2026-03-10",
            "tipo_pago": "CREDITO",
            "plazo_credito_dias": 60,
        },
        items=[{
            "producto_id": producto["producto_id"],
            "cantidad": 12,
            "precio_unitario": 3.45,
            "incluye_iva": 1,
        }],
        usuario_id=1
    )

    test("TX-01: Compra registrada", compra is not None and compra["total"] > 0)
    test("TX-01: Estado REGISTRADA", compra["estado"] == "REGISTRADA")

    prod_despues = prod_model.get_by_id(producto["producto_id"])
    test("TX-01: Stock incrementado en 12",
         prod_despues["stock_actual"] == stock_antes + 12,
         f"Esperado {stock_antes + 12}, real {prod_despues['stock_actual']}")

    # Cuenta por pagar creada (es crédito)
    cp = CuentaPagarModel().get_by_compra(compra["compra_id"])
    test("TX-01: Cuenta por pagar creada", cp is not None and cp["saldo_pendiente"] > 0)

    # Movimientos de inventario
    movs = MovimientoInventarioModel().get_by_documento("COMPRA", compra["compra_id"])
    test("TX-01: Movimiento ENTRADA registrado", len(movs) == 1 and movs[0]["tipo_movimiento"] == "ENTRADA")

    # Factura duplicada
    try:
        svc.registrar_compra(
            cabecera={"numero_factura": "FAC-SVC-001", "proveedor_id": proveedor["proveedor_id"],
                      "fecha_compra": "2026-03-10", "tipo_pago": "CONTADO"},
            items=[{"producto_id": producto["producto_id"], "cantidad": 1, "precio_unitario": 3.00, "incluye_iva": 0}]
        )
        test("TX-01: Factura duplicada rechazada", False)
    except ValueError:
        test("TX-01: Factura duplicada rechazada", True)

    return compra


# ══════════════════════════════════════════════════
# TEST 5: TX-02 REGISTRAR VENTA (SERVICIO)
# ══════════════════════════════════════════════════

def test_05_venta(producto, cliente):
    print("\n" + "=" * 60)
    print("TEST 5: TX-02 REGISTRAR VENTA (SERVICIO)")
    print("=" * 60)

    svc = VentaService()
    prod_model = ProductoModel()

    stock_antes = prod_model.get_by_id(producto["producto_id"])["stock_actual"]

    # Venta al contado
    venta_ef = svc.registrar_venta(
        cabecera={
            "metodo_pago": "EFECTIVO",
            "monto_recibido": 20.00,
            "es_credito": 0,
        },
        items=[{
            "producto_id": producto["producto_id"],
            "cantidad": 3,
        }],
        usuario_id=1
    )
    test("TX-02: Venta efectivo registrada", venta_ef is not None)
    test("TX-02: Total calculado",
         venta_ef["total"] == round(5.50 * 3, 2),
         f"Esperado {5.50 * 3}, real {venta_ef['total']}")
    test("TX-02: Cambio calculado",
         venta_ef["cambio"] == round(20.00 - 5.50 * 3, 2))

    prod_post = prod_model.get_by_id(producto["producto_id"])
    test("TX-02: Stock descontado en 3",
         prod_post["stock_actual"] == stock_antes - 3)

    # Comprobante emitido (> $3.00)
    test("TX-02: Comprobante emitido (> $3)", venta_ef["comprobante_emitido"] == 1)

    # Venta a crédito (fiado)
    stock_antes2 = prod_model.get_by_id(producto["producto_id"])["stock_actual"]
    venta_cr = svc.registrar_venta(
        cabecera={
            "cliente_id": cliente["cliente_id"],
            "metodo_pago": "CREDITO",
            "es_credito": 1,
        },
        items=[{
            "producto_id": producto["producto_id"],
            "cantidad": 2,
        }],
        usuario_id=1
    )
    test("TX-02: Venta crédito registrada", venta_cr is not None)

    cc = CuentaCobrarModel().get_by_venta(venta_cr["venta_id"])
    test("TX-02: Cuenta por cobrar creada", cc is not None and cc["saldo_pendiente"] == venta_cr["total"])

    cli_post = ClienteModel().get_by_id(cliente["cliente_id"])
    test("TX-02: Saldo cliente actualizado", cli_post["saldo_pendiente"] == venta_cr["total"])

    # Stock insuficiente
    try:
        svc.registrar_venta(
            cabecera={"metodo_pago": "EFECTIVO", "monto_recibido": 9999, "es_credito": 0},
            items=[{"producto_id": producto["producto_id"], "cantidad": 99999}]
        )
        test("TX-02: Stock insuficiente rechazado", False)
    except ValueError:
        test("TX-02: Stock insuficiente rechazado", True)

    # Crédito sin cliente
    try:
        svc.registrar_venta(
            cabecera={"metodo_pago": "CREDITO", "es_credito": 1},
            items=[{"producto_id": producto["producto_id"], "cantidad": 1}]
        )
        test("TX-02: Crédito sin cliente rechazado", False)
    except ValueError:
        test("TX-02: Crédito sin cliente rechazado", True)

    return venta_ef, venta_cr


# ══════════════════════════════════════════════════
# TEST 6: TX-03 PAGO DE CLIENTE (SERVICIO)
# ══════════════════════════════════════════════════

def test_06_cobro(cliente, venta_credito):
    print("\n" + "=" * 60)
    print("TEST 6: TX-03 PAGO DE CLIENTE (SERVICIO)")
    print("=" * 60)

    svc = CobroService()
    cc = CuentaCobrarModel().get_by_venta(venta_credito["venta_id"])
    monto_original = cc["saldo_pendiente"]

    # Pago parcial
    pago1 = svc.registrar_pago(
        cuenta_cobrar_id=cc["cuenta_cobrar_id"],
        monto=5.00,
        metodo_pago="EFECTIVO",
        fecha_pago="2026-03-15"
    )
    test("TX-03: Pago parcial registrado", pago1 is not None)

    cc_post = svc.get_cuenta(cc["cuenta_cobrar_id"])
    saldo_esperado = round(monto_original - 5.00, 2)
    test("TX-03: Saldo actualizado", cc_post["saldo_pendiente"] == saldo_esperado,
         f"Esperado {saldo_esperado}, real {cc_post['saldo_pendiente']}")
    test("TX-03: Estado PARCIAL", cc_post["estado_pago"] == "PARCIAL")

    # Pago total (el resto)
    pago2 = svc.registrar_pago(
        cuenta_cobrar_id=cc["cuenta_cobrar_id"],
        monto=saldo_esperado,
        metodo_pago="TRANSFERENCIA",
        fecha_pago="2026-03-20",
        referencia="TRF-001"
    )
    test("TX-03: Pago total registrado", pago2 is not None)

    cc_post2 = svc.get_cuenta(cc["cuenta_cobrar_id"])
    test("TX-03: Saldo cero", cc_post2["saldo_pendiente"] == 0)
    test("TX-03: Estado PAGADO", cc_post2["estado_pago"] == "PAGADO")

    cli = ClienteModel().get_by_id(cliente["cliente_id"])
    test("TX-03: Saldo cliente cero", cli["saldo_pendiente"] == 0)

    # Pagar cuenta ya pagada
    try:
        svc.registrar_pago(cc["cuenta_cobrar_id"], 1.00, "EFECTIVO", "2026-03-21")
        test("TX-03: Pago en cuenta pagada rechazado", False)
    except ValueError:
        test("TX-03: Pago en cuenta pagada rechazado", True)

    # Resumen del cliente
    resumen = svc.get_resumen_cliente(cliente["cliente_id"])
    test("TX-03: Resumen cliente disponible", resumen is not None)


# ══════════════════════════════════════════════════
# TEST 7: TX-04 PAGO A PROVEEDOR (SERVICIO)
# ══════════════════════════════════════════════════

def test_07_pago_proveedor(compra):
    print("\n" + "=" * 60)
    print("TEST 7: TX-04 PAGO A PROVEEDOR (SERVICIO)")
    print("=" * 60)

    svc = PagoService()
    cp = CuentaPagarModel().get_by_compra(compra["compra_id"])
    monto_original = cp["saldo_pendiente"]

    # Pago parcial
    pago = svc.registrar_pago(
        cuenta_pagar_id=cp["cuenta_pagar_id"],
        monto=10.00,
        metodo_pago="EFECTIVO",
        fecha_pago="2026-03-18"
    )
    test("TX-04: Pago parcial registrado", pago is not None)

    cp_post = svc.get_cuenta(cp["cuenta_pagar_id"])
    test("TX-04: Saldo reducido", cp_post["saldo_pendiente"] == round(monto_original - 10.00, 2))
    test("TX-04: Estado PARCIAL", cp_post["estado_pago"] == "PARCIAL")

    # Pago excesivo
    try:
        svc.registrar_pago(cp["cuenta_pagar_id"], 99999, "EFECTIVO", "2026-03-19")
        test("TX-04: Pago excesivo rechazado", False)
    except ValueError:
        test("TX-04: Pago excesivo rechazado", True)


# ══════════════════════════════════════════════════
# TEST 8: TX-05 AJUSTE DE INVENTARIO (SERVICIO)
# ══════════════════════════════════════════════════

def test_08_ajuste(producto):
    print("\n" + "=" * 60)
    print("TEST 8: TX-05 AJUSTE DE INVENTARIO (SERVICIO)")
    print("=" * 60)

    svc = InventarioService()
    prod_model = ProductoModel()

    stock_antes = prod_model.get_by_id(producto["producto_id"])["stock_actual"]

    # Consumo personal (-2)
    ajuste = svc.registrar_ajuste(
        producto_id=producto["producto_id"],
        tipo_ajuste="CONSUMO_PERSONAL",
        cantidad=-2,
        motivo="Uso personal propietaria"
    )
    test("TX-05: Ajuste consumo personal", ajuste is not None)

    prod_post = prod_model.get_by_id(producto["producto_id"])
    test("TX-05: Stock reducido en 2", prod_post["stock_actual"] == stock_antes - 2)

    # Entrada manual (+5)
    stock_antes2 = prod_post["stock_actual"]
    ajuste2 = svc.registrar_ajuste(
        producto_id=producto["producto_id"],
        tipo_ajuste="ENTRADA_MANUAL",
        cantidad=5,
        motivo="Corrección de conteo"
    )
    test("TX-05: Ajuste entrada manual", ajuste2 is not None)

    prod_post2 = prod_model.get_by_id(producto["producto_id"])
    test("TX-05: Stock incrementado en 5", prod_post2["stock_actual"] == stock_antes2 + 5)

    # Stock insuficiente
    try:
        svc.registrar_ajuste(producto["producto_id"], "MERMA", -99999, "Test")
        test("TX-05: Stock insuficiente rechazado", False)
    except ValueError:
        test("TX-05: Stock insuficiente rechazado", True)

    # Cantidad cero
    try:
        svc.registrar_ajuste(producto["producto_id"], "CORRECCION", 0, "Test")
        test("TX-05: Cantidad cero rechazada", False)
    except ValueError:
        test("TX-05: Cantidad cero rechazada", True)

    # Alertas
    alertas = svc.get_alertas()
    test("TX-05: Alertas inventario", alertas is not None)


# ══════════════════════════════════════════════════
# TEST 9: TX-06 ANULAR VENTA (SERVICIO)
# ══════════════════════════════════════════════════

def test_09_anular_venta(venta_efectivo, producto):
    print("\n" + "=" * 60)
    print("TEST 9: TX-06 ANULAR VENTA (SERVICIO)")
    print("=" * 60)

    svc = VentaService()
    prod_model = ProductoModel()

    stock_antes = prod_model.get_by_id(producto["producto_id"])["stock_actual"]

    anulada = svc.anular_venta(venta_efectivo["venta_id"])
    test("TX-06: Venta anulada", anulada["estado"] == "ANULADA")

    prod_post = prod_model.get_by_id(producto["producto_id"])
    test("TX-06: Stock revertido (+3)",
         prod_post["stock_actual"] == stock_antes + 3)

    movs = MovimientoInventarioModel().get_by_documento("ANULACION", venta_efectivo["venta_id"])
    test("TX-06: Movimiento ANULACION registrado", len(movs) >= 1)

    # Anular de nuevo
    try:
        svc.anular_venta(venta_efectivo["venta_id"])
        test("TX-06: Re-anulación rechazada", False)
    except ValueError:
        test("TX-06: Re-anulación rechazada", True)


# ══════════════════════════════════════════════════
# TEST 10: TX-07 CIERRE DE CAJA (SERVICIO)
# ══════════════════════════════════════════════════

def test_10_cierre_caja():
    print("\n" + "=" * 60)
    print("TEST 10: TX-07 CIERRE DE CAJA (SERVICIO)")
    print("=" * 60)

    svc = CierreCajaService()

    # Vista previa
    preview = svc.preparar_cierre("2026-03-10")
    test("TX-07: Vista previa calculada", preview is not None)
    test("TX-07: Tiene campos necesarios",
         "efectivo_esperado" in preview and "total_ventas_general" in preview)

    # Cerrar caja
    cierre = svc.cerrar_caja(
        efectivo_real=preview["efectivo_esperado"],
        fecha="2026-03-10",
        observaciones="Cierre de prueba",
    )
    test("TX-07: Cierre registrado", cierre is not None)
    test("TX-07: Diferencia = 0 (cuadra)", cierre["diferencia"] == 0)

    # Cierre duplicado
    try:
        svc.cerrar_caja(0, fecha="2026-03-10")
        test("TX-07: Cierre duplicado rechazado", False)
    except ValueError:
        test("TX-07: Cierre duplicado rechazado", True)


# ══════════════════════════════════════════════════
# TEST 11: TX-08 ANULAR COMPRA (SERVICIO)
# ══════════════════════════════════════════════════

def test_11_anular_compra(compra, producto):
    print("\n" + "=" * 60)
    print("TEST 11: TX-08 ANULAR COMPRA (SERVICIO)")
    print("=" * 60)

    svc = CompraService()
    prod_model = ProductoModel()

    stock_antes = prod_model.get_by_id(producto["producto_id"])["stock_actual"]

    anulada = svc.anular_compra(compra["compra_id"])
    test("TX-08: Compra anulada", anulada["estado"] == "ANULADA")

    prod_post = prod_model.get_by_id(producto["producto_id"])
    test("TX-08: Stock revertido (-12)",
         prod_post["stock_actual"] == stock_antes - 12)

    cp = CuentaPagarModel().get_by_compra(compra["compra_id"])
    test("TX-08: Cuenta por pagar anulada", cp["estado"] == "INA")

    movs = MovimientoInventarioModel().get_by_documento("ANULACION", compra["compra_id"])
    test("TX-08: Movimiento ANULACION registrado", len(movs) >= 1)

    # Re-anulación
    try:
        svc.anular_compra(compra["compra_id"])
        test("TX-08: Re-anulación rechazada", False)
    except ValueError:
        test("TX-08: Re-anulación rechazada", True)


# ══════════════════════════════════════════════════
# TEST 12: GASTOS OPERATIVOS
# ══════════════════════════════════════════════════

def test_12_gastos():
    print("\n" + "=" * 60)
    print("TEST 12: SERVICIO DE GASTOS OPERATIVOS")
    print("=" * 60)

    svc = GastoService()

    gasto = svc.registrar({
        "tipo_gasto": "ARRIENDO",
        "descripcion": "Arriendo local marzo",
        "monto": 200.00,
        "fecha_gasto": "2026-03-01",
        "metodo_pago": "TRANSFERENCIA",
    })
    test("Gasto registrado", gasto is not None and gasto["monto"] == 200.00)

    gasto2 = svc.registrar({
        "tipo_gasto": "TRANSPORTE",
        "descripcion": "Bus productos",
        "monto": 5.50,
        "fecha_gasto": "2026-03-10",
        "metodo_pago": "EFECTIVO",
    })
    test("Segundo gasto registrado", gasto2 is not None)

    total = svc.get_total_periodo("2026-03-01", "2026-03-31")
    test("Total gastos marzo", total == 205.50, f"Real: {total}")

    # Monto cero
    try:
        svc.registrar({"tipo_gasto": "OTROS", "descripcion": "Bad", "monto": 0,
                        "fecha_gasto": "2026-03-10", "metodo_pago": "EFECTIVO"})
        test("Gasto monto cero rechazado", False)
    except ValueError:
        test("Gasto monto cero rechazado", True)


# ══════════════════════════════════════════════════
# TEST 13: REPORTES Y DASHBOARD
# ══════════════════════════════════════════════════

def test_13_reportes():
    print("\n" + "=" * 60)
    print("TEST 13: SERVICIO DE REPORTES Y DASHBOARD")
    print("=" * 60)

    svc = ReporteService()

    dash = svc.get_dashboard()
    test("Dashboard generado", dash is not None)
    test("Dashboard tiene ventas_hoy", "ventas_hoy" in dash)
    test("Dashboard tiene valor_inventario", "valor_inventario_costo" in dash)

    rv = svc.reporte_ventas_periodo("2026-03-01", "2026-03-31")
    test("Reporte ventas período", rv is not None and "total_ventas" in rv)

    rc = svc.reporte_compras_periodo("2026-03-01", "2026-03-31")
    test("Reporte compras período", rc is not None)

    rg = svc.reporte_gastos_periodo("2026-03-01", "2026-03-31")
    test("Reporte gastos período", rg is not None and rg["total_gastos"] == 205.50)

    ru = svc.reporte_utilidad_periodo("2026-03-01", "2026-03-31")
    test("Reporte utilidad", ru is not None and "utilidad_neta" in ru)
    test("Utilidad neta calculada", isinstance(ru["utilidad_neta"], (int, float)))

    ri = svc.reporte_inventario()
    test("Reporte inventario", ri is not None)

    rcc = svc.reporte_cuentas_cobrar()
    test("Reporte cuentas cobrar", rcc is not None)

    rcp = svc.reporte_cuentas_pagar()
    test("Reporte cuentas pagar", rcp is not None)


# ══════════════════════════════════════════════════
# TEST 14: AUDITORÍA
# ══════════════════════════════════════════════════

def test_14_auditoria():
    print("\n" + "=" * 60)
    print("TEST 14: SERVICIO DE AUDITORÍA")
    print("=" * 60)

    svc = AuditoriaService()

    registros = svc.get_todos(200)
    test("Auditoría tiene registros", len(registros) > 0)
    test(f"Total registros auditoría: {len(registros)}", True)

    por_tabla = svc.get_por_tabla("compra")
    test("Auditoría filtrada por tabla", len(por_tabla) > 0)


# ══════════════════════════════════════════════════
# TEST 15: USUARIOS
# ══════════════════════════════════════════════════

def test_15_usuarios():
    print("\n" + "=" * 60)
    print("TEST 15: SERVICIO DE USUARIOS")
    print("=" * 60)

    svc = UsuarioService()

    # Crear usuario
    usr = svc.crear({
        "nombre_completo": "Operadora Test",
        "email": "oper@milburbujas.local",
        "contrasena": "test123",
        "rol": "OPERADOR",
    })
    test("Crear usuario", usr is not None)

    # Autenticar
    auth = svc.autenticar("oper@milburbujas.local", "test123")
    test("Autenticación correcta", auth is not None)

    auth_bad = svc.autenticar("oper@milburbujas.local", "mala")
    test("Autenticación incorrecta rechazada", auth_bad is None)

    # Cambiar contraseña
    ok = svc.cambiar_contrasena(usr["usuario_id"], "test123", "nueva456")
    test("Cambiar contraseña", ok)

    auth2 = svc.autenticar("oper@milburbujas.local", "nueva456")
    test("Autenticar con nueva contraseña", auth2 is not None)

    # Email duplicado
    try:
        svc.crear({"nombre_completo": "Dup", "email": "oper@milburbujas.local", "contrasena": "x"})
        test("Email duplicado rechazado", False)
    except ValueError:
        test("Email duplicado rechazado", True)


# ══════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════

def main():
    global passed, failed, total

    print("\n" + "🔧" * 30)
    print("  Mil Burbujas - VERIFICACIÓN FASE 2 (SERVICIOS)")
    print("🔧" * 30)

    limpiar_db()

    producto, marca = test_01_catalogo()
    proveedor = test_02_proveedor(producto)
    cliente = test_03_cliente()
    compra = test_04_compra(producto, proveedor)
    venta_ef, venta_cr = test_05_venta(producto, cliente)
    test_06_cobro(cliente, venta_cr)
    test_07_pago_proveedor(compra)
    test_08_ajuste(producto)
    test_09_anular_venta(venta_ef, producto)
    test_10_cierre_caja()
    test_11_anular_compra(compra, producto)
    test_12_gastos()
    test_13_reportes()
    test_14_auditoria()
    test_15_usuarios()

    # Resumen
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE VERIFICACIÓN - FASE 2")
    print("=" * 60)
    print(f"  Total de tests:  {total}")
    print(f"  ✅ Pasaron:       {passed}")
    print(f"  ❌ Fallaron:      {failed}")
    print(f"  Porcentaje:      {(passed / total * 100) if total > 0 else 0:.1f}%")

    if failed == 0:
        print("\n  🎉 FASE 2 COMPLETADA - SERVICIOS CONGELADOS")
        print("  👉 Puedes proceder a la FASE 3 (Pruebas)")
    else:
        print(f"\n  ⚠️  Hay {failed} test(s) fallido(s). Revisar antes de continuar.")

    print("=" * 60)

    DatabaseConnection().close()
    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
