# -*- coding: utf-8 -*-
"""
Mil Burbujas - FASE 3: RUNNER COMPLETO
Ejecuta las 3 suites de pruebas en secuencia:
  1. Integración (flujos completos de negocio)
  2. Casos borde (edge cases)
  3. Reglas de negocio
"""
import os, sys, time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests.test_integracion import main as run_integracion
from tests.test_casos_borde import main as run_casos_borde
from tests.test_reglas_negocio import main as run_reglas_negocio


def main():
    print("\n" + "🏗️ " * 20)
    print("  Mil Burbujas — FASE 3: SUITE COMPLETA DE PRUEBAS")
    print("🏗️ " * 20)

    inicio = time.time()
    resultados = {}

    # ── Suite 1: Integración ──
    print("\n\n" + "█" * 60)
    print("  SUITE 1/3: INTEGRACIÓN")
    print("█" * 60)
    resultados["Integración"] = run_integracion()

    # ── Suite 2: Casos Borde ──
    print("\n\n" + "█" * 60)
    print("  SUITE 2/3: CASOS BORDE")
    print("█" * 60)
    resultados["Casos Borde"] = run_casos_borde()

    # ── Suite 3: Reglas de Negocio ──
    print("\n\n" + "█" * 60)
    print("  SUITE 3/3: REGLAS DE NEGOCIO")
    print("█" * 60)
    resultados["Reglas de Negocio"] = run_reglas_negocio()

    # ══════════════════════════════════
    # RESUMEN FINAL
    # ══════════════════════════════════
    duracion = round(time.time() - inicio, 2)

    print("\n\n" + "═" * 60)
    print("  🏆 RESUMEN FINAL — FASE 3 COMPLETA")
    print("═" * 60)

    todo_ok = True
    for suite, ok in resultados.items():
        icono = "✅" if ok else "❌"
        print(f"  {icono}  {suite}")
        if not ok:
            todo_ok = False

    print(f"\n  ⏱️  Tiempo total: {duracion}s")

    if todo_ok:
        print("\n  🎉🎉🎉  FASE 3 COMPLETADA AL 100%  🎉🎉🎉")
        print("  👉  Puedes proceder a la FASE 4 (UI con CustomTkinter)")
    else:
        print("\n  ⚠️  Hay suites con fallos. Revisar antes de continuar.")

    print("═" * 60)
    return todo_ok


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
