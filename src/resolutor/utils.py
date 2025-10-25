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

def generar_indice(pin_actual,pin_llegada,numero_de_pines):
    return pin_llegada*numero_de_pines + pin_actual

def secuencia_pines_a_error(secuencia_pines:list[int],error_acumulado:np.ndarray,linea_cache_y:np.ndarray,
                            linea_cache_x:np.ndarray, ancho:int,numero_de_pines,peso_de_linea:int)->np.ndarray:
        
        return agregar_lineas_al_error(indices_a_agregar= [generar_indice(x,y,numero_de_pines) for x,y in zip(secuencia_pines,secuencia_pines[1:])],
                                       error_acumulado= error_acumulado,
                                       linea_cache_y=linea_cache_y,
                                       linea_cache_x=linea_cache_x,
                                       ancho=ancho,
                                       peso_de_linea=peso_de_linea)