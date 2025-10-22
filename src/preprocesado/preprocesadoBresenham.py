import numpy as np
import cv2
from typing import Callable, Tuple, Unpack
from pathlib import Path

from .preprocesado import ReturnPreprocesado, ParametrosPreprocesado,recortar_rectangulo,\
                          pasar_img_a_grises, aplicar_mascara_circular,\
                          redimensionar_a_rectangulo, construir_vector_imagen, \
                          calcular_posicion_pins, marcar_bordes_en_img

def bresenham(x0: int, y0: int, x1: int, y1: int) -> Tuple[np.ndarray, np.ndarray]:

    x0, y0, x1, y1 = int(x0), int(y0), int(x1), int(y1)
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy
    points_x, points_y = [], []

    while True:
        points_x.append(x0)
        points_y.append(y0)
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x0 += sx
        if e2 < dx:
            err += dx
            y0 += sy

    return np.array(points_x, dtype=np.int64), np.array(points_y, dtype=np.int64)

def precalcular_todas_las_posibles_lineas_bresenham(numero_de_pines: int, coord_xs: np.ndarray,
                                          coord_ys: np.ndarray, distancia_minima:int=3,
                                          **kwargs)->Tuple[np.ndarray]:
    
    linea_cache_y = np.empty(dtype=np.ndarray, shape=(numero_de_pines*numero_de_pines,))
    linea_cache_x = np.empty(dtype=np.ndarray, shape=(numero_de_pines*numero_de_pines,))

    for i in range(numero_de_pines):
        for j in range(i+distancia_minima,numero_de_pines,1):
            #Partimos de
            x0 = coord_xs[i]
            y0 = coord_ys[i]
            #LLegamos a:
            x1 = coord_xs[j]
            y1 = coord_ys[j]

            #Convertimos a int para redondeo
            pasamos_por_xs, pasamos_por_ys= bresenham(x0,y0,x1,y1)

            # Almacenamos en sus posiciones
            linea_cache_y[j*numero_de_pines+i] = pasamos_por_ys
            linea_cache_y[i*numero_de_pines+j] = pasamos_por_ys
            linea_cache_x[j*numero_de_pines+i] = pasamos_por_xs
            linea_cache_x[i*numero_de_pines+j] = pasamos_por_xs

    return linea_cache_x, linea_cache_y
   

def tuberia_preprocesado_bresenham(ruta_a_la_imagen:Path, numero_de_pines:int = 256,
                         distancia_minima:int = 0, filtro_bordes_inferior:int =150,
                         pasar_a_grises:bool = True, filtro_bordes_superior:int = 190,
                         redimensionar:bool = False, recortar:bool = True,
                         mascara_circular:bool = True, marcar_bordes:bool = True,
                         **kwargs:Unpack[ParametrosPreprocesado]) -> ReturnPreprocesado:
    
    imagen = cv2.imread(ruta_a_la_imagen)
    imagen = cv2.flip(imagen,0)

    if pasar_a_grises:
        imagen = pasar_img_a_grises(imagen)

    imagen = cv2.normalize(imagen,None, 0, 255, cv2.NORM_MINMAX)

    if recortar:
        imagen = recortar_rectangulo(imagen)

    if mascara_circular:
        imagen = aplicar_mascara_circular(imagen)

    if redimensionar:
        imagen = redimensionar_a_rectangulo(imagen)
    
    if marcar_bordes:
        imagen = marcar_bordes_en_img(imagen,filtro_bordes_inferior,filtro_bordes_superior)

    vector_de_la_imagen = construir_vector_imagen(imagen)
    posiciones_pines =  calcular_posicion_pins(numero_de_pines, ancho = imagen.shape[1], alto = imagen.shape[0])
    cache_linea_x, cache_linea_y = precalcular_todas_las_posibles_lineas_bresenham(numero_de_pines,posiciones_pines[0],posiciones_pines[1],distancia_minima)
    return ReturnPreprocesado(ruta_a_la_imagen=ruta_a_la_imagen,
                            numero_de_pines=numero_de_pines, 
                            ancho=imagen.shape[1],
                            alto=imagen.shape[0],
                            vector_de_la_imagen=vector_de_la_imagen,
                            posiciones_pines=np.column_stack(posiciones_pines),
                            linea_cache_x=cache_linea_x,
                            linea_cache_y=cache_linea_y)

