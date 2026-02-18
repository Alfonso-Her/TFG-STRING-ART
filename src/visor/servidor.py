from pathlib import Path

import os
import time
import http.server
import socketserver
import threading
import webbrowser

# Parte del codigo generado con IA

def lanzar_servidor_y_web(output_dir: Path, port: int = 8085):
    """
    Lanza un servidor HTTP simple en la carpeta `output_dir`
    y mantiene el proceso activo hasta que el usuario lo cierre.
    """
    handler = http.server.SimpleHTTPRequestHandler
    cwd_anterior = os.getcwd()
    os.chdir(output_dir)
    
    with socketserver.TCPServer(("", port), handler) as httpd:
        print(f"\n🌍 Servidor activo en http://127.0.0.1:{port}/")
        print(f"📁 Sirviendo contenido desde: {output_dir}")
        print("🛑 Pulsa Ctrl+C para detener el servidor.\n")

        threading.Thread(
            target=lambda: (time.sleep(3), webbrowser.open(f"http://127.0.0.1:{port}/index.html")),
            daemon=True
        ).start()

        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 Servidor detenido manualmente.")
        finally:
            httpd.server_close()
            os.chdir(cwd_anterior)
def revisar_estudio(output_dir: Path, port: int = 8085):
    """
    Sirve una carpeta de estudio anterior (que contenga index.html y datos.json)
    en un servidor HTTP local y abre el navegador automáticamente.
    
    Ejemplo:
        revisar_estudio(Path("resultados/estudio_2025_10_19"))
    """
    output_dir = Path(output_dir).resolve()

    if not output_dir.exists():
        raise FileNotFoundError(f"La ruta {output_dir} no existe.")
    if not output_dir.joinpath("index.html").exists():
        raise FileNotFoundError(f"No se encontró index.html en {output_dir}")

    handler = http.server.SimpleHTTPRequestHandler
    cwd_anterior = os.getcwd()
    os.chdir(output_dir)

    with socketserver.TCPServer(("", port), handler) as httpd:
        print(f"\n🌍 Servidor activo en http://127.0.0.1:{port}/")
        print(f"📁 Sirviendo contenido desde: {output_dir}")
        print("🛑 Pulsa Ctrl+C para detener el servidor.\n")

        threading.Thread(
            target=lambda: (time.sleep(1), webbrowser.open(f"http://127.0.0.1:{port}/index.html")),
            daemon=True
        ).start()

        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 Servidor detenido manualmente.")
        finally:
            httpd.server_close()
            os.chdir(cwd_anterior)

import http.server
import socketserver
import threading
import webbrowser
import time
import os
from pathlib import Path

# --- FUNCIONES DE SERVIDOR MEJORADAS ---

def servidor_en_hilo(path_dir: Path, puerto: int):
    """Lanza un servidor en un hilo independiente para una carpeta específica."""
    
    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            # Esto permite servir la carpeta sin usar os.chdir()
            super().__init__(*args, directory=str(path_dir), **kwargs)

    def run_server():
        # Allow_reuse_address para evitar errores de "puerto en uso" al reiniciar rápido
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

# --- LÓGICA DE EJECUCIÓN ---

if __name__ == "__main__":
    # Configuración de carpetas (Asegúrate de que estas rutas existan)
    proyectos = {
        "0": {"nombre": "Voraz básico", "ruta": Path("./resultados/aco")},
        "1": {"nombre": "Voraz error general", "ruta": Path("./resultados/geneticos")},
        "2": {"nombre": "Refinamiento de soluciones", "ruta": Path("./resultados/redes")},
        "3": {"nombre": "Algoritmos genéticos", "ruta": Path("./resultados/tabu")},
        "4": {"nombre": "ACO", "ruta": Path("./resultados/annealing")},
    }

    puerto_base = 8080
    servidores_activos = {}

    print("--- 🚀 GESTOR DE VISUALIZACIÓN MULTI-INSTANCIA ---")
    print("Selecciona un número para lanzar el servidor de ese estudio.")
    print("Puedes abrir hasta 5 diferentes en paralelo.")

    try:
        while True:
            print("\nOpciones disponibles:")
            for k, v in proyectos.items():
                estado = "🌐 Online" if k in servidores_activos else "💤 Offline"
                print(f"  {k} -> {v['nombre']} [{estado}]")
            
            print("  q -> Salir de todo")
            
            seleccion = input("\n¿Qué estudio quieres ver? > ").lower()

            if seleccion == 'q':
                print("Cerrando gestor...")
                break

            if seleccion in proyectos:
                if seleccion in servidores_activos:
                    print(f"⚠️ El servidor de {proyectos[seleccion]['nombre']} ya está corriendo.")
                    webbrowser.open(f"http://127.0.0.1:{servidores_activos[seleccion]}/index.html")
                else:
                    ruta = proyectos[seleccion]['ruta']
                    
                    # Verificar si la carpeta existe antes de lanzar
                    if not ruta.exists():
                        print(f"❌ Error: No existe la carpeta {ruta}")
                        # Opcional: crearla para pruebas
                        # ruta.mkdir(parents=True, exist_ok=True)
                        continue

                    nuevo_puerto = puerto_base + len(servidores_activos)
                    servidor_en_hilo(ruta, nuevo_puerto)
                    servidores_activos[seleccion] = nuevo_puerto
            else:
                print("❌ Opción no válida.")

    except KeyboardInterrupt:
        print("\n🛑 Finalizando todos los servidores...")