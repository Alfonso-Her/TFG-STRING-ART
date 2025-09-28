from pathlib import Path
import time
import numpy as np
from .preprocesado import tuberia_preprocesado
from .resolutor import obtener_camino
from .reconstruccion import draw_string_art_svg

def string_art(ruta_imagen:str,ruta_salida:str,
               numero_de_pines:int = 256, distancia_minima:int = 20,
               peso_de_linea:int=1, maximo_lineas:int = 4000,
               px_imagen_resultado:int=5000, ancho_clavos:int=6,
               ancho_linea:int = 1, color_clavos:str = "#5c4c07",
               color_bg:str ="#c2c2c2" , color_hilo:str = "#000000")->None:
    
    print("Comenzando el preprocesado de la imagen")
    diccionario_preprocesado= tuberia_preprocesado(Path(ruta_imagen),numero_de_pines,distancia_minima)

    print("Resolviendo el problema")
    secuencia_pines = obtener_camino(numero_de_pines ,maximo_lineas,
                   distancia_minima,**diccionario_preprocesado,peso_de_linea= peso_de_linea)
    
    print(f"Creando y guardando la imagen {ruta_salida}")
    draw_string_art_svg(diccionario_preprocesado["posiciones_pines"], secuencia_pines["secuencia_pines"], ruta_a_resultado=ruta_salida,
                        tamano_lado_px=px_imagen_resultado,
                        ancho_clavos=ancho_clavos,
                        ancho_de_hilo=ancho_linea,
                        color_de_clavo=color_clavos,
                        color_de_hilo=color_hilo,
                        ratio_distancia=0.5,
                        color_de_fondo=color_bg)
    

if __name__ == "__main__":
    ruta_carpeta="../../ejemplos/"
    st = time.time()
    string_art(ruta_imagen = ruta_carpeta+"ae300.jpg",ruta_salida=ruta_carpeta+"local/solI4000.svg", 
               numero_de_pines=256,distancia_minima=2,maximo_lineas=4000,ancho_linea=1,
               px_imagen_resultado=3000, peso_de_linea = 20, color_bg="#000000", color_hilo= "#FFFFFF")
    en = time.time()
    print(f"He tardado: {en-st}")       
