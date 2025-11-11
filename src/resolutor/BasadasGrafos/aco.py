import numpy as np
from typing import Unpack, Callable, List, Optional,Tuple
from random import randint

from ..parametros import ReturnResolutor, ParametrosResolucion
from ..utils import get_line_err, agregar_lineas_al_error

# from.solverModificado import StringArtSolver
from calcular_error import mse

from ..utils import secuencia_pines_a_error

class OCH_StringArt:
    def __init__(
        self,
        _error_de_secuencia: Callable[[np.ndarray], float],
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
        q:float=1.0,
        distancia_minima: int = 0,
        verbose:bool =False):

        self._error_de_secuencia = _error_de_secuencia # ojo

        self.funcion_error_bruto =\
            lambda secuencia: secuencia_pines_a_error(secuencia_pines=secuencia,
                                                      error_acumulado=vector_de_la_imagen.copy(),
                                                      linea_cache_x=linea_cache_x,
                                                      linea_cache_y=linea_cache_y,
                                                      ancho=ancho,
                                                      numero_de_pines=numero_de_pines,
                                                      peso_de_linea=peso_de_linea)  
        
        self.funcion_fitness =\
              lambda secuencia: _error_de_secuencia(self.funcion_error_bruto(secuencia=secuencia))
        
        self.numero_de_pines =  numero_de_pines
        self.vector_de_la_imagen = vector_de_la_imagen
        self.linea_cache_x = linea_cache_x
        self.linea_cache_y = linea_cache_y
        self.ancho = ancho
        self.peso_de_linea = peso_de_linea
        self.verbose = verbose
        self.maximo_lineas = int(maximo_lineas)
        self.cantidad_poblacion = int(cantidad_poblacion)
        self.max_iter = int(max_iter)
        self.alpha = float(alpha)
        self.beta = float(beta) 
        self.rho = float(rho)
        self.q = q
        self.distancia_minima = int(distancia_minima)
        self.pin_comienzo = 0


        self.Tau = np.ones((self.numero_de_pines, self.numero_de_pines), dtype=float)

        self.Table = -np.ones((self.cantidad_poblacion, self.maximo_lineas), dtype=int) # ojo

        self.mejores_soluciones: List[np.ndarray] = []
        self.mejores_errores: List[float] = []
        self.mejor_solucion: Optional[np.ndarray] = None
        self.mejor_error: Optional[float] = None

    def _obtener_indice(self, pin_a: int, pin_b: int) -> int:
        return pin_b * self.numero_de_pines + pin_a

    def _es_arista_valida(self, a: int, b: int) -> bool:
        dist = min(abs(a - b), self.numero_de_pines - abs(a - b))
        idx = self._obtener_indice(a, b)
        if a == b:
            return False  # evitar auto-bucle
        if dist < self.distancia_minima:
            return False
        if idx < 0 or idx >= len(self.linea_cache_x):
            return False
        if self.linea_cache_x[idx] is None or self.linea_cache_y[idx] is None:
            return False
        return True
    
    def _normalizar_prob(self, probs: np.ndarray) -> np.ndarray:
        total = probs.sum()
        if total <= 0 or np.isnan(total):
            if probs.size == 0:
                return probs
            return np.ones_like(probs) / probs.size
        return probs / total
    
    def run(self) -> Tuple[np.ndarray,np.ndarray, float]:

        eps = 1e-12

        for iteration in range(self.max_iter):

            for j in range(self.cantidad_poblacion):
                print("Entramos a rellenar otra hormiga")
                vector_actual = self.vector_de_la_imagen.copy() 
                error_actual = float(self._error_de_secuencia(vector_actual))

                # inicio
                if self.pin_comienzo is None:
                    pin_actual = randint(0, self.numero_de_pines-1)
                else:
                    pin_actual = self.pin_comienzo
                self.Table[j, 0] = pin_actual

                # pasos restantes
                pasos = 0 
                for k in range(self.maximo_lineas - 1):

                    indices_validos = []
                    pesos_validos = []

                    fila_tau = self.Tau[pin_actual, :]


                    for pin_candidato in range(self.numero_de_pines):

                        if not self._es_arista_valida(pin_actual, pin_candidato):
                            continue

                        tau_val = fila_tau[pin_candidato] ** self.alpha
                        
                        if self.beta == 0.0:
                            eta_val = 1.0
                        else:
                            idx = self._obtener_indice(pin_actual, pin_candidato)
                            x_coords = self.linea_cache_x[idx]
                            y_coords = self.linea_cache_y[idx]
                      
                            if x_coords is None or y_coords is None:
                                continue

                            indices = (y_coords * self.ancho + x_coords).astype(int)
                            valor_antiguo = vector_actual[indices].copy()
                            vector_actual[indices] = np.maximum(vector_actual[indices] - self.peso_de_linea, 0.0)
                            nuevo_error = float(self._error_de_secuencia(vector_actual))
                            mejoria = error_actual - nuevo_error
                            vector_actual[indices] = valor_antiguo
                            eta_val = max(mejoria, eps)

                        weight = tau_val * (eta_val ** self.beta)
                        if weight > 0:
                            indices_validos.append(pin_candidato)
                            pesos_validos.append(weight)
                        else:
                            indices_validos.append(pin_candidato)
                            pesos_validos.append(0.0)

                    if len(indices_validos) == 0:
                        break

                    pesos_validos = np.array(pesos_validos, dtype=float)
                    probs = self._normalizar_prob(pesos_validos)

                    # elegir siguiente pin entre indices_validos
                    siguiente_pin = int(np.random.choice(indices_validos, p=probs))
                    pasos += 1
                    self.Table[j, pasos] = siguiente_pin

                    # aplicar línea realmente al vector local
                    idx_line = self._obtener_indice(pin_actual, siguiente_pin)
                    x_coords = self.linea_cache_x[idx_line]
                    y_coords = self.linea_cache_y[idx_line]

                    indices = (y_coords * self.ancho + x_coords).astype(int)
                    vector_actual[indices] = np.maximum(vector_actual[indices] - self.peso_de_linea, 0.0)
                    # actualizar error actual
                    error_actual = float(self._error_de_secuencia(vector_actual))
                    # avanzar
                    pin_actual = siguiente_pin


            # Evaluación de la población: calcular error por cada fila (recortar -1)
            errores = np.zeros(self.cantidad_poblacion, dtype=float)
            for j in range(self.cantidad_poblacion):
                secuencia_inicial = self.Table[j, :]
                secuencia_limpia = secuencia_inicial[secuencia_inicial >= 0].astype(int).tolist()
                error = float(self.funcion_fitness(secuencia_limpia))
                errores[j] = error

            # guardar mejor de la generación
            inidice_mejor_gen = int(errores.argmin())
            mejor_solucion = self.Table[inidice_mejor_gen, :].copy()
            mejor_error = float(errores[inidice_mejor_gen])
            self.mejores_soluciones.append(mejor_solucion)
            self.mejores_errores.append(mejor_error)

            if self.verbose:
                print(f"[iter {iteration+1}/{self.max_iter}] best_gen_error={mejor_error:.6f}")

            # Actualización de feromonas: delta_tau en función de la calidad (inversa del error)
            delta_tau = np.zeros_like(self.Tau, dtype=float)

            for j in range(self.cantidad_poblacion):
                secuencia_inicial = self.Table[j, :]
                secuencia_limpia = secuencia_inicial[secuencia_inicial >= 0].astype(int).tolist()
                error = errores[j]
                contrib = self.q / (error + eps)
                for k in range(len(secuencia_limpia) - 1):
                    n1 = secuencia_limpia[k]
                    n2 = secuencia_limpia[k + 1]
                    if self._es_arista_valida(n1, n2):
                        delta_tau[n1, n2] += contrib
                        delta_tau[n2, n1] += contrib  # mantener simetría

            # evaporación + depósito
            self.Tau = (1.0 - self.rho) * self.Tau + delta_tau
            # simetria
            self.Tau = (self.Tau + self.Tau.T) / 2.0

        # seleccionar la mejor generación global
        mejor_idx = int(np.argmin(np.array(self.mejores_errores)))
        self.solucion_final = self.mejores_soluciones[mejor_idx].copy()

        # construir el vector de error post-resolutor aplicando la secuencia final
        seq_final = self.solucion_final
        secuencia_limpia = seq_final[seq_final >= 0].astype(int).tolist()
        imagen_error_post_resolutor = self.funcion_error_bruto(secuencia_limpia)
        self.error_final = float(self._error_de_secuencia(imagen_error_post_resolutor))

        return self.solucion_final, imagen_error_post_resolutor, self.error_final

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
                        _error_de_secuencia: Callable[[np.ndarray], np.float64] = mse,
                        cantidad_poblacion: int = 20, 
                        max_iter: int = 100, 
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
    
    
    resolutor = OCH_StringArt(_error_de_secuencia =_error_de_secuencia,
                                numero_de_pines =numero_de_pines,
                                vector_de_la_imagen =vector_de_la_imagen,
                                linea_cache_x = linea_cache_x,
                                linea_cache_y = linea_cache_y,
                                ancho = ancho,
                                peso_de_linea = peso_de_linea, 
                                maximo_lineas = maximo_lineas, 
                                cantidad_poblacion = cantidad_poblacion, 
                                max_iter = max_iter, 
                                alpha=alpha,
                                beta=beta,
                                rho=rho,
                                q=q,
                                distancia_minima=distancia_minima,
                                verbose=verbose
                              )
    
    secuencia_sol,imagen_error_post_resolutor,error_final = resolutor.run()

    imagen_error_post_resolutor 
    if verbose:
        imagen_error_post_resolutor = imagen_error_post_resolutor.reshape(alto, ancho)
        return ReturnResolutor(
            peso_de_linea=peso_de_linea,
            distancia_minima=distancia_minima,
            maximo_lineas=maximo_lineas,
            error_total=error_final,
            secuencia_pines=np.array(secuencia_sol),
            imagen_preprocesada=imagen_preprocesada,
            imagen_error_preresolutor=imagen_error_preresolutor,
            imagen_error_post_resolutor=imagen_error_post_resolutor,
        )
    
    return ReturnResolutor(
        peso_de_linea=peso_de_linea,
        distancia_minima=distancia_minima,
        maximo_lineas=maximo_lineas,
        error_total=error_final,
        secuencia_pines=np.array(secuencia_sol)
    )