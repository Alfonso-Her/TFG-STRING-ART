import numpy as np 
import cv2


def recortar_rectangulo(img,pixel_inicial_ancho = 0 ,pixel_inicial_alto = 0): # TODO permitir recortar lo que se quiera
    """
        Dada una imagen rectangular recorta el cuadrado mas grande posible (si ya es cuadrada no hace nada)
    """
    alto,ancho = img.shape[0:2]
    padding = abs((alto-ancho) // 2)
    return img[padding:padding+ancho,:] if ancho < alto else img[:,padding:padding+alto]

def aplicar_mascara_circular(img:np.ndarray):
    alto,ancho = img.shape[0:2]
    y,x = np.indices((alto,ancho))
    distancias = np.sqrt((x-ancho/2)**2+(y-alto/2)**2)
    mascara = distancias <= min(ancho,alto)/2
    img_return = img.copy()

    if img.ndim == 3:  # Imagen en color 
        img_return[~mascara] = [255, 255, 255]
    else:  # Imagen en escala de grises
        img_return[~mascara] = 255

    return img_return

def redimensionar_a_rectangulo(img:np.ndarray)->np.ndarray:
    # OJO esta funcion deforma las imagenes
    alto, ancho = img.shape[0:2]
    lado_cuadrado = max(alto,ancho)

    return cv2.resize(img,(lado_cuadrado,lado_cuadrado), interpolation=cv2.INTER_AREA)

def pasar_img_a_grises(img:np.ndarray)->np.ndarray:
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



def marcar_bordes_en_img(img:np.ndarray,num_inf:int=150,num_sup:int=190)->np.ndarray:
    bordes_inv = 255-cv2.Canny(img,num_inf,num_sup)
    return np.minimum(img, bordes_inv)
    


def preprocesar_imagen( imagen:np.ndarray, filtro_bordes_inferior:int =150,
                         pasar_a_grises:bool = True, filtro_bordes_superior:int = 190,
                         redimensionar:bool = False, recortar:bool = True,
                         mascara_circular:bool = True, marcar_bordes:bool = True) -> np.ndarray: 
    
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

    return imagen