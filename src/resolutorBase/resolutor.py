import numpy as np

def get_line_err(err: np.ndarray, coords1: np.ndarray, coords2: np.ndarray, ancho: np.float64) ->  np.float64:
    indices = (coords1 * ancho + coords2).astype(int)
    return np.sum(err[indices])

def obtener_camino(linea_cache_x:np.ndarray,linea_cache_y:np.ndarray,
                   ancho:int,vector_de_la_imagen:np.ndarray,
                   numero_de_pines:int = 256 ,maximo_lineas:int= 4000,
                   distancia_minima:int = 0,peso_de_linea:int = 20)->np.ndarray:
    
    error_acumulado = np.full(ancho*ancho, 255.0) - vector_de_la_imagen
    secuencia_pines =np.empty(0,dtype=int)
    ultimos_pines = np.empty(0,dtype=int)
    pin_actual = 0
    mejor_pin = -1
    error_en_la_linea = np.float64(0)
    error_maximo = np.float64(0)
    index = 0
    index_interno = 0

    for i in range(maximo_lineas):
        # Restauramos variables para cada linea a pintar
        mejor_pin = -1
        error_en_la_linea = np.float64(0)
        error_maximo = np.float64(0)

        for desfase_desde_pin in range(distancia_minima,numero_de_pines-distancia_minima):
            pin_a_probar = (pin_actual + desfase_desde_pin) % numero_de_pines
            if pin_a_probar in ultimos_pines:
                continue
            else:
                index_interno = pin_a_probar*numero_de_pines + pin_actual
                error_en_la_linea = get_line_err(error_acumulado, linea_cache_y[index_interno],linea_cache_x[index_interno], ancho)
                if (error_en_la_linea > error_maximo):
                    error_maximo = error_en_la_linea
                    mejor_pin = pin_a_probar
                    index = index_interno
        
        secuencia_pines = np.append(secuencia_pines,mejor_pin)
        coords1 = linea_cache_y[index]
        coords2 = linea_cache_x[index]

        for i in range(coords1.shape[0]):
            v = int(coords1[i] * ancho +coords2[i])
            error_acumulado[v] -= peso_de_linea 

        ultimos_pines= np.append(ultimos_pines, mejor_pin)
        ultimos_pines = ultimos_pines[1:]
        pin_actual = mejor_pin
    return {"secuencia_pines":secuencia_pines}