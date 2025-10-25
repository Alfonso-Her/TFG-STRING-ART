from deap import creator,base,tools,algorithms
from typing import Unpack, Callable, Tuple
import random
import numpy as np

from .parametros import ParametrosResolucion,ReturnResolutor
from .utils import secuencia_pines_a_error

from calcular_error import mse

def _crear_funcion_error(secuencia_pines:list[int],
                         error_acumulado:np.ndarray,
                         linea_cache_y:np.ndarray,
                         linea_cache_x:np.ndarray,
                         ancho:int,
                         numero_de_pines,peso_de_linea:int,
                         funcion_calculo_error:Callable[[np.ndarray],np.float64] = mse):
    """
        Dada la imagen del error y una solucion evalua la solucion mediante funcion_calculo_error
        devuelve una tupla error,_ por necesidad de cudrar tipos con la API de DEAP
    """
    return funcion_calculo_error(secuencia_pines_a_error(secuencia_pines,
                                                         error_acumulado.copy(),
                                                         linea_cache_y,
                                                         linea_cache_x,
                                                         ancho,
                                                         numero_de_pines,
                                                         peso_de_linea)),

def inicializar_ag(funcion_evaluacion: Callable[[list[int]],Tuple[np.float64,None]],
                   numero_de_pines:int = 256,
                   maximo_lineas:int=4000,
                   probabilidad_mutacion_gen: float = 0.3
                   ) -> base.Toolbox:
    """
        Configuramos la API para que nos permita resolver nuestro problema,
        para ello lo que hacemos es definir cada elemento en una interfaz de
        alto nivel
    """
    try:
        creator.create("FitnessMin",base.Fitness, weights=(-1.0,))
        creator.create("individuo", list, fitness=creator.FitnessMin)
    except Exception:
        pass # por si acaso multiples llamadas a incializar_ag no es un error se reutilizan

    toolbox = base.Toolbox()
    # Definimos el "cromosoma"
    toolbox.register("pin" ,random.randint, 0, numero_de_pines-1)
    # Definimos un individuo como una secuencia de cromosomas
    toolbox.register("individuo",
                     tools.initRepeat,
                     creator.individuo,
                     toolbox.pin,
                     maximo_lineas)
    # Definimos una poblacion como un conjunto de indivuduos
    toolbox.register("poblacion", tools.initRepeat, list, toolbox.individuo)
    # Definimos una funcion para medir que tan buenas son nuestras soluciones
    toolbox.register("evaluar",funcion_evaluacion)

    # Definimos operaciones clave en el algoritmo genetico
    toolbox.register("aparear", tools.cxTwoPoint)
    toolbox.register("mutacion",
                     tools.mutUniformInt,
                     low= 0,
                     up=numero_de_pines-1,
                     indpb=probabilidad_mutacion_gen)
    return toolbox

def obtener_camino_ag(linea_cache_x:np.ndarray,
                    linea_cache_y:np.ndarray,
                    ancho:int,
                    alto:int,
                    vector_de_la_imagen:np.ndarray,
                    funcion_calculo_error :Callable[[np.ndarray],np.float64] = mse,
                    numero_de_pines:int = 256,
                    maximo_lineas:int= 4000,
                    peso_de_linea:int = 20,
                    verbose:bool = False,
                    cantidad_poblacion: int = 100,
                    cantidad_teletransportar_entre_gen:int = 1,
                    numero_generaciones: int = 50,
                    probabilidad_cruce: float = 0.7,
                    probabilidad_mutacion: float = 0.2,
                    probabilidad_mutacion_gen: float = 0.1,
                    cantidad_torneo: int = 3,
                    **kwargs:Unpack[ParametrosResolucion])->ReturnResolutor:
    
    #Creamos imagen error
    error_acumulado = np.full(ancho*alto, 255.0) - vector_de_la_imagen

    # Crear funcion de error
    funcion_evaluacion = lambda secuencia_solucion: _crear_funcion_error(secuencia_pines=secuencia_solucion,
                                                                   error_acumulado=error_acumulado,
                                                                   linea_cache_y=linea_cache_y,
                                                                   linea_cache_x=linea_cache_x,
                                                                   ancho= ancho,
                                                                   numero_de_pines=numero_de_pines,
                                                                   peso_de_linea=peso_de_linea,
                                                                   funcion_calculo_error=funcion_calculo_error)
    #inicializar api
    toolbox = inicializar_ag(numero_de_pines=numero_de_pines,
                             maximo_lineas=maximo_lineas,
                             funcion_evaluacion=funcion_evaluacion)
    # algoritmo genetico
    poblacion = toolbox.poblacion(n= cantidad_poblacion)
    
    hall_of_fame  = tools.HallOfFame(maxsize=cantidad_teletransportar_entre_gen)

    # Estadisticas
    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("avg", np.mean)    # Error promedio de la población
    stats.register("std", np.std)     # Desviación estándar
    stats.register("min", np.min)     # Mejor fitness (menor error)
    stats.register("max", np.max)     # Peor fitness (mayor error)
    
    poblacion_final, logbook = algorithms.eaSimple(
        poblacion,
        toolbox,
        cxpb=probabilidad_cruce,      
        mutpb=probabilidad_mutacion,  
        ngen=numero_generaciones,     
        stats=stats,
        halloffame=hall_of_fame,
        verbose=verbose
    )

    mejor_individuo = hall_of_fame[0]
    mejor_error = mejor_individuo.fitness.values[0]

    
    if verbose:
        imagen_error_final = secuencia_pines_a_error(
                            mejor_individuo,
                            error_acumulado.copy(),
                            linea_cache_y,
                            linea_cache_x,
                            ancho,
                            numero_de_pines,
                            peso_de_linea
                        )
        
        return ReturnResolutor(
            peso_de_linea=peso_de_linea,
            distancia_minima=kwargs.get('distancia_minima', 0),
            maximo_lineas=maximo_lineas,
            error_total=mejor_error,
            secuencia_pines=np.array(mejor_individuo),
            imagen_preprocesada=vector_de_la_imagen.reshape(alto, ancho),
            imagen_error_pre_resolutor=error_acumulado.reshape(alto, ancho),
            imagen_error_post_resolutor=imagen_error_final.reshape(alto, ancho)
        )
    else:
        return ReturnResolutor(
            peso_de_linea=peso_de_linea,
            distancia_minima=kwargs.get('distancia_minima', 0),
            maximo_lineas=maximo_lineas,
            error_total=mejor_error,
            secuencia_pines=np.array(mejor_individuo)
        )