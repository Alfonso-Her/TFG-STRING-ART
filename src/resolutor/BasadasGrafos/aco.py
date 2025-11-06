import numpy as np
from typing import Unpack, Callable, List, Optional,Tuple
from random import randint, choice

from ..parametros import ReturnResolutor, ParametrosResolucion
from ..utils import get_line_err, agregar_lineas_al_error
from .utilsGrafos import generar_grafo
# from.solverModificado import StringArtSolver
from calcular_error import mse

from ..utils import secuencia_pines_a_error

class OCH_StringArt:
    def __init__(
        self,
        funcion_calculo_error: Callable[[np.ndarray], float],
        numero_de_pines: int,
        vector_de_la_imagen: np.ndarray,
        linea_cache_x: List[Optional[np.ndarray]],
        linea_cache_y: List[Optional[np.ndarray]],
        ancho: int,
        peso_de_linea: int = 20,
        maximo_lineas: int = 1000,
        cantidad_poblacion: int = 10,
        max_iter: int = 100,
        alpha: float = 1.0,
        beta: float = 0.0,
        rho: float = 0.1,
        distancia_minima: int = 0):

        self.funcion_error_bruto =\
            lambda secuencia: secuencia_pines_a_error(secuencia_pines=secuencia,
                                                      error_acumulado=vector_de_la_imagen,
                                                      linea_cache_x=linea_cache_x,
                                                      linea_cache_y=linea_cache_y,
                                                      ancho=ancho,
                                                      numero_de_pines=numero_de_pines,
                                                      peso_de_linea=peso_de_linea)  
        self.numero_de_pines =  numero_de_pines
        self.vector_de_la_imagen = vector_de_la_imagen
        self.linea_cache_x = linea_cache_x
        self.linea_cache_y = linea_cache_y
        self.ancho = ancho
        self.peso_de_linea = peso_de_linea

        self.maximo_lineas = int(maximo_lineas)
        self.cantidad_poblacion = int(cantidad_poblacion)
        self.max_iter = int(max_iter)
        self.alpha = float(alpha)
        self.beta = float(beta) 
        self.rho = float(rho)
        self.distancia_minima = int(distancia_minima)
        self.pin_comienzo = 0


        self.Tau = np.ones((self.n_pins, self.n_pins), dtype=float)
        self.Table = np.zeros((self.cantidad_poblacion, self.maximo_lineas), dtype=int)

        self.mejores_soluciones: List[np.ndarray] = []
        self.mejores_errores: List[float] = []
        self.mejor_solucion: Optional[np.ndarray] = None
        self.mejor_error: Optional[float] = None

    def _obtener_indice(self, pin_a: int, pin_b: int) -> int:
        return pin_b * self.n_pins + pin_a

    def _es_arista_valida(self, a: int, b: int) -> bool:
        if a == b:
            return False  # evitar auto-bucle
        idx = self._obtener_indice(a, b)
        if idx < 0 or idx >= len(self.linea_cache_x):
            return False
        if self.linea_cache_x[idx] is None or self.linea_cache_y[idx] is None:
            return False
        return True
    
    def _normalizar_prob(self, probs: np.ndarray) -> np.ndarray:
        total = probs.sum()
        if total <= 0 or np.isnan(total):
            mask = probs >= 0 
            if mask.sum() == 0:
                # último recurso: uniforme sobre todos
                return np.ones_like(probs) / probs.size
            else:
                res = np.zeros_like(probs)
                res[mask] = 1.0 / mask.sum()
                return res
        return probs / total
    
    def run(self, verbose: bool = False) -> Tuple[np.ndarray, float]:

        eps = 1e-12

        for iteration in range(self.max_iter):

            matriz_probabilidades_crudas = (self.Tau ** self.alpha)

            for j in range(self.cantidad_poblacion):
                # inicio
                if self.pin_comienzo is None:
                    pin_actual = randint(0, self.numero_de_pines)
                else:
                    pin_actual = self.pin_comienzo
                self.Table[j, 0] = pin_actual

                # pasos restantes
                for k in range(self.maximo_lineas - 1):

                    probs = np.zeros(self.numero_de_pines, dtype=float)
                    fila = matriz_probabilidades_crudas[pin_actual, :]

                    for pin_candidato in range(self.numero_de_pines):
                        if self._es_arista_valida(pin_actual, pin_candidato):
                            probs[pin_candidato] = fila[pin_candidato]

            
                    probs = self._normalizar_prob(probs)

                    # elegir siguiente pin (según probs)
                    siguiente_pin = int(choice(self.n_pins, p=probs))
                    self.Table[j, k + 1] = siguiente_pin
                    pin_actual = siguiente_pin

            # Evaluación
            errores = np.zeros(self.cantidad_poblacion, dtype=float)

            for j in range(self.cantidad_poblacion):
                secuencia = list(map(int, self.Table[j, :]))
                error = float(self.funcion_fitness(secuencia))
                errores[j] = error

            # guardar mejor de la generación
            idx_best_gen = errores.argmin()
            mejor_solucion = self.Table[idx_best_gen, :].copy()
            mejor_error = float(errores[idx_best_gen])
            self.mejores_soluciones.append(mejor_solucion)
            self.mejores_errores.append(mejor_error)

            if verbose:
                print(f"[iter {iteration+1}/{self.max_iter}] best_gen_error={mejor_error:.6f}")

            # Actualización de feromonas: delta_tau en función de la calidad (inversa del error)
            delta_tau = np.zeros_like(self.Tau, dtype=float)

            for j in range(self.cantidad_poblacion):
                secuencia = list(map(int, self.Table[j, :]))
                error = errores[j]
                # protección contra división por cero
                contrib = 1.0 / (error + eps)
                # sumar contribución a cada arista recorrida (sin cerrar ciclo)
                for k in range(self.maximo_lineas - 1):
                    n1 = secuencia[k]
                    n2 = secuencia[k + 1]
                    if self._es_arista_valida(n1, n2):
                        delta_tau[n1, n2] += contrib

            # evaporación + depósito
            self.Tau = (1.0 - self.rho) * self.Tau + delta_tau

        # seleccionar la mejor generación global
        mejor_idx = int(np.argmin(np.array(self.mejores_errores)))
        self.solucion_final = self.mejores_soluciones[mejor_idx].copy()
        self.error_final = float(self.mejores_errores[mejor_idx])

        return self.solucion_final, self.error_final
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