from pathlib import Path
from solvers import estudioParametrico

def estudio_calidad_visual_alternando_color_fondos_y_hilo(ruta_salida: str, **kwargs):
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

if __name__ == "__main__":
   estudio_calidad_visual_alternando_color_fondos_y_hilo(ruta_salida="../ejemplos/local/prueba_balnco_y_negro", ruta_a_la_imagen = ["../ejemplos/ae300.jpg", "../ejemplos/acue.jpg"])
