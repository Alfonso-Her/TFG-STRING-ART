from typing import TypedDict, NotRequired, Callable
from pathlib import Path
from numpy import ndarray


class ParametrosReconstruccion(TypedDict, total=False):
    funcion_reconstruccion: NotRequired[Callable]
    tamano_lado_px: NotRequired[int]
    ancho_clavos: NotRequired[float]
    ancho_de_hilo: NotRequired[float]
    ratio_distancia: NotRequired[float]
    color_de_hilo: NotRequired[str]
    color_de_fondo: NotRequired[str]
    color_de_clavo: NotRequired[str]
    verbose: NotRequired[bool]

class ReturnReconstruccion(TypedDict, total=False):
    ruta_resultado: str
    ruta_imagen_preprocesada: str
    ruta_imagen_error_preresolutor: str
    ruta_imagen_post_resolutor: str

    
