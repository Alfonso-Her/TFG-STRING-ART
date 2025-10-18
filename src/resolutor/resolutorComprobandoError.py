import numpy as np
from copy import deepcopy
from typing import Callable, Unpack
import cv2

from .parametros import ReturnResolutor, ParametrosResolucion
from calcular_error import suma_abs,suma_cuad,mad,mae,mse
from .resolutorCambioPinMedio import agregar_lineas_al_error, eliminar_lineas_del_error


def get_error_general(indice_linea:int, error_acumulado:np.ndarray,
                      linea_cache_y:np.ndarray, linea_cache_x:np.ndarray,
                      ancho:int, peso_de_linea:int,
                      funcion_calculo_error :Callable[[np.ndarray],np.float64]):
    """
        Agrego la linea, calculo el error, elimino la linea, devuelvo el error
    """
    error_acumulado = agregar_lineas_al_error([indice_linea], error_acumulado, linea_cache_y,
                                                linea_cache_x, ancho, peso_de_linea)
    error = funcion_calculo_error(error_acumulado)
    error_acumulado = eliminar_lineas_del_error([indice_linea], error_acumulado, linea_cache_y,
                                                linea_cache_x, ancho, peso_de_linea)
    
    return error, error_acumulado

def obtener_camino_con_error_total(linea_cache_x:np.ndarray,linea_cache_y:np.ndarray,
                   ancho:int,alto:int,vector_de_la_imagen:np.ndarray,
                   funcion_calculo_error :Callable[[np.ndarray],np.float64] = suma_abs,
                   numero_de_pines:int = 256 ,maximo_lineas:int= 4000,
                   distancia_minima:int = 0,peso_de_linea:int = 20,
                   numero_de_pines_recientes_a_evitar:int=5,
                   **kwargs:Unpack[ParametrosResolucion])->ReturnResolutor:
    
    # Haciendo esto basicamente invertimos colores y pintamos de negro los blancos 
    error_acumulado = np.full(ancho*alto, 255.0) - vector_de_la_imagen

    if "verbose" in kwargs and kwargs["verbose"]:
        imagen_preprocesada = vector_de_la_imagen.reshape(-1,ancho)
        imagen_error_preresolutor = deepcopy(error_acumulado).reshape(-1,ancho)

    secuencia_pines =np.empty(0,dtype=int)
    secuencia_pines = np.append(secuencia_pines,0)
    pines_ya_recorridos = np.empty(0,dtype=int)
    pin_actual = 0
    mejor_pin = -1
    error_al_agregar_la_linea = np.float64(0)
    error_maximo = np.float64(0)
    index = 0
    index_interno = 0

    for i in range(maximo_lineas):
        # Restauramos variables para cada linea a pintar
        mejor_pin = -1
        error_al_agregar_la_linea = np.float64(0)
        error_maximo = funcion_calculo_error(error_acumulado)

        for desfase_desde_pin in range(distancia_minima,numero_de_pines-distancia_minima):
            pin_a_probar = (pin_actual + desfase_desde_pin) % numero_de_pines
            if pin_a_probar in pines_ya_recorridos:
                continue
            else:

                index_interno = pin_a_probar*numero_de_pines + pin_actual
                error_al_agregar_la_linea,error_acumulado = get_error_general(indice_linea=index_interno, error_acumulado=error_acumulado,
                                                                 linea_cache_y=linea_cache_y, linea_cache_x=linea_cache_x,
                                                                 ancho=ancho, peso_de_linea=peso_de_linea,
                                                                 funcion_calculo_error=funcion_calculo_error)

                if (error_al_agregar_la_linea < error_maximo):
                    error_maximo = error_al_agregar_la_linea
                    mejor_pin = pin_a_probar
                    index = index_interno
        
        if mejor_pin == -1:
            # evitamos quedarnos atrapados haciendo iteraciones que no salen del pin actual
            break

        secuencia_pines = np.append(secuencia_pines,mejor_pin)
        coords1 = linea_cache_y[index]
        coords2 = linea_cache_x[index]
        for i in range(coords1.shape[0]):
            v = int(coords1[i] * ancho +coords2[i])
            error_acumulado[v] -= peso_de_linea 

    
        pines_ya_recorridos= np.append(pines_ya_recorridos, mejor_pin)
        if len(pines_ya_recorridos)> numero_de_pines_recientes_a_evitar:
            pines_ya_recorridos = pines_ya_recorridos[1:]
        pin_actual = mejor_pin

    if "verbose" in kwargs and kwargs["verbose"]:
        imagen_error_post_resolutor = error_acumulado.reshape(-1,ancho)

        return ReturnResolutor(
            peso_de_linea=peso_de_linea,
            distancia_minima=distancia_minima,
            maximo_lineas=maximo_lineas,
            error_total=error_acumulado,
            secuencia_pines=secuencia_pines,
            imagen_preprocesada=imagen_preprocesada,
            imagen_error_preresolutor=imagen_error_preresolutor,
            imagen_error_post_resolutor=imagen_error_post_resolutor,
        )
    
    return ReturnResolutor(
            peso_de_linea=peso_de_linea,
            distancia_minima=distancia_minima,
            maximo_lineas=maximo_lineas,
            error_total=error_acumulado,
            secuencia_pines=secuencia_pines
        )
