# -*- coding: utf-8 -*-
"""
Mil Burbujas - Fase 3 · Test 3/3: REGLAS DE NEGOCIO
Verifica que todas las reglas de negocio del RISE, IVA, comprobantes,
secuencias, soft-delete, auditoría y cálculos financieros estén correctas.
"""
import os, sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import DB_DIR, IVA_PORCENTAJE, MONTO_MINIMO_COMPROBANTE
from database.connection import DatabaseConnection

from services.catalogo_service import CatalogoService
from services.proveedor_service import ProveedorService
from services.cliente_service import ClienteService
from services.compra_service import CompraService
from services.venta_service import VentaService
from services.cobro_service import CobroService
from services.pago_service import PagoService
from services.inventario_service import InventarioService
from services.gasto_service import GastoService
from services.reporte_service import ReporteService
from services.auditoria_service import AuditoriaService
from services.cierre_caja_service import CierreCajaService

from models.producto import ProductoModel
from models.cliente import ClienteModel
from models.compra import CompraModel
from models.compra_detalle import CompraDetalleModel
from models.venta import VentaModel
from models.venta_detalle import VentaDetalleModel
from models.cuenta_cobrar import CuentaCobrarModel
from models.cuenta_pagar import CuentaPagarModel
from models.movimiento_inventario import MovimientoInventarioModel
from models.configuracion import ConfiguracionModel

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


def crear_producto(cat_svc, codigo, nombre, precio_venta=10.00, stock=50,
                   precio_compra=5.00, aplica_iva=1):
    cats = cat_svc.get_categorias_raiz()
    unds = cat_svc.get_unidades()
    return cat_svc.crear_producto({
        "codigo_barras": codigo, "nombre": nombre,
        "categoria_id": cats[0]["categoria_id"],
        "unidad_id": unds[0]["unidad_id"],
        "precio_referencia_compra": precio_compra,
        "precio_venta": precio_venta,
        "precio_venta_minimo": round(precio_venta * 0.7, 2),
        "stock_actual": stock, "stock_minimo": 5, "stock_maximo": 500,
        "aplica_iva_compra": aplica_iva,
    })


# ══════════════════════════════════════════════════════════════════
# REGLA 1: IVA ECUADOR 15% EN COMPRAS
# ══════════════════════════════════════════════════════════════════

def test_01_iva_compras():
    print("\n" + "=" * 60)
    print("REGLA 1: IVA ECUADOR 15% EN COMPRAS")
    print("=" * 60)

    test(f"Configuración IVA = {IVA_PORCENTAJE}%", IVA_PORCENTAJE == 15)

    cat_svc = CatalogoService()
    prov_svc = ProveedorService()
    compra_svc = CompraService()

    prod = crear_producto(cat_svc, "IVA-001", "Producto IVA Test")
    prov = prov_svc.crear({"ruc_cedula": "1301010101", "razon_social": "Prov IVA Test"})

    # ── Caso A: precio CON IVA (incluye_iva=1) ──
    # Precio unitario $11.50 con IVA → sin IVA = 11.50 / 1.15 = 10.00
    compra_a = compra_svc.registrar_compra(
        cabecera={"numero_factura": "IVA-A-001", "proveedor_id": prov["proveedor_id"],
                  "fecha_compra": "2026-03-10", "tipo_pago": "CONTADO"},
        items=[{"producto_id": prod["producto_id"], "cantidad": 10,
                "precio_unitario": 11.50, "incluye_iva": 1}]
    )
    # subtotal_sin_iva ≈ 10.00 * 10 = 100.00, iva ≈ 15.00, total ≈ 115.00
    test("IVA Caso A: Total = subtotal + iva",
         abs(compra_a["total"] - (compra_a["subtotal_sin_iva"] + compra_a["monto_iva"])) < 0.02,
         f"Total={compra_a['total']}, Sub={compra_a['subtotal_sin_iva']}, IVA={compra_a['monto_iva']}")

    iva_pct_real = round(compra_a["monto_iva"] / compra_a["subtotal_sin_iva"] * 100, 0)
    test("IVA Caso A: Porcentaje ≈ 15%", iva_pct_real == 15.0,
         f"Real: {iva_pct_real}%")

    # ── Caso B: precio SIN IVA (incluye_iva=0) ──
    prod2 = crear_producto(cat_svc, "IVA-002", "Producto sin IVA", aplica_iva=0)
    compra_b = compra_svc.registrar_compra(
        cabecera={"numero_factura": "IVA-B-001", "proveedor_id": prov["proveedor_id"],
                  "fecha_compra": "2026-03-10", "tipo_pago": "CONTADO"},
        items=[{"producto_id": prod2["producto_id"], "cantidad": 10,
                "precio_unitario": 10.00, "incluye_iva": 0}]
    )
    test("IVA Caso B: Subtotal sin IVA = $100", compra_b["subtotal_sin_iva"] == 100.00)
    test("IVA Caso B: IVA = $15", compra_b["monto_iva"] == 15.00)
    test("IVA Caso B: Total = $115", compra_b["total"] == 115.00)

    # ── Cálculos del servicio de catálogo ──
    con_iva = cat_svc.calcular_precio_con_iva(100.00)
    test("Calc: $100 + 15% = $115", con_iva == 115.00)

    sin_iva = cat_svc.calcular_precio_sin_iva(115.00)
    test("Calc: $115 / 1.15 = $100", sin_iva == 100.00)

    con_iva2 = cat_svc.calcular_precio_con_iva(3.50)
    test("Calc: $3.50 + 15% = $4.02", con_iva2 == 4.02, f"Real: {con_iva2}")


# ══════════════════════════════════════════════════════════════════
# REGLA 2: RISE — NO SE COBRA IVA EN VENTAS
# ══════════════════════════════════════════════════════════════════

def test_02_rise_ventas():
    print("\n" + "=" * 60)
    print("REGLA 2: RISE — VENTAS SIN IVA AL CLIENTE")
    print("=" * 60)

    cat_svc = CatalogoService()
    venta_svc = VentaService()

    prod = crear_producto(cat_svc, "RISE-001", "Prod RISE Test", precio_venta=10.00, stock=100)

    # Venta: precio directo sin IVA al consumidor (RISE)
    v = venta_svc.registrar_venta(
        cabecera={"metodo_pago": "EFECTIVO", "monto_recibido": 50, "es_credito": 0},
        items=[{"producto_id": prod["producto_id"], "cantidad": 3}]
    )
    test("RISE: Total = precio * cantidad (sin IVA)",
         v["total"] == 30.00,
         f"Total={v['total']}, Esperado=30.00")

    # Verificar detalle: precio = precio_venta del catálogo
    detalles = VentaDetalleModel().get_by_venta(v["venta_id"])
    test("RISE: Detalle precio = catálogo", detalles[0]["precio_unitario"] == 10.00)

    # No hay campo monto_iva en ventas (régimen RISE no cobra IVA)
    test("RISE: Venta sin campo IVA",
         "monto_iva" not in v or v.get("monto_iva", 0) == 0 or v.get("monto_iva") is None, True)


# ══════════════════════════════════════════════════════════════════
# REGLA 3: COMPROBANTE OBLIGATORIO > $3.00
# ══════════════════════════════════════════════════════════════════

def test_03_comprobante():
    print("\n" + "=" * 60)
    print("REGLA 3: COMPROBANTE OBLIGATORIO > $3.00")
    print("=" * 60)

    test(f"Config MONTO_MINIMO_COMPROBANTE = ${MONTO_MINIMO_COMPROBANTE}",
         MONTO_MINIMO_COMPROBANTE == 3.00)

    cat_svc = CatalogoService()
    venta_svc = VentaService()

    prod_barato = crear_producto(cat_svc, "COMP-001", "Jabón Barato", 1.50, 100, precio_compra=1.00)
    prod_caro = crear_producto(cat_svc, "COMP-002", "Crema Cara", 5.00, 100, precio_compra=3.00)

    # ── Venta < $3.00 → sin comprobante ──
    v_baja = venta_svc.registrar_venta(
        cabecera={"metodo_pago": "EFECTIVO", "monto_recibido": 5, "es_credito": 0},
        items=[{"producto_id": prod_barato["producto_id"], "cantidad": 1}]
    )
    test("Venta $1.50 → sin comprobante", v_baja["comprobante_emitido"] == 0)

    # ── Venta = $3.00 → CON comprobante ──
    v_justo = venta_svc.registrar_venta(
        cabecera={"metodo_pago": "EFECTIVO", "monto_recibido": 5, "es_credito": 0},
        items=[{"producto_id": prod_barato["producto_id"], "cantidad": 2}]
    )
    test("Venta $3.00 → CON comprobante", v_justo["comprobante_emitido"] == 1,
         f"Total={v_justo['total']}, Emitido={v_justo['comprobante_emitido']}")

    # ── Venta > $3.00 → CON comprobante ──
    v_alta = venta_svc.registrar_venta(
        cabecera={"metodo_pago": "EFECTIVO", "monto_recibido": 10, "es_credito": 0},
        items=[{"producto_id": prod_caro["producto_id"], "cantidad": 1}]
    )
    test("Venta $5.00 → CON comprobante", v_alta["comprobante_emitido"] == 1)


# ══════════════════════════════════════════════════════════════════
# REGLA 4: SECUENCIAS AUTONUMÉRICAS
# ══════════════════════════════════════════════════════════════════

def test_04_secuencias():
    print("\n" + "=" * 60)
    print("REGLA 4: SECUENCIAS AUTONUMÉRICAS")
    print("=" * 60)

    config = ConfiguracionModel()
    venta_svc = VentaService()
    cat_svc = CatalogoService()

    prod = crear_producto(cat_svc, "SEQ-001", "Prod Secuencia", 10.00, 200)

    # Obtener secuencia actual
    seq_antes = config.get_valor("SECUENCIA_COMPROBANTE")
    test("Secuencia comprobante existe", seq_antes is not None)

    # Registrar 3 ventas y verificar que secuencia crece
    v1 = venta_svc.registrar_venta(
        cabecera={"metodo_pago": "EFECTIVO", "monto_recibido": 50, "es_credito": 0},
        items=[{"producto_id": prod["producto_id"], "cantidad": 1}]
    )
    v2 = venta_svc.registrar_venta(
        cabecera={"metodo_pago": "EFECTIVO", "monto_recibido": 50, "es_credito": 0},
        items=[{"producto_id": prod["producto_id"], "cantidad": 1}]
    )
    v3 = venta_svc.registrar_venta(
        cabecera={"metodo_pago": "EFECTIVO", "monto_recibido": 50, "es_credito": 0},
        items=[{"producto_id": prod["producto_id"], "cantidad": 1}]
    )

    # Comprobantes deben ser secuenciales
    nums = [v1["numero_comprobante"], v2["numero_comprobante"], v3["numero_comprobante"]]
    test("3 comprobantes distintos", len(set(nums)) == 3)

    # Extraer números y verificar orden
    seq_nums = [int(n.split("-")[1]) for n in nums]
    test("Secuencia creciente", seq_nums == sorted(seq_nums) and seq_nums[-1] > seq_nums[0])

    seq_despues = config.get_valor("SECUENCIA_COMPROBANTE")
    test("Secuencia incrementó en config", int(seq_despues) > int(seq_antes))


# ══════════════════════════════════════════════════════════════════
# REGLA 5: SOFT-DELETE (ACT/INA)
# ══════════════════════════════════════════════════════════════════

def test_05_soft_delete():
    print("\n" + "=" * 60)
    print("REGLA 5: SOFT-DELETE (ACT/INA)")
    print("=" * 60)

    cat_svc = CatalogoService()
    cli_svc = ClienteService()

    # ── Producto: desactivar ──
    prod = crear_producto(cat_svc, "SD-001", "Prod Soft Delete", 10.00, 0)
    test("Producto creado con estado ACT", prod["estado"] == "ACT")

    cat_svc.desactivar_producto(prod["producto_id"])
    p = ProductoModel().get_by_id(prod["producto_id"])
    test("Producto desactivado → INA", p["estado"] == "INA")

    # El producto sigue existiendo (no se borró)
    test("Producto sigue en BD", p is not None)

    # ── Cliente: desactivar ──
    cli = cli_svc.crear({"cedula": "8888888888", "nombres": "Soft", "apellidos": "Delete"})
    test("Cliente creado ACT", cli["estado"] == "ACT")

    cli_svc.desactivar(cli["cliente_id"])
    c = ClienteModel().get_by_id(cli["cliente_id"])
    test("Cliente desactivado → INA", c["estado"] == "INA")
    test("Cliente sigue en BD", c is not None)


# ══════════════════════════════════════════════════════════════════
# REGLA 6: INTEGRIDAD STOCK (entrada = salida + actual)
# ══════════════════════════════════════════════════════════════════

def test_06_integridad_stock():
    print("\n" + "=" * 60)
    print("REGLA 6: INTEGRIDAD DEL STOCK")
    print("=" * 60)

    cat_svc = CatalogoService()
    venta_svc = VentaService()
    compra_svc = CompraService()
    inv_svc = InventarioService()
    prov_svc = ProveedorService()
    prod_model = ProductoModel()

    prod = crear_producto(cat_svc, "STK-INT-001", "Stock Integridad", 10.00, 100)
    prov = prov_svc.crear({"ruc_cedula": "1401010101", "razon_social": "Prov Stock Int"})

    stock_ini = 100

    # +30 compra
    compra_svc.registrar_compra(
        cabecera={"numero_factura": "STK-C01", "proveedor_id": prov["proveedor_id"],
                  "fecha_compra": "2026-03-10", "tipo_pago": "CONTADO"},
        items=[{"producto_id": prod["producto_id"], "cantidad": 30,
                "precio_unitario": 5.00, "incluye_iva": 0}]
    )

    # -15 venta
    venta_svc.registrar_venta(
        cabecera={"metodo_pago": "EFECTIVO", "monto_recibido": 200, "es_credito": 0},
        items=[{"producto_id": prod["producto_id"], "cantidad": 15}]
    )

    # -3 consumo personal
    inv_svc.registrar_ajuste(prod["producto_id"], "CONSUMO_PERSONAL", -3, "Uso personal")

    # +5 entrada manual
    inv_svc.registrar_ajuste(prod["producto_id"], "ENTRADA_MANUAL", 5, "Corrección")

    # -2 daño
    inv_svc.registrar_ajuste(prod["producto_id"], "DANIO", -2, "Envase roto")

    # Cálculo esperado: 100 + 30 - 15 - 3 + 5 - 2 = 115
    esperado = stock_ini + 30 - 15 - 3 + 5 - 2
    p = prod_model.get_by_id(prod["producto_id"])
    test(f"Stock final = {esperado}", p["stock_actual"] == esperado,
         f"Real: {p['stock_actual']}")

    # Verificar consistencia con movimientos
    movs = MovimientoInventarioModel().get_by_producto(prod["producto_id"], 100)
    entradas = sum(m["cantidad"] for m in movs if m["tipo_movimiento"] == "ENTRADA")
    salidas = sum(m["cantidad"] for m in movs if m["tipo_movimiento"] == "SALIDA")
    stock_calc = stock_ini + entradas - salidas
    test(f"Stock = ini({stock_ini}) + entradas({entradas}) - salidas({salidas})",
         stock_calc == p["stock_actual"],
         f"Calculado: {stock_calc}, Real: {p['stock_actual']}")


# ══════════════════════════════════════════════════════════════════
# REGLA 7: CUENTAS POR COBRAR — CICLO COMPLETO
# ══════════════════════════════════════════════════════════════════

def test_07_cuentas_cobrar_ciclo():
    print("\n" + "=" * 60)
    print("REGLA 7: CUENTAS POR COBRAR — CICLO COMPLETO")
    print("=" * 60)

    cat_svc = CatalogoService()
    cli_svc = ClienteService()
    venta_svc = VentaService()
    cobro_svc = CobroService()

    prod = crear_producto(cat_svc, "CXC-001", "Prod CxC", 20.00, 100)
    cli = cli_svc.crear({
        "cedula": "1501010101", "nombres": "Test", "apellidos": "CxC",
        "habilitado_credito": 1, "limite_credito": 200.00, "saldo_pendiente": 0.00,
    })

    # Venta a crédito
    v = venta_svc.registrar_venta(
        cabecera={"cliente_id": cli["cliente_id"], "metodo_pago": "CREDITO", "es_credito": 1},
        items=[{"producto_id": prod["producto_id"], "cantidad": 5}]  # $100
    )
    test("CxC: Venta crédito $100", v["total"] == 100.00)

    cc = CuentaCobrarModel().get_by_venta(v["venta_id"])
    test("CxC: Cuenta creada", cc is not None)
    test("CxC: Monto original = $100", cc["monto_original"] == 100.00)
    test("CxC: Saldo pendiente = $100", cc["saldo_pendiente"] == 100.00)
    test("CxC: Estado PENDIENTE", cc["estado_pago"] == "PENDIENTE")
    test("CxC: Tiene fecha vencimiento", cc["fecha_vencimiento"] is not None)

    # Pago parcial $30
    cobro_svc.registrar_pago(cc["cuenta_cobrar_id"], 30.00, "EFECTIVO", "2026-03-15")
    cc = CuentaCobrarModel().get_by_id(cc["cuenta_cobrar_id"])
    test("CxC: Saldo tras $30 = $70", cc["saldo_pendiente"] == 70.00)
    test("CxC: Estado PARCIAL", cc["estado_pago"] == "PARCIAL")

    # Pago parcial $50
    cobro_svc.registrar_pago(cc["cuenta_cobrar_id"], 50.00, "TRANSFERENCIA", "2026-03-20")
    cc = CuentaCobrarModel().get_by_id(cc["cuenta_cobrar_id"])
    test("CxC: Saldo tras $50 más = $20", cc["saldo_pendiente"] == 20.00)

    # Pago final $20
    cobro_svc.registrar_pago(cc["cuenta_cobrar_id"], 20.00, "EFECTIVO", "2026-03-25")
    cc = CuentaCobrarModel().get_by_id(cc["cuenta_cobrar_id"])
    test("CxC: Saldo final = $0", cc["saldo_pendiente"] == 0)
    test("CxC: Estado PAGADO", cc["estado_pago"] == "PAGADO")

    # Cliente sin deuda
    cli_post = ClienteModel().get_by_id(cli["cliente_id"])
    test("CxC: Cliente saldo = $0", cli_post["saldo_pendiente"] == 0)


# ══════════════════════════════════════════════════════════════════
# REGLA 8: CUENTAS POR PAGAR — CICLO COMPLETO
# ══════════════════════════════════════════════════════════════════

def test_08_cuentas_pagar_ciclo():
    print("\n" + "=" * 60)
    print("REGLA 8: CUENTAS POR PAGAR — CICLO COMPLETO")
    print("=" * 60)

    cat_svc = CatalogoService()
    prov_svc = ProveedorService()
    compra_svc = CompraService()
    pago_svc = PagoService()

    prod = crear_producto(cat_svc, "CXP-001", "Prod CxP", 10.00, 50)
    prov = prov_svc.crear({
        "ruc_cedula": "1601010101", "razon_social": "Prov CxP",
        "tipo_credito": "CREDITO_15", "plazo_credito_dias": 15,
    })

    # Compra a crédito
    compra = compra_svc.registrar_compra(
        cabecera={"numero_factura": "CXP-F01", "proveedor_id": prov["proveedor_id"],
                  "fecha_compra": "2026-03-05", "tipo_pago": "CREDITO", "plazo_credito_dias": 30},
        items=[{"producto_id": prod["producto_id"], "cantidad": 20,
                "precio_unitario": 5.00, "incluye_iva": 0}]
    )
    test("CxP: Compra crédito registrada", compra["total"] == 115.00)

    cp = CuentaPagarModel().get_by_compra(compra["compra_id"])
    test("CxP: Cuenta creada", cp is not None)
    test("CxP: Monto = $115", cp["monto_original"] == 115.00)
    test("CxP: Estado PENDIENTE", cp["estado_pago"] == "PENDIENTE")
    test("CxP: Fecha vencimiento = 30 días", cp["fecha_vencimiento"] == "2026-04-04")

    # Pagar todo de una vez
    pago_svc.registrar_pago(cp["cuenta_pagar_id"], 115.00, "TRANSFERENCIA", "2026-03-30",
                            referencia="TRF-CXP-001")
    cp = CuentaPagarModel().get_by_id(cp["cuenta_pagar_id"])
    test("CxP: Pago total → PAGADO", cp["estado_pago"] == "PAGADO")
    test("CxP: Saldo = $0", cp["saldo_pendiente"] == 0)


# ══════════════════════════════════════════════════════════════════
# REGLA 9: AUDITORÍA COMPLETA
# ══════════════════════════════════════════════════════════════════

def test_09_auditoria():
    print("\n" + "=" * 60)
    print("REGLA 9: AUDITORÍA COMPLETA")
    print("=" * 60)

    audit = AuditoriaService()
    todos = audit.get_todos(500)

    test("Auditoría > 20 registros", len(todos) >= 20, f"Total: {len(todos)}")

    # Cada registro tiene campos requeridos
    if todos:
        r = todos[0]
        test("Audit: tiene tabla_afectada", "tabla_afectada" in r and r["tabla_afectada"])
        test("Audit: tiene operacion", "operacion" in r and r["operacion"])
        test("Audit: tiene registro_id", "registro_id" in r and r["registro_id"] is not None)
        test("Audit: tiene fecha", "fecha_hora" in r and r["fecha_hora"])

    # Buscar por tablas específicas
    for tabla in ["compra", "venta", "producto", "cliente"]:
        regs = audit.get_por_tabla(tabla)
        test(f"Audit: tabla '{tabla}' tiene registros", len(regs) > 0)


# ══════════════════════════════════════════════════════════════════
# REGLA 10: CÁLCULO DE UTILIDAD
# ══════════════════════════════════════════════════════════════════

def test_10_calculo_utilidad():
    print("\n" + "=" * 60)
    print("REGLA 10: CÁLCULO DE UTILIDAD (Ventas - Compras - Gastos)")
    print("=" * 60)

    rep_svc = ReporteService()
    gasto_svc = GastoService()

    # Registrar gastos conocidos
    gasto_svc.registrar({"tipo_gasto": "ARRIENDO", "descripcion": "Arriendo local",
                          "monto": 150.00, "fecha_gasto": "2026-03-01",
                          "metodo_pago": "TRANSFERENCIA"})
    gasto_svc.registrar({"tipo_gasto": "SERVICIOS", "descripcion": "Luz + agua",
                          "monto": 35.00, "fecha_gasto": "2026-03-05",
                          "metodo_pago": "EFECTIVO"})

    util = rep_svc.reporte_utilidad_periodo("2026-03-01", "2026-03-31")
    test("Utilidad: total_ventas ≥ 0", util["total_ventas"] >= 0)
    test("Utilidad: total_compras ≥ 0", util["total_compras"] >= 0)
    test("Utilidad: total_gastos ≥ 185", util["total_gastos"] >= 185.00,
         f"Real: {util['total_gastos']}")

    # Fórmula
    ub_esperada = round(util["total_ventas"] - util["total_compras"], 2)
    test("Utilidad bruta = ventas - compras",
         util["utilidad_bruta"] == ub_esperada,
         f"Esperada: {ub_esperada}, Real: {util['utilidad_bruta']}")

    un_esperada = round(ub_esperada - util["total_gastos"], 2)
    test("Utilidad neta = bruta - gastos",
         util["utilidad_neta"] == un_esperada,
         f"Esperada: {un_esperada}, Real: {util['utilidad_neta']}")

    # Margen (sin div/0)
    if util["total_ventas"] > 0:
        mb_esperado = round(ub_esperada / util["total_ventas"] * 100, 2)
        test("Margen bruto correcto",
             util["margen_bruto"] == mb_esperado,
             f"Esperado: {mb_esperado}, Real: {util['margen_bruto']}")


# ══════════════════════════════════════════════════════════════════
# REGLA 11: MARGEN DE GANANCIA POR PRODUCTO
# ══════════════════════════════════════════════════════════════════

def test_11_margen_producto():
    print("\n" + "=" * 60)
    print("REGLA 11: MARGEN DE GANANCIA POR PRODUCTO")
    print("=" * 60)

    cat_svc = CatalogoService()

    # margen = (PV - costo) / costo * 100
    m1 = cat_svc.calcular_margen(3.00, 5.50)
    test("Margen $3→$5.50 = 83.33%", m1 == 83.33, f"Real: {m1}")

    m2 = cat_svc.calcular_margen(10.00, 10.00)
    test("Margen mismo precio = 0%", m2 == 0.0)

    m3 = cat_svc.calcular_margen(0, 10.00)
    test("Margen costo=0 retorna 0", m3 == 0.0)

    # Sugerencia de precio
    s1 = cat_svc.sugerir_precio_venta(3.00, 30)
    test("Sugerido $3 + 30% = $3.90", s1 == 3.90)

    s2 = cat_svc.sugerir_precio_venta(10.00, 50)
    test("Sugerido $10 + 50% = $15.00", s2 == 15.00)

    s3 = cat_svc.sugerir_precio_venta(8.00, 100)
    test("Sugerido $8 + 100% = $16.00", s3 == 16.00)


# ══════════════════════════════════════════════════════════════════
# REGLA 12: ANULACIONES NO GENERAN DATOS FANTASMA
# ══════════════════════════════════════════════════════════════════

def test_12_anulaciones_limpias():
    print("\n" + "=" * 60)
    print("REGLA 12: ANULACIONES LIMPIAS")
    print("=" * 60)

    cat_svc = CatalogoService()
    cli_svc = ClienteService()
    venta_svc = VentaService()

    prod = crear_producto(cat_svc, "ANUL-001", "Prod Anulación", 25.00, 50)
    cli = cli_svc.crear({
        "cedula": "1701010101", "nombres": "Test", "apellidos": "Anulación",
        "habilitado_credito": 1, "limite_credito": 100.00, "saldo_pendiente": 0.00,
    })

    # Venta a crédito
    v = venta_svc.registrar_venta(
        cabecera={"cliente_id": cli["cliente_id"], "metodo_pago": "CREDITO", "es_credito": 1},
        items=[{"producto_id": prod["producto_id"], "cantidad": 2}]  # $50
    )
    cli_post1 = ClienteModel().get_by_id(cli["cliente_id"])
    test("Pre-anulación: saldo cliente = $50", cli_post1["saldo_pendiente"] == 50.00)

    stock_pre = ProductoModel().get_by_id(prod["producto_id"])["stock_actual"]

    # Anular
    venta_svc.anular_venta(v["venta_id"])

    # Verificar que todo se revirtió
    cli_post2 = ClienteModel().get_by_id(cli["cliente_id"])
    test("Post-anulación: saldo cliente = $0", cli_post2["saldo_pendiente"] == 0)

    stock_post = ProductoModel().get_by_id(prod["producto_id"])["stock_actual"]
    test("Post-anulación: stock revertido", stock_post == stock_pre + 2)

    cc = CuentaCobrarModel().get_by_venta(v["venta_id"])
    test("Post-anulación: CxC anulada", cc["estado"] == "INA")

    v_post = VentaModel().get_by_id(v["venta_id"])
    test("Post-anulación: venta ANULADA", v_post["estado"] == "ANULADA")


# ══════════════════════════════════════════════════════════════════
# REGLA 13: PRECIO MÍNIMO DE VENTA
# ══════════════════════════════════════════════════════════════════

def test_13_precio_minimo():
    print("\n" + "=" * 60)
    print("REGLA 13: PRECIO MÍNIMO DE VENTA")
    print("=" * 60)

    cat_svc = CatalogoService()
    venta_svc = VentaService()

    # Producto con pvmin=7.00 y pv=10.00
    prod = crear_producto(cat_svc, "PVMIN-001", "Prod PV Mínimo", precio_venta=10.00, stock=50)
    pvmin = ProductoModel().get_by_id(prod["producto_id"])["precio_venta_minimo"]
    test(f"PV mínimo configurado = ${pvmin}", pvmin > 0)

    # Venta con precio bajo el mínimo
    try:
        venta_svc.registrar_venta(
            cabecera={"metodo_pago": "EFECTIVO", "monto_recibido": 100, "es_credito": 0},
            items=[{"producto_id": prod["producto_id"], "cantidad": 1,
                    "precio_unitario": pvmin - 1}]
        )
        test("Precio bajo mínimo rechazado", False)
    except ValueError:
        test("Precio bajo mínimo rechazado", True)

    # Venta con precio exacto al mínimo (OK)
    v = venta_svc.registrar_venta(
        cabecera={"metodo_pago": "EFECTIVO", "monto_recibido": 100, "es_credito": 0},
        items=[{"producto_id": prod["producto_id"], "cantidad": 1,
                "precio_unitario": pvmin}]
    )
    test("Precio exacto al mínimo permitido", v["total"] == pvmin)

    # Crear producto donde pvmin > pv → rechazado
    # El servicio calcula pvmin desde precio_referencia_compra + 23% margen
    # Con costo=8.00, pvmin=8*1.23=9.84 > precio_venta=5.00 → debe rechazar
    try:
        cat_svc.crear_producto({
            "codigo_barras": "PVMIN-BAD", "nombre": "Bad PVMin",
            "categoria_id": cat_svc.get_categorias_raiz()[0]["categoria_id"],
            "unidad_id": cat_svc.get_unidades()[0]["unidad_id"],
            "precio_referencia_compra": 8.00,
            "precio_venta": 5.00,
        })
        test("PVmin > PV rechazado en creación", False)
    except ValueError:
        test("PVmin > PV rechazado en creación", True)


# ══════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════

def main():
    global passed, failed, total

    print("\n" + "📐" * 30)
    print("  Mil Burbujas - FASE 3 · REGLAS DE NEGOCIO")
    print("📐" * 30)

    limpiar_db()

    test_01_iva_compras()
    test_02_rise_ventas()
    test_03_comprobante()
    test_04_secuencias()
    test_05_soft_delete()
    test_06_integridad_stock()
    test_07_cuentas_cobrar_ciclo()
    test_08_cuentas_pagar_ciclo()
    test_09_auditoria()
    test_10_calculo_utilidad()
    test_11_margen_producto()
    test_12_anulaciones_limpias()
    test_13_precio_minimo()

    print("\n" + "=" * 60)
    print("📊 RESUMEN REGLAS DE NEGOCIO")
    print("=" * 60)
    print(f"  Total: {total}  ✅ {passed}  ❌ {failed}  ({passed/total*100:.1f}%)")
    if failed == 0:
        print("  🎉 REGLAS DE NEGOCIO — Todas verificadas")
    else:
        print(f"  ⚠️  {failed} fallo(s) requieren revisión")
    print("=" * 60)

    DatabaseConnection().close()
    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
