from pathlib import Path
from numpy import ndarray
from datetime import datetime
from copy import deepcopy
from resolutorBase import tuberia_preprocesado, obtener_camino, draw_string_art_svg

parametros_preprocesado = ["ruta_a_la_imagen","numero_de_pines","distancia_minima"]
parametros_resolucion = ["numero_de_pines","distnacia_minima","maximo_lineas","peso_de_linea"]
parametros_reconstruccion = ["tamanno_lado_px","ancho_clavos","ancho_de_hilo","ratio_distancia","color_de_hilo","color_de_fondo"]
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
    # Necesitamos una primera lista de parametros
    if parametros_iterables:
        clave_con_iterable = parametros_iterables.pop()
        for valor in kwargs[clave_con_iterable]:
            parametros_agrupados = deepcopy(parametros_fijos)
            agregarValor(parametros_agrupados,clave_con_iterable,valor)
            parametros_totales.append(parametros_agrupados)
    
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
    # Generamos la carpeta 
    if output_dir.exists() and not continuacion_estudio:
        output_dir = Path(str(output_dir)+"_"+datetime.now().strftime("%d%m%Y_%H%M"))

    output_dir.mkdir( exist_ok= True)
    # Conseguimos los parametros ya empaquetados para cada parte del problema
    lista_con_todos_los_parametros = construirParametros(**kwargs)

    for paquete_argumentos in lista_con_todos_los_parametros:
        try:
            datos_preprocesados = tuberia_preprocesado(**paquete_argumentos[0])
        except Exception as e:
            print(f"Error {e} al hacer el preprocesado con parametros: {paquete_argumentos[0]}")
        try:
            datos_solucion_problema = obtener_camino(**(paquete_argumentos[1].update(datos_preprocesados)))
        except Exception as e:
            print(f"Error {e} al solucionar con parametros: {paquete_argumentos[1]}")
        try:
            sol_final = obtener_camino(**(paquete_argumentos[2].update(datos_solucion_problema)))
        except Exception as e:
            print(f"Error {e} al pintar la solucion con parametros: {paquete_argumentos[1]}")

## TESTING

if __name__ == "__main__":
    print(construirParametros(ruta_a_la_imagen= "HOLA", numero_de_pines= 25, peso_de_linea= [2,20], ancho_clavos = list(range(2))))
    estudioParametrico(output_dir=Path("../ejemplos/local/prueba"), estudio_web= False,ruta_a_la_imagen= "HOLA",
                        numero_de_pines= 25, peso_de_linea= [2,20], ancho_clavos = list(range(2)))