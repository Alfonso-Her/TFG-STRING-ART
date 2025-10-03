import json
from pathlib import Path
import numpy as np
from numpy import ndarray
from datetime import datetime
from time import time
import cv2
from copy import deepcopy
from resolutorBase import tuberia_preprocesado, obtener_camino, draw_string_art_svg

parametros_preprocesado = ["ruta_a_la_imagen","numero_de_pines","distancia_minima"]
parametros_resolucion = ["numero_de_pines","distancia_minima","maximo_lineas","peso_de_linea"]
parametros_reconstruccion = ["tamano_lado_px","ancho_clavos","ancho_de_hilo","ratio_distancia","color_de_hilo","color_de_fondo","color_de_clavo"]
parametros_a_guardar_json = ["imagen_original","numero_de_pines","secuencia_pines","distancia_minima","maximo_lineas","peso_de_linea","error_total","tiempo_ejecucion","ruta_resultado"]
Ruta_a_web = Path("index.html")

def agregarValor(parametros_fijos,clave,valor):
    if clave in parametros_preprocesado:
        parametros_fijos[0][clave] = valor
    if clave in parametros_resolucion:
        parametros_fijos[1][clave] = valor
    if clave in parametros_reconstruccion:
        parametros_fijos[2][clave] = valor
    return parametros_fijos
def construirParametros(**kwargs):
    """
        Dado kwargs devuelve los parametros organizados por ejecuciones y consistentes entre si
        [({params_preprocesado},{params_resolucion},{params_reconstruccion}),({params_preprocesado},{params_resolucion},{params_reconstruccion})...]
    """
    parametros_iterables = []
    parametros_totales = []
    parametros_fijos = ({},{},{})

    # Fijamos los parametros que nos pasan y solo tienen un valor
    for k,v in kwargs.items():
        # no tomamos aquellos que con valor iterable:
        if k in parametros_preprocesado or k in parametros_reconstruccion or k in parametros_resolucion:
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
                copia_parametro = deepcopy(parametros)
                agregarValor(copia_parametro, clave_iter, valor)
                nuevo_total.append(copia_parametro)
        parametros_totales = nuevo_total

    return parametros_totales

def validacionesSaltoCaso(paquete_de_parametros):
    """
        Devuelve true si detecta que los parametros pasados contienen casos
        que no debemos estudiar
    """
    for parametros in paquete_de_parametros:
        
        if "color_de_hilo" in parametros:
            if "color_de_fondo" in parametros:
                if parametros["color_de_hilo"] == parametros["color_de_fondo"]:
                    return "has introducido el mismo color de fondo que de hilo saltamos"
    return ""

def concatenar_sobre_json(ruta: Path, metadatos:dict):
    def convert(o):
        if isinstance(o, np.integer):
            return int(o)
        if isinstance(o, np.floating):
            return float(o)
        if isinstance(o, np.ndarray):
            return o.tolist()
        
    if ruta.exists():
        with ruta.open("r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = []
    
    data.append(metadatos)

    with ruta.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4,default=convert)

def estudioParametrico(output_dir:Path, estudio_web:bool,continuacion_estudio:bool, **kwargs):
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
    
    # Conseguimos los parametros ya empaquetados para cada parte del problema
    lista_con_todos_los_parametros = construirParametros(**kwargs)

    for paquete_argumentos in lista_con_todos_los_parametros:
        inicio = time()
        metadatos_ejecucion= {}
        hora_proceso = "_"+datetime.now().strftime("%d%m%Y_%H%M%S_%f")
        print("\n Estamos procesando los argumentos:",
              f"\n    para el preprocesado:{paquete_argumentos[0]}",
              f"\n    para el preprocesado:{paquete_argumentos[1]}",
              f"\n    para el preprocesado:{paquete_argumentos[2]}")
        
        
        info_si_saltamos = validacionesSaltoCaso(paquete_argumentos)
        if info_si_saltamos != "":
                print(f"\n {info_si_saltamos}")
                continue
        try:
            nombre_foto_con_ext = paquete_argumentos[0]["ruta_a_la_imagen"].split("/")[-1].split(".")
            datos_preprocesados = tuberia_preprocesado(**paquete_argumentos[0])
            print("\n Pasamos con exito el preprocesado")
        except Exception as e:
            print(f"\n Error {e} al hacer el preprocesado continuando con el siguiente")
            continue
        try:
            paquete_argumentos[1].update({k:v for k,v in datos_preprocesados.items() if k != "posiciones_pines"})
            datos_solucion_problema = obtener_camino(**paquete_argumentos[1])
            ruta_fichero = output_dir.joinpath(Path(nombre_foto_con_ext[0]+hora_proceso+"_procesado.svg"))
            datos_solucion_problema.update({"ruta_a_resultado": ruta_fichero })
            print("\n Pasamos con exito el proceso de resolucion")
        except Exception as e:
            print(f"\n Error {e} al solucionar, continuando con el siguiente")
            continue
        try:
            paquete_argumentos[2].update(datos_solucion_problema)
            paquete_argumentos[2].update({"posiciones_pines": datos_preprocesados["posiciones_pines"]})

            datos_sol_final = draw_string_art_svg(**paquete_argumentos[2])
            print(f"\n imagen guardada con exito en {datos_sol_final["ruta_resultado"]} !!!")
        except Exception as e:
            print(f"\n Error {e} al pintar la solucion, continuando con el siguiente")
            continue


        #Agregramos la imagen original si no existe en la carpeta
        ruta_imagen_original_en_destino = str(output_dir)+"\\"+".".join(nombre_foto_con_ext)
        if not Path(ruta_imagen_original_en_destino).exists():
            img_padre = cv2.imread(datos_preprocesados["ruta_a_la_imagen"])
            cv2.imwrite(ruta_imagen_original_en_destino,img_padre)
        fin = time()

        metadatos_ejecucion["imagen_original"] = ".".join(nombre_foto_con_ext)
        metadatos_ejecucion["numero_de_pines"] = datos_preprocesados["numero_de_pines"]
        metadatos_ejecucion["secuencia_pines"] = datos_solucion_problema["secuencia_pines"].tolist()
        metadatos_ejecucion["distancia_minima"] = datos_solucion_problema["distancia_minima"]
        metadatos_ejecucion["maximo_lineas"] = datos_solucion_problema["maximo_lineas"]
        metadatos_ejecucion["peso_de_linea"] = datos_solucion_problema["peso_de_linea"]
        metadatos_ejecucion["error_total"] = float(np.sum(datos_solucion_problema["error_total"]))
        metadatos_ejecucion["tiempo_ejecucion"] = fin - inicio
        metadatos_ejecucion["ruta_resultado"] = str(datos_sol_final["ruta_resultado"]).split("\\")[-1]
        
        concatenar_sobre_json(ruta_json,metadatos_ejecucion)
        metadatos.append(metadatos_ejecucion)

    if estudio_web:
        ruta_web = output_dir.joinpath("index.html")
        with open("index.html","r", encoding="utf-8") as web_origen:
            contenido = web_origen.read()
            contenido = contenido.replace("const data = ['cenicero'];",f"const data = {metadatos} ;")
        with open(ruta_web, "w", encoding="utf-8") as web_destino:
            web_destino.write(contenido)
    


## TESTING

if __name__ == "__main__":

    estudioParametrico(output_dir=Path("../ejemplos/local/prueba"), estudio_web= True, continuacion_estudio=False,
                       ruta_a_la_imagen="../ejemplos/ae300.jpg", numero_de_pines= [2**a for a in range(7,12)],
                       peso_de_linea= [15,25,50], ancho_clavos = 2, color_de_hilo = "#000000", color_de_fondo = "#ffffff")