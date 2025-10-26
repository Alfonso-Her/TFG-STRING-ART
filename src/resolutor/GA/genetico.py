from deap import creator,base,tools,algorithms
from typing import Unpack, Callable, Tuple
import random
import numpy as np

from multiprocessing import Pool

# from .visuales import imprimir_poblacion_pandas
from .guardar import guardar_checkpoint,guardar_checkpoint_final,\
                    cargar_checkpoint,limpiar_checkpoints_antiguos,\
                    crear_directorio_temporal
from ..parametros import ParametrosResolucion,ReturnResolutor
from ..utils import secuencia_pines_a_error

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



def reparar_individuo(ind: list[int], numero_de_pines: int, dist_min: int) -> list[int]:
    """
    Repara secuencia post-mutación/cruce, ajustando pines inválidos secuencialmente.
    """
    for i in range(1, len(ind)):
        dist = min(abs(ind[i] - ind[i-1]), numero_de_pines - abs(ind[i] - ind[i-1]))
        while dist < dist_min:
            ind[i] = random.choice([p for p in range(numero_de_pines) if min(abs(p - ind[i-1]), numero_de_pines - abs(p - ind[i-1])) >= dist_min])
            dist = min(abs(ind[i] - ind[i-1]), numero_de_pines - abs(ind[i] - ind[i-1]))
    return ind


def inicializar_ag(funcion_evaluacion: Callable[[list[int]],Tuple[np.float64,None]],
                   numero_de_pines:int = 256,
                   maximo_lineas:int=4000,
                   distancia_minima:int = 0,
                   probabilidad_mutacion_gen: float = 0.3,
                   cantidad_torneo: int = 3
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

    # toolbox.register("map", Pool().map)

    def crear_individuo_con_restrucciones(maximo_lineas:int,
                                      numero_de_pines:int,
                                        distancia_minima:int,
                                        ):
        longitud = random.randint(maximo_lineas//2,maximo_lineas)

        pin_actual = random.randint(0,numero_de_pines-1)
        
        individuo = [pin_actual] #todas las sol empizan en 0

        for _ in range(longitud):
            # Get available pins based on constraints
            pines_disponibles = [p for p in range(numero_de_pines) if (abs(pin_actual-p)%numero_de_pines)>distancia_minima] 
            
            if not pines_disponibles:
                pines_disponibles = [p for p in range(numero_de_pines) if p != pin_actual]
                
            siguiente_pin = random.choice(pines_disponibles)
            individuo.append(siguiente_pin)
            pin_actual = siguiente_pin
        
        return creator.individuo(individuo)
    
    # Definimos un individuo como una secuencia de cromosomas
    toolbox.register("individuo",
                     crear_individuo_con_restrucciones,
                     maximo_lineas=maximo_lineas,
                     numero_de_pines=numero_de_pines,
                     distancia_minima=distancia_minima)

    # Definimos una poblacion como un conjunto de indivuduos
    toolbox.register("poblacion", tools.initRepeat, list, toolbox.individuo)


    # Definimos una funcion para medir que tan buenas son nuestras soluciones
    toolbox.register("evaluar",funcion_evaluacion)

    # Definimos operaciones clave en el algoritmo genetico

    def mutar_reparando(ind:list[int]):
        ind, = tools.mutUniformInt(ind, low=0, up=numero_de_pines-1, indpb=probabilidad_mutacion_gen)
        reparar_individuo(ind, numero_de_pines, distancia_minima)
        del ind.fitness.values
        return ind,

    def aparear_reparado(ind1, ind2):
        ind1, ind2 = tools.cxTwoPoint(ind1, ind2)
        reparar_individuo(ind1, numero_de_pines, distancia_minima)
        reparar_individuo(ind2, numero_de_pines, distancia_minima)
        del ind1.fitness.values
        del ind2.fitness.values
        return ind1, ind2
    
    toolbox.register("aparear", aparear_reparado)
    toolbox.register("mutar",
                     mutar_reparando)
    toolbox.register("seleccionar", tools.selTournament, tournsize=cantidad_torneo)
    return toolbox

def obtener_camino_ag(linea_cache_x:np.ndarray,
                    linea_cache_y:np.ndarray,
                    ancho:int,
                    alto:int,
                    vector_de_la_imagen:np.ndarray,
                    ruta_a_resultado: str,
                    distancia_minima:int=0,
                    funcion_calculo_error :Callable[[np.ndarray],np.float64] = mse,
                    numero_de_pines:int = 256,
                    maximo_lineas:int= 4000,
                    peso_de_linea:int = 20,
                    verbose:bool = False,
                    reanudar:bool = False,
                    frecuencia_checkpoint:int = 10,
                    mantener_checkpoints:int = 2,
                    cantidad_poblacion: int = 100,
                    elitismo_size:int = 1,
                    numero_generaciones: int = 50,
                    probabilidad_cruce: float = 0.7,
                    probabilidad_mutacion: float = 0.2,
                    cantidad_torneo: int = 3,
                    **kwargs:Unpack[ParametrosResolucion])->ReturnResolutor:
    
    #Creamos imagen error y inicializamos directorios y variables
    error_acumulado = np.full(ancho*alto, 255.0) - vector_de_la_imagen
    funcion_evaluacion = lambda secuencia_solucion: _crear_funcion_error(secuencia_pines=secuencia_solucion,
                                                                   error_acumulado=error_acumulado,
                                                                   linea_cache_y=linea_cache_y,
                                                                   linea_cache_x=linea_cache_x,
                                                                   ancho= ancho,
                                                                   numero_de_pines=numero_de_pines,
                                                                   peso_de_linea=peso_de_linea,
                                                                   funcion_calculo_error=funcion_calculo_error)
    toolbox = inicializar_ag(numero_de_pines=numero_de_pines,
                             maximo_lineas=maximo_lineas,
                             funcion_evaluacion=funcion_evaluacion,
                             distancia_minima=distancia_minima,
                             cantidad_torneo=cantidad_torneo)
    
    directorio_checkpoints = crear_directorio_temporal(ruta_a_resultado)
    generacion_inicial=0
    poblacion = toolbox.poblacion(n= cantidad_poblacion)
    hall_of_fame  = tools.HallOfFame(maxsize=elitismo_size)
    logbook = tools.Logbook()
    
    if reanudar:
        try:
            ckp_data = cargar_checkpoint(directorio_checkpoints)
        except Exception as e:
            raise(Exception(f"Ocurrio un error en la carga del chekcpoint: {e}"))
        if ckp_data is not None:
            poblacion = ckp_data['poblacion']
            hall_of_fame = ckp_data['hall_of_fame']
            logbook = ckp_data['logbook']
            generacion_inicial = ckp_data['generacion'] + 1

            if ckp_data['random_state'] is not None:
                random.setstate(ckp_data['random_state'])

            print(f"[AG] Reanudando desde generación {generacion_inicial}")
        else:
            print(f"[AG] Iniciando nueva ejecución")

    # Estadisticas para el logbook
    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("avg", np.mean)    # Error promedio de la población
    stats.register("std", np.std)     # Desviación estándar
    stats.register("min", np.min)     # Mejor fitness (menor error)
    stats.register("max", np.max)     # Peor fitness (mayor error)

    

    try:
        # Bucle manual de generaciones para control de checkpoints
        for gen in range(generacion_inicial, numero_generaciones):
            
            
            # Evaluar individuos sin fitness
            individuos_invalidos = [ind for ind in poblacion if not ind.fitness.valid]
            if individuos_invalidos:  # Solo si hay inválidos
                fitnesses = toolbox.map(toolbox.evaluar, individuos_invalidos)
                for ind, fit in zip(individuos_invalidos, fitnesses):
                    ind.fitness.values = fit
            
            # Usar y actualizar hall of fame
            poblacion.sort(key=lambda ind: ind.fitness.values[0]) 
            for i, elite in enumerate(hall_of_fame):
                poblacion[-1 - i] = toolbox.clone(elite)

            print("HOLA PRUEBA EL ERROR ES :",poblacion[0].fitness.values[0],"Y LA FINAL ES: ",poblacion[1].fitness.values[0]) 

            hall_of_fame.update(poblacion)
            
            
            # Registrar estadísticas
            record = stats.compile(poblacion)
            logbook.record(gen=gen, **record)
            
            # Mostrar progreso
            if verbose:
                print(f"Gen {gen:4d} | "
                      f"Min: {record['min']:.6f} | "
                      f"Avg: {record['avg']:.6f} | "
                      f"Max: {record['max']:.6f}")
            
            
            # Guardar checkpoint periódicamente
            if (gen + 1) % frecuencia_checkpoint == 0:
                ruta_ckp= guardar_checkpoint(
                    directorio_checkpoints,
                    gen,
                    poblacion,
                    hall_of_fame,
                    logbook,
                    random_state=random.getstate()
                )
                print(f"[Checkpoint] Guardado en generación {ruta_ckp}")
                
                # Limpiar checkpoints antiguos
                limpiar_checkpoints_antiguos(
                    directorio_checkpoints,
                    mantener=mantener_checkpoints
                )
            
            # Si es la última generación, no generar descendencia
            if gen == numero_generaciones - 1:
                break
            
            
            # Seleccionar siguiente generación
            descendencia = toolbox.seleccionar(poblacion, len(poblacion))
            descendencia = list(toolbox.map(toolbox.clone, descendencia))
            
            
            # Aplicar cruce
            for hijo1, hijo2 in zip(descendencia[::2], descendencia[1::2]):
                if random.random() < probabilidad_cruce:
                    toolbox.aparear(hijo1, hijo2)
            
            
            # Aplicar mutación
            for mutante in descendencia:
                if random.random() < probabilidad_mutacion:
                    toolbox.mutar(mutante)
            

            # Reemplazar población
            poblacion[:] = descendencia
            print("poblacion: ", type(poblacion),poblacion[-1].fitness.values)
        
        print("[AG] Evolución completada exitosamente")
        
    except KeyboardInterrupt:
        print("\n[AG] Interrupción detectada. Guardando checkpoint...")
        guardar_checkpoint(
            directorio_checkpoints,
            gen,
            poblacion,
            hall_of_fame,
            logbook,
            random_state=random.getstate()
        )
        print("[AG] Checkpoint guardado. Puedes reanudar con reanudar=True")
        raise



    # poblacion_final, logbook = algorithms.eaSimple(
    #     poblacion,
    #     toolbox,
    #     cxpb=probabilidad_cruce,      
    #     mutpb=probabilidad_mutacion,  
    #     ngen=numero_generaciones,     
    #     stats=stats,
    #     halloffame=hall_of_fame,
    #     verbose=verbose
    # )

    mejor_individuo = hall_of_fame[0]
    mejor_error = mejor_individuo.fitness.values[0]

    imagen_error_final = secuencia_pines_a_error(
                            mejor_individuo,
                            error_acumulado.copy(),
                            linea_cache_y,
                            linea_cache_x,
                            ancho,
                            numero_de_pines,
                            peso_de_linea
                        )

    guardar_checkpoint_final(
        directorio_checkpoints,
        list(mejor_individuo),
        mejor_error,
        logbook,
    )
    if verbose:
        
        print(logbook)

        return ReturnResolutor(
            peso_de_linea=peso_de_linea,
            distancia_minima=kwargs.get('distancia_minima', 0),
            maximo_lineas=maximo_lineas,
            error_total=imagen_error_final,
            secuencia_pines=np.array(mejor_individuo),
            imagen_preprocesada=vector_de_la_imagen.reshape(-1, ancho),
            imagen_error_preresolutor=error_acumulado.reshape(-1, ancho),
            imagen_error_post_resolutor=imagen_error_final.reshape(-1, ancho)
        )
    else:
        return ReturnResolutor(
            peso_de_linea=peso_de_linea,
            distancia_minima=kwargs.get('distancia_minima', 0),
            maximo_lineas=maximo_lineas,
            error_total=imagen_error_final,
            secuencia_pines=np.array(mejor_individuo)
        )