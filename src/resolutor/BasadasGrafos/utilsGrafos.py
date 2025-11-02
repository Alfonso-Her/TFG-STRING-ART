import numpy as np
import networkx as nx

from ..utils import get_line_err


    
def generar_grafo(numero_de_pines:int,error_acumulado:np.ndarray,distancia_minima:int,
                  ancho:int,linea_cache_y:list,linea_cache_x:list)->nx.Graph:
    
    """
        Devuelve un grafo completo con todas las aristas y sus pesos calculados en funcion las
        linea_cache_k
    """
    grafo = nx.Graph()
    grafo.add_nodes_from(range(numero_de_pines))

    for i in range(numero_de_pines):
        for j in range(i + distancia_minima, numero_de_pines):
            index = j * numero_de_pines + i
            reduccion_error = get_line_err(error_acumulado, linea_cache_y[index], linea_cache_x[index], ancho)
            grafo.add_edge(i, j, eta=reduccion_error)

    return grafo

def generar_matriz_feromonas(numero_de_pines:int):
    return np.ones((numero_de_pines,numero_de_pines)) + np.eye(numero_de_pines)*-np.inf

def probabilidades_caminos(pin_actual:int,numero_de_pines:int,grafo:nx.Graph,feromonas:np.array, alfa:np.float64,beta:np.float64):
    disponibles = list(grafo.neighbors(pin_actual))
    denominador = np.sum([((grafo[pin_actual][i])**alfa)*(feromonas[pin_actual][i])**beta 
                          for i in disponibles])
    return np.array([(((grafo[pin_actual][i])**alfa)*(feromonas[pin_actual][i])**beta)/denominador 
                        if i in disponibles else 0 for i in range(numero_de_pines)])
