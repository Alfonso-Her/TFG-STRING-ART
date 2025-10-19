from pathlib import Path
import numpy as np
from typing import Unpack,Callable
from pathlib import Path
import time
from preprocesado import ParametrosPreprocesado,ReturnPreprocesado,\
                    tuberia_preprocesado, tuberia_preprocesado_bresenham
from resolutor import ParametrosResolucion,ReturnResolutor,\
                        obtener_camino, obtener_camino_cambio_pin_medio, obtener_camino_con_error_total
from postOpt import ParametrosPostOpt,ReturnPostOpt,\
                    no_reoptimizar
from solvers import  EstudioParametros,estudioParametrico, estudioParametricoNoParalelo
from calcular_error import mse, mad, mae, suma_abs, suma_cuad, psnr, nrmse


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
                              continuacion_estudio:bool = False,
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
    estudioParametrico(output_dir=Path(ruta_salida),estudio_web= True, continuacion_estudio= continuacion_estudio, **parametros_basicos)
    estudioParametrico(output_dir=Path(ruta_salida),estudio_web= True, continuacion_estudio= True,
                        funcion_resolucion=funcion_resolucion, **parametros_basicos)

def probar_funciones_resolutoras_lista_de_errores(ruta_salida:str, lista_funciones_error:list[Callable[[np.ndarray],np.float64]],
                              lista_funciones_resolutor: list[Callable[[ParametrosResolucion, ReturnPreprocesado], ReturnResolutor]],
                              continuacion_estudio:bool = False,
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

    for funcion_resolutora in lista_funciones_resolutor:
        estudioParametrico(output_dir=Path(ruta_salida),estudio_web= True, funcion_calculo_error= lista_funciones_error[0],
                            continuacion_estudio= continuacion_estudio,  funcion_resolucion= funcion_resolutora,
                            **parametros_basicos)
        
        continuacion_estudio = True # apaño feo 
        for i in range(1,len(lista_funciones_error)-1):
            estudioParametrico(output_dir=Path(ruta_salida),estudio_web= True, funcion_calculo_error= lista_funciones_error[i],
                            continuacion_estudio= True,  funcion_resolucion= funcion_resolutora, **parametros_basicos)
        
if __name__ == "__main__":

    np.set_printoptions(threshold=2)
    nombreEstudio = "p"
    ruta_salida = f"../ejemplos/local/{nombreEstudio}"
    todas_las_imagenes = ["../ejemplos/ae300.jpg","../ejemplos/acue.jpg","../ejemplos/cervantesColor.jpg"]
    todas_las_funciones_error = [mse, mad, mae, suma_abs, suma_cuad, psnr, nrmse]
    todas_las_funciones_preprocesado = [tuberia_preprocesado, tuberia_preprocesado_bresenham]
    todas_las_funciones_resolutoras = [obtener_camino, obtener_camino_cambio_pin_medio, obtener_camino_con_error_total]
    todas_las_funciones_postOpt = [no_reoptimizar]

    # estudioParametrico(output_dir=Path(ruta_salida),estudio_web= True, continuacion_estudio= False,
    #                     ruta_salida=ruta_salida, funcion_calculo_error=mse,
    #                     funcion_preprocesado=tuberia_preprocesado_bresenham,
    #                     funcion_resolucion=obtener_camino_cambio_pin_medio,
    #                     ruta_a_la_imagen=todas_las_imagenes, numero_de_pines=256,
    #                     itereaciones_re_optimizado= 256,
    #                     peso_de_linea=[2,32,128], verbose= True)
    ini1=time.time()
    estudioParametricoNoParalelo(output_dir=Path(ruta_salida),estudio_web= True, continuacion_estudio= False,
                        ruta_salida=ruta_salida, ruta_a_la_imagen=todas_las_imagenes,
                        numero_de_pines=[256], peso_de_linea= 20,
                        verbose=True)
    fin1=time.time()
