import json
import numpy as np

from pathlib import Path
from .parametros import mapaJson

def concatenar_sobre_json(ruta: Path, metadatos:list):
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
    
    data += metadatos

    with ruta.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4,default=convert)


def tratar_json(datos_totales):
    """
        Renombra para que cuadre con el codigo de index.html
        usando mapaJson como esquema 
    """
    diccionario = {}
    
    for k,v in mapaJson.items():
        valor = 0
        print(k,v,datos_totales)
        if v in datos_totales:
            valor = datos_totales[v]
        diccionario.update({k:valor})

    return diccionario