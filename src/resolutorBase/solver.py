from pathlib import Path
import time
import numpy as np
from preprocesado import tuberia_preprocesado
from resolutor import obtener_camino
from reconstruccion import draw_string_art_svg

def string_art(ruta_imagen:str,ruta_salida:str,
               numero_de_pines:int = 256, distancia_minima:int = 20,
               peso_de_linea:int=1, maximo_lineas:int = 4000,
               px_imagen_resultado:int=5000, nail_r:int=6,
               ancho_linea:int = 1, color_clavos:str = "#5c4c07",
               color_bg:str ="#c2c2c2" , color_hilo:str = "#000000")->None:
    
    print("Comenzando el preprocesado de la imagen")
    ancho,vector_de_la_imagen,posiciones_pines,cache_linea = tuberia_preprocesado(Path(ruta_imagen),numero_de_pines,distancia_minima)

    print("Resolviendo el problema")
    secuencia_pines = obtener_camino(numero_de_pines ,maximo_lineas,
                   distancia_minima, linea_cache_x = cache_linea[0],
                   linea_cache_y = cache_linea[1], ancho=ancho ,
                   vector_de_la_imagen= vector_de_la_imagen, peso_de_linea= peso_de_linea)
    
    print(f"Creando y guardando la imagen {ruta_salida}")
    draw_string_art_svg(posiciones_pines, secuencia_pines, filename=ruta_salida,
                        size_px=px_imagen_resultado,
                        nail_r=nail_r,
                        thread_width=ancho_linea,
                        nail_color=color_clavos,
                        thread_color=color_hilo,
                        padding_ratio=0.5,
                        background_color=color_bg)
    

if __name__ == "__main__":
    ruta_carpeta="../../ejemplos/"
    st = time.time()
    string_art(ruta_imagen = ruta_carpeta+"ae300.jpg",ruta_salida=ruta_carpeta+"local/solI4000.svg", 
               numero_de_pines=256,distancia_minima=2,maximo_lineas=4000,ancho_linea=1,
               px_imagen_resultado=3000, peso_de_linea = 20, color_bg="#000000", color_hilo= "#FFFFFF")
    en = time.time()
    print(f"He tardado: {en-st}")       
