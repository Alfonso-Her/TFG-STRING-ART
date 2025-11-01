import numpy as np

from typing import List




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


if __name__ == "__main__":
    #MANUALIDAD para comprobar que el error queda igual
    from  preprocesado import tuberia_preprocesado_bresenham
    from . import obtener_camino
    from calcular_error import mse
    import cv2
    parametros = tuberia_preprocesado_bresenham(ruta_a_la_imagen="../ejemplos/acue.jpg",numero_de_pines=256)
    imagen_preprocesada = parametros["vector_de_la_imagen"].copy()
    
    resolucion = obtener_camino(**parametros)
    error_normal = mse(resolucion["error_total"])
    error_acumulado = secuencia_pines_a_error(secuencia_pines=resolucion["secuencia_pines"],
                                      error_acumulado=imagen_preprocesada,
                                      linea_cache_y=parametros["linea_cache_y"],
                                      linea_cache_x=parametros["linea_cache_x"],
                                      ancho= parametros["ancho"],
                                      numero_de_pines=256,
                                      peso_de_linea=20)
    error_nuevo = mse(error_acumulado)
    print(all(error_acumulado ==resolucion["error_total"]))
    print("ERROR NORMAL:", error_normal)
    print("ERROR NUEVO:", error_nuevo)
  
    cv2.imshow("Imagen 1", cv2.flip(resolucion["error_total"].reshape(-1,parametros["ancho"]),0))
    cv2.imshow("Imagen 2", cv2.flip(error_acumulado.reshape(-1,parametros["ancho"]),0))
    cv2.waitKey(0)

    # Cerrar las ventanas
    cv2.destroyAllWindows()
    assert error_nuevo == error_normal
