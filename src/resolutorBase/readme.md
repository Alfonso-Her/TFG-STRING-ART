# Funcionamiento de este paquete:
Estoy guiandome por el codigo del repositorio (StringArtGenerator
/main.go)[https://github.com/halfmonty/StringArtGenerator/blob/master/main.go]

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


# Concretando mas sobre que hacemos en cada apartado

## Preprocesado [preprocesado.py](preprocesado.py):

### Tratamiento de la imagen
Aqui vamos a pasar de una imagen en formato ndarray de numpy (una lista de listas de listas con la informacion del color de cada pixel) a un vector de float64 (elijo float64 por tener algo mas de precisión pero se podría subir incluso, a coste de memoria claro) por el momento nos estamos quedando con el valor del rojo de cada pixel (**¿Quiza podriamos hacer algo genetico para la seleccion de colores?**)

El codigo que estoy siguiendo esta escrito en go y al abrir la imagen la obtiene con canales de 16 bits aunque luego se queda con el rojo y lo comprime (dividiendo entre 257), nosotros nos saltamos ese paso porque al usar opencv abrimos la imagen con canales en tipo uint 8 (entre 0 - 255).

Hay que tener cuidado porque OpenCv no utiliza RGB sino BGR

### Generacion de pines

### Precalculo de hiladas

## Resolutor [resolutor.py](resolutor.py)

En esta parte queremos definir toda la logica del algoritmo voraz desde definir las coordenadas de los pines a elegir el camino que sigue en hilo.


