import numpy as np
from typing import List, Unpack, Callable
import cv2

from calcular_error import mse


def get_line_err(err: np.ndarray, coords1: np.ndarray, coords2: np.ndarray, ancho: np.float64) ->  np.float64:
    return err[(coords1 * ancho + coords2).astype(np.int64)].sum()

def eliminar_lineas_del_error(indices_a_eliminar:List[int],error_acumulado:np.ndarray,linea_cache_y:np.ndarray,
                              linea_cache_x:np.ndarray,ancho:int,peso_de_linea:int):
    for index in indices_a_eliminar:
        coords1 = linea_cache_y[index]
        coords2 = linea_cache_x[index]

        for i in range(coords1.shape[0]):
            v = int(coords1[i] * ancho +coords2[i])
            error_acumulado[v] += peso_de_linea

    return error_acumulado 

def agregar_lineas_al_error(indices_a_agregar:List[int],error_acumulado:np.ndarray,linea_cache_y:np.ndarray,
                            linea_cache_x:np.ndarray, ancho:int,peso_de_linea:int):
    
    for index in indices_a_agregar:
        coords1 = linea_cache_y[index]
        coords2 = linea_cache_x[index]

        for i in range(coords1.shape[0]):
            v = int(coords1[i] * ancho +coords2[i])
            error_acumulado[v] -= peso_de_linea

    return error_acumulado 
