# -*- coding: utf-8 -*-
"""
Mil Burbujas — Test End-to-End (E2E) del Frontend
Simula paso a paso lo que haría un usuario real desde la interfaz.
Usa exactamente los mismos servicios que la UI invoca.

Flujo completo:
  1. Login
  2. Crear categoría
  3. Crear marca
  4. Crear proveedor
  5. Crear productos (con stock=0)
  6. Registrar compra (stock se llena)
  7. Registrar segunda compra (stock se acumula)
  8. Registrar cliente
  9. Venta en efectivo (con cambio)
  10. Venta por transferencia
  11. Venta a crédito
  12. Cobro parcial y total del crédito
  13. Pago a proveedor
  14. Ajuste de inventario
  15. Registrar gastos operativos
  16. Cierre de caja
  17. Anular venta
  18. Anular compra
  19. Dashboard y reportes
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime
from config import DB_DIR
from database.connection import DatabaseConnection

# Mismos servicios que importa la UI
from services.usuario_service import UsuarioService
from services.catalogo_service import CatalogoService
from services.proveedor_service import ProveedorService
from services.cliente_service import ClienteService
from services.compra_service import CompraService
from services.venta_service import VentaService
from services.cobro_service import CobroService
from services.pago_service import PagoService
from services.inventario_service import InventarioService
from services.gasto_service import GastoService
from services.cierre_caja_service import CierreCajaService
from services.reporte_service import ReporteService

# Modelos para verificación directa
from models.producto import ProductoModel
from models.cliente import ClienteModel

# ──────────────────────────────────
# Contadores
# ──────────────────────────────────
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


def separador(titulo, icono="📋"):
    print(f"\n{'=' * 65}")
    print(f"  {icono} {titulo}")
    print(f"{'=' * 65}")


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


# ══════════════════════════════════════════════════════════════
# PASO 1: LOGIN (como en ui/login.py)
# ══════════════════════════════════════════════════════════════

def paso_01_login():
    separador("PASO 1: LOGIN", "🔐")
    svc = UsuarioService()

    # Intentar con credenciales incorrectas
    bad = svc.autenticar("admin@milburbujas.local", "wrongpassword")
    test("Login incorrecto rechazado", bad is None)

    # Login correcto
    user = svc.autenticar("admin@milburbujas.local", "admin123")
    test("Login correcto (admin)", user is not None)
    test("Rol del usuario = ADMIN", user and user["rol"] == "ADMIN")

    return user


# ══════════════════════════════════════════════════════════════
# PASO 2: CREAR CATEGORÍAS (como en ui/views/catalogo.py)
# ══════════════════════════════════════════════════════════════

def paso_02_categorias():
    separador("PASO 2: CREAR CATEGORÍAS", "📂")
    svc = CatalogoService()

    # Verificar categorías precargadas
    cats = svc.get_categorias_raiz()
    test("Categorías precargadas existen", len(cats) >= 11,
         f"Encontradas: {len(cats)}")

    # Crear nueva categoría (como si el usuario hiciera clic en "+ Nueva Categoría")
    nueva = svc.crear_categoria({"nombre": "Fragancias Premium", "nivel": 0})
    test("Crear categoría 'Fragancias Premium'", nueva is not None)
    test("Categoría tiene ID", nueva["categoria_id"] > 0)

    cats_post = svc.get_categorias_raiz()
    test("Categorías ahora = +1", len(cats_post) == len(cats) + 1)

    return nueva


# ══════════════════════════════════════════════════════════════
# PASO 3: CREAR MARCA (como en ui/views/catalogo.py tab Marcas)
# ══════════════════════════════════════════════════════════════

def paso_03_marcas():
    separador("PASO 3: CREAR MARCAS", "🏷️")
    svc = CatalogoService()

    m1 = svc.crear_marca({"nombre": "L'Oréal", "descripcion": "Marca francesa de belleza"})
    test("Crear marca L'Oréal", m1 is not None)

    m2 = svc.crear_marca({"nombre": "Sedal", "descripcion": "Cuidado capilar"})
    test("Crear marca Sedal", m2 is not None)

    # Duplicado rechazado
    try:
        svc.crear_marca({"nombre": "L'Oréal"})
        test("Marca duplicada rechazada", False)
    except ValueError:
        test("Marca duplicada rechazada", True)

    marcas = svc.get_marcas()
    test("Total marcas = 2", len(marcas) == 2)

    return m1, m2


# ══════════════════════════════════════════════════════════════
# PASO 4: CREAR PROVEEDOR (como en ui/views/proveedores.py)
# ══════════════════════════════════════════════════════════════

def paso_04_proveedores():
    separador("PASO 4: CREAR PROVEEDORES", "🏭")
    svc = ProveedorService()

    prov = svc.crear({
        "ruc_cedula": "0991234567001",
        "razon_social": "Distribuidora Belleza S.A.",
        "nombre_contacto": "Carlos Pérez",
        "telefono": "0991234567",
        "whatsapp": "0991234567",
        "email": "ventas@distbelleza.com",
        "direccion": "Av. Principal 123, Guayaquil",
        "tipo_credito": "CREDITO_60",
        "plazo_credito_dias": 60,
        "frecuencia_pedido": "QUINCENAL",
    })
    test("Crear proveedor 'Distribuidora Belleza'", prov is not None)
    test("Proveedor ID generado", prov["proveedor_id"] > 0)
    test("Proveedor estado ACT", prov["estado"] == "ACT")

    # Duplicado
    try:
        svc.crear({"ruc_cedula": "0991234567001", "razon_social": "Otro"})
        test("RUC duplicado rechazado", False)
    except ValueError:
        test("RUC duplicado rechazado", True)

    return prov


# ══════════════════════════════════════════════════════════════
# PASO 5: CREAR PRODUCTOS (como en ui/views/catalogo.py)
# ══════════════════════════════════════════════════════════════

def paso_05_productos(cat, marca1, marca2):
    separador("PASO 5: CREAR PRODUCTOS (stock=0)", "📦")
    svc = CatalogoService()

    unds = svc.get_unidades()
    und_id = unds[0]["unidad_id"]  # "Unidad"
    cat_id = cat["categoria_id"]

    productos = []

    specs = [
        ("7501234500001", "Shampoo Elvive 400ml",    3.50, 6.50, cat_id, marca1["marca_id"]),
        ("7501234500002", "Acondicionador Sedal 350ml", 2.80, 5.00, cat_id, marca2["marca_id"]),
        ("7501234500003", "Perfume Floral 50ml",     8.00, 18.00, cat_id, marca1["marca_id"]),
    ]

    for cb, nombre, costo, pv, cid, mid in specs:
        p = svc.crear_producto({
            "codigo_barras": cb,
            "nombre": nombre,
            "categoria_id": cid,
            "marca_id": mid,
            "unidad_id": und_id,
            "precio_referencia_compra": costo,
            "precio_venta": pv,
            "stock_actual": 0,  # ¡Empieza en 0! Se llenará con compras
            "stock_minimo": 5,
            "stock_maximo": 200,
            "aplica_iva_compra": 1,
        })
        productos.append(p)
        test(f"Crear '{nombre}' (stock=0)", p is not None and p["stock_actual"] == 0)

    # Verificar precio mínimo auto-calculado
    pmin = productos[0]["precio_venta_minimo"]
    test(f"Precio mínimo auto-calculado (${pmin:.2f})", pmin > 0)

    return productos


# ══════════════════════════════════════════════════════════════
# PASO 6: PRIMERA COMPRA (stock se llena)
# Como en ui/views/compras.py → _dlg_nueva_compra → _save
# ══════════════════════════════════════════════════════════════

def paso_06_primera_compra(prov, productos):
    separador("PASO 6: PRIMERA COMPRA (stock se llena)", "🛒")
    compra_svc = CompraService()
    prod_model = ProductoModel()

    # Verificar stock antes
    for p in productos:
        stock_pre = prod_model.get_by_id(p["producto_id"])["stock_actual"]
        test(f"Stock pre-compra '{p['nombre'][:25]}' = 0", stock_pre == 0)

    # Registrar compra (como la vista: seleccionar proveedor, agregar items, guardar)
    compra = compra_svc.registrar_compra(
        cabecera={
            "numero_factura": "FAC-2026-001",
            "proveedor_id": prov["proveedor_id"],
            "fecha_compra": datetime.now().strftime("%Y-%m-%d"),
            "tipo_pago": "CREDITO",
            "plazo_credito_dias": 60,
        },
        items=[
            {"producto_id": productos[0]["producto_id"], "cantidad": 24,
             "precio_unitario": 4.03, "incluye_iva": 1},
            {"producto_id": productos[1]["producto_id"], "cantidad": 20,
             "precio_unitario": 3.22, "incluye_iva": 1},
            {"producto_id": productos[2]["producto_id"], "cantidad": 10,
             "precio_unitario": 9.20, "incluye_iva": 1},
        ]
    )
    test("Compra registrada (FAC-2026-001)", compra["estado"] == "REGISTRADA")
    test(f"Total compra: ${compra['total']:.2f}", compra["total"] > 0)

    # Verificar stock después
    s1 = prod_model.get_by_id(productos[0]["producto_id"])["stock_actual"]
    s2 = prod_model.get_by_id(productos[1]["producto_id"])["stock_actual"]
    s3 = prod_model.get_by_id(productos[2]["producto_id"])["stock_actual"]
    test(f"Stock Shampoo: 0 → {s1}", s1 == 24)
    test(f"Stock Acondicionador: 0 → {s2}", s2 == 20)
    test(f"Stock Perfume: 0 → {s3}", s3 == 10)

    return compra


# ══════════════════════════════════════════════════════════════
# PASO 7: SEGUNDA COMPRA (stock se ACUMULA)
# ══════════════════════════════════════════════════════════════

def paso_07_segunda_compra(prov, productos):
    separador("PASO 7: SEGUNDA COMPRA (stock se acumula)", "🛒➕")
    compra_svc = CompraService()
    prod_model = ProductoModel()

    stock_antes = prod_model.get_by_id(productos[0]["producto_id"])["stock_actual"]

    compra2 = compra_svc.registrar_compra(
        cabecera={
            "numero_factura": "FAC-2026-002",
            "proveedor_id": prov["proveedor_id"],
            "fecha_compra": datetime.now().strftime("%Y-%m-%d"),
            "tipo_pago": "CONTADO",
        },
        items=[
            {"producto_id": productos[0]["producto_id"], "cantidad": 12,
             "precio_unitario": 3.95, "incluye_iva": 1},
        ]
    )
    test("Segunda compra registrada", compra2["estado"] == "REGISTRADA")

    stock_despues = prod_model.get_by_id(productos[0]["producto_id"])["stock_actual"]
    test(f"Stock ACUMULADO: {stock_antes} + 12 = {stock_despues}",
         stock_despues == stock_antes + 12)

    return compra2


# ══════════════════════════════════════════════════════════════
# PASO 8: CREAR CLIENTE (como en ui/views/clientes.py)
# ══════════════════════════════════════════════════════════════

def paso_08_clientes():
    separador("PASO 8: CREAR CLIENTES", "👤")
    svc = ClienteService()

    # Cliente con crédito habilitado
    cli_credito = svc.crear({
        "cedula": "0912345678",
        "nombres": "María",
        "apellidos": "González López",
        "telefono": "0987654321",
        "direccion": "Calle 10 de Agosto",
        "habilitado_credito": 1,
        "limite_credito": 100.00,
        "saldo_pendiente": 0,
        "frecuencia_pago": "QUINCENAL",
    })
    test("Crear cliente María (con crédito)", cli_credito is not None)
    test("Crédito habilitado", cli_credito["habilitado_credito"] == 1)
    test("Límite crédito = $100", cli_credito["limite_credito"] == 100.00)

    # Cliente sin crédito
    cli_normal = svc.crear({
        "cedula": "0987654321",
        "nombres": "Juan",
        "apellidos": "Pérez",
        "telefono": "0912345678",
        "direccion": "",
        "habilitado_credito": 0,
        "limite_credito": 0,
        "saldo_pendiente": 0,
        "frecuencia_pago": "MENSUAL",
    })
    test("Crear cliente Juan (sin crédito)", cli_normal is not None)

    return cli_credito, cli_normal


# ══════════════════════════════════════════════════════════════
# PASO 9: VENTA EN EFECTIVO (como en ui/views/ventas.py)
# Flujo: buscar producto → agregar → seleccionar EFECTIVO →
#        ingresar monto → se calcula cambio → registrar
# ══════════════════════════════════════════════════════════════

def paso_09_venta_efectivo(productos):
    separador("PASO 9: VENTA EN EFECTIVO (con cambio)", "💵")
    venta_svc = VentaService()
    prod_model = ProductoModel()

    stock_pre = prod_model.get_by_id(productos[0]["producto_id"])["stock_actual"]

    # Simular: agregar 2 Shampoo ($6.50 c/u) + 1 Acondicionador ($5.00)
    v = venta_svc.registrar_venta(
        cabecera={
            "metodo_pago": "EFECTIVO",
            "monto_recibido": 20.00,
            "es_credito": 0,
        },
        items=[
            {"producto_id": productos[0]["producto_id"], "cantidad": 2},
            {"producto_id": productos[1]["producto_id"], "cantidad": 1},
        ]
    )
    total_esperado = 6.50 * 2 + 5.00  # $18.00
    cambio_esperado = 20.00 - total_esperado  # $2.00

    test(f"Venta efectivo registrada (${v['total']:.2f})", v["total"] == total_esperado)
    test(f"Cambio calculado: ${v['cambio']:.2f}", v["cambio"] == cambio_esperado)
    test("Método = EFECTIVO", v["metodo_pago"] == "EFECTIVO")
    test("Estado = COMPLETADA", v["estado"] == "COMPLETADA")

    stock_post = prod_model.get_by_id(productos[0]["producto_id"])["stock_actual"]
    test(f"Stock descontado: {stock_pre} → {stock_post}", stock_post == stock_pre - 2)

    return v


# ══════════════════════════════════════════════════════════════
# PASO 10: VENTA POR TRANSFERENCIA
# Flujo: seleccionar TRANSFERENCIA → solo pedir referencia →
#        NO pedir monto → NO calcular cambio
# ══════════════════════════════════════════════════════════════

def paso_10_venta_transferencia(productos):
    separador("PASO 10: VENTA POR TRANSFERENCIA", "🏦")
    venta_svc = VentaService()

    v = venta_svc.registrar_venta(
        cabecera={
            "metodo_pago": "TRANSFERENCIA",
            "referencia_transferencia": "TRF-20260314-001",
            "es_credito": 0,
            # NO se envía monto_recibido (no aplica en transferencia)
        },
        items=[
            {"producto_id": productos[2]["producto_id"], "cantidad": 1},
        ]
    )
    test(f"Venta transferencia: ${v['total']:.2f}", v["total"] == 18.00)
    test("Método = TRANSFERENCIA", v["metodo_pago"] == "TRANSFERENCIA")
    test("Sin cambio (no aplica)", v.get("cambio", 0) == 0)

    return v


# ══════════════════════════════════════════════════════════════
# PASO 11: VENTA A CRÉDITO
# Flujo: seleccionar CREDITO → solo requiere cliente →
#        NO pedir monto → NO calcular cambio → genera CxC
# ══════════════════════════════════════════════════════════════

def paso_11_venta_credito(productos, cliente):
    separador("PASO 11: VENTA A CRÉDITO (fiado)", "📝")
    venta_svc = VentaService()
    cli_model = ClienteModel()

    saldo_pre = cli_model.get_by_id(cliente["cliente_id"])["saldo_pendiente"]

    v = venta_svc.registrar_venta(
        cabecera={
            "metodo_pago": "CREDITO",
            "es_credito": 1,
            "cliente_id": cliente["cliente_id"],
            # NO se envía monto_recibido (es crédito, no está pagando)
            # NO se envía referencia_transferencia
        },
        items=[
            {"producto_id": productos[0]["producto_id"], "cantidad": 3},
            {"producto_id": productos[1]["producto_id"], "cantidad": 2},
        ]
    )
    total_esperado = 6.50 * 3 + 5.00 * 2  # $29.50
    test(f"Venta crédito: ${v['total']:.2f}", v["total"] == total_esperado)
    test("Método = CREDITO", v["metodo_pago"] == "CREDITO")
    test("Es crédito = 1", v["es_credito"] == 1)
    test("Sin cambio (crédito)", v.get("cambio", 0) == 0)
    test("Sin monto_recibido", v.get("monto_recibido") is None or v.get("monto_recibido", 0) == 0)

    saldo_post = cli_model.get_by_id(cliente["cliente_id"])["saldo_pendiente"]
    test(f"Saldo cliente: ${saldo_pre:.2f} → ${saldo_post:.2f}",
         saldo_post == saldo_pre + total_esperado)

    # Crédito sin cliente rechazado
    try:
        venta_svc.registrar_venta(
            cabecera={"metodo_pago": "CREDITO", "es_credito": 1},
            items=[{"producto_id": productos[0]["producto_id"], "cantidad": 1}]
        )
        test("Crédito sin cliente rechazado", False)
    except ValueError:
        test("Crédito sin cliente rechazado", True)

    return v


# ══════════════════════════════════════════════════════════════
# PASO 12: COBROS (pago del crédito)
# Como en ui/views/cobros.py
# ══════════════════════════════════════════════════════════════

def paso_12_cobros(cliente):
    separador("PASO 12: COBROS (cliente paga el crédito)", "💰")
    cobro_svc = CobroService()
    cli_model = ClienteModel()
    hoy = datetime.now().strftime("%Y-%m-%d")

    # Ver cuentas pendientes
    cuentas = cobro_svc.get_pendientes_por_cliente(cliente["cliente_id"])
    test("Existe cuenta por cobrar", len(cuentas) > 0)

    cc = cuentas[0]
    saldo_cc = cc["saldo_pendiente"]
    test(f"Saldo pendiente: ${saldo_cc:.2f}", saldo_cc > 0)

    # Cobro parcial: $10
    pago1 = cobro_svc.registrar_pago(
        cuenta_cobrar_id=cc["cuenta_cobrar_id"],
        monto=10.00,
        metodo_pago="EFECTIVO",
        fecha_pago=hoy,
    )
    test("Cobro parcial $10 registrado", pago1 is not None)

    cc_post = cobro_svc.get_cuenta(cc["cuenta_cobrar_id"])
    test(f"Saldo tras cobro: ${cc_post['saldo_pendiente']:.2f}",
         cc_post["saldo_pendiente"] == saldo_cc - 10)
    test("Estado: PARCIAL", cc_post["estado_pago"] == "PARCIAL")

    # Cobro total del resto
    resto = cc_post["saldo_pendiente"]
    pago2 = cobro_svc.registrar_pago(
        cuenta_cobrar_id=cc["cuenta_cobrar_id"],
        monto=resto,
        metodo_pago="TRANSFERENCIA",
        fecha_pago=hoy,
    )
    test(f"Cobro final ${resto:.2f} registrado", pago2 is not None)

    cc_final = cobro_svc.get_cuenta(cc["cuenta_cobrar_id"])
    test("Saldo = $0", cc_final["saldo_pendiente"] == 0)
    test("Estado: PAGADO", cc_final["estado_pago"] == "PAGADO")

    cli_saldo = cli_model.get_by_id(cliente["cliente_id"])["saldo_pendiente"]
    test(f"Saldo cliente = $0", cli_saldo == 0)


# ══════════════════════════════════════════════════════════════
# PASO 13: PAGO A PROVEEDOR
# Como en ui/views/pagos.py
# ══════════════════════════════════════════════════════════════

def paso_13_pago_proveedor(compra):
    separador("PASO 13: PAGO A PROVEEDOR", "💸")
    pago_svc = PagoService()
    hoy = datetime.now().strftime("%Y-%m-%d")

    # Buscar cuenta por pagar de la primera compra (crédito)
    cuentas = pago_svc.get_pendientes_por_proveedor(compra["proveedor_id"])
    test("Existe cuenta por pagar", len(cuentas) > 0)

    cp = cuentas[0]
    total_deuda = cp["saldo_pendiente"]

    # Pago total
    pago = pago_svc.registrar_pago(
        cuenta_pagar_id=cp["cuenta_pagar_id"],
        monto=total_deuda,
        metodo_pago="TRANSFERENCIA",
        fecha_pago=hoy,
        referencia="TRF-PAGO-001",
    )
    test(f"Pago a proveedor ${total_deuda:.2f}", pago is not None)

    cp_post = pago_svc.get_cuenta(cp["cuenta_pagar_id"])
    test("Saldo proveedor = $0", cp_post["saldo_pendiente"] == 0)
    test("Estado: PAGADO", cp_post["estado_pago"] == "PAGADO")


# ══════════════════════════════════════════════════════════════
# PASO 14: AJUSTE DE INVENTARIO
# Como en ui/views/inventario.py
# ══════════════════════════════════════════════════════════════

def paso_14_ajuste_inventario(productos):
    separador("PASO 14: AJUSTE DE INVENTARIO", "📊")
    inv_svc = InventarioService()
    prod_model = ProductoModel()

    pid = productos[1]["producto_id"]
    stock_pre = prod_model.get_by_id(pid)["stock_actual"]

    # Ajuste: consumo personal -2 (cantidad negativa = sale del stock)
    ajuste = inv_svc.registrar_ajuste(
        producto_id=pid,
        tipo_ajuste="CONSUMO_PERSONAL",
        cantidad=-2,
        motivo="Uso personal de acondicionador",
    )
    test("Ajuste consumo personal", ajuste is not None)

    stock_post = prod_model.get_by_id(pid)["stock_actual"]
    test(f"Stock ajustado: {stock_pre} → {stock_post}", stock_post == stock_pre - 2)

    # Ajuste: entrada manual +5 (cantidad positiva = entra al stock)
    stock_pre2 = stock_post
    ajuste2 = inv_svc.registrar_ajuste(
        producto_id=pid,
        tipo_ajuste="ENTRADA_MANUAL",
        cantidad=5,
        motivo="Corrección de conteo físico",
    )
    test("Ajuste entrada manual +5", ajuste2 is not None)

    stock_post2 = prod_model.get_by_id(pid)["stock_actual"]
    test(f"Stock post-entrada: {stock_pre2} + 5 = {stock_post2}",
         stock_post2 == stock_pre2 + 5)

    # Alertas de inventario
    alertas = inv_svc.get_alertas()
    test("Alertas de stock disponibles", alertas is not None)


# ══════════════════════════════════════════════════════════════
# PASO 15: GASTOS OPERATIVOS
# Como en ui/views/gastos.py
# ══════════════════════════════════════════════════════════════

def paso_15_gastos():
    separador("PASO 15: GASTOS OPERATIVOS", "🧾")
    gasto_svc = GastoService()
    hoy = datetime.now().strftime("%Y-%m-%d")

    g1 = gasto_svc.registrar({
        "tipo_gasto": "ARRIENDO",
        "descripcion": "Pago mensual arriendo marzo 2026",
        "monto": 150.00,
        "fecha_gasto": hoy,
        "metodo_pago": "TRANSFERENCIA",
    })
    test("Gasto arriendo $150", g1 is not None)

    g2 = gasto_svc.registrar({
        "tipo_gasto": "SERVICIOS",
        "descripcion": "Planilla de luz marzo",
        "monto": 35.00,
        "fecha_gasto": hoy,
        "metodo_pago": "EFECTIVO",
    })
    test("Gasto luz $35", g2 is not None)

    # Gasto $0 rechazado
    try:
        gasto_svc.registrar({
            "tipo_gasto": "OTROS", "descripcion": "Nada",
            "monto": 0, "fecha_gasto": hoy, "metodo_pago": "EFECTIVO",
        })
        test("Gasto $0 rechazado", False)
    except ValueError:
        test("Gasto $0 rechazado", True)


# ══════════════════════════════════════════════════════════════
# PASO 16: CIERRE DE CAJA
# Como en ui/views/cierre_caja.py
# ══════════════════════════════════════════════════════════════

def paso_16_cierre_caja():
    separador("PASO 16: CIERRE DE CAJA", "🏪")
    cierre_svc = CierreCajaService()

    hoy = datetime.now().strftime("%Y-%m-%d")

    # Preview (lo que se muestra antes de cerrar)
    preview = cierre_svc.preparar_cierre(hoy)
    test("Preview cierre generado", preview is not None)
    test(f"Ventas del día: ${preview['total_ventas_general']:.2f}",
         preview["total_ventas_general"] > 0)
    test(f"Efectivo esperado: ${preview['efectivo_esperado']:.2f}",
         "efectivo_esperado" in preview)

    # Realizar cierre (efectivo contado = el esperado → diferencia 0)
    cierre = cierre_svc.cerrar_caja(
        efectivo_real=preview["efectivo_esperado"],
        fecha=hoy,
        observaciones="Cierre sin diferencia",
    )
    test("Cierre registrado", cierre is not None)
    test("Diferencia = $0 (cuadra)",
         cierre.get("diferencia", 0) == 0 or
         abs(cierre.get("diferencia", 0)) < 0.01)

    # Cierre duplicado rechazado
    try:
        cierre_svc.cerrar_caja(efectivo_real=0, fecha=hoy)
        test("Cierre duplicado rechazado", False)
    except ValueError:
        test("Cierre duplicado rechazado", True)


# ══════════════════════════════════════════════════════════════
# PASO 17: ANULAR VENTA
# Como en ui/views/ventas.py → _anular
# ══════════════════════════════════════════════════════════════

def paso_17_anular_venta(venta_efectivo, productos):
    separador("PASO 17: ANULAR VENTA", "❌")
    venta_svc = VentaService()
    prod_model = ProductoModel()

    vid = venta_efectivo["venta_id"]
    stock_pre = prod_model.get_by_id(productos[0]["producto_id"])["stock_actual"]

    # Anular
    anulada = venta_svc.anular_venta(vid)
    test("Venta anulada", anulada["estado"] == "ANULADA")

    stock_post = prod_model.get_by_id(productos[0]["producto_id"])["stock_actual"]
    test(f"Stock revertido: {stock_pre} + 2 = {stock_post}", stock_post == stock_pre + 2)

    # Re-anular rechazada
    try:
        venta_svc.anular_venta(vid)
        test("Re-anulación rechazada", False)
    except ValueError:
        test("Re-anulación rechazada", True)


# ══════════════════════════════════════════════════════════════
# PASO 18: ANULAR COMPRA
# Como en ui/views/compras.py → _anular
# ══════════════════════════════════════════════════════════════

def paso_18_anular_compra(compra2, productos):
    separador("PASO 18: ANULAR COMPRA", "❌")
    compra_svc = CompraService()
    prod_model = ProductoModel()

    cid = compra2["compra_id"]
    stock_pre = prod_model.get_by_id(productos[0]["producto_id"])["stock_actual"]

    anulada = compra_svc.anular_compra(cid)
    test("Compra anulada", anulada["estado"] == "ANULADA")

    stock_post = prod_model.get_by_id(productos[0]["producto_id"])["stock_actual"]
    test(f"Stock revertido: {stock_pre} - 12 = {stock_post}", stock_post == stock_pre - 12)


# ══════════════════════════════════════════════════════════════
# PASO 19: DASHBOARD Y REPORTES
# Como en ui/views/dashboard.py y ui/views/reportes.py
# ══════════════════════════════════════════════════════════════

def paso_19_reportes():
    separador("PASO 19: DASHBOARD Y REPORTES", "📈")
    reporte_svc = ReporteService()

    hoy = datetime.now().strftime("%Y-%m-%d")

    dash = reporte_svc.get_dashboard()
    test("Dashboard generado", dash is not None)
    test("Dashboard tiene ventas_hoy", "ventas_hoy" in dash)
    test("Dashboard tiene valor_inventario_costo", "valor_inventario_costo" in dash)

    rv = reporte_svc.reporte_ventas_periodo(hoy, hoy)
    test("Reporte ventas del día", rv is not None)

    rc = reporte_svc.reporte_compras_periodo(hoy, hoy)
    test("Reporte compras del día", rc is not None)

    util = reporte_svc.reporte_utilidad_periodo(hoy, hoy)
    test("Reporte utilidad", util is not None)
    test("Utilidad neta calculada", "utilidad_neta" in util)

    inv = reporte_svc.reporte_inventario()
    test("Reporte inventario", inv is not None)

    cxc = reporte_svc.reporte_cuentas_cobrar()
    test("Reporte CxC", cxc is not None)

    cxp = reporte_svc.reporte_cuentas_pagar()
    test("Reporte CxP", cxp is not None)


# ══════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════

def main():
    global passed, failed, total

    print("\n" + "🖥️ " * 20)
    print("  Mil Burbujas — TEST END-TO-END FRONTEND")
    print("  Simula flujo completo de un usuario real")
    print("🖥️ " * 20)

    limpiar_db()

    # ── Ejecutar todos los pasos en orden ──
    user = paso_01_login()
    cat = paso_02_categorias()
    marca1, marca2 = paso_03_marcas()
    prov = paso_04_proveedores()
    productos = paso_05_productos(cat, marca1, marca2)
    compra1 = paso_06_primera_compra(prov, productos)
    compra2 = paso_07_segunda_compra(prov, productos)
    cli_credito, cli_normal = paso_08_clientes()
    venta_efect = paso_09_venta_efectivo(productos)
    venta_transf = paso_10_venta_transferencia(productos)
    venta_cred = paso_11_venta_credito(productos, cli_credito)
    paso_12_cobros(cli_credito)
    paso_13_pago_proveedor(compra1)
    paso_14_ajuste_inventario(productos)
    paso_15_gastos()
    paso_16_cierre_caja()
    paso_17_anular_venta(venta_efect, productos)
    paso_18_anular_compra(compra2, productos)
    paso_19_reportes()

    # ── Resumen ──
    print(f"\n{'═' * 65}")
    print(f"  🏆 RESUMEN FINAL — TEST E2E FRONTEND")
    print(f"{'═' * 65}")
    print(f"  Total:    {total}")
    print(f"  ✅ Pasaron: {passed}")
    print(f"  ❌ Fallaron: {failed}")
    print(f"  Porcentaje: {passed / total * 100:.1f}%")

    if failed == 0:
        print(f"\n  🎉🎉🎉  TODO EL FLUJO DE USUARIO VERIFICADO  🎉🎉🎉")
        print(f"  El sistema está listo para producción.")
    else:
        print(f"\n  ⚠️  {failed} paso(s) fallido(s). Revisar antes de producción.")

    print(f"{'═' * 65}\n")

    return failed == 0


if __name__ == "__main__":
    import time
    start = time.time()
    success = main()
    elapsed = time.time() - start
    print(f"  ⏱️  Tiempo total: {elapsed:.2f}s\n")
    sys.exit(0 if success else 1)
