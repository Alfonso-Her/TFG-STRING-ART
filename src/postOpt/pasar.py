from typing import Unpack
from .parametros import ReturnPostOpt, ParametrosPostOpt


def no_reoptimizar(**kwargs:Unpack[ParametrosPostOpt])->ReturnPostOpt:
    kwargs.update({"iteraciones_re_optimizado_realizadas": 0, "tiempo_usado_re_optimizando": 0})
    return kwargs