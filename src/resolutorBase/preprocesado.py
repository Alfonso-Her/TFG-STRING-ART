import cv2
import numpy as np

# Tratamiento de la imagen

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


# Generacion de pines
def calcular_posicion_pins()->:

# Precalculo de hiladas


if __name__ == "__main__":
    a = construir_vector_imagen_bucles(cv2.imread("../../ejemplos/ae300.jpg"))
    b = construir_vector_imagen(cv2.imread("../../ejemplos/ae300.jpg"))
    construir_vector_imagen_bucles(cv2.imread("../../ejemplos/ae300.jpg"))
    construir_vector_imagen(cv2.imread("../../ejemplos/ae300.jpg"))
    print((a == b).all())
