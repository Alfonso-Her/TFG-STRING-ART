# import pandas as pd
from pathlib import Path
from typing import TypedDict, NotRequired, Callable
import numpy as np

from calcular_error import mse

class ParametrosResolucionBasicos(TypedDict, total=False):
    ruta_a_resultado: str|Path
    linea_cache_x : np.ndarray
    linea_cache_y: np.ndarray
    ancho: int
    alto:int
    vector_de_la_imagen: np.ndarray
    numero_de_pines: NotRequired[int]
    distancia_minima: NotRequired[float]
    maximo_lineas: NotRequired[int]
    peso_de_linea: NotRequired[float]
    numero_de_pines_recientes_a_evitar: NotRequired[int]
    funcion_calculo_error: NotRequired[Callable[[np.ndarray],np.float64]]
    verbose: NotRequired[bool]


class ParametrosResolucion(ParametrosResolucionBasicos, total=False):
    funcion_resolucion: NotRequired[Callable]
    cantidad_poblacion: int 
    numero_generaciones: int 
    probabilidad_cruce: float 
    probabilidad_mutacion: float
    probabilidad_mutacion_gen: float
    cantidad_torneo: int
    alpha: float
    beta: float
    rho: float
    q: float
    max_iter:int
    reanudar:bool
    
class ReturnResolutor(TypedDict, total=False):
    peso_de_linea: int
    distancia_minima: int
    maximo_lineas: int
    error_total: np.ndarray
    secuencia_pines: np.ndarray
    imagen_preprocesada: np.ndarray
    imagen_error_preresolutor: np.ndarray
    imagen_error_post_resolutor: np.ndarray
    probabilidad_mutacion_gen:float = 0.
    cantidad_torneo:int = 0
    probabilidad_cruce:float = 0.
    elitismo_size:int = 0
    alpha: float = 0
    beta: float = 0
    rho: float = 0
    q: float = 0