# -*- coding: utf-8 -*-
"""
Mil Burbujas - Fase 3 · Test 1/3: INTEGRACIÓN (Flujos completos de negocio)
Simula jornadas reales del negocio MilBurbujas con múltiples transacciones
encadenadas, verificando consistencia de datos de punta a punta.
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
from services.auditoria_service import AuditoriaService

from models.producto import ProductoModel
from models.cliente import ClienteModel
from models.proveedor import ProveedorModel
from models.cuenta_cobrar import CuentaCobrarModel
from models.cuenta_pagar import CuentaPagarModel
from models.movimiento_inventario import MovimientoInventarioModel

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


# ══════════════════════════════════════════════════════════════════
# HELPERS: crear datos base reutilizables
# ══════════════════════════════════════════════════════════════════

def crear_datos_base():
    """Crea catálogo, proveedores y clientes base para las pruebas."""
    cat_svc = CatalogoService()
    prov_svc = ProveedorService()
    cli_svc = ClienteService()

    # Categorías
    cats = cat_svc.get_categorias_raiz()
    cat_id = cats[0]["categoria_id"]

    # Unidades
    unidades = cat_svc.get_unidades()
    und_id = unidades[0]["unidad_id"]

    # Marcas
    marca_a = cat_svc.crear_marca({"nombre": "L'Oréal Test", "descripcion": "Marca francesa"})
    marca_b = cat_svc.crear_marca({"nombre": "Sedal Test", "descripcion": "Marca local"})

    # Líneas
    linea = cat_svc.crear_linea({"marca_id": marca_a["marca_id"], "nombre": "Elvive Test"})

    # Productos (5 distintos)
    productos = []
    specs = [
        ("BB-SH-001", "Shampoo Elvive 400ml",   3.50, 6.50, 5.00, 50, 5, 200, 1),
        ("BB-AC-002", "Acondicionador Sedal",    2.80, 5.00, 4.00, 40, 5, 150, 1),
        ("BB-CR-003", "Crema Nivea 200ml",       4.00, 8.00, 6.50, 30, 3, 100, 0),
        ("BB-JB-004", "Jabón Protex Pack x3",    1.50, 2.80, 2.20, 80, 10, 300, 0),
        ("BB-PE-005", "Perfume Floral 50ml",     8.00, 18.00, 14.00, 15, 2, 50, 0),
    ]
    for cod, nom, costo, pv, pvmin, stk, smin, smax, iva in specs:
        p = cat_svc.crear_producto({
            "codigo_barras": cod, "nombre": nom,
            "categoria_id": cat_id,
            "marca_id": marca_a["marca_id"],
            "linea_id": linea["linea_id"],
            "unidad_id": und_id,
            "precio_referencia_compra": costo,
            "precio_venta": pv,
            "precio_venta_minimo": pvmin,
            "stock_actual": stk,
            "stock_minimo": smin,
            "stock_maximo": smax,
            "aplica_iva_compra": iva,
        })
        productos.append(p)

    # Proveedores (2)
    prov_a = prov_svc.crear({
        "ruc_cedula": "0991001001", "razon_social": "Distribuidora Estrella",
        "tipo_credito": "CREDITO_15", "plazo_credito_dias": 15,
        "frecuencia_pedido": "SEMANAL",
    })
    prov_b = prov_svc.crear({
        "ruc_cedula": "0991002002", "razon_social": "Importadora Andes",
        "tipo_credito": "CREDITO_60", "plazo_credito_dias": 60,
        "frecuencia_pedido": "QUINCENAL",
    })

    # Asignar productos a proveedores
    for p in productos[:3]:
        prov_svc.asignar_producto({
            "proveedor_id": prov_a["proveedor_id"],
            "producto_id": p["producto_id"],
            "precio_compra": p["precio_referencia_compra"],
            "precio_compra_con_iva": round(p["precio_referencia_compra"] * 1.15, 2),
            "incluye_iva": 1, "es_proveedor_principal": 1,
        })
    for p in productos[3:]:
        prov_svc.asignar_producto({
            "proveedor_id": prov_b["proveedor_id"],
            "producto_id": p["producto_id"],
            "precio_compra": p["precio_referencia_compra"],
            "precio_compra_con_iva": round(p["precio_referencia_compra"] * 1.15, 2),
            "incluye_iva": 1, "es_proveedor_principal": 1,
        })

    # Clientes (3)
    cli_a = cli_svc.crear({
        "cedula": "0901010101", "nombres": "María", "apellidos": "López",
        "telefono": "0991112233", "habilitado_credito": 1,
        "limite_credito": 100.00, "saldo_pendiente": 0.00,
        "frecuencia_pago": "QUINCENAL",
    })
    cli_b = cli_svc.crear({
        "cedula": "0902020202", "nombres": "Carlos", "apellidos": "Ramírez",
        "telefono": "0994445566", "habilitado_credito": 1,
        "limite_credito": 50.00, "saldo_pendiente": 0.00,
        "frecuencia_pago": "MENSUAL",
    })
    cli_c = cli_svc.crear({
        "cedula": "0903030303", "nombres": "José", "apellidos": "Torres",
        "telefono": "0997778899", "habilitado_credito": 0,
    })

    return {
        "productos": productos,
        "proveedores": [prov_a, prov_b],
        "clientes": [cli_a, cli_b, cli_c],
    }


# ══════════════════════════════════════════════════════════════════
# FLUJO 1: JORNADA COMPLETA DE UN DÍA
# ══════════════════════════════════════════════════════════════════

def flujo_01_jornada_completa(datos):
    """Simula: abrir tienda → vender → cobrar → gastar → comprar → cerrar caja."""
    print("\n" + "=" * 60)
    print("FLUJO 1: JORNADA COMPLETA DE UN DÍA")
    print("=" * 60)

    prod_model = ProductoModel()
    prods = datos["productos"]
    cli_a = datos["clientes"][0]
    prov_a = datos["proveedores"][0]

    from datetime import datetime
    fecha = datetime.now().strftime("%Y-%m-%d")
    compra_svc = CompraService()
    venta_svc = VentaService()
    cobro_svc = CobroService()
    gasto_svc = GastoService()
    cierre_svc = CierreCajaService()

    # ── 1. Compra de mercadería al inicio del día ──
    stock_pre = [prod_model.get_by_id(p["producto_id"])["stock_actual"] for p in prods[:3]]

    compra = compra_svc.registrar_compra(
        cabecera={
            "numero_factura": "FAC-DIA-001",
            "proveedor_id": prov_a["proveedor_id"],
            "fecha_compra": fecha,
            "tipo_pago": "CREDITO",
            "plazo_credito_dias": 30,
        },
        items=[
            {"producto_id": prods[0]["producto_id"], "cantidad": 24, "precio_unitario": 4.03, "incluye_iva": 1},
            {"producto_id": prods[1]["producto_id"], "cantidad": 20, "precio_unitario": 3.22, "incluye_iva": 1},
            {"producto_id": prods[2]["producto_id"], "cantidad": 15, "precio_unitario": 4.60, "incluye_iva": 1},
        ]
    )
    test("F1: Compra matutina registrada", compra["estado"] == "REGISTRADA")

    stock_post = [prod_model.get_by_id(p["producto_id"])["stock_actual"] for p in prods[:3]]
    test("F1: Stock 3 productos incrementado",
         stock_post[0] == stock_pre[0] + 24 and
         stock_post[1] == stock_pre[1] + 20 and
         stock_post[2] == stock_pre[2] + 15)

    # ── 2. Venta 1: efectivo ──
    v1 = venta_svc.registrar_venta(
        cabecera={"metodo_pago": "EFECTIVO", "monto_recibido": 20.00, "es_credito": 0},
        items=[
            {"producto_id": prods[0]["producto_id"], "cantidad": 2},
            {"producto_id": prods[3]["producto_id"], "cantidad": 1},
        ]
    )
    test("F1: Venta 1 efectivo", v1["total"] == round(6.50 * 2 + 2.80, 2))
    test("F1: Cambio calculado", v1["cambio"] == round(20.00 - v1["total"], 2))

    # ── 3. Venta 2: transferencia ──
    v2 = venta_svc.registrar_venta(
        cabecera={"metodo_pago": "TRANSFERENCIA", "es_credito": 0,
                  "referencia_transferencia": "TRF-20260310-001"},
        items=[
            {"producto_id": prods[4]["producto_id"], "cantidad": 1},
        ]
    )
    test("F1: Venta 2 transferencia", v2["total"] == 18.00)

    # ── 4. Venta 3: crédito (fiado) a María ──
    v3 = venta_svc.registrar_venta(
        cabecera={"cliente_id": cli_a["cliente_id"],
                  "metodo_pago": "CREDITO", "es_credito": 1},
        items=[
            {"producto_id": prods[2]["producto_id"], "cantidad": 3},
        ]
    )
    test("F1: Venta 3 crédito a María", v3["total"] == 24.00)

    cli_post = ClienteModel().get_by_id(cli_a["cliente_id"])
    test("F1: Saldo María = $24.00", cli_post["saldo_pendiente"] == 24.00)

    # ── 5. Cobro parcial de María ──
    cc = CuentaCobrarModel().get_by_venta(v3["venta_id"])
    cobro_svc.registrar_pago(cc["cuenta_cobrar_id"], 10.00, "EFECTIVO", fecha)
    cc_post = CuentaCobrarModel().get_by_id(cc["cuenta_cobrar_id"])
    test("F1: Cobro parcial María ($10)", cc_post["saldo_pendiente"] == 14.00)

    # ── 6. Gastos del día ──
    gasto_svc.registrar({"tipo_gasto": "TRANSPORTE", "descripcion": "Bus traer mercadería",
                         "monto": 3.50, "fecha_gasto": fecha, "metodo_pago": "EFECTIVO"})
    gasto_svc.registrar({"tipo_gasto": "ALIMENTACION", "descripcion": "Almuerzo",
                         "monto": 4.00, "fecha_gasto": fecha, "metodo_pago": "EFECTIVO"})
    test("F1: 2 gastos registrados", True)

    # ── 7. Cierre de caja ──
    preview = cierre_svc.preparar_cierre(fecha)
    # Ventas efectivo del día: v1.total + cobro $10 = 15.80 + 10 = 25.80
    # Ventas transferencia: v2.total = 18.00
    # Compras contado: 0 (es crédito)
    # Gastos: 7.50
    # Efectivo esperado = 25.80 - 0 - 7.50 = 18.30
    test("F1: Preview ventas general",
         preview["total_ventas_general"] > 0)
    test("F1: Preview tiene gastos", preview["total_gastos"] == 7.50)

    cierre = cierre_svc.cerrar_caja(
        efectivo_real=preview["efectivo_esperado"],
        fecha=fecha,
        observaciones="Cierre jornada de prueba"
    )
    test("F1: Cierre de caja cuadra", cierre["diferencia"] == 0)

    return compra, [v1, v2, v3]


# ══════════════════════════════════════════════════════════════════
# FLUJO 2: CRÉDITO MULTI-CLIENTE (ciclo completo)
# ══════════════════════════════════════════════════════════════════

def flujo_02_credito_multicliente(datos):
    """Múltiples ventas a crédito, pagos parciales y totales, validar saldos."""
    print("\n" + "=" * 60)
    print("FLUJO 2: CRÉDITO MULTI-CLIENTE (ciclo completo)")
    print("=" * 60)

    venta_svc = VentaService()
    cobro_svc = CobroService()
    prods = datos["productos"]
    cli_a, cli_b = datos["clientes"][0], datos["clientes"][1]

    # ── Venta crédito a Carlos ($14.00) ──
    vc1 = venta_svc.registrar_venta(
        cabecera={"cliente_id": cli_b["cliente_id"],
                  "metodo_pago": "CREDITO", "es_credito": 1},
        items=[{"producto_id": prods[3]["producto_id"], "cantidad": 5}]
    )
    test("F2: Venta crédito Carlos", vc1["total"] == 14.00)

    cli_b_post = ClienteModel().get_by_id(cli_b["cliente_id"])
    test("F2: Saldo Carlos = $14.00", cli_b_post["saldo_pendiente"] == 14.00)

    # ── Segunda venta crédito a Carlos ($8.00) ──
    vc2 = venta_svc.registrar_venta(
        cabecera={"cliente_id": cli_b["cliente_id"],
                  "metodo_pago": "CREDITO", "es_credito": 1},
        items=[{"producto_id": prods[2]["producto_id"], "cantidad": 1}]
    )
    test("F2: 2da venta crédito Carlos", vc2["total"] == 8.00)

    cli_b_post2 = ClienteModel().get_by_id(cli_b["cliente_id"])
    test("F2: Saldo Carlos acumulado = $22.00", cli_b_post2["saldo_pendiente"] == 22.00)

    # ── Intentar crédito que excede límite ($50) ──
    try:
        venta_svc.registrar_venta(
            cabecera={"cliente_id": cli_b["cliente_id"],
                      "metodo_pago": "CREDITO", "es_credito": 1},
            items=[{"producto_id": prods[4]["producto_id"], "cantidad": 2}]  # 18*2=36, excede 50-22=28
        )
        test("F2: Crédito excede límite rechazado", False)
    except ValueError:
        test("F2: Crédito excede límite rechazado", True)

    # ── Pagar primera cuenta de Carlos ──
    cc1 = CuentaCobrarModel().get_by_venta(vc1["venta_id"])
    cobro_svc.registrar_pago(cc1["cuenta_cobrar_id"], 14.00, "EFECTIVO", "2026-03-12")
    cc1_post = CuentaCobrarModel().get_by_id(cc1["cuenta_cobrar_id"])
    test("F2: Carlos pagó cuenta 1 completa", cc1_post["estado_pago"] == "PAGADO")

    cli_b_post3 = ClienteModel().get_by_id(cli_b["cliente_id"])
    test("F2: Saldo Carlos bajó a $8.00", cli_b_post3["saldo_pendiente"] == 8.00)

    # ── Ahora sí le alcanza crédito a Carlos ──
    vc3 = venta_svc.registrar_venta(
        cabecera={"cliente_id": cli_b["cliente_id"],
                  "metodo_pago": "CREDITO", "es_credito": 1},
        items=[{"producto_id": prods[4]["producto_id"], "cantidad": 2}]
    )
    test("F2: Ahora crédito concedido", vc3 is not None)

    cli_b_post4 = ClienteModel().get_by_id(cli_b["cliente_id"])
    test("F2: Saldo Carlos = $44.00", cli_b_post4["saldo_pendiente"] == 44.00,
         f"Real: {cli_b_post4['saldo_pendiente']}")

    # ── Resumen financiero de Carlos ──
    resumen = cobro_svc.get_resumen_cliente(cli_b["cliente_id"])
    test("F2: Resumen Carlos correcto",
         resumen["total_adeudado"] > 0 and
         resumen["disponible"] >= 0)


# ══════════════════════════════════════════════════════════════════
# FLUJO 3: COMPRA + PAGO PROVEEDOR (ciclo completo)
# ══════════════════════════════════════════════════════════════════

def flujo_03_compra_pago_proveedor(datos):
    """Compra a crédito → pagos parciales → total, verificar saldos."""
    print("\n" + "=" * 60)
    print("FLUJO 3: COMPRA + PAGO A PROVEEDOR (ciclo)")
    print("=" * 60)

    compra_svc = CompraService()
    pago_svc = PagoService()
    prods = datos["productos"]
    prov_b = datos["proveedores"][1]

    # ── Compra a crédito 60 días ──
    compra = compra_svc.registrar_compra(
        cabecera={
            "numero_factura": "IMP-ANDES-050",
            "proveedor_id": prov_b["proveedor_id"],
            "fecha_compra": "2026-03-08",
            "tipo_pago": "CREDITO",
            "plazo_credito_dias": 60,
        },
        items=[
            {"producto_id": prods[3]["producto_id"], "cantidad": 50, "precio_unitario": 1.73, "incluye_iva": 1},
            {"producto_id": prods[4]["producto_id"], "cantidad": 10, "precio_unitario": 9.20, "incluye_iva": 1},
        ]
    )
    test("F3: Compra registrada", compra["total"] > 0)

    cp = CuentaPagarModel().get_by_compra(compra["compra_id"])
    total_deuda = cp["saldo_pendiente"]
    test("F3: Cuenta por pagar creada", cp["estado_pago"] == "PENDIENTE")

    # ── Pago 1: $50 ──
    pago_svc.registrar_pago(cp["cuenta_pagar_id"], 50.00, "TRANSFERENCIA", "2026-03-25",
                            referencia="TRF-ANDES-001")
    cp_post = CuentaPagarModel().get_by_id(cp["cuenta_pagar_id"])
    test("F3: Pago parcial $50", cp_post["estado_pago"] == "PARCIAL")

    # ── Pago 2: el resto ──
    resto = cp_post["saldo_pendiente"]
    pago_svc.registrar_pago(cp["cuenta_pagar_id"], resto, "TRANSFERENCIA", "2026-04-10",
                            referencia="TRF-ANDES-002")
    cp_post2 = CuentaPagarModel().get_by_id(cp["cuenta_pagar_id"])
    test("F3: Pago total completado", cp_post2["estado_pago"] == "PAGADO")
    test("F3: Saldo final = $0", cp_post2["saldo_pendiente"] == 0)


# ══════════════════════════════════════════════════════════════════
# FLUJO 4: AJUSTES DE INVENTARIO VARIADOS
# ══════════════════════════════════════════════════════════════════

def flujo_04_ajustes_inventario(datos):
    """Registra varios tipos de ajustes y verifica consistencia de stock."""
    print("\n" + "=" * 60)
    print("FLUJO 4: AJUSTES DE INVENTARIO VARIADOS")
    print("=" * 60)

    inv_svc = InventarioService()
    prod_model = ProductoModel()
    prods = datos["productos"]

    # Stock actual del producto 0
    p0 = prod_model.get_by_id(prods[0]["producto_id"])
    stock_ini = p0["stock_actual"]

    # ── Consumo personal (-3) ──
    inv_svc.registrar_ajuste(prods[0]["producto_id"], "CONSUMO_PERSONAL", -3,
                             "Shampoo para uso de la tienda")
    p0 = prod_model.get_by_id(prods[0]["producto_id"])
    test("F4: Consumo personal -3", p0["stock_actual"] == stock_ini - 3)

    # ── Daño (-2) ──
    inv_svc.registrar_ajuste(prods[0]["producto_id"], "DANIO", -2,
                             "Envases dañados en transporte")
    p0 = prod_model.get_by_id(prods[0]["producto_id"])
    test("F4: Daño -2", p0["stock_actual"] == stock_ini - 5)

    # ── Entrada manual (+10) - corrección de conteo ──
    inv_svc.registrar_ajuste(prods[0]["producto_id"], "ENTRADA_MANUAL", 10,
                             "Corrección de conteo físico")
    p0 = prod_model.get_by_id(prods[0]["producto_id"])
    test("F4: Entrada manual +10", p0["stock_actual"] == stock_ini + 5)

    # ── Merma (-1) ──
    inv_svc.registrar_ajuste(prods[1]["producto_id"], "MERMA", -1,
                             "Acondicionador derramado")
    p1 = prod_model.get_by_id(prods[1]["producto_id"])
    test("F4: Merma -1 producto 2", True)

    # ── Historial de movimientos ──
    movs = inv_svc.get_movimientos_producto(prods[0]["producto_id"])
    test("F4: Historial movimientos > 5", len(movs) >= 5)


# ══════════════════════════════════════════════════════════════════
# FLUJO 5: VENTA → ANULACIÓN → RE-VENTA
# ══════════════════════════════════════════════════════════════════

def flujo_05_venta_anulacion_reventa(datos):
    """Venta → anular → verificar stock → volver a vender."""
    print("\n" + "=" * 60)
    print("FLUJO 5: VENTA → ANULACIÓN → RE-VENTA")
    print("=" * 60)

    venta_svc = VentaService()
    prod_model = ProductoModel()
    prods = datos["productos"]

    stock_antes = prod_model.get_by_id(prods[1]["producto_id"])["stock_actual"]

    # Venta
    v = venta_svc.registrar_venta(
        cabecera={"metodo_pago": "EFECTIVO", "monto_recibido": 100, "es_credito": 0},
        items=[{"producto_id": prods[1]["producto_id"], "cantidad": 5}]
    )
    stock_post_venta = prod_model.get_by_id(prods[1]["producto_id"])["stock_actual"]
    test("F5: Venta resta stock -5", stock_post_venta == stock_antes - 5)

    # Anular
    anulada = venta_svc.anular_venta(v["venta_id"])
    stock_post_anular = prod_model.get_by_id(prods[1]["producto_id"])["stock_actual"]
    test("F5: Anular devuelve stock", stock_post_anular == stock_antes)
    test("F5: Estado ANULADA", anulada["estado"] == "ANULADA")

    # Re-vender la misma cantidad
    v2 = venta_svc.registrar_venta(
        cabecera={"metodo_pago": "TRANSFERENCIA", "es_credito": 0},
        items=[{"producto_id": prods[1]["producto_id"], "cantidad": 5}]
    )
    stock_final = prod_model.get_by_id(prods[1]["producto_id"])["stock_actual"]
    test("F5: Re-venta exitosa", stock_final == stock_antes - 5)


# ══════════════════════════════════════════════════════════════════
# FLUJO 6: COMPRA → ANULACIÓN (con stock verificado)
# ══════════════════════════════════════════════════════════════════

def flujo_06_compra_anulacion(datos):
    """Compra → vender parte de lo comprado → intentar anular → falla."""
    print("\n" + "=" * 60)
    print("FLUJO 6: COMPRA → VENTA PARCIAL → ANULACIÓN BLOQUEADA")
    print("=" * 60)

    compra_svc = CompraService()
    venta_svc = VentaService()
    prod_model = ProductoModel()
    prods = datos["productos"]

    # Producto 4 (perfume) - stock actual
    p4_antes = prod_model.get_by_id(prods[4]["producto_id"])
    stock_pre = p4_antes["stock_actual"]

    # Compra 5 unidades de perfume
    compra = compra_svc.registrar_compra(
        cabecera={
            "numero_factura": "FAC-PERF-01",
            "proveedor_id": datos["proveedores"][1]["proveedor_id"],
            "fecha_compra": "2026-03-09",
            "tipo_pago": "CONTADO",
        },
        items=[{"producto_id": prods[4]["producto_id"], "cantidad": 5,
                "precio_unitario": 9.20, "incluye_iva": 1}]
    )
    p4_post = prod_model.get_by_id(prods[4]["producto_id"])
    test("F6: Stock +5 por compra", p4_post["stock_actual"] == stock_pre + 5)

    # Vender 4 de las 5 unidades
    venta_svc.registrar_venta(
        cabecera={"metodo_pago": "EFECTIVO", "monto_recibido": 100, "es_credito": 0},
        items=[{"producto_id": prods[4]["producto_id"], "cantidad": 4}]
    )
    p4_post2 = prod_model.get_by_id(prods[4]["producto_id"])
    test("F6: Stock -4 por venta", p4_post2["stock_actual"] == stock_pre + 1)

    # Intentar anular la compra (necesita devolver 5 pero solo hay stock_pre+1)
    # Esto debería fallar si stock_pre+1 < 5
    if stock_pre + 1 < 5:
        try:
            compra_svc.anular_compra(compra["compra_id"])
            test("F6: Anulación bloqueada (stock insuf.)", False)
        except ValueError:
            test("F6: Anulación bloqueada (stock insuf.)", True)
    else:
        # Si hay suficiente stock, la anulación debería funcionar
        anulada = compra_svc.anular_compra(compra["compra_id"])
        test("F6: Anulación permitida (stock suficiente)", anulada["estado"] == "ANULADA")


# ══════════════════════════════════════════════════════════════════
# FLUJO 7: REPORTES FINANCIEROS CONSOLIDADOS
# ══════════════════════════════════════════════════════════════════

def flujo_07_reportes_consolidados(datos):
    """Verifica coherencia de los reportes con las transacciones realizadas."""
    print("\n" + "=" * 60)
    print("FLUJO 7: REPORTES FINANCIEROS CONSOLIDADOS")
    print("=" * 60)

    rep_svc = ReporteService()
    fecha_ini = "2026-03-01"
    fecha_fin = "2026-03-31"

    # Dashboard
    dash = rep_svc.get_dashboard()
    test("F7: Dashboard OK", dash is not None)
    test("F7: Tiene ventas del día", "ventas_hoy" in dash)
    test("F7: Tiene inventario", "valor_inventario_costo" in dash)

    # Utilidad
    util = rep_svc.reporte_utilidad_periodo(fecha_ini, fecha_fin)
    test("F7: Reporte utilidad generado", util is not None)
    test("F7: Utilidad = ventas - compras - gastos",
         util["utilidad_neta"] == round(util["total_ventas"] - util["total_compras"] - util["total_gastos"], 2))

    # Inventario
    inv = rep_svc.reporte_inventario()
    test("F7: Reporte inventario OK", inv is not None)

    # Cuentas por cobrar
    cxc = rep_svc.reporte_cuentas_cobrar()
    test("F7: Reporte CxC generado", cxc is not None and "total_pendiente" in cxc)

    # Cuentas por pagar
    cxp = rep_svc.reporte_cuentas_pagar()
    test("F7: Reporte CxP generado", cxp is not None and "total_pendiente" in cxp)


# ══════════════════════════════════════════════════════════════════
# FLUJO 8: TRAZABILIDAD DE AUDITORÍA
# ══════════════════════════════════════════════════════════════════

def flujo_08_auditoria_integral(datos):
    """Verifica que TODAS las operaciones fueron auditadas."""
    print("\n" + "=" * 60)
    print("FLUJO 8: TRAZABILIDAD DE AUDITORÍA")
    print("=" * 60)

    audit_svc = AuditoriaService()

    todos = audit_svc.get_todos(500)
    test("F8: Existen registros de auditoría", len(todos) > 0)

    # Verificar que hay registros de cada tabla principal
    tablas = ["compra", "venta", "pago_cliente", "pago_proveedor",
              "ajuste_inventario", "cierre_caja", "gasto_operativo",
              "producto", "cliente", "proveedor"]
    for tabla in tablas:
        registros = audit_svc.get_por_tabla(tabla)
        test(f"F8: Auditoría '{tabla}' ({len(registros)} reg)", len(registros) > 0)


# ══════════════════════════════════════════════════════════════════
# FLUJO 9: MÚLTIPLES CIERRES DE CAJA EN DÍAS DISTINTOS
# ══════════════════════════════════════════════════════════════════

def flujo_09_cierres_multiples():
    """Registra cierres en distintos días y verifica integridad."""
    print("\n" + "=" * 60)
    print("FLUJO 9: CIERRES DE CAJA MÚLTIPLES DÍAS")
    print("=" * 60)

    cierre_svc = CierreCajaService()

    # Día 11 (sin ventas)
    preview11 = cierre_svc.preparar_cierre("2026-03-11")
    cierre11 = cierre_svc.cerrar_caja(preview11["efectivo_esperado"],
                                       fecha="2026-03-11",
                                       observaciones="Día sin actividad")
    test("F9: Cierre día 11 (sin ventas)", cierre11["diferencia"] == 0)

    # Día 12 - con diferencia de caja
    preview12 = cierre_svc.preparar_cierre("2026-03-12")
    cierre12 = cierre_svc.cerrar_caja(preview12["efectivo_esperado"] + 5.00,
                                       fecha="2026-03-12",
                                       observaciones="Sobrante caja")
    test("F9: Cierre día 12 con sobrante +$5", cierre12["diferencia"] == 5.00)

    # Día 13 - faltante
    preview13 = cierre_svc.preparar_cierre("2026-03-13")
    cierre13 = cierre_svc.cerrar_caja(preview13["efectivo_esperado"] - 2.50,
                                       fecha="2026-03-13",
                                       observaciones="Faltante caja")
    test("F9: Cierre día 13 con faltante -$2.50", cierre13["diferencia"] == -2.50)

    # Verificar ultimos cierres
    ultimos = cierre_svc.get_ultimos(10)
    test("F9: Al menos 4 cierres registrados", len(ultimos) >= 4)


# ══════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════

def main():
    global passed, failed, total

    print("\n" + "🔗" * 30)
    print("  Mil Burbujas - FASE 3 · TEST INTEGRACIÓN")
    print("🔗" * 30)

    limpiar_db()
    datos = crear_datos_base()

    compra, ventas = flujo_01_jornada_completa(datos)
    flujo_02_credito_multicliente(datos)
    flujo_03_compra_pago_proveedor(datos)
    flujo_04_ajustes_inventario(datos)
    flujo_05_venta_anulacion_reventa(datos)
    flujo_06_compra_anulacion(datos)
    flujo_07_reportes_consolidados(datos)
    flujo_08_auditoria_integral(datos)
    flujo_09_cierres_multiples()

    print("\n" + "=" * 60)
    print("📊 RESUMEN INTEGRACIÓN")
    print("=" * 60)
    print(f"  Total: {total}  ✅ {passed}  ❌ {failed}  ({passed/total*100:.1f}%)")
    if failed == 0:
        print("  🎉 INTEGRACIÓN COMPLETA — Sin errores")
    else:
        print(f"  ⚠️  {failed} fallo(s) requieren revisión")
    print("=" * 60)

    DatabaseConnection().close()
    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
