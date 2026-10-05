"""
Suite de Pruebas Unitarias: Agente de Riego Agrícola de Precisión
================================================================
Verifica la exactitud matemática y biofísica de todos los módulos.
Ejecución: python -m unittest 05_Scripts/agente_riego/test_agente_riego.py

Autor: Cristián González Huenchún & Antigravity
"""

import unittest
from pathlib import Path
import sys

# Agregar ruta al sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from smart_irrigation import (
    calcular_et0_penman_monteith,
    calcular_et0_hargreaves,
    calcular_vpd,
    Suelo,
    Cultivo,
    SectorRiego,
    AgenteRiego,
    calcular_potencia_bomba
)


class TestAgenteRiego(unittest.TestCase):

    def test_penman_monteith_realista(self):
        """Verifica que el cálculo FAO-56 de ET0 arroje valores coherentes para verano central."""
        res = calcular_et0_penman_monteith(
            tmax_c=32.0,
            tmin_c=14.0,
            rh_mean_pct=45.0,
            viento_2m_m_s=2.0,
            radiacion_solar_mj_m2_dia=27.0,
            latitud_grados=-34.0,
            altitud_m=300.0,
            dia_del_ano=15
        )
        self.assertIn("et0_mm_dia", res)
        # En verano en Chile central, ET0 oscila típicamente entre 5.0 y 7.5 mm/día
        self.assertGreater(res["et0_mm_dia"], 4.5)
        self.assertLess(res["et0_mm_dia"], 8.0)
        self.assertGreater(res["vpd_kpa"], 1.0)

    def test_hargreaves_simplificado(self):
        """Verifica la aproximación de Hargreaves."""
        et0 = calcular_et0_hargreaves(tmax_c=30.0, tmin_c=12.0, latitud_grados=-34.0, dia_del_ano=15)
        self.assertGreater(et0, 4.0)
        self.assertLess(et0, 8.5)

    def test_edafologia_cad_y_afa(self):
        """Verifica el cálculo de retención hídrica en suelo Franco con pedregosidad."""
        suelo = Suelo(textura="Franco", profundidad_raices_m=0.80, pedregosidad_pct=20.0)
        # CC = 24%, PMP = 11% -> Retención = 13% = 0.13
        # Profundidad = 800 mm
        # Factor tierra fina = 0.80
        # CAD = 0.13 * 800 * 0.80 = 83.2 mm
        self.assertAlmostEqual(suelo.cad_mm, 83.2, places=1)
        afa = suelo.afa_mm(0.40)
        self.assertAlmostEqual(afa, 83.2 * 0.40, places=1)

    def test_fisiologia_kc_y_rdc(self):
        """Verifica que el RDC reduzca adecuadamente el Kc en vid tinta."""
        vid_estandar = Cultivo("Vid_Vinifera_Tinta", "Cuaja_a_Envero", aplicar_rdc=False)
        self.assertEqual(vid_estandar.kc_actual, 0.50)

        vid_rdc = Cultivo("Vid_Vinifera_Tinta", "Cuaja_a_Envero", aplicar_rdc=True)
        self.assertEqual(vid_rdc.kc_actual, 0.38)
        self.assertLess(vid_rdc.kc_actual, vid_estandar.kc_actual)

    def test_evaluacion_sensor_scholander(self):
        """Verifica la escala de diagnóstico con cámara de presión."""
        vid = Cultivo("Vid_Vinifera_Tinta", "Cuaja_a_Envero", aplicar_rdc=True)
        # Caso confort
        eval_confort = vid.evaluar_sensor_scholander(-0.80)
        self.assertEqual(eval_confort["factor_ks"], 1.0)

        # Caso RDC óptimo
        eval_rdc = vid.evaluar_sensor_scholander(-1.15)
        self.assertEqual(eval_rdc["factor_ks"], 0.85)

        # Caso estrés severo
        eval_severo = vid.evaluar_sensor_scholander(-1.55)
        self.assertEqual(eval_severo["factor_ks"], 0.65)

    def test_hidraulica_sector_y_potencia(self):
        """Verifica la precipitación del sistema, caudal total y potencia de bombeo."""
        sector = SectorRiego(
            nombre="Sector Test",
            superficie_ha=4.0,
            distancia_hileras_m=2.50,
            distancia_plantas_m=1.00,
            caudal_emisor_l_h=2.0,
            espaciamiento_emisores_m=0.50,
            lineas_por_hilera=1,
            presion_trabajo_bar=1.5
        )
        # Ph = 2.0 / (2.5 * 0.5) = 2.0 / 1.25 = 1.60 mm/h
        self.assertAlmostEqual(sector.precipitación_horaria_mm_h, 1.60, places=2)
        # Q = 1.60 * 4.0 * 10 = 64.0 m3/h
        self.assertAlmostEqual(sector.caudal_total_m3_h, 64.0, places=1)

        bomba = sector.calcular_dimensionamiento_motor()
        self.assertGreater(bomba["potencia_hp"], 5.0)
        self.assertGreater(bomba["hmt_mca"], 20.0)

    def test_flujo_completo_agente_y_orden(self):
        """Verifica el ciclo completo de simulación y emisión de orden Markdown."""
        agente = AgenteRiego("Viña Central")
        sec = SectorRiego("Sector 1", superficie_ha=2.0, caudal_emisor_l_h=2.0, espaciamiento_emisores_m=0.5)
        suelo = Suelo("Franco", profundidad_raices_m=0.6)
        cultivo = Cultivo("Vid_Vinifera_Tinta", "Cuaja_a_Envero", aplicar_rdc=True)

        agente.registrar_cuartel("S1", sec, suelo, cultivo)
        balance = agente.procesar_balance_diario("S1", "2026-01-10", et0_mm=6.0)

        self.assertIn("balance", balance)
        self.assertGreater(balance["deficit_acumulado_mm"], 0.0)

        orden = agente.emitir_orden_riego("S1")
        md = orden.generar_markdown()
        self.assertIn("# 💧 Orden de Riego: Sector 1", md)
        self.assertIn("Tiempo de Riego Requerido", md)


if __name__ == "__main__":
    unittest.main()
