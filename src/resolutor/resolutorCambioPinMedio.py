import numpy as np
from copy import deepcopy
from typing import List
from .resolutor import obtener_camino, get_line_err
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
                    linea_cache_x:np.ndarray,linea_cache_y:np.ndarray,
                    estricto:bool):
    """
        Recorremos toda la solucion obtenida sacando ternas de pines, buscamos obtener una mejor solucion replazando
        el pin del medio, el parametro estricto fuerza a que no podamos elegir el mimo pin intermedio actual siempre
        que encontremos uno mejor
    """
    secuencia_pines_resultado = secuencia_pines.copy()

    for posicion, terna in enumerate(zip(secuencia_pines,secuencia_pines[1:],secuencia_pines[2:])):
        mejor_pin = terna[1]
        indice_A_B = terna[1]*numero_de_pines + terna[0]
        indice_B_C = terna[2]*numero_de_pines + terna[1]
        error_acumulado = eliminar_lineas_del_error([indice_A_B,indice_B_C],error_acumulado,
                                                     linea_cache_y, linea_cache_x, ancho,
                                                     peso_de_linea)
        error_subsanado_al_agregar_las_lineas = np.float64(0)
        error_subsanado_maximo = np.float64(0)
        pines_intermedios_posibles = [i for i in range(numero_de_pines) if abs(i-terna[0])>distancia_minima 
                                                                and abs(i-terna[2])>distancia_minima ]
        if estricto and terna[1] in pines_intermedios_posibles:
            pines_intermedios_posibles.remove(terna[1])
        
        for pin_candidato in pines_intermedios_posibles:
            index_interno_desde = pin_candidato*numero_de_pines + terna[0]
            index_interno_hasta = terna[2]*numero_de_pines + pin_candidato
            error_subsanado_al_agregar_las_lineas = get_line_err(error_acumulado, linea_cache_y[index_interno_desde],
                                                                 linea_cache_x[index_interno_desde],ancho)
            error_subsanado_al_agregar_las_lineas += get_line_err(error_acumulado, linea_cache_y[index_interno_hasta],
                                                                 linea_cache_x[index_interno_hasta],ancho)
            if (error_subsanado_al_agregar_las_lineas > error_subsanado_maximo) :
                error_subsanado_maximo = error_subsanado_al_agregar_las_lineas
                mejor_pin = pin_candidato
                indice_A_B = index_interno_desde
                indice_B_C = index_interno_hasta

        secuencia_pines_resultado[posicion+1] = mejor_pin

        error_acumulado = agregar_lineas_al_error([indice_A_B,indice_B_C],error_acumulado,
                                                     linea_cache_y, linea_cache_x, ancho,
                                                     peso_de_linea)
    return secuencia_pines_resultado
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