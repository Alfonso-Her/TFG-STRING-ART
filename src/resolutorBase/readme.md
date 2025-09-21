# Funcionamiento de este paquete:

La idea principal es separar el proceso en 3 problemas mas pequeños:
    1. preprocesado [preprocesado.py](preprocesado.py), 
    2. generacion de lista de clavos [resolutor.py](resolutor.py)
    3. obtener una imagen desde la lista de clavos [reconstructor.py](reconstructor.py)

Ademas usamos clases auxiliares definidas en otros ficheros:
    - punto [Punto.py](punto.py) define los puntos y funciones relevantes que hacer sobre ellos

Por ultimo creamos una funcion que permita llamar automaticamente a todo el flujo de trabajo en [solver.py](solver.py) con la funcion:
==hilar(Aqui van los parametros)==

donde los parametros significan:
    - Algo