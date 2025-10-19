from pathlib import Path

import shutil
from .servidor import lanzar_servidor_y_web

def crear_web_con_dir(output_dir:Path, ruta_a_web:Path):
    origen = ruta_a_web.resolve()
    destino = output_dir.resolve()

    
    if not ruta_a_web.exists():
        raise FileNotFoundError(f"No encontramos la web")

    
    for item in origen.iterdir():
        destino_item = destino / item.name

        if item.is_dir():
            # Copiar directorio completo (por ejemplo "utils")
            if destino_item.exists():
                shutil.rmtree(destino_item)
            shutil.copytree(item, destino_item)
        else:
            # Copiar archivo individual como index.html
            shutil.copy2(item, destino_item)
    lanzar_servidor_y_web(output_dir=output_dir)