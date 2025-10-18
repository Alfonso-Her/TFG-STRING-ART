from typing import TypedDict, NotRequired, Callable
from pathlib import Path
from numpy import ndarray


class ParametrosPreprocesado(TypedDict, total=False):
    funcion_preprocesado: NotRequired[Callable]
    ruta_a_la_imagen: str  # Requerido solo aquí
    numero_de_pines: NotRequired[int]
    distancia_minima: NotRequired[float]
    pasar_a_grises: NotRequired[bool]
    redimensionar: NotRequired[bool]
    mascara_circular: NotRequired[bool]
    recortar: NotRequired[bool]
    verbose: NotRequired[bool]

class ReturnPreprocesado(TypedDict, total=False):
    ruta_a_la_imagen: Path
    numero_de_pines: int 
    ancho:int
    alto:int 
    vector_de_la_imagen:ndarray
    posiciones_pines:ndarray
    linea_cache_x:ndarray
    linea_cache_y:ndarray
    
