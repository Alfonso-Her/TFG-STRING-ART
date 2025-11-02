import numpy as np
from typing import Unpack, Callable


from ..parametros import ReturnResolutor, ParametrosResolucion
from ..utils import get_line_err, agregar_lineas_al_error
from .utilsGrafos import generar_grafo
# from.solverModificado import StringArtSolver
from calcular_error import mse



def obtener_camino_aco(
                        linea_cache_x: np.ndarray,
                        linea_cache_y: np.ndarray,
                        ancho: int,
                        alto: int,
                        vector_de_la_imagen: np.ndarray,
                        numero_de_pines: int = 256,
                        maximo_lineas: int = 4000,
                        distancia_minima: int = 0,
                        peso_de_linea: int = 20,
                        numero_de_pines_recientes_a_evitar: int = 5,
                        funcion_calculo_error: Callable[[np.ndarray], np.float64] = mse,
                        numero_hormigas: int = 20, 
                        iteraciones_aco: int = 100, 
                        alpha: float = 1.0,
                        beta: float = 2.0,
                        rho: float = 0.1,
                        q: float = 1.0,
                        verbose: bool = False,
                        **kwargs: Unpack[ParametrosResolucion]
                    ) -> ReturnResolutor:
    
    error_acumulado = vector_de_la_imagen.copy()
    if verbose:
        imagen_preprocesada = vector_de_la_imagen.copy().reshape(alto, ancho)
        imagen_error_preresolutor = error_acumulado.copy().reshape(alto, ancho)
    
    grafo = generar_grafo(numero_de_pines=numero_de_pines,
                          error_acumulado=error_acumulado,
                          distancia_minima=distancia_minima,
                          ancho=ancho,
                          linea_cache_y=linea_cache_y,
                          linea_cache_x=linea_cache_x)
    
    

    # if verbose:
    #     print(f"Mejor error final: {mejor_error}")

    # indices_lineas = [mejor_secuencia[i+1] * numero_de_pines + mejor_secuencia[i] for i in range(len(mejor_secuencia)-1)]
    # error_final = agregar_lineas_al_error(indices_lineas, error_acumulado, linea_cache_y, linea_cache_x, ancho, peso_de_linea)
    
    # if verbose:
    #     imagen_error_post_resolutor = error_final.reshape(alto, ancho)
    #     return ReturnResolutor(
    #         peso_de_linea=peso_de_linea,
    #         distancia_minima=distancia_minima,
    #         maximo_lineas=maximo_lineas,
    #         error_total=error_final,
    #         secuencia_pines=np.array(mejor_secuencia),
    #         imagen_preprocesada=imagen_preprocesada,
    #         imagen_error_preresolutor=imagen_error_preresolutor,
    #         imagen_error_post_resolutor=imagen_error_post_resolutor,
    #     )
    
    # return ReturnResolutor(
    #     peso_de_linea=peso_de_linea,
    #     distancia_minima=distancia_minima,
    #     maximo_lineas=maximo_lineas,
    #     error_total=error_final,
    #     secuencia_pines=np.array(mejor_secuencia)
    # )