"""
Módulo Climatología & Demanda Atmosférica (FAO-56 Penman-Monteith)
==================================================================
Implementación física y matemática del estándar internacional FAO-56 para el
cálculo de Evapotranspiración de Referencia (ET0), Déficit de Presión de Vapor (VPD)
y Precipitación Efectiva (Pe) ajustada a las macro-zonas agrícolas de Chile.

Autor: Cristián González Huenchún & Antigravity
"""

import math
from typing import Dict, Any, Optional

# Constantes físicas universales FAO-56
CONSTANTE_SOLAR = 0.0820  # MJ m-2 min-1
STEFAN_BOLTZMANN = 4.903e-9  # MJ K-4 m-2 d-1

# Macro-zonas agroclimáticas de Chile con valores típicos estacionales
ZONAS_CHILE: Dict[str, Dict[str, Any]] = {
    "Copiapo": {
        "region": "Atacama (III)",
        "latitud": -27.36,
        "altitud_m": 390,
        "et0_verano_dia": 6.8,
        "et0_primavera_dia": 4.5,
        "clima": "Desértico cálido con extrema radiación y HR baja",
        "cultivos_clave": ["Uva de Mesa", "Olivos", "Granados"]
    },
    "Limari_Ovalle": {
        "region": "Coquimbo (IV)",
        "latitud": -30.60,
        "altitud_m": 230,
        "et0_verano_dia": 5.9,
        "et0_primavera_dia": 4.0,
        "clima": "Semiárido templado de interior, alta radiación",
        "cultivos_clave": ["Cítricos", "Paltos", "Vid Vinífera", "Nogales"]
    },
    "Aconcagua_SanFelipe": {
        "region": "Valparaíso (V)",
        "latitud": -32.75,
        "altitud_m": 650,
        "et0_verano_dia": 6.2,
        "et0_primavera_dia": 4.2,
        "clima": "Mediterráneo continental cálido",
        "cultivos_clave": ["Uva de Mesa", "Paltos", "Nogales", "Cerezos"]
    },
    "Maipo_Pirque": {
        "region": "Metropolitana (RM)",
        "latitud": -33.67,
        "altitud_m": 660,
        "et0_verano_dia": 5.8,
        "et0_primavera_dia": 3.8,
        "clima": "Mediterráneo con influencia de piedemonte andino",
        "cultivos_clave": ["Vid Vinífera (Cabernet)", "Nogales", "Almendros"]
    },
    "Cachapoal_Millahue": {
        "region": "O'Higgins (VI)",
        "latitud": -34.33,
        "altitud_m": 320,
        "et0_verano_dia": 5.5,
        "et0_primavera_dia": 3.7,
        "clima": "Mediterráneo subhúmedo cálido, brisa de valle",
        "cultivos_clave": ["Vid Vinífera (Alta Gama)", "Cerezos", "Cítricos"]
    },
    "Colchagua_SantaCruz": {
        "region": "O'Higgins (VI)",
        "latitud": -34.63,
        "altitud_m": 160,
        "et0_verano_dia": 5.4,
        "et0_primavera_dia": 3.6,
        "clima": "Mediterráneo cálido con amplitud térmica",
        "cultivos_clave": ["Vid Vinífera", "Cerezos", "Olivos", "Ciruelos"]
    },
    "Curico_SagradaFamilia": {
        "region": "Maule (VII)",
        "latitud": -35.00,
        "altitud_m": 220,
        "et0_verano_dia": 5.2,
        "et0_primavera_dia": 3.4,
        "clima": "Mediterráneo templado con alta inversión en cerezos",
        "cultivos_clave": ["Cerezos", "Manzanos", "Vid Vinífera", "Kiwis"]
    },
    "Nuble_Chillan": {
        "region": "Ñuble (XVI)",
        "latitud": -36.60,
        "altitud_m": 140,
        "et0_verano_dia": 4.8,
        "et0_primavera_dia": 3.1,
        "clima": "Mediterráneo húmedo de transición",
        "cultivos_clave": ["Arándanos", "Cerezos", "Avellano Europeo", "Viñedos"]
    }
}


def presion_vapor_saturacion(temp_c: float) -> float:
    """Calcula la presión de vapor de saturación e°(T) en kPa según Tetens."""
    return 0.61078 * math.exp((17.27 * temp_c) / (temp_c + 237.3))


def calcular_vpd(tmax_c: float, tmin_c: float, rh_mean_pct: float) -> Dict[str, float]:
    """
    Calcula el Déficit de Presión de Vapor (VPD) atmosférico en kPa.
    VPD = es - ea.
    Indica la fuerza secante del aire que tracciona la transpiración de los estomas.
    """
    es_tmax = presion_vapor_saturacion(tmax_c)
    es_tmin = presion_vapor_saturacion(tmin_c)
    es = (es_tmax + es_tmin) / 2.0
    ea = es * (rh_mean_pct / 100.0)
    vpd = max(0.0, es - ea)

    # Diagnóstico del nivel de VPD para frutales y vides
    if vpd < 0.5:
        estado = "Muy Bajo (Saturación/Riesgo fúngico)"
    elif vpd <= 1.5:
        estado = "Óptimo para fotosíntesis y transpiración"
    elif vpd <= 2.5:
        estado = "Moderado a Alto (Cierre estomático parcial)"
    else:
        estado = "Severo / Extremo (Cierre estomático y estrés térmico)"

    return {
        "es_kpa": round(es, 3),
        "ea_kpa": round(ea, 3),
        "vpd_kpa": round(vpd, 3),
        "diagnostico": estado
    }


def calcular_et0_penman_monteith(
    tmax_c: float,
    tmin_c: float,
    rh_mean_pct: float,
    viento_2m_m_s: float,
    radiacion_solar_mj_m2_dia: float,
    latitud_grados: float = -34.0,
    altitud_m: float = 300.0,
    dia_del_ano: int = 15
) -> Dict[str, Any]:
    """
    Calcula la Evapotranspiración de Referencia (ET0) diaria en mm/día según la ecuación
    estándar de FAO-56 Penman-Monteith.

    Args:
        tmax_c: Temperatura máxima diaria (°C).
        tmin_c: Temperatura mínima diaria (°C).
        rh_mean_pct: Humedad relativa media diaria (%).
        viento_2m_m_s: Velocidad media del viento a 2 m de altura (m/s).
        radiacion_solar_mj_m2_dia: Radiación solar global medida en estación (MJ/m2/día).
        latitud_grados: Latitud en grados decimales (negativo en hemisferio sur, ej. -34.0).
        altitud_m: Altura sobre el nivel del mar en metros.
        dia_del_ano: Día juliano del año (1 a 365).

    Returns:
        Diccionario con ET0 (mm/día), radiación neta (Rn), VPD y parámetros intermedios.
    """
    tmean = (tmax_c + tmin_c) / 2.0

    # 1. Presión atmosférica P (kPa)
    p = 101.3 * math.pow((293.0 - 0.0065 * altitud_m) / 293.0, 5.26)

    # 2. Constante psicrométrica gamma (kPa/°C)
    gamma = 0.000665 * p

    # 3. Pendiente de la curva de presión de saturación de vapor Delta (kPa/°C)
    es_tmean = presion_vapor_saturacion(tmean)
    delta = (4098.0 * es_tmean) / math.pow(tmean + 237.3, 2)

    # 4. Presión de vapor de saturación media (es) y real (ea)
    es_tmax = presion_vapor_saturacion(tmax_c)
    es_tmin = presion_vapor_saturacion(tmin_c)
    es = (es_tmax + es_tmin) / 2.0
    ea = es * (rh_mean_pct / 100.0)

    # 5. Radiación extraterrestre Ra (MJ m-2 d-1)
    phi = (math.pi / 180.0) * latitud_grados
    dr = 1.0 + 0.033 * math.cos((2.0 * math.pi / 365.0) * dia_del_ano)
    delta_sol = 0.409 * math.sin((2.0 * math.pi / 365.0) * dia_del_ano - 1.39)
    ws = math.acos(-math.tan(phi) * math.tan(delta_sol))
    ra = ((24.0 * 60.0) / math.pi) * CONSTANTE_SOLAR * dr * (
        ws * math.sin(phi) * math.sin(delta_sol) +
        math.cos(phi) * math.cos(delta_sol) * math.sin(ws)
    )

    # 6. Radiación solar de cielo despejado Rso (MJ m-2 d-1)
    rso = (0.75 + 2e-5 * altitud_m) * ra
    rs = radiacion_solar_mj_m2_dia

    # 7. Radiación neta de onda corta Rns (albedo de pasto de referencia = 0.23)
    rns = (1.0 - 0.23) * rs

    # 8. Radiación neta de onda larga Rnl (MJ m-2 d-1)
    tmax_k4 = math.pow(tmax_c + 273.16, 4)
    tmin_k4 = math.pow(tmin_c + 273.16, 4)
    ratio_rs = min(1.0, max(0.3, rs / rso if rso > 0 else 0.7))
    rnl = STEFAN_BOLTZMANN * ((tmax_k4 + tmin_k4) / 2.0) * (0.34 - 0.14 * math.sqrt(max(0.0, ea))) * (1.35 * ratio_rs - 0.35)

    # 9. Radiación neta total Rn (MJ m-2 d-1)
    rn = rns - rnl
    g = 0.0  # Para periodos diarios, flujo de calor del suelo G ~ 0

    # 10. Ecuación combinada FAO-56
    u2 = max(0.5, viento_2m_m_s)
    numerador = 0.408 * delta * (rn - g) + gamma * (900.0 / (tmean + 273.0)) * u2 * (es - ea)
    denominador = delta + gamma * (1.0 + 0.34 * u2)

    et0 = max(0.1, numerador / denominador)

    return {
        "et0_mm_dia": round(et0, 2),
        "tmean_c": round(tmean, 1),
        "vpd_kpa": round(es - ea, 3),
        "rn_mj_m2": round(rn, 2),
        "ra_mj_m2": round(ra, 2),
        "presion_kpa": round(p, 1),
        "metodo": "FAO-56 Penman-Monteith"
    }


def calcular_et0_hargreaves(
    tmax_c: float,
    tmin_c: float,
    latitud_grados: float = -34.0,
    dia_del_ano: int = 15
) -> float:
    """
    Alternativa rápida de Hargreaves-Samani cuando solo se dispone de sensores
    de temperatura (Tmax y Tmin). Útil para estaciones meteorológicas rústicas.
    """
    tmean = (tmax_c + tmin_c) / 2.0
    phi = (math.pi / 180.0) * latitud_grados
    dr = 1.0 + 0.033 * math.cos((2.0 * math.pi / 365.0) * dia_del_ano)
    delta_sol = 0.409 * math.sin((2.0 * math.pi / 365.0) * dia_del_ano - 1.39)
    ws = math.acos(-math.tan(phi) * math.tan(delta_sol))
    ra = ((24.0 * 60.0) / math.pi) * CONSTANTE_SOLAR * dr * (
        ws * math.sin(phi) * math.sin(delta_sol) +
        math.cos(phi) * math.cos(delta_sol) * math.sin(ws)
    )
    # Convertir Ra de MJ m-2 d-1 a mm/día (1 mm ~ 2.45 MJ m-2)
    ra_mm = ra / 2.45
    delta_t = max(0.0, tmax_c - tmin_c)
    et0 = 0.0023 * (tmean + 17.8) * math.sqrt(delta_t) * ra_mm
    return round(max(0.2, et0), 2)


def calcular_precipitacion_efectiva(precipitacion_total_mm: float) -> float:
    """
    Calcula la fracción de lluvia que efectivamente queda almacenada en el suelo
    aprovechable por las raíces, según el método USDA Soil Conservation Service (SCS).
    """
    p = max(0.0, precipitacion_total_mm)
    if p <= 5.0:
        # Lluvias menores a 5 mm en verano se evaporan directamente de la canopia/suelo
        return 0.0
    elif p <= 250.0:
        pe = (p * (125.0 - 0.2 * p)) / 125.0
    else:
        pe = 125.0 + 0.1 * p
    return round(max(0.0, pe), 2)
