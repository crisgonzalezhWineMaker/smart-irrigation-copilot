"""
Módulo Hidráulica Agrícola & Ingeniería de Riego Tecnificado
============================================================
Cálculo de parámetros hidráulicos de campo: precipitación horaria (mm/h), caudal del sector,
número de emisores, porcentaje de suelo mojado (Pw) y dimensionamiento de grupos motobomba
(Caudal en m3/h, Altura Manométrica Total HMT, Potencia en HP/kW y consumo energético).

Autor: Cristián González Huenchún & Antigravity
"""

import math
from typing import Dict, Any, Optional


def calcular_potencia_bomba(
    caudal_m3_h: float,
    hmt_mca: float,
    eficiencia_bomba: float = 0.72,
    eficiencia_motor: float = 0.90
) -> Dict[str, float]:
    """
    Calcula la potencia hidráulica y de placa del motor de bombeo.

    Fórmula: Potencia (HP) = (Q [m3/h] * HMT [m]) / (270 * eta_bomba * eta_motor)
    Potencia (kW) = Potencia (HP) * 0.7457

    Args:
        caudal_m3_h: Caudal total volumétrico en m3/h.
        hmt_mca: Altura Manométrica Total en metros de columna de agua (m.c.a.).
        eficiencia_bomba: Rendimiento hidráulico de la bomba (típico 0.65 - 0.78).
        eficiencia_motor: Rendimiento eléctrico del motor (típico 0.88 - 0.94).

    Returns:
        Diccionario con potencia en HP, kW, caudal en L/s y consumo por hora en kWh.
    """
    if caudal_m3_h <= 0 or hmt_mca <= 0:
        raise ValueError("Caudal y HMT deben ser mayores a 0.")

    eta_global = max(0.2, min(0.95, eficiencia_bomba * eficiencia_motor))
    potencia_hp = (caudal_m3_h * hmt_mca) / (270.0 * eta_global)
    potencia_kw = potencia_hp * 0.7457
    caudal_l_s = caudal_m3_h / 3.6

    return {
        "caudal_m3_h": round(caudal_m3_h, 2),
        "caudal_l_s": round(caudal_l_s, 2),
        "hmt_mca": round(hmt_mca, 2),
        "potencia_hp": round(potencia_hp, 2),
        "potencia_kw": round(potencia_kw, 2),
        "consumo_kwh_por_hora": round(potencia_kw, 2)
    }


class SectorRiego:
    """
    Modela un sector, válvula o cuartel de riego tecnificado (goteo o microaspersión).
    """

    def __init__(
        self,
        nombre: str = "Sector 1",
        superficie_ha: float = 5.0,
        distancia_hileras_m: float = 2.50,
        distancia_plantas_m: float = 1.00,
        caudal_emisor_l_h: float = 2.0,
        espaciamiento_emisores_m: float = 0.50,
        lineas_por_hilera: int = 1,
        eficiencia_aplicacion_ea: float = 0.90,
        presion_trabajo_bar: float = 1.5,
        desnivel_topografico_m: float = 5.0,
        perdidas_friccion_m: float = 8.0,
        perdidas_cabezal_m: float = 7.0
    ) -> None:
        self.nombre = nombre
        self.superficie_ha = max(0.1, superficie_ha)
        self.distancia_hileras_m = max(0.5, distancia_hileras_m)
        self.distancia_plantas_m = max(0.3, distancia_plantas_m)
        self.caudal_emisor_l_h = max(0.2, caudal_emisor_l_h)
        self.espaciamiento_emisores_m = max(0.1, espaciamiento_emisores_m)
        self.lineas_por_hilera = max(1, lineas_por_hilera)
        self.eficiencia_ea = min(0.98, max(0.60, eficiencia_aplicacion_ea))

        # Parámetros hidráulicos de presión y bombeo
        self.presion_trabajo_bar = max(0.5, presion_trabajo_bar)
        self.desnivel_m = desnivel_topografico_m
        self.perdidas_friccion_m = max(1.0, perdidas_friccion_m)
        self.perdidas_cabezal_m = max(2.0, perdidas_cabezal_m)

    @property
    def densidad_plantas_ha(self) -> float:
        """Número de plantas por hectárea."""
        return 10000.0 / (self.distancia_hileras_m * self.distancia_plantas_m)

    @property
    def precipitación_horaria_mm_h(self) -> float:
        """
        Precipitación horaria del sistema en mm/h (o L/m2/h):
        Ph (mm/h) = (Caudal_emisor [L/h] * Líneas) / (Dist_hileras [m] * Espaciamiento_emisores [m])
        """
        area_por_emisor = (self.distancia_hileras_m * self.espaciamiento_emisores_m) / float(self.lineas_por_hilera)
        ph = self.caudal_emisor_l_h / area_por_emisor
        return round(max(0.1, ph), 2)

    @property
    def caudal_total_m3_h(self) -> float:
        """
        Caudal instantáneo demandado por el sector en m3/h:
        Q (m3/h) = Ph (mm/h) * Superficie (ha) * 10
        """
        return round(self.precipitación_horaria_mm_h * self.superficie_ha * 10.0, 2)

    @property
    def caudal_total_l_s(self) -> float:
        """Caudal del sector en Litros por segundo."""
        return round(self.caudal_total_m3_h / 3.6, 2)

    @property
    def hmt_mca(self) -> float:
        """
        Altura Manométrica Total requerida en cabezal de impulsión:
        HMT (m.c.a.) = (Presión_emisor [bar] * 10.2) + Desnivel + Pérdidas_tuberías + Pérdidas_filtro
        """
        presion_emisor_mca = self.presion_trabajo_bar * 10.197
        return round(presion_emisor_mca + self.desnivel_m + self.perdidas_friccion_m + self.perdidas_cabezal_m, 2)

    def calcular_dimensionamiento_motor(
        self,
        eficiencia_bomba: float = 0.72,
        eficiencia_motor: float = 0.90
    ) -> Dict[str, float]:
        """Calcula los requerimientos de potencia del motor para este sector."""
        return calcular_potencia_bomba(
            caudal_m3_h=self.caudal_total_m3_h,
            hmt_mca=self.hmt_mca,
            eficiencia_bomba=eficiencia_bomba,
            eficiencia_motor=eficiencia_motor
        )

    def calcular_tiempo_riego(self, lamina_bruta_mm: float) -> Dict[str, Any]:
        """
        Calcula las horas de riego requeridas para aplicar una lámina bruta determinada:
        Tiempo (h) = Lámina_Bruta (mm) / Precipitación_Horaria (mm/h)
        """
        ph = self.precipitación_horaria_mm_h
        horas = lamina_bruta_mm / ph if ph > 0 else 0.0
        horas_enteras = int(horas)
        minutos = int(round((horas - horas_enteras) * 60))

        volumen_m3 = (lamina_bruta_mm * 10.0) * self.superficie_ha

        return {
            "lamina_bruta_mm": round(lamina_bruta_mm, 2),
            "horas_decimales": round(horas, 2),
            "formato_tiempo": f"{horas_enteras} h {minutos:02d} min",
            "volumen_total_m3": round(volumen_m3, 1),
            "precipitacion_sistema_mm_h": ph
        }
