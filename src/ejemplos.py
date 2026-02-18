from pathlib import Path

import os
import time
import http.server
import socketserver
import threading
import webbrowser


def servidor_en_hilo(path_dir: Path, puerto: int):
    """Lanza un servidor en un hilo independiente para una carpeta específica."""
    
    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            # Esto permite servir la carpeta sin usar os.chdir()
            super().__init__(*args, directory=str(path_dir), **kwargs)

    def run_server():
        socketserver.TCPServer.allow_reuse_address = True
        with socketserver.TCPServer(("", puerto), Handler) as httpd:
            print(f"✅ [ACTIVO] Servidor en puerto {puerto} -> {path_dir.name}")
            
            # Abrir el navegador tras 1 segundo
            threading.Thread(
                target=lambda: (time.sleep(1), webbrowser.open(f"http://127.0.0.1:{puerto}/index.html")),
                daemon=True
            ).start()
            
            httpd.serve_forever()

    # Creamos el hilo como demonio para que se cierre al cerrar el programa principal
    hilo = threading.Thread(target=run_server, daemon=True)
    hilo.start()
    return hilo



if __name__ == "__main__":
    # Configuración de carpetas (Asegúrate de que estas rutas existan)
    proyectos = {
        "5": {"nombre": "Voraz básico", "ruta": Path("../ejemplos/entrega/voraz/voraz_final/")},
        "6": {"nombre": "Voraz error general", "ruta": Path("../ejemplos/entrega/voraz_error/vorazerrorgeneral/")},
        "7": {"nombre": "Refinamiento de soluciones", "ruta": Path("../ejemplos/entrega/pin_medio/pinMedioFinal/")},
        "8": {"nombre": "Algoritmos genéticos", "ruta": Path("../ejemplos/entrega/GA/GA_final/")},
        "9": {"nombre": "ACO", "ruta": Path("../ejemplos/entrega/ACO/ACO_FINAL/")},
    }

    puerto_base = 8080
    servidores_activos = {}

    print("--- GESTOR DE VISUALIZACIÓN MULTI-INSTANCIA ---")
    print("Selecciona el número de seccion para lanzar el servidor de ese estudio (Vacio los habre todos).")
    print("Puedes abrir hasta 5 diferentes en paralelo.")

    try:
        while True:
            print("\nOpciones disponibles:")
            for k, v in proyectos.items():
                estado = "Online" if k in servidores_activos else "Offline"
                print(f"  {k} -> {v['nombre']} [{estado}]")
            
            print("  q -> Salir de todo")
            
            seleccion = input("\n¿Qué estudio quieres ver? > ").lower()
            print(f"Has seleccionado: {seleccion}")

            if seleccion == 'q':
                print("Cerrando gestor...")
                break
            
            if seleccion == "":
                for pt in proyectos.keys():
                    if not pt in servidores_activos.keys():
                        ruta = proyectos[pt]['ruta']
                        nuevo_puerto = puerto_base + len(servidores_activos)
                        servidor_en_hilo(ruta, nuevo_puerto)
                        servidores_activos[pt] = nuevo_puerto

            if seleccion in proyectos:
                if seleccion in servidores_activos:
                    print(f"WARNING: El servidor de {proyectos[seleccion]['nombre']} ya está corriendo.")
                    webbrowser.open(f"http://127.0.0.1:{servidores_activos[seleccion]}/index.html")
                else:
                    ruta = proyectos[seleccion]['ruta']
                    nuevo_puerto = puerto_base + len(servidores_activos)
                    servidor_en_hilo(ruta, nuevo_puerto)
                    servidores_activos[seleccion] = nuevo_puerto
            else:
                print("Opción no válida.")

    except KeyboardInterrupt:
        print("\n Finalizando todos los servidores...")