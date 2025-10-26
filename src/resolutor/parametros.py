import pandas as pd
from pathlib import Path
from typing import TypedDict, NotRequired, Callable
from numpy import ndarray, float64

from calcular_error import mse

class ParametrosResolucionBasicos(TypedDict, total=False):
    ruta_a_resultado: str|Path
    numero_de_pines: NotRequired[int]
    distancia_minima: NotRequired[float]
    maximo_lineas: NotRequired[int]
    peso_de_linea: NotRequired[float]
    numero_de_pines_recientes_a_evitar: NotRequired[int]
    funcion_calculo_error: NotRequired[Callable[[ndarray],float64]]
    verbose: NotRequired[bool]


class ParametrosResolucion(ParametrosResolucionBasicos, total=False):
    funcion_resolucion: NotRequired[Callable]
    cantidad_poblacion: int 
    numero_generaciones: int 
    probabilidad_cruce: float 
    probabilidad_mutacion: float
    probabilidad_mutacion_gen: float
    cantidad_torneo: int
    
class ReturnResolutor(TypedDict, total=False):
    peso_de_linea: int
    distancia_minima: int
    maximo_lineas: int
    error_total: ndarray
    secuencia_pines: ndarray
    imagen_preprocesada: ndarray
    imagen_error_preresolutor: ndarray
    imagen_error_post_resolutor: ndarray


    
