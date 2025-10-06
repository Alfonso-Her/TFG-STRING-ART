from typing import TypedDict, NotRequired
from pathlib import Path

class ParametrosPreprocesado(TypedDict, total=False):
    ruta_a_la_imagen: str  # Requerido solo aquí
    numero_de_pines: NotRequired[int]
    distancia_minima: NotRequired[float]
    pasar_a_grises: NotRequired[bool]
    redimensionar: NotRequired[tuple[int, int]]
    recortar: NotRequired[tuple[int, int, int, int]]
    verbose: NotRequired[bool]

class ParametrosResolucion(TypedDict, total=False):
    numero_de_pines: NotRequired[int]
    distancia_minima: NotRequired[float]
    maximo_lineas: NotRequired[int]
    peso_de_linea: NotRequired[float]
    numero_de_pines_recientes_a_evitar: NotRequired[int]
    verbose: NotRequired[bool]

class ParametrosReconstruccion(TypedDict, total=False):
    tamano_lado_px: NotRequired[int]
    ancho_clavos: NotRequired[float]
    ancho_de_hilo: NotRequired[float]
    ratio_distancia: NotRequired[float]
    color_de_hilo: NotRequired[str]
    color_de_fondo: NotRequired[str]
    color_de_clavo: NotRequired[str]
    verbose: NotRequired[bool]

class EstudioParametros(ParametrosPreprocesado, ParametrosResolucion, ParametrosReconstruccion):
    # Basicos de la funcion:
    output_dir: str
    estudio_web:NotRequired[bool]
    continuacion_estudio:NotRequired[bool]

