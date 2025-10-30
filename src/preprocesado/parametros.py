from typing import TypedDict, NotRequired, Callable
from pathlib import Path
from numpy import ndarray,float64


class ParametrosPreprocesado(TypedDict, total=False):
    funcion_preprocesado: NotRequired[Callable]
    funcion_calculo_error: NotRequired[Callable[[ndarray],float64]]
    ruta_a_la_imagen: str  
    numero_de_pines: NotRequired[int]
    distancia_minima: NotRequired[float]
    filtro_bordes_inferior: NotRequired[int]
    filtro_bordes_superior: NotRequired[int]
    pasar_a_grises: NotRequired[bool]
    redimensionar: NotRequired[bool]
    mascara_circular: NotRequired[bool]
    marcar_bordes: NotRequired[bool]
    recortar: NotRequired[bool]
    verbose: NotRequired[bool]

class ReturnPreprocesado(TypedDict, total=False):
    ruta_a_la_imagen: Path
    numero_de_pines: int 
    funcion_calculo_error: NotRequired[Callable[[ndarray],float64]]
    ancho:int
    alto:int 
    vector_de_la_imagen:ndarray
    posiciones_pines:ndarray
    linea_cache_x:ndarray
    linea_cache_y:ndarray
    
