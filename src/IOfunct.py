from typing import TypedDict, NotRequired, Callable
from pathlib import Path
import numpy as np
from numpy import ndarray,float64

from calcular_error import suma_abs,suma_cuad
# ────────────────────────────────
# SECCIÓN 1 — PREPROCESADO
# ────────────────────────────────

class ParametrosPreprocesado(TypedDict, total=False):
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
    

    
# ────────────────────────────────
# SECCIÓN 2 — RESOLUCIÓN
# ────────────────────────────────


class ParametrosResolucion(TypedDict, total=False):
    numero_de_pines: NotRequired[int]
    distancia_minima: NotRequired[float]
    maximo_lineas: NotRequired[int]
    peso_de_linea: NotRequired[float]
    numero_de_pines_recientes_a_evitar: NotRequired[int]
    funcion_calculo_error: NotRequired[Callable[[np.ndarray],np.float64]] | {suma_abs,suma_cuad}
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


# ────────────────────────────────
# SECCIÓN 3 — RECONSTRUCCIÓN (HILADO)
# ────────────────────────────────

class ParametrosReconstruccion(TypedDict, total=False):
    tamano_lado_px: NotRequired[int]
    ancho_clavos: NotRequired[float]
    ancho_de_hilo: NotRequired[float]
    ratio_distancia: NotRequired[float]
    color_de_hilo: NotRequired[str]
    color_de_fondo: NotRequired[str]
    color_de_clavo: NotRequired[str]
    verbose: NotRequired[bool]

class ReturnHilar(TypedDict, total=False):
    ruta_resultado: str
    ruta_imagen_preprocesada: str
    ruta_imagen_error_preresolutor: str
    ruta_imagen_post_resolutor: str

# ────────────────────────────────
# SECCIÓN 4 — ESTUDIO PARAMÉTRICO
# ────────────────────────────────


class EstudioParametros(ParametrosPreprocesado,
                        ParametrosResolucion,
                        ParametrosReconstruccion):
    # Basicos de la funcion:
    output_dir: str
    estudio_web:NotRequired[bool]
    continuacion_estudio:NotRequired[bool]
    # Funciones para el proceso
    funcion_preprocesado: NotRequired[Callable[[ParametrosPreprocesado], ReturnPreprocesado]]
    funcion_resolucion: NotRequired[Callable[[ParametrosResolucion, ReturnPreprocesado], ReturnResolutor]]
    funcion_reconstruccion: NotRequired[Callable[[ParametrosReconstruccion, ReturnPreprocesado, ReturnResolutor], ReturnHilar]]
    funcion_calculo_error: NotRequired[Callable[[np.ndarray],np.float64]] | {suma_abs,suma_cuad}
