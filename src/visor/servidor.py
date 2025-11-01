from pathlib import Path

import os
import time
import http.server
import socketserver
import threading
import webbrowser

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
def revisar_estudio(output_dir: Path, port: int = 8080):
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