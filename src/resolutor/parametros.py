from typing import TypedDict, NotRequired, Callable
from pathlib import Path
from numpy import ndarray, float64

from calcular_error import mse, mad

class ParametrosResolucion(TypedDict, total=False):
    numero_de_pines: NotRequired[int]
    distancia_minima: NotRequired[float]
    maximo_lineas: NotRequired[int]
    peso_de_linea: NotRequired[float]
    numero_de_pines_recientes_a_evitar: NotRequired[int]
    funcion_calculo_error: NotRequired[Callable[[ndarray],float64]] | {mse,mad}
    verbose: NotRequired[bool]

class ReturnResolutor(TypedDict, total=False):
    peso_de_linea: int
    distancia_minima: int
    maximo_lineas: int
    error_total: ndarray
    secuencia_pines: ndarray
    imagen_preprocesada: ndarray
    imagen_error_preresolutor: ndarray
    imagen_error_post_resolutor: ndarray

    
