"""
Módulo Fisiología Vegetal & Coeficientes de Cultivo (Kc) para Chile
===================================================================
Base de datos agronómica de especies frutales y vitícolas de Chile:
Vid Vinífera, Uva de Mesa, Cerezos, Nogales, Paltos, Cítricos y Olivos.
Modelación de curvas de Kc fenológicas, estrategias de Riego Deficitario Controlado (RDC)
e integración de sensores de planta (Cámara de Presión Scholander).

Autor: Cristián González Huenchún & Antigravity
"""

from typing import Dict, Any, List, Optional

# Base de datos agronómica de especies cultivadas en Chile
CULTIVOS_CHILE: Dict[str, Dict[str, Any]] = {
    "Vid_Vinifera_Tinta": {
        "nombre_comun": "Vid Vinífera Tinta (Cabernet, Carmenere, Syrah)",
        "especie": "Vitis vinifera L.",
        "profundidad_raices_optima_m": 0.80,
        "factor_agotamiento_p": 0.45,
        "estrategia_riego": "Riego Deficitario Controlado (RDC) post-cuaja a envero",
        "psi_tallo_optimo_rdi_mpa": -1.10,
        "psi_tallo_limite_estres_mpa": -1.40,
        "fenofases": {
            "Brotacion_a_Floracion": {"kc": 0.25, "duracion_dias": 45, "rdc_permitido": False},
            "Floracion_a_Cuaja": {"kc": 0.40, "duracion_dias": 25, "rdc_permitido": False},
            "Cuaja_a_Envero": {"kc": 0.50, "duracion_dias": 50, "rdc_permitido": True, "kc_rdc": 0.38},
            "Envero_a_Cosecha": {"kc": 0.45, "duracion_dias": 60, "rdc_permitido": True, "kc_rdc": 0.35},
            "Poscosecha": {"kc": 0.55, "duracion_dias": 40, "rdc_permitido": False}
        }
    },
    "Vid_Vinifera_Blanca": {
        "nombre_comun": "Vid Vinífera Blanca (Chardonnay, Sauvignon Blanc)",
        "especie": "Vitis vinifera L.",
        "profundidad_raices_optima_m": 0.70,
        "factor_agotamiento_p": 0.40,
        "estrategia_riego": "Estrés hídrico muy leve; preservar acidez y tioles",
        "psi_tallo_optimo_rdi_mpa": -0.85,
        "psi_tallo_limite_estres_mpa": -1.20,
        "fenofases": {
            "Brotacion_a_Floracion": {"kc": 0.25, "duracion_dias": 45, "rdc_permitido": False},
            "Floracion_a_Cuaja": {"kc": 0.45, "duracion_dias": 25, "rdc_permitido": False},
            "Cuaja_a_Envero": {"kc": 0.60, "duracion_dias": 45, "rdc_permitido": False},
            "Envero_a_Cosecha": {"kc": 0.55, "duracion_dias": 45, "rdc_permitido": False},
            "Poscosecha": {"kc": 0.50, "duracion_dias": 40, "rdc_permitido": False}
        }
    },
    "Uva_de_Mesa": {
        "nombre_comun": "Uva de Mesa (Crimson, Thompson, Sweet Globe)",
        "especie": "Vitis vinifera L.",
        "profundidad_raices_optima_m": 0.75,
        "factor_agotamiento_p": 0.35,
        "estrategia_riego": "Riego sin restricción para maximizar calibre de baya",
        "psi_tallo_optimo_rdi_mpa": -0.75,
        "psi_tallo_limite_estres_mpa": -1.10,
        "fenofases": {
            "Brotacion_a_Floracion": {"kc": 0.30, "duracion_dias": 40, "rdc_permitido": False},
            "Floracion_a_Cuaja": {"kc": 0.55, "duracion_dias": 20, "rdc_permitido": False},
            "Crecimiento_Baya_I": {"kc": 0.75, "duracion_dias": 35, "rdc_permitido": False},
            "Envero_a_Cosecha": {"kc": 0.85, "duracion_dias": 45, "rdc_permitido": False},
            "Poscosecha": {"kc": 0.60, "duracion_dias": 40, "rdc_permitido": False}
        }
    },
    "Cerezos": {
        "nombre_comun": "Cerezos (Lapins, Santina, Regina, Bing)",
        "especie": "Prunus avium L.",
        "profundidad_raices_optima_m": 0.85,
        "factor_agotamiento_p": 0.35,
        "estrategia_riego": "Confort total pre-cosecha; RDC en poscosecha para ahorro de agua",
        "psi_tallo_optimo_rdi_mpa": -1.25,  # En poscosecha
        "psi_tallo_limite_estres_mpa": -1.60,
        "fenofases": {
            "Brotacion_a_Floracion": {"kc": 0.40, "duracion_dias": 30, "rdc_permitido": False},
            "Caida_Chaqueta_a_Carozo": {"kc": 0.75, "duracion_dias": 35, "rdc_permitido": False},
            "Llenado_Fruto_a_Cosecha": {"kc": 0.95, "duracion_dias": 30, "rdc_permitido": False},
            "Poscosecha_Temprana": {"kc": 0.80, "duracion_dias": 45, "rdc_permitido": True, "kc_rdc": 0.55},
            "Poscosecha_Tardia": {"kc": 0.65, "duracion_dias": 45, "rdc_permitido": True, "kc_rdc": 0.45}
        }
    },
    "Nogales": {
        "nombre_comun": "Nogales (Chandler, Serr)",
        "especie": "Juglans regia L.",
        "profundidad_raices_optima_m": 1.10,
        "factor_agotamiento_p": 0.40,
        "estrategia_riego": "Alta demanda en llenado de nuez (Ene-Feb); evitar asfixia",
        "psi_tallo_optimo_rdi_mpa": -0.80,
        "psi_tallo_limite_estres_mpa": -1.20,
        "fenofases": {
            "Foliacion_a_Floracion": {"kc": 0.40, "duracion_dias": 35, "rdc_permitido": False},
            "Cuaja_a_Tamano_Final": {"kc": 0.85, "duracion_dias": 50, "rdc_permitido": False},
            "Llenado_Pulpa_Kernel": {"kc": 1.10, "duracion_dias": 60, "rdc_permitido": False},
            "Maduracion_a_Cosecha": {"kc": 0.80, "duracion_dias": 35, "rdc_permitido": False},
            "Poscosecha": {"kc": 0.55, "duracion_dias": 30, "rdc_permitido": False}
        }
    },
    "Paltos": {
        "nombre_comun": "Paltos / Aguacate (Hass)",
        "especie": "Persea americana Mill.",
        "profundidad_raices_optima_m": 0.50,  # Raíces superficiales
        "factor_agotamiento_p": 0.30,  # Riego muy frecuente
        "estrategia_riego": "Pulsos cortos de alta frecuencia; cero tolerancia a asfixia",
        "psi_tallo_optimo_rdi_mpa": -0.65,
        "psi_tallo_limite_estres_mpa": -0.95,
        "fenofases": {
            "Floracion_y_Cuaja": {"kc": 0.65, "duracion_dias": 60, "rdc_permitido": False},
            "Crecimiento_Fruto_Verano": {"kc": 0.75, "duracion_dias": 90, "rdc_permitido": False},
            "Otono_Invierno": {"kc": 0.60, "duracion_dias": 120, "rdc_permitido": False}
        }
    },
    "Citricos": {
        "nombre_comun": "Cítricos (Mandarinas W. Murcott, Naranjos)",
        "especie": "Citrus spp.",
        "profundidad_raices_optima_m": 0.70,
        "factor_agotamiento_p": 0.35,
        "estrategia_riego": "Evitar estrés en cuaja; RDC suave post-cuaja para azúcares",
        "psi_tallo_optimo_rdi_mpa": -1.00,
        "psi_tallo_limite_estres_mpa": -1.40,
        "fenofases": {
            "Floracion_a_Cuaja": {"kc": 0.70, "duracion_dias": 60, "rdc_permitido": False},
            "Crecimiento_Fruto": {"kc": 0.65, "duracion_dias": 90, "rdc_permitido": True, "kc_rdc": 0.55},
            "Maduracion": {"kc": 0.60, "duracion_dias": 90, "rdc_permitido": False}
        }
    },
    "Olivos": {
        "nombre_comun": "Olivos (Arbequina, Picual, Frantoio)",
        "especie": "Olea europaea L.",
        "profundidad_raices_optima_m": 0.90,
        "factor_agotamiento_p": 0.50,
        "estrategia_riego": "RDI en endurecimiento de carozo; alta tolerancia a sequía",
        "psi_tallo_optimo_rdi_mpa": -1.80,
        "psi_tallo_limite_estres_mpa": -2.50,
        "fenofases": {
            "Brotacion_a_Floracion": {"kc": 0.55, "duracion_dias": 50, "rdc_permitido": False},
            "Endurecimiento_Carozo": {"kc": 0.50, "duracion_dias": 60, "rdc_permitido": True, "kc_rdc": 0.30},
            "Acumulacion_Aceite": {"kc": 0.65, "duracion_dias": 60, "rdc_permitido": False},
            "Poscosecha": {"kc": 0.45, "duracion_dias": 40, "rdc_permitido": False}
        }
    }
}


class Cultivo:
    """
    Representa el estado fisiológico y las necesidades hídricas del cultivo en campo.
    """

    def __init__(
        self,
        clave_cultivo: str = "Vid_Vinifera_Tinta",
        fenofase_actual: Optional[str] = None,
        aplicar_rdc: bool = False
    ) -> None:
        self.clave = clave_cultivo if clave_cultivo in CULTIVOS_CHILE else "Vid_Vinifera_Tinta"
        self.datos = CULTIVOS_CHILE[self.clave]
        self.aplicar_rdc = aplicar_rdc

        fases = list(self.datos["fenofases"].keys())
        self.fenofase_actual = fenofase_actual if fenofase_actual in fases else fases[0]

    @property
    def kc_actual(self) -> float:
        """Obtiene el coeficiente de cultivo (Kc) considerando si aplica RDC."""
        fase_info = self.datos["fenofases"][self.fenofase_actual]
        if self.aplicar_rdc and fase_info.get("rdc_permitido", False):
            return float(fase_info.get("kc_rdc", fase_info["kc"]))
        return float(fase_info["kc"])

    @property
    def factor_agotamiento_p(self) -> float:
        """Fracción de agotamiento permisible de agua del suelo."""
        return float(self.datos["factor_agotamiento_p"])

    @property
    def profundidad_raices_m(self) -> float:
        """Profundidad radicular activa recomendada."""
        return float(self.datos["profundidad_raices_optima_m"])

    def evaluar_sensor_scholander(self, psi_tallo_medido_mpa: float) -> Dict[str, Any]:
        """
        Evalúa el potencial hídrico xilemático de tallo medido con la Cámara Scholander.
        """
        psi = psi_tallo_medido_mpa
        psi_opt = self.datos["psi_tallo_optimo_rdi_mpa"]
        psi_lim = self.datos["psi_tallo_limite_estres_mpa"]

        if psi > -0.6:
            diagnostico = "Sin estrés hídrico. Ápices en crecimiento activo."
            ajuste_riego = "Disminuir lámina para evitar vigor desmedido."
            factor_ks = 1.0
        elif psi >= psi_opt:
            diagnostico = "Estrés leve a moderado. Zona de confort para el cultivo."
            ajuste_riego = "Mantener lámina de riego programada."
            factor_ks = 1.0
        elif psi >= psi_lim:
            diagnostico = "Estrés moderado a fuerte (Objetivo RDC alcanzado)."
            ajuste_riego = "Monitorear de cerca. Mantener régimen RDC sin sobrepasar el límite."
            factor_ks = 0.85
        else:
            diagnostico = f"🚨 ESTRÉS SEVERO (Psi < {psi_lim} MPa). Cierre estomático y daño fotoquímico."
            ajuste_riego = "Adelantar e incrementar el riego de forma inmediata."
            factor_ks = 0.65

        return {
            "psi_medido_mpa": round(psi, 2),
            "psi_optimo_mpa": psi_opt,
            "psi_limite_mpa": psi_lim,
            "diagnostico": diagnostico,
            "ajuste_riego": ajuste_riego,
            "factor_ks": factor_ks
        }


def registrar_cultivo(clave: str, config: Dict[str, Any]) -> None:
    """Permite añadir o actualizar cultivos personalizados en tiempo de ejecución."""
    CULTIVOS_CHILE[clave] = config
