from typing import Callable, NotRequired, TypedDict
from pathlib import Path
import numpy as  np

from calcular_error import mse
from preprocesado import ParametrosPreprocesado, ReturnPreprocesado
from resolutor import ParametrosResolucion, ReturnResolutor
from postOpt import ParametrosPostOpt, ReturnPostOpt
from reconstruccion import ParametrosReconstruccion, ReturnReconstruccion

class EstudioParametrosInput(ParametrosPreprocesado,
                        ParametrosResolucion,
                        ParametrosPostOpt,
                        ParametrosReconstruccion):
    # Basicos de la funcion:
    output_dir: str
    estudio_web:NotRequired[bool]
    continuacion_estudio:NotRequired[bool]
    # Funciones para el proceso
    funcion_preprocesado: NotRequired[Callable[[ParametrosPreprocesado], ReturnPreprocesado]]
    funcion_resolucion: NotRequired[Callable[[ParametrosResolucion, ReturnPreprocesado], ReturnResolutor]]
    funcion_postOpt: NotRequired[Callable[[ParametrosPostOpt,ReturnResolutor],ReturnPostOpt]]   
    funcion_reconstruccion: NotRequired[Callable[[ParametrosReconstruccion, ReturnPreprocesado, ReturnResolutor], ReturnReconstruccion]]
    funcion_calculo_error: NotRequired[Callable[[np.ndarray],np.float64]]
    # Configuracion del server
    puerto: int    

class EstudioParametrosOutput(TypedDict, total=False):
    imagen_original: str
    numero_de_pines: int
    secuencia_pines: np.ndarray
    distancia_minima: int
    maximo_lineas: int
    lineas_usadas: int
    peso_de_linea: int
    error_total: np.float64
    tiempo_ejecucion: float
    tiempo_usado_re_optimizando: float
    iteraciones_re_optimizado_realizadas: int
    ruta_resultado: str|Path
    verbose:bool
    ruta_imagen_preprocesada:str|Path
    ruta_imagen_error_preresolutor:str|Path
    ruta_imagen_post_resolutor:str|Path
    funciones_usadas:str
    probabilidad_mutacion_gen: float
    cantidad_torneo: int
    probabilidad_cruce:float
    elitismo_size: int
