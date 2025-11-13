import numpy as np
from typing import Unpack, Callable, List, Optional,Tuple
from random import randint

from ..parametros import ReturnResolutor, ParametrosResolucion
from ..utils import get_line_err, agregar_lineas_al_error

# from.solverModificado import StringArtSolver
from calcular_error import mse

from ..utils import secuencia_pines_a_error

class OCH_StringArt_Error_aprox:
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
            max_iter: int = 50,
            alpha: float = 1.0, # Peso de la feromona (experiencia)
            beta: float = 3.0,  # Peso de la heurística (visión voraz) -> Auméntalo para String Art
            rho: float = 0.1,   # Evaporación
            q: float = 10.0,    # Cantidad de feromona a depositar
            distancia_minima: int = 0,
            verbose: bool = False
        ):
            self._error_de_secuencia = _error_de_secuencia
            self.numero_de_pines = numero_de_pines
            # Trabajamos con float para precisión en cálculos de error
            self.vector_de_la_imagen = vector_de_la_imagen.astype(np.float64)
            self.linea_cache_x = linea_cache_x
            self.linea_cache_y = linea_cache_y
            self.ancho = ancho
            self.peso_de_linea = float(peso_de_linea)
            
            self.maximo_lineas = int(maximo_lineas)
            self.cantidad_poblacion = int(cantidad_poblacion)
            self.max_iter = int(max_iter)
            
            self.alpha = float(alpha)
            self.beta = float(beta)
            self.rho = float(rho)
            self.q = float(q)
            self.distancia_minima = int(distancia_minima)
            self.verbose = verbose

            # Matriz de feromonas: Arista [i][j]
            self.Tau = np.ones((self.numero_de_pines, self.numero_de_pines), dtype=np.float64)
            
            # Historial
            self.mejores_errores: List[float] = []
            self.solucion_global_mejor = None
            self.error_global_mejor = float('inf')

    def _obtener_indice(self, pin_a: int, pin_b: int) -> int:
        return pin_b * self.numero_de_pines + pin_a

    def _es_arista_valida(self, a: int, b: int) -> bool:
        # Distancia circular mínima
        dist = min(abs(a - b), self.numero_de_pines - abs(a - b))
        if a == b or dist < self.distancia_minima:
            return False
        
        idx = self._obtener_indice(a, b)
        # Verificar cache
        if idx < 0 or idx >= len(self.linea_cache_x):
            return False
        if self.linea_cache_x[idx] is None:
            return False
        return True

    def run(self) -> Tuple[np.ndarray, np.ndarray, float]:
        
        for iteration in range(self.max_iter):
            
            soluciones_hormigas = []
            errores_hormigas = []

            # --- CONSTRUCCIÓN DE SOLUCIONES (Hormigas) ---
            for k in range(self.cantidad_poblacion):
                
        
                imagen_actual_hormiga = self.vector_de_la_imagen.copy()
                camino = []
                
                # Pin inicial aleatorio
                pin_actual = randint(0, self.numero_de_pines - 1)
                camino.append(pin_actual)

                # Construir camino paso a paso
                for _ in range(self.maximo_lineas):
                    # Calcular probabilidades para el siguiente paso
                    probs = np.zeros(self.numero_de_pines)
                    candidatos_validos = []
                    
                    for pin_siguiente in range(self.numero_de_pines):
                        if not self._es_arista_valida(pin_actual, pin_siguiente):
                            continue
                        
                        idx_linea = self._obtener_indice(pin_actual, pin_siguiente)
                        coords_x = self.linea_cache_x[idx_linea]
                        coords_y = self.linea_cache_y[idx_linea]
                        
                        intensidad_linea = get_line_err(imagen_actual_hormiga, coords_y, coords_x, self.ancho)
                        # no queremos quemar la imagen con lineas extras
                        if intensidad_linea <= 0:
                            continue

                        eta = max(intensidad_linea, 1e-6) 
                        
                        tau = self.Tau[pin_actual, pin_siguiente]
                        
                        # Formula ACO
                        p = (tau ** self.alpha) * (eta ** self.beta)
                        probs[pin_siguiente] = p
                        candidatos_validos.append(pin_siguiente)
                    

                    suma_probs = np.sum(probs)
                    if suma_probs == 0 or len(candidatos_validos) == 0:
                        break 
                    
                    probs = probs / suma_probs
                    
                    # Elegir siguiente pin
                    siguiente_pin = np.random.choice(range(self.numero_de_pines), p=probs)
                    
                    # ACTUALIZAr ESTADO DE LA HORMIGA
                    idx_linea_elegida = self._obtener_indice(pin_actual, siguiente_pin)
                    cx = self.linea_cache_x[idx_linea_elegida]
                    cy = self.linea_cache_y[idx_linea_elegida]
                    
                    # Actualización vectorizada (rápida)
                    indices_pixel = (cy * self.ancho + cx).astype(np.int64)
                    # Restamos peso (simulando hilo negro sobre fondo blanco -> invertido: restamos error)
                    imagen_actual_hormiga[indices_pixel] = imagen_actual_hormiga[indices_pixel] - self.peso_de_linea
                    
                    camino.append(siguiente_pin)
                    pin_actual = siguiente_pin

                # Fin de la hormiga k
                soluciones_hormigas.append(np.array(camino))
                
                # Calculamos el error final real de esta hormiga
                error_final_hormiga = self._error_de_secuencia(imagen_actual_hormiga)
                errores_hormigas.append(error_final_hormiga)
                
                if self.verbose:
                    print(f"  > Hormiga {k}: Error {error_final_hormiga:.2f}, Líneas {len(camino)}")

            # --- ACTUALIZACIÓN DE FEROMONAS (Global) ---
            
            # 1. Evaporación
            self.Tau *= (1.0 - self.rho)
            
            # 2. Depósito Elitista (Solo la mejor hormiga de esta iteración deposita)
            mejor_idx_iter = np.argmin(errores_hormigas)
            mejor_error_iter = errores_hormigas[mejor_idx_iter]
            mejor_camino_iter = soluciones_hormigas[mejor_idx_iter]
            
            # Guardamos el mejor global
            if mejor_error_iter < self.error_global_mejor:
                self.error_global_mejor = mejor_error_iter
                self.solucion_global_mejor = mejor_camino_iter
                if self.verbose:
                    print(f"*** Nuevo mejor global: {self.error_global_mejor:.4f} ***")

            # Depósito: La cantidad depende de la calidad fija
            deposito = self.q 
            
            for i in range(len(mejor_camino_iter) - 1):
                u, v = mejor_camino_iter[i], mejor_camino_iter[i+1]
                # Matriz simétrica
                self.Tau[u, v] += deposito
                self.Tau[v, u] += deposito
            
            if self.verbose:
                print(f"Iteración {iteration}: Mejor error iteración: {mejor_error_iter:.4f}")

        # Reconstruir resultado final
        imagen_final_error = secuencia_pines_a_error(
            secuencia_pines=self.solucion_global_mejor.tolist(),
            error_acumulado=self.vector_de_la_imagen.copy(),
            linea_cache_y=self.linea_cache_y,
            linea_cache_x=self.linea_cache_x,
            ancho=self.ancho,
            numero_de_pines=self.numero_de_pines,
            peso_de_linea=self.peso_de_linea
        )
        
        return self.solucion_global_mejor, imagen_final_error, self.error_global_mejor

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
                        max_iter: int = 50, 
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
    
    
    resolutor = OCH_StringArt_Error_aprox(_error_de_secuencia =_error_de_secuencia,
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