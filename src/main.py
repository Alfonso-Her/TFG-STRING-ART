from pathlib import Path
from solvers import estudioParametrico

def estudio_calidad_visual_alternando_color_fondos_y_hilo(ruta_salida: str, **kwargs):
    """
        Parece que se ven mejor las imagenes con hilo negro y fondo blanco 
    """
    parametros_basicos = {
        "ruta_a_la_imagen": "../ejemplos/ae300.jpg",
        "numero_de_pines": 256,
        "peso_de_linea" : 20,
        "color_de_hilo" : ["#000000","#ffffff"],
        "color_de_fondo" : ["#000000","#ffffff"]
     }
    parametros_basicos.update(kwargs)
    estudioParametrico(output_dir=Path(ruta_salida), estudio_web= True, continuacion_estudio=False, **parametros_basicos)
    return 

def estudio_peso_linea(ruta_salida:str, **kwargs):
    parametros_basicos = {
        "ruta_a_la_imagen": "../ejemplos/ae300.jpg",
        "recortar": True,
        "redimensionar": False,
        "numero_de_pines": 256,
        "peso_de_linea" : list(range(50)),
        "color_de_hilo" : "#000000",
        "color_de_fondo" :"#ffffff"
    }
    parametros_basicos.update(kwargs)
    estudioParametrico(output_dir=Path(ruta_salida), estudio_web= True, continuacion_estudio=False, **parametros_basicos)
    return 

if __name__ == "__main__":
#    estudio_calidad_visual_alternando_color_fondos_y_hilo(ruta_salida="../ejemplos/local/prueba_balnco_y_negro",
#                                                          ruta_a_la_imagen = ["../ejemplos/ae300.jpg", "../ejemplos/acue.jpg","../ejemplos/cervantesColor.jpg"],
#                                                          numero_de_pines=[2**a for a in range(6,11)])
   
   estudio_peso_linea(ruta_salida="../ejemplos/local/prueba_balnco_y_negro")
