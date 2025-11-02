from multiprocessing import Process,Queue
from visor import concatenar_sobre_json

class Escritor_json(Process):

    def __init__(self,lock, ruta, Cola_metadatos:Queue):
        super().__init__()
        self.lock = lock
        self.cola = Cola_metadatos
        self.ruta = ruta

    def run(self):
        metadatos = self.cola.get()
        while metadatos is not None:
            with self.lock:
                concatenar_sobre_json(ruta=self.ruta,metadatos=metadatos)
            del metadatos
            metadatos = self.cola.get()
