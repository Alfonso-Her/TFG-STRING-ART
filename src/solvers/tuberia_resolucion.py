from pathlib import Path
from time import time
from datetime import datetime
from memory_profiler import profile
import cv2
import gc

from resolutor import ParametrosResolucion
from postOpt import ParametrosPostOpt
from reconstruccion import ParametrosReconstruccion
from .parametros import EstudioParametrosOutput

def limpiar_ruta_para_raiz(ruta:str|Path)->str:
    return str(ruta).split("\\")[-1]

def validacionesSaltoCaso(paquete_de_parametros):
    """
        Devuelve texto si detecta que los parametros pasados contienen casos
        que no debemos estudiar
    """
    for parametros in paquete_de_parametros:
        
        if "color_de_hilo" in parametros:
            if "color_de_fondo" in parametros:
                if parametros["color_de_hilo"] == parametros["color_de_fondo"]:
                    return "has introducido el mismo color de fondo que de hilo saltamos"
        
        if "distancia_minima" in parametros:
            if "numero_de_pines" in parametros:
                if parametros["distancia_minima"] > parametros["numero_de_pines"]/2 :
                    return "Has intoruducido una distancia minima tal, que no sepuede hilar ninguna cuerda"
        if "peso_de_linea" in parametros:
            if parametros["peso_de_linea"] <=0:
                return "Has introducido un peso de linea erroneo"
    return ""

def agregar_datos_bioinspirados(datos_totales,datos_solucion_problema):
    actualizacion = {}
    if "funcion_resolucion" in datos_totales:
        if "AG" in datos_totales["funcion_resolucion"].__name__.upper():
            actualizacion.update({
                "probabilidad_mutacion_gen":datos_solucion_problema["probabilidad_mutacion_gen"],
                "cantidad_torneo":datos_solucion_problema["cantidad_torneo"],
                "probabilidad_cruce":datos_solucion_problema["probabilidad_cruce"],
                "Hall_Fama": datos_solucion_problema["elitismo_size"]
            })
        if "ACO" in datos_totales["funcion_resolucion"].__name__.upper():
            actualizacion.update({
                "alpha":datos_solucion_problema["alpha"],
                "beta":datos_solucion_problema["beta"],
                "rho":datos_solucion_problema["rho"],
                "q": datos_solucion_problema["q"]
            })
    datos_totales.update(actualizacion)

# @profile
def tuberia_resolucion(paquete_argumentos,output_dir,cola_metadatos):
    inicio = time()
    hora_proceso = "_"+datetime.now().strftime("%d%m%Y_%H%M%S_%f")
    args_preprocesado, args_resolucion,\
    args_postOpt,args_reconstruccion = paquete_argumentos
    
    print("\n Estamos procesando los argumentos:",
            f"\n    para el preprocesado:{args_preprocesado}",
            f"\n    para el resolutor:{args_resolucion}",
            f"\n    para el post-optimizador:{args_resolucion}",
            f"\n    para el reconstructor:{args_reconstruccion}")
        
    info_si_saltamos = validacionesSaltoCaso(paquete_argumentos)

    if info_si_saltamos != "":

        print(f"\n {info_si_saltamos}")
        return
    # PREPROCESADO--------------------------------------------------------------------
    try:
        nombre_foto_con_ext = args_preprocesado["ruta_a_la_imagen"].split("/")[-1].split(".")
        nombre_funcion_error = args_preprocesado["funcion_calculo_error"].__name__

        datos_preprocesados = args_preprocesado["funcion_preprocesado"](**args_preprocesado)

        # if "verbose" in args_preprocesado and args_preprocesado["verbose"]:
        #     print(" Del preprocesado obtenemos: ", datos_preprocesados)

        print("\n Pasamos con exito el preprocesado")
    except Exception as e:
        print(f"\n Error {e} al hacer el preprocesado con la funcion {args_preprocesado["funcion_preprocesado"]}, continuando con el siguiente")
        return
    # RESOLUTOR-----------------------------------------------------------------------
    # try:

    args_resolucion.update({k:v for k,v in datos_preprocesados.items() if k in ParametrosResolucion.__annotations__})

    datos_solucion_problema = args_resolucion["funcion_resolucion"](**args_resolucion)

    # if "verbose" in args_resolucion and args_resolucion["verbose"]:
    #     print(" Del resolutor obtenemos: ", datos_solucion_problema)

    print("\n Pasamos con exito el proceso de resolucion ")
    # except Exception as e:
    #     print(f"\n Error {e} al solucionar con la funcion {args_resolucion["funcion_resolucion"]}, continuando con el siguiente")
    #     return
    # POSTOPTIMIZADO------------------------------------------------------------------
    try:
        args_postOpt.update({k:v for k,v in datos_preprocesados.items() if k in ParametrosResolucion.__annotations__})
        args_postOpt.update({k:v for k,v in datos_solucion_problema.items() if k in ParametrosPostOpt.__annotations__})

        datos_solucion_problema_postOpt = args_postOpt["funcion_postOpt"](**args_postOpt)

        ruta_fichero = output_dir.joinpath(Path(nombre_foto_con_ext[0]+hora_proceso+"_procesado.svg"))
        datos_solucion_problema_postOpt.update({"ruta_a_resultado": ruta_fichero })

        # if "verbose" in args_resolucion and args_resolucion["verbose"]:
        #     print(" Del resolutor obtenemos: ", datos_solucion_problema)

        print("\n Pasamos con exito el proceso de post-optimizacion ")
    except Exception as e:
        print(f"\n Error {e} al reoptimizar con la funcion {args_postOpt["funcion_postOpt"]}, continuando con el siguiente")
        return
    # RECONSTRUCCION------------------------------------------------------------------
    try:
        args_reconstruccion.update({k:v for k,v in datos_solucion_problema_postOpt.items() if k in ParametrosReconstruccion.__annotations__})
        args_reconstruccion.update({k:v for k,v in datos_preprocesados.items() if k in ParametrosReconstruccion.__annotations__})


        datos_sol_final = args_reconstruccion["funcion_reconstruccion"](**args_reconstruccion)

        # if "verbose" in args_resolucion and args_resolucion["verbose"]:
        #     print("\n Del reconstructor obtenemos: ", datos_sol_final)

        print(f"\n imagen guardada con exito en {datos_sol_final["ruta_resultado"]} !!!")
    except Exception as e:
        print(f"\n Error {e} al pintar la solucion con la funcion {args_reconstruccion["funcion_reconstruccion"]}, continuando con el siguiente")
        return

    #Agregramos la imagen original si no existe en la carpeta
    ruta_imagen_original_en_destino = str(output_dir)+"\\"+".".join(nombre_foto_con_ext)
    if not Path(ruta_imagen_original_en_destino).exists():
        img_padre = cv2.imread(datos_preprocesados["ruta_a_la_imagen"])
        cv2.imwrite(ruta_imagen_original_en_destino,img_padre)
    fin = time()
    
    try:
        ruta_res = limpiar_ruta_para_raiz(datos_sol_final["ruta_resultado"])

        resultado = EstudioParametrosOutput(
            imagen_original=".".join(nombre_foto_con_ext),
            numero_de_pines=datos_preprocesados["numero_de_pines"],
            secuencia_pines=datos_solucion_problema_postOpt["secuencia_pines"].copy(),
            distancia_minima=datos_solucion_problema["distancia_minima"],
            maximo_lineas=datos_solucion_problema["maximo_lineas"],
            lineas_usadas= len(datos_solucion_problema_postOpt["secuencia_pines"].tolist())-1,
            peso_de_linea=datos_solucion_problema["peso_de_linea"],
            error_total=str(args_resolucion["funcion_calculo_error"](datos_solucion_problema_postOpt["error_total"])),
            tiempo_ejecucion=fin-inicio,
            tiempo_usado_re_optimizando=datos_solucion_problema_postOpt["tiempo_usado_re_optimizando"],
            iteraciones_re_optimizado_realizadas=datos_solucion_problema_postOpt["iteraciones_re_optimizado_realizadas"],
            ruta_resultado=ruta_res,
            verbose=str(True) if "verbose" in args_resolucion and args_resolucion["verbose"] else str(False),
            ruta_imagen_preprocesada=ruta_res,
            ruta_imagen_error_preresolutor=ruta_res,
            ruta_imagen_post_resolutor=ruta_res,
            funciones_usadas=", ".join([args_preprocesado["funcion_preprocesado"].__name__,args_resolucion["funcion_resolucion"].__name__,
                                            args_reconstruccion["funcion_reconstruccion"].__name__,args_postOpt["funcion_postOpt"].__name__,
                                            nombre_funcion_error]),
            probabilidad_mutacion_gen=0.0,
            cantidad_torneo=0,
            probabilidad_cruce=0.0,
            elitismo_size=0,
            alpha=0,
            beta=0,
            rho=0,
            q=0
        )

        agregar_datos_bioinspirados(resultado,datos_solucion_problema)
        if "verbose" in args_preprocesado and args_preprocesado["verbose"]:

            resultado.update({
                "ruta_imagen_preprocesada":limpiar_ruta_para_raiz(datos_sol_final["ruta_imagen_preprocesada"]),
                "ruta_imagen_error_preresolutor":limpiar_ruta_para_raiz(datos_sol_final["ruta_imagen_error_preresolutor"]),
                "ruta_imagen_post_resolutor":limpiar_ruta_para_raiz(datos_sol_final["ruta_imagen_post_resolutor"])
            })

    except Exception as e:
        print(f"\n Error{e} mientras actualizabamos valores de la ejecucion para su estudio")
        return 
    
    del args_preprocesado
    del args_resolucion
    del args_postOpt
    del args_reconstruccion
    del datos_preprocesados
    del datos_sol_final
    del datos_solucion_problema
    del datos_solucion_problema_postOpt

    cola_metadatos.put(resultado)
    gc.collect()
    cv2.destroyAllWindows()

