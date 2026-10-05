"""
Módulo Edafología & Hidrofísica de Suelos Agrícolas
===================================================
Parámetros físicos y dinámicos del perfil de suelo según la clasificación USDA:
Capacidad de Campo (CC), Punto de Marchitez Permanente (PMP), Densidad Aparente (Da),
Capacidad de Agua Disponible (CAD), Agua Fácilmente Aprovechable (AFA) y corrección por pedregosidad.

Autor: Cristián González Huenchún & Antigravity
"""

from typing import Dict, Any, Optional

# Parámetros hidrofísicos estándar por clase textural USDA
TEXTURAS_USDA: Dict[str, Dict[str, Any]] = {
    "Arenoso": {
        "cc_pct": 10.0,
        "pmp_pct": 4.0,
        "da_g_cm3": 1.55,
        "infiltracion_basica_mm_h": 40.0,
        "descripcion": "Alta macroporosidad, drenaje excesivo, retención mínima. Requiere pulsos cortos y frecuentes."
    },
    "Franco_Arenoso": {
        "cc_pct": 18.0,
        "pmp_pct": 8.0,
        "da_g_cm3": 1.45,
        "infiltracion_basica_mm_h": 25.0,
        "descripcion": "Excelente aireación, permeabilidad media-alta. Común en terrazas fluviales y aluviales."
    },
    "Franco": {
        "cc_pct": 24.0,
        "pmp_pct": 11.0,
        "da_g_cm3": 1.35,
        "infiltracion_basica_mm_h": 15.0,
        "descripcion": "Equilibrio ideal suelo-agua-aire. Gran versatilidad para frutales y viñedos de alta gama."
    },
    "Franco_Limoso": {
        "cc_pct": 28.0,
        "pmp_pct": 13.0,
        "da_g_cm3": 1.30,
        "infiltracion_basica_mm_h": 10.0,
        "descripcion": "Alta retención de humedad, tendencia a formar costras superficiales si hay laboreo."
    },
    "Franco_Arcilloso": {
        "cc_pct": 31.0,
        "pmp_pct": 16.0,
        "da_g_cm3": 1.30,
        "infiltracion_basica_mm_h": 8.0,
        "descripcion": "Buena retención hídrica, drenaje moderado a lento. Típico en valles centrales (Maipo, Colchagua)."
    },
    "Franco_Arcillo_Arenoso": {
        "cc_pct": 27.0,
        "pmp_pct": 14.0,
        "da_g_cm3": 1.38,
        "infiltracion_basica_mm_h": 12.0,
        "descripcion": "Transición entre depósitos de ladera y fondos de valle con drenaje balanceado."
    },
    "Arcilloso": {
        "cc_pct": 36.0,
        "pmp_pct": 21.0,
        "da_g_cm3": 1.25,
        "infiltracion_basica_mm_h": 4.0,
        "descripcion": "Máxima microporosidad, alta retención pero riesgo severo de asfixia radicular (Phytophthora) si se sobre-riega."
    }
}


class Suelo:
    """
    Representa las propiedades hidrofísicas del perfil de suelo en un cuartel agrícola.
    """

    def __init__(
        self,
        textura: str = "Franco",
        profundidad_raices_m: float = 0.60,
        pedregosidad_pct: float = 10.0,
        cc_custom_pct: Optional[float] = None,
        pmp_custom_pct: Optional[float] = None,
        da_custom_g_cm3: Optional[float] = None
    ) -> None:
        self.textura = textura if textura in TEXTURAS_USDA else "Franco"
        base = TEXTURAS_USDA[self.textura]

        self.cc_pct = float(cc_custom_pct if cc_custom_pct is not None else base["cc_pct"])
        self.pmp_pct = float(pmp_custom_pct if pmp_custom_pct is not None else base["pmp_pct"])
        self.da_g_cm3 = float(da_custom_g_cm3 if da_custom_g_cm3 is not None else base["da_g_cm3"])
        self.infiltracion_mm_h = float(base["infiltracion_basica_mm_h"])

        self.profundidad_raices_m = max(0.1, profundidad_raices_m)
        self.pedregosidad_pct = min(90.0, max(0.0, pedregosidad_pct))

    @property
    def factor_tierra_fina(self) -> float:
        """Fracción de suelo libre de piedras y gravas (capaz de almacenar agua)."""
        return 1.0 - (self.pedregosidad_pct / 100.0)

    @property
    def cad_mm(self) -> float:
        """
        Capacidad de Agua Disponible (CAD o Humedad Aprovechable HA) en el perfil radicular:
        CAD (mm) = ((CC% - PMP%) / 100) * Profundidad (mm) * Factor_Tierra_Fina
        """
        prof_mm = self.profundidad_raices_m * 1000.0
        retencion_vol = (self.cc_pct - self.pmp_pct) / 100.0
        cad = retencion_vol * prof_mm * self.factor_tierra_fina
        return round(max(5.0, cad), 1)

    def afa_mm(self, factor_agotamiento_p: float = 0.40) -> float:
        """
        Agua Fácilmente Aprovechable (AFA o Lámina de Riego Permitida) en mm:
        AFA = CAD * p
        Donde p es la fracción de agotamiento permisible antes de que la planta sufra estrés hídrico.
        """
        p = min(0.9, max(0.1, factor_agotamiento_p))
        return round(self.cad_mm * p, 1)

    def diagnostico_humedad_actual(self, humedad_vol_actual_pct: float) -> Dict[str, Any]:
        """
        Evalúa el estado hídrico del perfil a partir de una sonda FDR/TDR de terreno.
        """
        theta = humedad_vol_actual_pct
        prof_mm = self.profundidad_raices_m * 1000.0

        if theta >= self.cc_pct:
            estado = "💧 Saturación / Capacidad de Campo"
            accion = "No regar. Riesgo de asfixia radicular si persiste."
            lamina_deficit_mm = 0.0
        elif theta <= self.pmp_pct:
            estado = "🚨 Punto de Marchitez Permanente (PMP)"
            accion = "Alerta crítica: Estrés severo con marchitamiento irreversible."
            lamina_deficit_mm = ((self.cc_pct - theta) / 100.0) * prof_mm * self.factor_tierra_fina
        else:
            pct_disponible = ((theta - self.pmp_pct) / (self.cc_pct - self.pmp_pct)) * 100.0
            lamina_deficit_mm = ((self.cc_pct - theta) / 100.0) * prof_mm * self.factor_tierra_fina
            if pct_disponible > 60.0:
                estado = "🟢 Humedad Óptima"
                accion = "Humedad en rango confortable para la raíz."
            elif pct_disponible >= 40.0:
                estado = "🟡 Nivel de Riego Oportuno (Umbral URD)"
                accion = "Programar riego para reponer la lámina de déficit."
            else:
                estado = "🟠 Estrés Hídrico Moderado"
                accion = "Regar con urgencia si no se está aplicando Riego Deficitario Controlado."

        return {
            "humedad_vol_pct": round(theta, 1),
            "cad_mm": self.cad_mm,
            "lamina_deficit_mm": round(max(0.0, lamina_deficit_mm), 1),
            "estado": estado,
            "accion_recomendada": accion
        }
