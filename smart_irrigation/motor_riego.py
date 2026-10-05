"""
Módulo Orquestador: Agente de Riego Agrícola de Precisión
=========================================================
Integra Climatología (FAO-56), Edafología (CAD/AFA), Fisiología (Kc dinámico/RDC)
e Ingeniería Hidráulica para generar balances hídricos automáticos, programaciones semanales
y órdenes de riego operativas para casetas de campo.

Autor: Cristián González Huenchún & Antigravity
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, date

from .climatologia import (
    calcular_et0_penman_monteith,
    calcular_et0_hargreaves,
    calcular_precipitacion_efectiva,
    ZONAS_CHILE
)
from .edafologia import Suelo
from .fisiologia import Cultivo
from .hidraulica import SectorRiego


class BalanceDiario:
    """Modela el balance hídrico de un día para un sector específico."""

    def __init__(
        self,
        fecha: str,
        et0_mm: float,
        kc: float,
        ks: float = 1.0,
        precipitacion_mm: float = 0.0,
        eficiencia_ea: float = 0.90
    ) -> None:
        self.fecha = fecha
        self.et0_mm = max(0.0, et0_mm)
        self.kc = max(0.0, kc)
        self.ks = max(0.1, min(1.0, ks))
        self.precipitacion_mm = max(0.0, precipitacion_mm)
        self.eficiencia_ea = max(0.5, min(0.98, eficiencia_ea))

        # Cálculos de demanda
        self.etc_mm = self.et0_mm * self.kc * self.ks
        self.pe_mm = calcular_precipitacion_efectiva(self.precipitacion_mm)
        self.lamina_neta_mm = max(0.0, self.etc_mm - self.pe_mm)
        self.lamina_bruta_mm = self.lamina_neta_mm / self.eficiencia_ea if self.eficiencia_ea > 0 else 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "fecha": self.fecha,
            "et0_mm": round(self.et0_mm, 2),
            "kc": round(self.kc, 2),
            "ks": round(self.ks, 2),
            "etc_mm": round(self.etc_mm, 2),
            "lluvia_mm": round(self.precipitacion_mm, 1),
            "pe_mm": round(self.pe_mm, 1),
            "lamina_neta_mm": round(self.lamina_neta_mm, 2),
            "lamina_bruta_mm": round(self.lamina_bruta_mm, 2)
        }


class OrdenRiego:
    """Orden de trabajo operativa para el regador o caseta de automatización."""

    def __init__(
        self,
        sector_nombre: str,
        cultivo_nombre: str,
        fenofase: str,
        fecha_emision: str,
        lamina_bruta_acumulada_mm: float,
        tiempo_riego_formato: str,
        horas_decimales: float,
        volumen_m3: float,
        caudal_m3_h: float,
        potencia_motor_hp: float,
        consumo_kwh_estimado: float,
        recomendaciones: List[str]
    ) -> None:
        self.sector_nombre = sector_nombre
        self.cultivo_nombre = cultivo_nombre
        self.fenofase = fenofase
        self.fecha_emision = fecha_emision
        self.lamina_bruta_mm = lamina_bruta_acumulada_mm
        self.tiempo_formato = tiempo_riego_formato
        self.horas_decimales = horas_decimales
        self.volumen_m3 = volumen_m3
        self.caudal_m3_h = caudal_m3_h
        self.potencia_hp = potencia_motor_hp
        self.consumo_kwh = consumo_kwh_estimado
        self.recomendaciones = recomendaciones

    def generar_markdown(self) -> str:
        """Exporta la orden en formato Markdown para el Segundo Cerebro."""
        recs = "\n".join([f"- {r}" for r in self.recomendaciones])
        md = f"""# 💧 Orden de Riego: {self.sector_nombre} ({self.cultivo_nombre})
> **Fecha de Emisión:** {self.fecha_emision} | **Fenofase:** {self.fenofase}

### ⏱️ Parámetros de Operación
| Parámetro | Valor Operativo | Unidad |
| :--- | :--- | :--- |
| **Tiempo de Riego Requerido** | **{self.tiempo_formato}** | horas |
| **Lámina Bruta a Reponer** | **{self.lamina_bruta_mm:.1f}** | mm |
| **Volumen Total Demandado** | **{self.volumen_m3:,.0f}** | $m^3$ |
| **Caudal del Sector** | **{self.caudal_m3_h:.1f}** | $m^3/h$ |
| **Potencia Bombeo Estimada** | **{self.potencia_hp:.1f}** | HP |
| **Consumo Eléctrico Estimado**| **{self.consumo_kwh:.1f}** | kWh |

### 📋 Instrucciones Agronómicas:
{recs}
"""
        return md


class AgenteRiego:
    """
    Agente que orquesta los cuarteles, sensores y decisiones de riego del predio.
    """

    def __init__(self, nombre_predio: str = "Fundo Agrícola Central") -> None:
        self.nombre_predio = nombre_predio
        self.cuarteles: Dict[str, Dict[str, Any]] = {}

    def registrar_cuartel(
        self,
        id_sector: str,
        sector_hidraulico: SectorRiego,
        suelo: Suelo,
        cultivo: Cultivo
    ) -> None:
        """Registra una unidad agronómica completa de riego."""
        self.cuarteles[id_sector] = {
            "sector": sector_hidraulico,
            "suelo": suelo,
            "cultivo": cultivo,
            "historial_balances": [],
            "deficit_acumulado_mm": 0.0
        }

    def procesar_balance_diario(
        self,
        id_sector: str,
        fecha: str,
        et0_mm: float,
        precipitacion_mm: float = 0.0,
        psi_tallo_scholander: Optional[float] = None,
        humedad_vol_suelo: Optional[float] = None
    ) -> Dict[str, Any]:
        """Calcula y acumula el balance diario integrando sensores."""
        if id_sector not in self.cuarteles:
            raise KeyError(f"Cuartel '{id_sector}' no encontrado.")

        c = self.cuarteles[id_sector]
        sector: SectorRiego = c["sector"]
        suelo: Suelo = c["suelo"]
        cultivo: Cultivo = c["cultivo"]

        # Ajuste por sensor de planta (Scholander)
        ks = 1.0
        alerta_sensor = None
        if psi_tallo_scholander is not None:
            eval_psi = cultivo.evaluar_sensor_scholander(psi_tallo_scholander)
            ks = eval_psi["factor_ks"]
            alerta_sensor = f"Scholander: {eval_psi['psi_medido_mpa']} MPa -> {eval_psi['diagnostico']}"

        # Ajuste por sensor de suelo
        if humedad_vol_suelo is not None:
            eval_suelo = suelo.diagnostico_humedad_actual(humedad_vol_suelo)
            if eval_suelo["lamina_deficit_mm"] == 0.0:
                alerta_sensor = f"Suelo a Capacidad de Campo ({humedad_vol_suelo}% vol). Riego postergado."

        balance = BalanceDiario(
            fecha=fecha,
            et0_mm=et0_mm,
            kc=cultivo.kc_actual,
            ks=ks,
            precipitacion_mm=precipitacion_mm,
            eficiencia_ea=sector.eficiencia_ea
        )

        c["historial_balances"].append(balance)
        c["deficit_acumulado_mm"] += balance.lamina_bruta_mm

        # Evaluar si se debe disparar la orden de riego
        umbral_afa = suelo.afa_mm(cultivo.factor_agotamiento_p)
        debe_regar = c["deficit_acumulado_mm"] >= (umbral_afa / sector.eficiencia_ea)

        return {
            "id_sector": id_sector,
            "balance": balance.to_dict(),
            "deficit_acumulado_mm": round(c["deficit_acumulado_mm"], 2),
            "umbral_afa_mm": umbral_afa,
            "debe_regar": debe_regar,
            "alerta_sensor": alerta_sensor
        }

    def emitir_orden_riego(
        self,
        id_sector: str,
        fecha_emision: Optional[str] = None
    ) -> OrdenRiego:
        """Genera la orden formal de riego con el déficit acumulado."""
        if id_sector not in self.cuarteles:
            raise KeyError(f"Cuartel '{id_sector}' no encontrado.")

        c = self.cuarteles[id_sector]
        sector: SectorRiego = c["sector"]
        cultivo: Cultivo = c["cultivo"]
        lamina_bruta = max(5.0, c["deficit_acumulado_mm"])

        calculo_t = sector.calcular_tiempo_riego(lamina_bruta)
        motor_info = sector.calcular_dimensionamiento_motor()
        consumo_total_kwh = motor_info["consumo_kwh_por_hora"] * calculo_t["horas_decimales"]

        recs = [
            f"Cultivo: {cultivo.datos['nombre_comun']} en fenofase {cultivo.fenofase_actual}.",
            f"Precipitación del sistema: {sector.precipitación_horaria_mm_h} mm/h con caudal de {sector.caudal_total_m3_h} m3/h.",
            "Recomendación horaria: Iniciar riego a partir de las 21:00 h o temprano en la mañana (05:00 h) para evitar tarifas eléctricas punta y pérdidas por evaporación.",
            "Verificar manómetros en cabezal de filtrado antes y durante la postura (presión nominal: 1.5 - 2.0 bar)."
        ]
        if cultivo.aplicar_rdc:
            recs.append("⚠️ Régimen RDC activo: Mantener monitoreo de ápices y potencial Scholander.")

        fecha_str = fecha_emision if fecha_emision else datetime.now().strftime("%Y-%m-%d")

        orden = OrdenRiego(
            sector_nombre=sector.nombre,
            cultivo_nombre=cultivo.datos["nombre_comun"],
            fenofase=cultivo.fenofase_actual,
            fecha_emision=fecha_str,
            lamina_bruta_acumulada_mm=lamina_bruta,
            tiempo_riego_formato=calculo_t["formato_tiempo"],
            horas_decimales=calculo_t["horas_decimales"],
            volumen_m3=calculo_t["volumen_total_m3"],
            caudal_m3_h=sector.caudal_total_m3_h,
            potencia_motor_hp=motor_info["potencia_hp"],
            consumo_kwh_estimado=round(consumo_total_kwh, 1),
            recomendaciones=recs
        )

        # Reiniciar déficit acumulado tras emitir la orden
        c["deficit_acumulado_mm"] = 0.0

        return orden
