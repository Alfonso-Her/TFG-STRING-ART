import json
import numpy as np
import cv2
import webbrowser

from pathlib import Path
from multiprocessing import Pool
from copy import deepcopy
from numpy import ndarray
from datetime import datetime
from typing import Unpack, Callable
from time import time

from preprocesado import ParametrosPreprocesado,ReturnPreprocesado,tuberia_preprocesado
from resolutor import ParametrosResolucion,ReturnResolutor,obtener_camino
from postOpt import ParametrosPostOpt,ReturnPostOpt, no_reoptimizar
from reconstruccion import ParametrosReconstruccion,ReturnReconstruccion,hilar_secuencia_svg
from visor import concatenar_sobre_json,tratar_json, crear_web_con_dir
from calcular_error import mse

from .parametros import EstudioParametros
from .tuberia_resolucion import tuberia_resolucion

parametros_preprocesado = list(ParametrosPreprocesado.__annotations__.keys())
parametros_resolucion = list(ParametrosResolucion.__annotations__.keys())
parametros_postoprimizacion = list(ParametrosPostOpt.__annotations__.keys())
parametros_reconstruccion = list(ParametrosReconstruccion.__annotations__.keys())



parametros_a_guardar_json = ["imagen_original","numero_de_pines","secuencia_pines",
                             "distancia_minima","maximo_lineas","lineas_usadas","peso_de_linea",
                             "error_total","funcio_error","tiempo_ejecucion","ruta_resultado",
                             "verbose","ruta_imagen_preprocesada","ruta_imagen_error_preresolutor",
                             "ruta_imagen_error_post_resolutor", "funciones_usadas"]

Ruta_a_web = Path("visor/web/index.html")

def agregarValor(parametros_fijos,clave,valor):
    if clave in parametros_preprocesado:
        parametros_fijos[0][clave] = valor
    if clave in parametros_resolucion:
        parametros_fijos[1][clave] = valor
    if clave in parametros_postoprimizacion:
        parametros_fijos[2][clave] = valor
    if clave in parametros_reconstruccion:
        parametros_fijos[3][clave] = valor

    return parametros_fijos

def construirParametros(**kwargs):
    """
        Dado kwargs devuelve los parametros organizados por ejecuciones y consistentes entre si
        [({params_preprocesado},{params_resolucion},{params_postopt},{params_reconstruccion}),
        ({params_preprocesado},{params_resolucion},{params_postopt}{params_reconstruccion})...]
    """
    parametros_iterables = []
    parametros_totales = []
    parametros_fijos = ({},{},{},{})

    # Fijamos los parametros que nos pasan y solo tienen un valor
    for k,v in kwargs.items():
        # no tomamos aquellos que con valor iterable:
        if k  in parametros_preprocesado + parametros_resolucion\
              + parametros_postoprimizacion + parametros_reconstruccion  :
            if isinstance(v,list):
                parametros_iterables.append(k)
            else: 
                try:
                    parametros_fijos = agregarValor(parametros_fijos,k,v)
                except:
                    raise((f"error en el parametro: {k} con valor {v}"))
    parametros_totales.append(parametros_fijos)

    # ahora copias para iterar sin modificar lo que iteras y repites lo de arriba
    for clave_iter in parametros_iterables :
        parametros_en_construccion=deepcopy(parametros_totales)
        nuevo_total = []
        for parametros in parametros_en_construccion:
            for valor in kwargs[clave_iter]:
                copia_parametro = copia_parametro = (
                                        dict(parametros[0]),
                                        dict(parametros[1]),
                                        dict(parametros[2]),
                                        dict(parametros[3])
                                    )
                agregarValor(copia_parametro, clave_iter, valor)
                nuevo_total.append(copia_parametro)
        parametros_totales = nuevo_total

    return parametros_totales

def estudioParametrico(output_dir:Path, estudio_web:bool= True,
                       continuacion_estudio:bool = False,
                       numero_procesos:int=4,
                       funcion_preprocesado:Callable[[ParametrosPreprocesado], ReturnPreprocesado] = tuberia_preprocesado,
                       funcion_resolucion:Callable[[ParametrosResolucion, ReturnPreprocesado], ReturnResolutor] = obtener_camino,
                       funcion_postOpt: Callable[[ParametrosPostOpt, ReturnResolutor], ReturnPostOpt] = no_reoptimizar,
                       funcion_reconstruccion: Callable[[ParametrosReconstruccion, ReturnPreprocesado, ReturnResolutor], ReturnReconstruccion] = hilar_secuencia_svg,
                       funcion_calculo_error: Callable[[np.ndarray],np.float64] = mse,
                       **kwargs:Unpack[EstudioParametros]):
    """
        Esta funcion toma la imagen y los parametros dados en kwargs y va a construir todas las imagenes con esos parametros
        en caso de estudio_web arma un directorio con un index.html, un json, y todas las fotos, abriendo el index.html se veran
        todas las fotos con sus datos de creacion (extraidos del json).

        Formato para las kwargs:
            Esperamos parametros de las funciones en dos formatos:
                - un unico parametro (ej. numero_de_pines=356)
                - un iterable (ej. numero_de_pines=[256,100,712])
        La logica para iterar separa entre parametros de preprocesado, resolucion, reconstruccion por lo que no va a ser un proceso rapido,
        Para gestionar esto modifica las listas de strings del inicio de estudioParametrico (le vendria bien paralelizar pero TODO) 
    """
    if "ruta_a_la_imagen" not in kwargs:
        raise ValueError("Introduzca el parametro con la ruta de la imagen (ruta_a_la_imagen)")
    
    hora_proceso = "_"+datetime.now().strftime("%d%m%Y_%H%M%S")

    # Generamos la carpeta 
    if output_dir.exists() and not continuacion_estudio:
        output_dir = Path(str(output_dir)+hora_proceso)

    output_dir.mkdir( parents= True, exist_ok= True)
    ruta_json = output_dir.joinpath("datos.json")
    metadatos = []

    if continuacion_estudio:
        if ruta_json.exists():
            with open(ruta_json, "r") as f:
                metadatos = json.load(f)
 
    kwargs.update({"funcion_calculo_error":funcion_calculo_error,
                    "funcion_preprocesado": funcion_preprocesado,
                    "funcion_resolucion":funcion_resolucion,
                    "funcion_postOpt":funcion_postOpt,
                    "funcion_reconstruccion":funcion_reconstruccion
                   })
    # Conseguimos los parametros ya empaquetados para cada parte del problema
    lista_con_todos_los_parametros = construirParametros(**kwargs)

    with Pool(processes=numero_procesos) as pool:
        datos_ejecuciones = pool.starmap(func=tuberia_resolucion,
                                         iterable=[(paquete_argumentos,output_dir)
                                                    for paquete_argumentos in lista_con_todos_los_parametros])
    
    metadatos = [tratar_json(datos_totales) for datos_totales in datos_ejecuciones]

    if estudio_web:
        crear_web_con_dir(output_dir=output_dir, ruta_a_web=Ruta_a_web)
    
    concatenar_sobre_json(ruta=ruta_json, metadatos=metadatos)

## TESTING

if __name__ == "__main__":

    estudioParametrico(output_dir=Path("../ejemplos/local/prueba"), estudio_web= True, continuacion_estudio=False,
                       ruta_a_la_imagen="../ejemplos/ae300.jpg", numero_de_pines= [2**a for a in range(7,12)],
                       peso_de_linea= [15,25,50], ancho_clavos = 2, color_de_hilo = "#000000", color_de_fondo = "#ffffff")