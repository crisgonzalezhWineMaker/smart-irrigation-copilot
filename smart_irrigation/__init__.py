"""
Agente de Riego Agrícola de Precisión & Balance Hídrico Multiespecie (Chile v1.0)
================================================================================
Desarrollado para: Cristián González Huenchún
Ingeniero Agrónomo & Mg. Enología y Viticultura (Universidad de Chile)

Módulos:
- climatologia: Cálculo de ET0 (FAO-56 Penman-Monteith, Hargreaves), VPD, Pe y zonas climáticas de Chile.
- edafologia: Hidrofísica de suelos USDA, CAD, AFA, curvas de retención y umbrales de agotamiento.
- fisiologia: Biblioteca de cultivos (Vid vinífera, Uva de mesa, Cerezos, Nogales, Paltos, Cítricos, Olivos), Kc dinámico, RDC y sensores (Scholander, FDR).
- hidraulica: Ingeniería de riego presurizado (goteo, microaspersión), precipitación horaria, dimensionamiento de bombas (HP/kW) y consumos.
- motor_riego: Orquestador central de balance hídrico, láminas de reposición y generación de órdenes de riego.
"""

from .climatologia import calcular_et0_penman_monteith, calcular_et0_hargreaves, calcular_vpd, ZONAS_CHILE
from .edafologia import Suelo, TEXTURAS_USDA
from .fisiologia import Cultivo, registrar_cultivo, CULTIVOS_CHILE
from .hidraulica import SectorRiego, calcular_potencia_bomba
from .motor_riego import AgenteRiego, BalanceDiario, OrdenRiego

__version__ = "1.0.0"
__author__ = "Cristián González Huenchún"
