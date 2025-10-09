import numpy as np
from copy import deepcopy
from typing import List
from .resolutor import obtener_camino, get_line_err
from IOfunct import ReturnResolutor
import cv2



def eliminar_lineas_del_error(indices_a_eliminar:List[int],error_acumulado:np.ndarray, linea_cache_x:np.ndarray,
                              linea_cache_y:np.ndarray,ancho:int,peso_de_linea:int):
    for index in indices_a_eliminar:
        coords1 = linea_cache_y[index]
        coords2 = linea_cache_x[index]

        for i in range(coords1.shape[0]):
            v = int(coords1[i] * ancho +coords2[i])
            error_acumulado[v] += peso_de_linea

    return error_acumulado 

def agregar_lineas_al_error(indices_a_agregar:List[int],error_acumulado:np.ndarray, linea_cache_x:np.ndarray,
                              linea_cache_y:np.ndarray,ancho:int,peso_de_linea:int):
    
    for index in indices_a_agregar:
        coords1 = linea_cache_y[index]
        coords2 = linea_cache_x[index]

        for i in range(coords1.shape[0]):
            v = int(coords1[i] * ancho +coords2[i])
            error_acumulado[v] -= peso_de_linea

    return error_acumulado 

def cambioPinMedio(error_acumulado:np.ndarray,secuencia_pines:List[int],
                   ancho:int, alto:int, numero_de_pines:int,
                   distancia_minima: int ,peso_de_linea: np.float64,
                    linea_cache_x:np.ndarray,linea_cache_y:np.ndarray):
    """
        Recorremos toda la solucion obtenida sacando ternas de pines, buscamos obtener una mejor solucion replazando
        el pin del medio, el parametro estricto fuerza a que no podamos elegir el mimo pin intermedio actual siempre
        que encontremos uno mejor
    """
    secuencia_pines_local = secuencia_pines.copy()
    error_acumulado_local = error_acumulado.copy()
    i = 0
    n = len(secuencia_pines)
    while i+2<n:
        pin_origen = secuencia_pines_local[i]
        mejor_pin = secuencia_pines_local[i+1]
        pin_fin = secuencia_pines_local[i+2]

        print("Estamos trabajando con ", pin_origen," ", mejor_pin," ", pin_fin," ")
        indice_O_M = mejor_pin*numero_de_pines +pin_origen
        indice_M_F = pin_fin*numero_de_pines + mejor_pin

        error_acumulado_local = eliminar_lineas_del_error([indice_O_M,indice_M_F],error_acumulado_local,
                                                     linea_cache_y, linea_cache_x, ancho,
                                                     peso_de_linea)
        cv2.imwrite("temp.jpg",img=error_acumulado.reshape(-1,ancho))
        input("dame una a")
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
            
            if (error_subsanado_al_agregar_las_lineas > error_subsanado_maximo + 1e-6) :
                error_subsanado_maximo = error_subsanado_al_agregar_las_lineas
                mejor_pin = pin_candidato
                indice_O_M = index_interno_desde
                indice_M_F = index_interno_hasta

        secuencia_pines_local[i+1] = mejor_pin     
        i+=1

        error_acumulado_local = agregar_lineas_al_error([indice_O_M,indice_M_F],error_acumulado_local,
                                                     linea_cache_y, linea_cache_x, ancho,
                                                     peso_de_linea)
        
    return error_acumulado_local,secuencia_pines_local

def obtener_camino_cambio_pin_medio(linea_cache_x:np.ndarray,linea_cache_y:np.ndarray,
                   ancho:int,alto:int,vector_de_la_imagen:np.ndarray,
                   numero_de_pines:int = 256 ,maximo_lineas:int= 4000,
                   distancia_minima:int = 0,peso_de_linea:int = 20,
                   numero_de_pines_recientes_a_evitar:int=5,
                   **kwargs)->ReturnResolutor:
    
    diccionario_datos = obtener_camino(linea_cache_x,linea_cache_y,
                   ancho,alto,vector_de_la_imagen,
                   numero_de_pines,maximo_lineas,
                   distancia_minima,peso_de_linea,
                   numero_de_pines_recientes_a_evitar,
                   **kwargs)
    
    error_acumulado,secuencia_pines = cambioPinMedio(error_acumulado=diccionario_datos["error_total"],secuencia_pines=diccionario_datos["secuencia_pines"],
                                    ancho=ancho, alto=alto, numero_de_pines= numero_de_pines,
                                    distancia_minima=distancia_minima ,peso_de_linea=peso_de_linea,
                                    linea_cache_x=linea_cache_x,linea_cache_y=linea_cache_y)

    if "verbose" in kwargs and kwargs["verbose"]:
        imagen_error_post_resolutor = error_acumulado.reshape(-1,ancho)

        return ReturnResolutor(
            peso_de_linea=peso_de_linea,
            distancia_minima=distancia_minima,
            maximo_lineas=maximo_lineas,
            error_total=error_acumulado,
            secuencia_pines=secuencia_pines,
            imagen_preprocesada=diccionario_datos["imagen_preprocesada"],
            imagen_error_preresolutor=diccionario_datos["imagen_error_post_resolutor"],
            imagen_error_post_resolutor=imagen_error_post_resolutor,
        )
    
    return ReturnResolutor(
            peso_de_linea=peso_de_linea,
            distancia_minima=distancia_minima,
            maximo_lineas=maximo_lineas,
            error_total=error_acumulado,
            secuencia_pines=secuencia_pines
        )


if __name__ == "__main__":
    from ..preprocesado import tuberia_preprocesado

    parametros = tuberia_preprocesado(ruta_a_la_imagen="ejemplos/acue.jpg")
    print(obtener_camino_cambio_pin_medio(**parametros))