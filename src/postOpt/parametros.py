from typing import TypedDict, NotRequired, Callable
from pathlib import Path

import numpy as np

from resolutor import ParametrosResolucionBasicos, ReturnResolutor

class ParametrosPostOpt(ParametrosResolucionBasicos,
                        ReturnResolutor, total=False):

    funcion_postOpt: NotRequired[Callable]   
    itereaciones_re_optimizado: NotRequired[int]
    decremento_error_minimo: NotRequired[np.float64]


class ReturnPostOpt(ReturnResolutor, total=False):
    iteraciones_re_optimizado_realizadas: NotRequired[int]
    tiempo_usado_re_optimizando: NotRequired[int]

    
