"""
Demostrador & CLI Operativo: Agente de Riego Agrícola de Precisión
==================================================================
Simulación completa de un predio real en el Valle de Cachapoal / Colchagua (Chile).
Ejecuta balances diarios con Penman-Monteith, evalúa sensores Scholander y emite
órdenes de riego oficiales listas para terreno.

Uso:
    python 05_Scripts/agente_riego/interfaz_riego_cli.py

Autor: Cristián González Huenchún & Antigravity
"""

import sys
from pathlib import Path

# Agregar directorio scripts al PATH
sys.path.append(str(Path(__file__).resolve().parent.parent))

from agente_riego import (
    AgenteRiego,
    SectorRiego,
    Suelo,
    Cultivo,
    calcular_et0_penman_monteith,
    ZONAS_CHILE
)

# Asegurar UTF-8 en Windows
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


def simular_predio_modelo() -> None:
    print("=" * 80)
    print("🌿 AGENTE DE RIEGO AGRÍCOLA DE PRECISIÓN — CHILE v1.0")
    print("   Predio: 'Viñedo & Frutales Fundo Millahue' (Valle del Cachapoal)")
    print("   Operador: Cristián González Huenchún (Ing. Agrónomo, U. de Chile)")
    print("=" * 80)

    agente = AgenteRiego(nombre_predio="Fundo Millahue")

    # 1. Configurar Sectores de Riego Reales
    # Sector A: Cabernet Sauvignon (Alta Gama)
    sector_cabernet = SectorRiego(
        nombre="Cuartel 05 - Cabernet Sauvignon",
        superficie_ha=4.8,
        distancia_hileras_m=2.20,
        distancia_plantas_m=1.00,
        caudal_emisor_l_h=2.0,
        espaciamiento_emisores_m=0.50,
        lineas_por_hilera=1,
        eficiencia_aplicacion_ea=0.90,
        presion_trabajo_bar=1.5,
        desnivel_topografico_m=8.0
    )
    suelo_cabernet = Suelo(textura="Franco_Arcilloso", profundidad_raices_m=0.75, pedregosidad_pct=15.0)
    cultivo_cabernet = Cultivo(
        clave_cultivo="Vid_Vinifera_Tinta",
        fenofase_actual="Cuaja_a_Envero",
        aplicar_rdc=True  # RDC para potenciar antocianos tri-hidroxilados
    )
    agente.registrar_cuartel("C05_CAB", sector_cabernet, suelo_cabernet, cultivo_cabernet)

    # Sector B: Chardonnay
    sector_chardonnay = SectorRiego(
        nombre="Cuartel 08 - Chardonnay",
        superficie_ha=3.5,
        distancia_hileras_m=2.40,
        distancia_plantas_m=1.20,
        caudal_emisor_l_h=2.2,
        espaciamiento_emisores_m=0.60,
        lineas_por_hilera=1,
        eficiencia_aplicacion_ea=0.92,
        presion_trabajo_bar=1.6,
        desnivel_topografico_m=3.0
    )
    suelo_chardonnay = Suelo(textura="Franco", profundidad_raices_m=0.70, pedregosidad_pct=5.0)
    cultivo_chardonnay = Cultivo(
        clave_cultivo="Vid_Vinifera_Blanca",
        fenofase_actual="Cuaja_a_Envero",
        aplicar_rdc=False  # Cero estrés severo para proteger tioles
    )
    agente.registrar_cuartel("C08_CHARD", sector_chardonnay, suelo_chardonnay, cultivo_chardonnay)

    # Sector C: Cerezos Lapins (Poscosecha)
    sector_cerezos = SectorRiego(
        nombre="Sector 02 - Cerezos Lapins",
        superficie_ha=6.0,
        distancia_hileras_m=4.00,
        distancia_plantas_m=2.00,
        caudal_emisor_l_h=2.0,
        espaciamiento_emisores_m=0.50,
        lineas_por_hilera=2,  # Doble línea de goteo en frutales
        eficiencia_aplicacion_ea=0.90,
        presion_trabajo_bar=1.8,
        desnivel_topografico_m=10.0
    )
    suelo_cerezos = Suelo(textura="Franco_Arenoso", profundidad_raices_m=0.85, pedregosidad_pct=10.0)
    cultivo_cerezos = Cultivo(
        clave_cultivo="Cerezos",
        fenofase_actual="Poscosecha_Temprana",
        aplicar_rdc=True  # RDC poscosecha para ahorrar 30% agua
    )
    agente.registrar_cuartel("S02_CEREZOS", sector_cerezos, suelo_cerezos, cultivo_cerezos)

    # 2. Simulación Semanal de Clima (Semana Típica de Enero en Valle Central)
    clima_semana = [
        {"dia": "Lunes", "tmax": 31.5, "tmin": 13.2, "rh": 48.0, "viento": 2.1, "rs": 27.5},
        {"dia": "Martes", "tmax": 33.0, "tmin": 14.0, "rh": 42.0, "viento": 2.4, "rs": 28.2},
        {"dia": "Miércoles", "tmax": 34.5, "tmin": 14.8, "rh": 38.0, "viento": 2.6, "rs": 28.8},
        {"dia": "Jueves", "tmax": 32.0, "tmin": 13.8, "rh": 45.0, "viento": 1.9, "rs": 26.9},
        {"dia": "Viernes", "tmax": 30.5, "tmin": 12.5, "rh": 52.0, "viento": 1.8, "rs": 25.8},
        {"dia": "Sábado", "tmax": 31.0, "tmin": 13.0, "rh": 50.0, "viento": 2.0, "rs": 26.5},
        {"dia": "Domingo", "tmax": 32.5, "tmin": 13.5, "rh": 44.0, "viento": 2.2, "rs": 27.4}
    ]

    print("\n📊 1. ANÁLISIS CLIMATOLÓGICO SEMANAL (FAO-56 Penman-Monteith):")
    print("-" * 80)
    print(f"{'Día':<12} | {'Tmax (°C)':<9} | {'Tmin (°C)':<9} | {'HR (%)':<7} | {'VPD (kPa)':<10} | {'ET0 (mm/d)':<10}")
    print("-" * 80)

    et0_valores = []
    for c in clima_semana:
        met = calcular_et0_penman_monteith(
            tmax_c=c["tmax"],
            tmin_c=c["tmin"],
            rh_mean_pct=c["rh"],
            viento_2m_m_s=c["viento"],
            radiacion_solar_mj_m2_dia=c["rs"],
            latitud_grados=-34.33,
            altitud_m=320.0
        )
        et0_valores.append(met["et0_mm_dia"])
        print(f"{c['dia']:<12} | {c['tmax']:<9.1f} | {c['tmin']:<9.1f} | {c['rh']:<7.0f} | {met['vpd_kpa']:<10.2f} | {met['et0_mm_dia']:<10.2f}")

    prom_et0 = sum(et0_valores) / len(et0_valores)
    total_et0 = sum(et0_valores)
    print("-" * 80)
    print(f"Acumulado Semanal: {total_et0:.1f} mm | Promedio Diario: {prom_et0:.2f} mm/día\n")

    # 3. Procesar Balance para los 3 sectores a lo largo de la semana
    for i, c in enumerate(clima_semana):
        et0 = et0_valores[i]
        dia = c["dia"]

        # En día Miércoles (día de mayor calor), simulamos lectura de cámara Scholander
        psi_cab = -1.15 if dia == "Miércoles" else None
        agente.procesar_balance_diario("C05_CAB", dia, et0, psi_tallo_scholander=psi_cab)
        agente.procesar_balance_diario("C08_CHARD", dia, et0)
        agente.procesar_balance_diario("S02_CEREZOS", dia, et0)

    # 4. Emisión de Órdenes de Riego y Reportes de Ingeniería
    print("=" * 80)
    print("🚜 2. PROGRAMA DE RIEGO Y ÓRDENES DE TRABAJO EMITIDAS PARA CASÍO:")
    print("=" * 80)

    for id_sec in ["C05_CAB", "C08_CHARD", "S02_CEREZOS"]:
        orden = agente.emitir_orden_riego(id_sec, fecha_emision="2026-01-20")
        print(f"\n🏷️ SECTOR: {orden.sector_nombre}")
        print(f"   Cultivo: {orden.cultivo_nombre} ({orden.fenofase})")
        print(f"   Lámina Bruta a Reponer: {orden.lamina_bruta_mm:.1f} mm")
        print(f"   ⏱️ TIEMPO DE RIEGO POR POSTURA: {orden.tiempo_formato} ({orden.horas_decimales} h)")
        print(f"   💧 Volumen de Agua Requerido: {orden.volumen_m3:,.0f} m³")
        print(f"   ⚡ Caudal: {orden.caudal_m3_h:.1f} m³/h | Bomba Requerida: {orden.potencia_hp:.1f} HP | Consumo: {orden.consumo_kwh:.1f} kWh")
        print("   📌 Recomendaciones:")
        for r in orden.recomendaciones[:2]:
            print(f"      • {r}")
        print("-" * 80)


if __name__ == "__main__":
    simular_predio_modelo()
