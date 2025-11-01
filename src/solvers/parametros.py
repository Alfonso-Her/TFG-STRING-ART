from typing import Callable, NotRequired
from pathlib import Path
from numpy import ndarray, float64

from calcular_error import mse
from preprocesado import ParametrosPreprocesado, ReturnPreprocesado
from resolutor import ParametrosResolucion, ReturnResolutor
from postOpt import ParametrosPostOpt, ReturnPostOpt
from reconstruccion import ParametrosReconstruccion, ReturnReconstruccion

class EstudioParametros(ParametrosPreprocesado,
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
    funcion_calculo_error: NotRequired[Callable[[ndarray],float64]]
    # Configuracion del server
    puerto: int    
