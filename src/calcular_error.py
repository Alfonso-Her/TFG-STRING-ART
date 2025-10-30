import numpy as np
import enum

from skimage.metrics import structural_similarity 

# TODO ?
def retomar_grises_original(imagen_error_total:np.ndarray)->np.float64:
    """
        Esta funcion desace la transformacion que hacemos al iniciar el vector de error total en obtener camino
        de manera que el error cuadra con mas error cuanto mas blanco
    """
    return imagen_error_total 

def mse(imagen_error: np.ndarray) -> np.float64:
    """Mean Squared Error."""
    return np.float64(np.mean(np.square(retomar_grises_original(imagen_error))))

def rmse(imagen_error: np.ndarray) -> np.float64:
    """Root Mean Squared Error."""
    return np.float64(np.sqrt(np.mean(np.square(retomar_grises_original(imagen_error)))))

def mae(imagen_error: np.ndarray) -> np.float64:
    """Mean Absolute Error."""
    return np.float64(np.mean(np.abs(retomar_grises_original(imagen_error))))

def ssim(imagen_original:np.ndarray, imagen_resultado:np.ndarray) -> np.float64:
    """ ssim (Compara como de similares son dos imagenes), OJOOOO Requiere que hagas una lambda para
        Poder usarla (fijando la imagen original), como da valores entre -1 y 1,
        al hacer 1 - error obtenemos una funcion de error que cumple que cuanto menor es mas se parece
    """
    return 1 - np.float64(structural_similarity(imagen_original,imagen_resultado, data_range=255))
# BORRADAS PORQUE NO TIENEN SENTIDO TE EQUIVOCAS EN EL ORDEN EN VEZ DE SUMAR ABS O CUADRADOS
# HACES ABS/CUADRADOS DE SUMAS => ERROR
# def suma_abs(imagen_error_total:np.ndarray)->np.float64:
#     return np.float64(np.abs(np.sum(retomar_grises_original(imagen_error_total))))

# def suma_cuad(imagen_error_total:np.ndarray)->np.float64:
#     return np.float64(np.square(np.sum(retomar_grises_original(imagen_error_total))))

# ESTA FALLA PORQUE LA LOGICA ES JUSTO A LA INVERSA YA QUE ESTA DECRE CUANTO MAYOR ERROR HAY
# def psnr(imagen_error: np.ndarray, max_val: float = 255.0) -> np.float64:
#     """Peak Signal-to-Noise Ratio (en decibelios)."""
#     mse_val = np.mean(np.square(imagen_error))
#     if mse_val == 0:
#         return np.float64(np.inf)
#     return np.float64(10 * np.log10((max_val ** 2) / mse_val))

