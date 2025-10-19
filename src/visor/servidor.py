from pathlib import Path

import http.server
import socketserver
import threading
import webbrowser

def lanzar_servidor_y_web(output_dir: Path, port: int = 8000):
    """
    Lanza un servidor HTTP simple en un hilo y abre la web index.html en el navegador.
    """
    handler = http.server.SimpleHTTPRequestHandler

    # Cambiar temporalmente el directorio de trabajo
    import os
    os.chdir(output_dir)

    def serve():
        with socketserver.TCPServer(("", port), handler) as httpd:
            print(f"Servidor activo en http://127.0.0.1:{port}/ (sirviendo {output_dir})")
            print("Presiona Ctrl+C para detener.")
            httpd.serve_forever()

    # Lanza el servidor en un hilo (para que no bloquee)
    hilo = threading.Thread(target=serve, daemon=True)
    hilo.start()

    # Abrimos el navegador apuntando al index
    webbrowser.open(f"http://127.0.0.1:{port}/index.html")