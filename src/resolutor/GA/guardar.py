import pickle
from typing import Optional,Tuple

from deap import tools
from pathlib import Path

def crear_directorio_temporal(ruta_a_resultado:str)-> Path:
    directorio  = Path(ruta_a_resultado/"tempGA")
    directorio.mkdir(parents=True,exist_ok=True)
    return directorio

def guardar_checkpoint(
    directorio: Path,
    generacion: int,
    poblacion: list,
    hall_of_fame: tools.HallOfFame,
    logbook: tools.Logbook,
    random_state: Optional[Tuple] = None
) -> Path:

    checkpoint_file = directorio / f"checkpoint_gen_{generacion:04d}.pkl"
    
    # Preparar datos del checkpoint
    checkpoint_data = {
        'generacion': generacion,
        'poblacion': poblacion,
        'hall_of_fame': hall_of_fame,
        'logbook': logbook,
        'random_state': random_state
    }
    
    # Guardar usando pickle
    with open(checkpoint_file, 'wb') as f:
        pickle.dump(checkpoint_data, f, protocol=pickle.HIGHEST_PROTOCOL)
    
    return checkpoint_file

def cargar_checkpoint(directorio: Path) -> Optional[dict]:
    # Buscar todos los checkpoints
    checkpoints = list(directorio.glob("checkpoint_gen_*.pkl"))
    
    if not checkpoints:
        return None
    
    # Ordenar por número de generación (más reciente primero)
    checkpoints.sort(reverse=True)
    ultimo_checkpoint = checkpoints[0]
    
    # Cargar checkpoint
    with open(ultimo_checkpoint, 'rb') as f:
        checkpoint_data = pickle.load(f)
    
    print(f"[Checkpoint] Cargado desde: {ultimo_checkpoint.name}")
    print(f"[Checkpoint] Generación: {checkpoint_data['generacion']}")
    
    return checkpoint_data

def limpiar_checkpoints_antiguos(directorio: Path, mantener: int = 5):
    checkpoints = sorted(list(directorio.glob("checkpoint_gen_*.pkl")), reverse=True)
    
    # Eliminar todos excepto los N más recientes
    for checkpoint in checkpoints[mantener:]:
        checkpoint.unlink()
        print(f"[Checkpoint] Eliminado: {checkpoint.name}")

def guardar_checkpoint_final(
    directorio: Path,
    mejor_individuo: list,
    mejor_fitness: float,
    logbook: tools.Logbook,
    parametros: dict
) -> Path:

    resultado_final = directorio / "resultado_final.pkl"
    
    datos_finales = {
        'mejor_individuo': mejor_individuo,
        'mejor_fitness': mejor_fitness,
        'logbook': logbook,
        'generaciones_totales': len(logbook)
    }
    
    with open(resultado_final, 'wb') as f:
        pickle.dump(datos_finales, f, protocol=pickle.HIGHEST_PROTOCOL)
    
    return resultado_final