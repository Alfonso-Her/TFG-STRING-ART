import numpy as np
from copy import deepcopy
from .resolutor import obtener_camino
import cv2

def cambioPinMedio():
    pass

def get_line_err(err: np.ndarray, coords1: np.ndarray, coords2: np.ndarray, ancho: np.float64) ->  np.float64:
    indices = (coords1 * ancho + coords2).astype(int)
    return np.sum(err[indices])

def obtener_camino_cambio_pin_medio(linea_cache_x:np.ndarray,linea_cache_y:np.ndarray,
                   ancho:int,alto:int,vector_de_la_imagen:np.ndarray,
                   numero_de_pines:int = 256 ,maximo_lineas:int= 4000,
                   distancia_minima:int = 0,peso_de_linea:int = 20,
                   **kwargs)->np.ndarray:
    
    diccionario_datos = obtener_camino(linea_cache_x,linea_cache_y,
                   ancho,alto,vector_de_la_imagen,
                   numero_de_pines,maximo_lineas,
                   distancia_minima,peso_de_linea,
                   **kwargs)
    
    error_acumulado = "error_total"
    error_acumulado,secuencia_pines = cambioPinMedio(error_acumulado,secuencia_pines,
                                                     distancia_minima,peso_de_linea,
                                                     linea_cache_x,linea_cache_y)
    
    if "verbose" in kwargs and kwargs["verbose"]:
        imagen_error_post_resolutor = error_acumulado.reshape(-1,ancho)

        return {"peso_de_linea": peso_de_linea,
            "distancia_minima":distancia_minima,
            "maximo_lineas":maximo_lineas,
            "error_total":error_acumulado,
            "secuencia_pines":secuencia_pines,
            "imagen_preprocesada": diccionario_datos["imagen_preprocesada"],
            "imagen_error_preresolutor": diccionario_datos["imagen_error_post_resolutor"],
            "imagen_error_post_resolutor": imagen_error_post_resolutor
            }
    
    return {"peso_de_linea": peso_de_linea,
            "distancia_minima":distancia_minima,
            "maximo_lineas":maximo_lineas,
            "error_total":error_acumulado,
            "secuencia_pines":secuencia_pines}

if __name__ == "__main__":
    from ..preprocesado import tuberia_preprocesado

    parametros = tuberia_preprocesado(ruta_a_la_imagen="ejemplos/acue.jpg")
    print(obtener_camino(**parametros))