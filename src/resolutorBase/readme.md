# Funcionamiento de este paquete:
Estoy guiandome por el codigo del repositorio (StringArtGenerator
/main.go)[https://github.com/halfmonty/StringArtGenerator/blob/master/main.go]

La idea principal es separar el proceso en 3 problemas mas pequeños:
    1. preprocesado [preprocesado.py](preprocesado.py), 
    2. generacion de lista de clavos [resolutor.py](resolutor.py)
    3. obtener una imagen desde la lista de clavos [reconstructor.py](reconstructor.py)

Ademas usamos clases auxiliares definidas en otros ficheros:


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

Usamos numpy para generar los angulos de los pines centrados (de momento) en (ancho/2,alto/2) despues construimos las coordenas de los puntos.
Usamos como radio para la distribucion ancho/2 - 1 hay que tenerlo en cuenta porque dependiendo de la imagen podemos llegar a poner clavos fuera de la imagen TODO

### Precalculo de lineas

Recorremos todos los pines en orden evitando los que estan a distancia distancia_minima o menos (manera euristica de evitar lineas pequeñas),
para ello fijamos dos pares de cordenadas (x0,y0) y (x1,y1),
obtenemos la distancia euclidea entre los pines y la truncamos convieritendola en entero,
por ultimo generamos puntos equidistantes entre x0 y x1 tomando tantas mediciones como distancia obtuvimos antes (idem para y0, y1),
almacenamos en nuestras matrices de pasos con la siguiente logica
linea_cache_y[llegando_a * numero_pines + llegado a]

Creo que se podria mejorar evitando recalcular alguna solucion pero no lo se seguro TODO


## Resolutor [resolutor.py](resolutor.py)

En esta parte queremos definir toda la logica del algoritmo voraz desde definir las coordenadas de los pines a elegir el camino que sigue en hilo.


