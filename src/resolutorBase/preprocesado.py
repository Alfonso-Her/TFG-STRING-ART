import cv2
import numpy as np
from pathlib import Path
from typing import Callable,Tuple

# ---------------------------------------Tratamiento de la imagen---------------------------------- 

def pasar_a_grises(img:np.ndarray)->np.ndarray:
    """
        Posible futura implementacion como una opcion de preprocesado
        Toma una imagen abierta (un np.ndarray) y la devuelve en escala de grises
    """
    return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

def _construir_vector_imagen_bucles(img:np.ndarray)->np.ndarray:
    """
        Dejo esta funcion solo a modo de documentacion, aqui es mas explicito que tomamos el color rojo de cada pixel y lo almacenamos en un vector
        en el resto del codigo usaremos consturir_vector_imagen porque es mas rapido
    """
    vector = np.empty(0,dtype=np.float64)

    for fila in img:
        for pixel in fila:
            vector = np.append(vector,np.float64(pixel[2]))
    return vector

def construir_vector_imagen(img:np.ndarray)->np.ndarray:

    return (img[:,:,2].flatten()).astype(np.float64)


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
def tuberia_preprocesado(ruta_a_la_imagen:Path, numero_de_pines:int = 256, distancia_minima:int = 0):
    imagen =cv2.imread(ruta_a_la_imagen)
    imagen = cv2.flip(imagen,0)
    vector_de_la_imagen = construir_vector_imagen(imagen)
    posiciones_pines =  calcular_posicion_pins(numero_de_pines, ancho = imagen.shape[1], alto = imagen.shape[0])
    cache_linea_x, cache_linea_y = precaluclar_todas_las_posibles_lineas(numero_de_pines,posiciones_pines[0],posiciones_pines[1],distancia_minima)
    return {"ancho":imagen.shape[0],
            "vector_de_la_imagen":vector_de_la_imagen,
            "posiciones_pines":np.column_stack(posiciones_pines),
            "linea_cache_x":cache_linea_x,
            "linea_cache_y":cache_linea_y}

# testing
if __name__ == "__main__":
    a = _construir_vector_imagen_bucles(cv2.imread("../../ejemplos/ae300.jpg"))
    b = construir_vector_imagen(cv2.imread("../../ejemplos/ae300.jpg"))
    _construir_vector_imagen_bucles(cv2.imread("../../ejemplos/ae300.jpg"))
    construir_vector_imagen(cv2.imread("../../ejemplos/ae300.jpg"))
    print((a == b).all())
