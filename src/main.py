from pathlib import Path
import numpy as np
from typing import Unpack,Callable
from pathlib import Path

from resolutor import obtener_camino, obtener_camino_cambio_pin_medio
from solvers import estudioParametrico
from IOfunct import *

def obtener_imagenes_por_carpeta(ruta_carpeta:str):
    extensiones_validas = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".gif", ".webp"}
    carpeta = Path(ruta_carpeta)

    if not carpeta.exists():
        raise FileNotFoundError(f"La carpeta '{ruta_carpeta}' no existe.")

    if not carpeta.is_dir():
        raise NotADirectoryError(f"'{ruta_carpeta}' no es una carpeta válida.")

    return [
        f.resolve().as_posix()
        for f in carpeta.iterdir()
        if f.suffix.lower() in extensiones_validas and f.is_file()
    ]

def probar_funcion_resolutora(ruta_salida:str,
                              funcion_resolucion: Callable[[ParametrosResolucion, ReturnPreprocesado], ReturnResolutor],
                              **kwargs:Unpack[EstudioParametros]):
    parametros_basicos = {
        "ruta_a_la_imagen": "../ejemplos/ae300.jpg",
        "recortar": True,
        "redimensionar": False,
        "numero_de_pines": 256,
        "peso_de_linea" : 20,
        "color_de_hilo" : "#000000",
        "color_de_fondo" :"#ffffff",
        "verbose": False
    }

    parametros_basicos.update(kwargs)
    estudioParametrico(output_dir=Path(ruta_salida),estudio_web= True, continuacion_estudio= False, **parametros_basicos)
    estudioParametrico(output_dir=Path(ruta_salida),estudio_web= True, continuacion_estudio= True,
                        funcion_resolucion=funcion_resolucion, **parametros_basicos)
if __name__ == "__main__":

    np.set_printoptions(threshold=2)
    nombreEstudio = "arreglandoPinMedio"
    ruta_salida = f"../ejemplos/local/{nombreEstudio}"
    todas_las_imagenes = ["../ejemplos/ae300.jpg","../ejemplos/acue.jpg","../ejemplos/cervantesColor.jpg"]


    # probar_funcion_resolutora(ruta_salida=ruta_salida,
    #                         funcion_resolucion=obtener_camino_cambio_pin_medio,
    #                         # ruta_a_la_imagen=todas_las_imagenes,
    #                         peso_de_linea=15, verbose= True)
    estudioParametrico(output_dir=Path(ruta_salida),estudio_web= True, continuacion_estudio= False,
                        ruta_salida=ruta_salida,
                        # funcion_resolucion=obtener_camino_cambio_pin_medio,
                        ruta_a_la_imagen=todas_las_imagenes[0], numero_de_pines=256,
                        peso_de_linea=20, verbose= True, maximo_lineas=4000)
   
   
