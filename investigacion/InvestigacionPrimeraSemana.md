# Que tipo de algoritmo usan para resolver

## Algoritmos Greedy:
    - [2018.EG.Birsak.StringArt.pdf](2018.EG.Birsak.StringArt.pdf)

# Numero de pines:
    - En [2018.EG.Birsak.StringArt.pdf](2018.EG.Birsak.StringArt.pdf) : 256 pines
    - [2024.ComputationalStringArtRubenSocha.pdf](2024.ComputationalStringArtRubenSocha.pdf) : 200> y en muchos casos estudia 256

# Notas tecnicas

- En el paper [2018.EG.Birsak.StringArt.pdf](2018.EG.Birsak.StringArt.pdf): 
    * se presupone que el hilo es totalmente opaco, y que por tanto, no se modifica la imagen una vez el hilo para entre dos clavos.
    * Asume que siendo t el ancho del hilo y d el diametro de la imagen (canvas circular) se mantiene: Z = d/t (Z es la resolucion de la imagen) se hace para simplificar el calculo del camino, de esta manera asegura que si un hilo pasa por mitad de un pixel, el pixel esta cuvierto entero
    * Recalca que hay 4 maneras de conectar un hilo entre dos clavos y dice que el codigo supone clavos con seccion de 2mm ~ 13 px
    * Como quieren que sea fabricable, toman un camino euclidiano
    * Hay un planteamiento formal del problema interesante (paginas 3-4), importante que este planteamiento no tiene en cuenta todas las restricciones

- Del archivo [2024.ComputationalStringArtRubenSocha.pdf](2024.ComputationalStringArtRubenSocha.pdf):
    * Tiene pinta de ser un tfg centrado en el analisis computacional del algoritmo introduciendo diferentes parametros
    * Ojo que calcula difernte la resolucion
    * Concluye que debe de existir un rango optimo entre numero de pines y eficiencia por lo que muestra en las graficas del punto 4.3 el rango optimo para su resolucion debe de estar a partir de los 200.

- Paper sobre resolucion mediante algoritmos que usan paralelismo [SolucionandoParalelismo.pdf](SolucionandoParalelismo.pdf): 
    - Le heche un vistazo rapido pero usa c++ y paralelismo con CUDA y aunque consigue reducir mucho los tiempos no consigue resultados satisfactorios visualmente hablando
    - # (Para ALfonso) Lee este con mas profundidad