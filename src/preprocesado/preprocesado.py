import cv2
import numpy as np
from pathlib import Path
from typing import Callable,Tuple, Unpack

from calcular_error import mse,ssim

from .parametros import ReturnPreprocesado,ParametrosPreprocesado
from .imagen import preprocesar_imagen


def construir_vector_imagen(img:np.ndarray)->np.ndarray:

    # No pasamos a escala de grises TODO hacer que esto funcione bien
    if len(img.shape)==3:
        return (255-img[:,:,2].flatten()).astype(np.float64)
    # Estamos en escala de grises
    if len(img.shape)==2:
        return (255-img[:,:].flatten()).astype(np.float64)
    
# ---------------------------------------Generacion de pines----------------------------------

def _distancia_eu(x0,y0,x1,y1):
    return np.floor(np.sqrt(np.float64((x1-x0)*(x1-x0) + (y1-y0)*(y1-y0))))

def calcular_posicion_pins(numero_de_pines:int, ancho:int, alto:int, calculo_radio:Callable = lambda x: x/2-1)->np.ndarray:
    """
        Dado el numero de pins/clavos y los tamaños de la imagen obtiene
        la posicion de los clavos centrando sobre el centro del ancho y el alto.
        Admite funciones distintas para calcular el radio del
        circulo con el que se calculara la imagen y no es segura,
        puedes tomar imagenes cuyos pines se salgan de la imagen en si.
        
    """
    centro_x =  np.float64(ancho/2)
    centro_y =  np.float64(alto/2)
    radio = calculo_radio(ancho)

    angulos = np.linspace(0, 2* np.pi, numero_de_pines, dtype=np.float64,endpoint= False)

    return [centro_x + radio * np.cos(angulos),centro_y + radio * np.sin(angulos)]

# ---------------------------------------Precalculo de lineas----------------------------------

def precaluclar_todas_las_posibles_lineas(numero_de_pines: int, coord_xs: np.ndarray,
                                          coord_ys: np.ndarray, distancia_minima:int=3,
                                          calculo_distancia: Callable = _distancia_eu) ->Tuple[np.ndarray]:
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

            # Tomamos la distancia entre los pines para luego construir una "malla" de pixeles recorridos usando linspace
            distancia_entre_pines = calculo_distancia(x0,y0,x1,y1)
            #Convertimos a int para redondeo
            pasamos_por_xs = np.linspace(x0,x1,int(distancia_entre_pines),dtype=int).astype(np.float64)
            pasamos_por_ys = np.linspace(y0,y1,int(distancia_entre_pines),dtype=int).astype(np.float64)

            # Almacenamos en sus posiciones
            linea_cache_y[j*numero_de_pines+i] = pasamos_por_ys
            linea_cache_y[i*numero_de_pines+j] = pasamos_por_ys
            linea_cache_x[j*numero_de_pines+i] = pasamos_por_xs
            linea_cache_x[i*numero_de_pines+j] = pasamos_por_xs

    return linea_cache_x, linea_cache_y


# ---------------------------------------Tuberia de preprocesado----------------------------------
def tuberia_preprocesado(ruta_a_la_imagen:Path, funcion_calculo_error:Callable = mse,numero_de_pines:int = 256,
                         distancia_minima:int = 0, filtro_bordes_inferior:int =150,
                         pasar_a_grises:bool = True, filtro_bordes_superior:int = 190,
                         redimensionar:bool = False, recortar:bool = True,
                         mascara_circular:bool = True, marcar_bordes:bool = True,
                         **kwargs:Unpack[ParametrosPreprocesado]) -> ReturnPreprocesado:
    
    # print(ruta_a_la_imagen)
    imagen = cv2.imread(ruta_a_la_imagen)
    imagen = cv2.flip(imagen,0)
    imagen = preprocesar_imagen(imagen, filtro_bordes_inferior,
                         pasar_a_grises, filtro_bordes_superior,
                         redimensionar, recortar,
                         mascara_circular, marcar_bordes)
    
    if funcion_calculo_error.__name__ == "ssim":
        funcion_calculo_error = lambda imagen_resultado: ssim(255-imagen,imagen_resultado.reshape(-1, imagen.shape[1]))

    vector_de_la_imagen = construir_vector_imagen(imagen)
    posiciones_pines =  calcular_posicion_pins(numero_de_pines, ancho = imagen.shape[1], alto = imagen.shape[0])
    cache_linea_x, cache_linea_y = precaluclar_todas_las_posibles_lineas(numero_de_pines,posiciones_pines[0],posiciones_pines[1],distancia_minima)
    return ReturnPreprocesado(ruta_a_la_imagen=ruta_a_la_imagen,
                            numero_de_pines=numero_de_pines, 
                            funcion_calculo_error=funcion_calculo_error,
                            ancho=imagen.shape[1],
                            alto=imagen.shape[0],
                            vector_de_la_imagen=vector_de_la_imagen,
                            posiciones_pines=np.column_stack(posiciones_pines),
                            linea_cache_x=cache_linea_x,
                            linea_cache_y=cache_linea_y)

# testing
if __name__ == "__main__":
    # a = _construir_vector_imagen_bucles(cv2.imread("../../ejemplos/ae300.jpg"))
    # b = construir_vector_imagen(cv2.imread("../../ejemplos/ae300.jpg"))
    # _construir_vector_imagen_bucles(cv2.imread("../../ejemplos/ae300.jpg"))
    # construir_vector_imagen(cv2.imread("../../ejemplos/ae300.jpg"))
    # print((a == b).all())

    # print(tuberia_preprocesado(ruta_a_la_imagen="../../ejemplos/acue.jpg"))
    # foto =cv2.imread("../../ejemplos/cervantesColor.jpg") 
    # print(foto[0:15])
    # cerva= pasar_a_grises(foto)
    # print(cerva[0:15])
    # cv2.imwrite(filename="AAAAAA.jpg",img=cerva)

    img = cv2.imread("../../ejemplos/cervantesColor.jpg", cv2.IMREAD_GRAYSCALE)
    # cv2.imwrite(filename="AAAAAA.jpg",img=img)
    # imagen_normalizada = cv2.normalize(img,None, 0, 255, cv2.NORM_MINMAX)
    # cv2.imwrite(filename="AAAdAAA.jpg",img=imagen_normalizada)
    a = np.full(shape =img.shape, fill_value=np.float64(255.0)) - img
    cv2.imwrite(filename="AAAdAAA.jpg",img=a)