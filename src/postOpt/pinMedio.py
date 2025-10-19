import numpy as np
from typing import List, Unpack, Callable
from time import time

from resolutor import get_line_err, agregar_lineas_al_error,eliminar_lineas_del_error
from calcular_error import mse

from .parametros import ParametrosPostOpt, ReturnPostOpt


def cambioPinMedio(error_acumulado:np.ndarray,secuencia_pines:List[int],
                   ancho:int, alto:int, numero_de_pines:int,
                   distancia_minima: int ,peso_de_linea: np.float64,
                    linea_cache_x:np.ndarray,linea_cache_y:np.ndarray):
    """
        Recorremos toda la solucion obtenida sacando ternas de pines, buscamos obtener una mejor solucion replazando
        el pin del medio
    """
    secuencia_pines_local = secuencia_pines.copy()
    error_acumulado_local = error_acumulado.copy()
    i = 0
    n = len(secuencia_pines)
    while i+2<n:
        pin_origen = secuencia_pines_local[i]
        mejor_pin = secuencia_pines_local[i+1]
        pin_fin = secuencia_pines_local[i+2]
        indice_O_M = mejor_pin*numero_de_pines +pin_origen
        indice_M_F = pin_fin*numero_de_pines + mejor_pin
        error_acumulado_local = eliminar_lineas_del_error(indices_a_eliminar=[indice_O_M,indice_M_F],
                                                          error_acumulado=error_acumulado_local,
                                                          linea_cache_y=linea_cache_y,
                                                          linea_cache_x=linea_cache_x,
                                                          ancho= ancho,
                                                          peso_de_linea=peso_de_linea)
        
        error_subsanado_al_agregar_las_lineas = np.float64(0)
        error_subsanado_maximo = np.float64(0)

        pines_intermedios_posibles = [j for j in range(numero_de_pines) 
                                            if abs(j-pin_origen)>distancia_minima 
                                            and abs(j-pin_fin)>distancia_minima]
        
        for pin_candidato in pines_intermedios_posibles:
            index_interno_desde = pin_candidato*numero_de_pines + pin_origen
            index_interno_hasta = pin_fin*numero_de_pines + pin_candidato

            error_subsanado_al_agregar_las_lineas = get_line_err(error_acumulado_local, linea_cache_y[index_interno_desde],
                                                                 linea_cache_x[index_interno_desde],ancho)
            error_subsanado_al_agregar_las_lineas += get_line_err(error_acumulado_local, linea_cache_y[index_interno_hasta],
                                                                 linea_cache_x[index_interno_hasta],ancho)
            
            if (error_subsanado_al_agregar_las_lineas > error_subsanado_maximo +1e-6) :
                error_subsanado_maximo = error_subsanado_al_agregar_las_lineas
                mejor_pin = pin_candidato
                indice_O_M = index_interno_desde
                indice_M_F = index_interno_hasta

        # print("A el pin: ", mejor_pin)
        secuencia_pines_local[i+1] = mejor_pin     
        i+=1

        error_acumulado_local = agregar_lineas_al_error(indices_a_agregar=[indice_O_M,indice_M_F],
                                                          error_acumulado=error_acumulado_local,
                                                          linea_cache_y=linea_cache_y,
                                                          linea_cache_x=linea_cache_x,
                                                          ancho= ancho,
                                                          peso_de_linea=peso_de_linea)
        
        # cv2.imwrite("despues.jpg",cv2.flip(error_acumulado_local.reshape(-1,ancho),0))

    return error_acumulado_local,secuencia_pines_local

def cambio_pin_medio(linea_cache_x:np.ndarray,linea_cache_y:np.ndarray,
                   ancho:int,alto:int,vector_de_la_imagen:np.ndarray,
                   secuencia_pines:List[int],error_total:np.ndarray,
                   imagen_preprocesada:np.ndarray, imagen_error_preresolutor: np.ndarray,
                   imagen_error_post_resolutor: np.ndarray,
                   numero_de_pines:int = 256 ,maximo_lineas:int= 4000,
                   distancia_minima:int = 0,peso_de_linea:int = 20,
                   numero_de_pines_recientes_a_evitar:int=5,
                   funcion_calculo_error: Callable[[np.ndarray],np.float64] = mse,
                   itereaciones_re_optimizado:int = 1,
                   decremento_error_minimo: np.float64 = np.float64(0.1),
                   **kwargs: Unpack[ParametrosPostOpt])->ReturnPostOpt:
    

    k = 0
    error_acumulado = error_total
    error_anterior = np.float64(0)
    error_posterior = np.float64(decremento_error_minimo) + 10
    inicio = time()
    while k < itereaciones_re_optimizado and error_posterior-error_anterior >= decremento_error_minimo:
        error_anterior = error_posterior
        error_acumulado,secuencia_pines = cambioPinMedio(error_acumulado=error_acumulado,secuencia_pines=secuencia_pines,
                                    ancho=ancho, alto=alto, numero_de_pines= numero_de_pines,
                                    distancia_minima=distancia_minima ,peso_de_linea=peso_de_linea,
                                    linea_cache_x=linea_cache_x,linea_cache_y=linea_cache_y)
        
        error_posterior = funcion_calculo_error(error_acumulado)
        k+=1
    fin= time()
    if "verbose" in kwargs and kwargs["verbose"]:
        imagen_error_post_resolutor_opt = error_acumulado.reshape(-1,ancho)

        return ReturnPostOpt(
            peso_de_linea=peso_de_linea,
            distancia_minima=distancia_minima,
            maximo_lineas=maximo_lineas,
            iteraciones_re_optimizado_realizadas = k,
            tiempo_usado_re_optimizando = fin-inicio,
            error_total=error_acumulado,
            secuencia_pines=secuencia_pines,
            imagen_preprocesada=imagen_preprocesada,
            imagen_error_preresolutor=imagen_error_post_resolutor,
            imagen_error_post_resolutor=imagen_error_post_resolutor_opt,
        )
    
    return ReturnPostOpt(
            peso_de_linea=peso_de_linea,
            distancia_minima=distancia_minima,
            maximo_lineas=maximo_lineas,
            iteraciones_re_optimizado_realizadas = k,
            tiempo_usado_re_optimizando = fin-inicio,
            error_total=error_acumulado,
            secuencia_pines=secuencia_pines
        )