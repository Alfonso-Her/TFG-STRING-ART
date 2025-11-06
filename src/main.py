from pathlib import Path
import numpy as np
from typing import Unpack,Callable
from pathlib import Path
import time

from preprocesado import ParametrosPreprocesado,ReturnPreprocesado,\
                    tuberia_preprocesado, tuberia_preprocesado_bresenham

from resolutor import ParametrosResolucion,ReturnResolutor,\
                        obtener_camino, obtener_camino_con_error_total,\
                        obtener_camino_ag, obtener_camino_ag_con_semilla,\
                        obtener_camino_ag_cultivado#obtener_camino_aco
from postOpt import ParametrosPostOpt,ReturnPostOpt,\
                    no_reoptimizar, cambio_pin_medio

from solvers import  EstudioParametrosInput,estudioParametrico, estudioParametricoNoParalelo
from calcular_error import mse, mae, rmse, ssim
from visor import revisar_estudio

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
                              **kwargs:Unpack[EstudioParametrosInput]):
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
                              **kwargs:Unpack[EstudioParametrosInput]):
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
    nombreEstudio = "GA_con_obtener_camino_GEX_P100"
    ruta_salida = f"../ejemplos/local/{nombreEstudio}"
    todas_las_imagenes = ["../ejemplos/ae300.jpg","../ejemplos/acue.jpg","../ejemplos/cervantesColor.jpg"]
    todas_las_funciones_error = [mse, mae, rmse,ssim]
    todas_las_funciones_preprocesado = [tuberia_preprocesado, tuberia_preprocesado_bresenham]
    todas_las_funciones_resolutoras = [obtener_camino, obtener_camino_con_error_total, obtener_camino_ag_con_semilla, obtener_camino_ag]#, obtener_camino_aco]
    todas_las_funciones_postOpt = [no_reoptimizar,cambio_pin_medio]

    # estudioParametrico(output_dir=Path(ruta_salida),estudio_web= True, continuacion_estudio= False,
    #                     ruta_salida=ruta_salida, funcion_calculo_error=mse,
    #                     funcion_preprocesado=tuberia_preprocesado_bresenham,
    #                     funcion_resolucion=obtener_camino_cambio_pin_medio,
    #                     ruta_a_la_imagen=todas_las_imagenes, numero_de_pines=256,
    #                     itereaciones_re_optimizado= 256,
    #                     peso_de_linea=[2,32,128], verbose= True)
    # ini1=time.time()
    # estudioParametricoNoParalelo(output_dir=Path(ruta_salida),estudio_web= True, continuacion_estudio= False,
    #                     ruta_salida=ruta_salida, ruta_a_la_imagen=todas_las_imagenes[0],
    #                     numero_de_pines=[256], peso_de_linea= 20,
    #                     verbose=True)
    #
    # fin1=time.time()
    # revisar_estudio(output_dir=Path("../ejemplos/local/Version que no respeta AG con 500 poblaciones resto default Version que no respeta HoF/"))
    # revisar_estudio(output_dir=Path("../ejemplos/local/GA_G750_P400_PC80_PM_20_HF5_T7_03112025_214306/"))
    # revisar_estudio(output_dir=Path("../ejemplos/local/EjecucionMuchosParametrosIntro/"))

    # estudioParametricoNoParalelo(output_dir=Path(ruta_salida),estudio_web= True, continuacion_estudio= False,
    #                     ruta_salida=ruta_salida, funcion_calculo_error=ssim,
    #                     funcion_preprocesado=todas_las_funciones_preprocesado,
    #                     funcion_resolucion=[obtener_camino],
    #                     funcion_postOpt=no_reoptimizar,
    #                     ruta_a_la_imagen=todas_las_imagenes, numero_de_pines=256,
    #                     itereaciones_re_optimizado= 0, decremento_error_minimo=0.000001,
    #                     peso_de_linea=[20], verbose= True)

    # estudioParametricoNoParalelo(output_dir=Path(ruta_salida),estudio_web= True, continuacion_estudio= True,
    #                              ruta_salida=ruta_salida, puerto=8030,
    #                              funcion_calculo_error=[mse],
    #                              reanudar=True,
    #                             #  marcar_bordes=[True,False],
    #                              funcion_preprocesado= tuberia_preprocesado_bresenham,
    #                              funcion_resolucion=[obtener_camino_ag_cultivado],
    #                              numero_generaciones=10,
    #                              cantidad_poblacion=5402, 
    #                             #  probabilidad_cruce=0.8,
    #                             #  probabilidad_mutacion=0.15,
    #                             #  elitismo_size = 5,
    #                             #  cantidad_torneo= 7,
    #                              funcion_postOpt=no_reoptimizar,
    #                              ruta_a_la_imagen=todas_las_imagenes[0],
    #                              numero_de_pines=256,
    #                              maximo_lineas=4000,
    #                              peso_de_linea=20,
    #                              verbose= True)
    
    # estudioParametricoNoParalelo(output_dir=Path(ruta_salida),estudio_web= True, continuacion_estudio= False,
    #                              ruta_a_la_imagen=todas_las_imagenes[1], funcion_preprocesado=tuberia_preprocesado_bresenham,
    #                              verbose= True)

    # estudioParametricoNoParalelo(output_dir=Path(ruta_salida),estudio_web= True, continuacion_estudio= True,
    #                              ruta_salida=ruta_salida, puerto=8020,
    #                              funcion_preprocesado= tuberia_preprocesado_bresenham,
    #                              funcion_resolucion=obtener_camino_aco,
    #                              numero_de_hormigas = 5,
    #                              alpha=1.0,
    #                              beta=3.0,
    #                              rho=0.2,
    #                              q=1.0,
    #                              iteraciones_aco=10,
    #                              funcion_postOpt=no_reoptimizar,
    #                              ruta_a_la_imagen=todas_las_imagenes,
    #                              numero_de_pines=256,
    #                              maximo_lineas=500,
    #                              peso_de_linea=20,
    #                              verbose= True)
    # estudioParametrico(output_dir=Path(ruta_salida),estudio_web= True, continuacion_estudio= False,
    #                     funcion_calculo_error=mse, puerto=8121, numero_procesos=4,
    #                     funcion_preprocesado=tuberia_preprocesado_bresenham,
    #                     funcion_resolucion=obtener_camino,
    #                     ruta_a_la_imagen=todas_las_imagenes,
    #                     numero_de_pines=[128*k for k in range(1,3)],
    #                     distancia_minima=[2*k for k in range(1,4)],
    #                     numero_de_pines_recientes_a_evitar=[2*k for k in range(1,4)],
    #                     maximo_lineas=[1000*k for k in range(1,5)],
    #                     peso_de_linea=[10*k for k in range(1,9)],
    #                     verbose= True)