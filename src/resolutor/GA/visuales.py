# import numpy as np
# # import pandas as pd

# import matplotlib.pyplot as plt

# from typing import List, Unpack, Callable

# from calcular_error import mse
# def guardar_poblacion_pandas(poblacion: list, 
#                             hall_of_fame, 
#                             logbook,
#                             top_n: int = 20,
                            
#                             funcion_calculo_error: Callable[[np.ndarray],np.float64] = mse,
#                             ):
#     """
#     Imprime población como DataFrame de pandas con formato bonito

#     """
#     # Ordenar por fitness
#     poblacion_ordenada = sorted(poblacion, key=lambda ind: ind.fitness.values[0])
    
#     errores = [ind.fitness.values[0] for ind in poblacion]
#     mejor_error = hall_of_fame[0].fitness.values[0]

#     # Crear DataFrame
#     datos = []
#     for i, individuo in enumerate(poblacion_ordenada[:top_n], 1):
#         error = individuo.fitness.values[0]
#         diferencia_porcentual = ((error - mejor_error) / mejor_error * 100) if mejor_error > 0 else 0
        
#         datos.append({
#             'Rank': i,
#             f'Error {funcion_calculo_error.__name__}': error,
#             '% vs Mejor': diferencia_porcentual,
#             'Longitud': len(individuo)
#         })
    
#     df = pd.DataFrame(datos)
    
#     # Configurar formato de salida
#     pd.options.display.float_format = '{:.6f}'.format
#     pd.options.display.max_columns = None
#     pd.options.display.width = None

#     print("\n" + "="*100)
#     print(" 🧬 ALGORITMO GENÉTICO - POBLACIÓN FINAL ".center(100, "="))
#     print("="*100)


#     # print(f"\n📊 ESTADÍSTICAS DE LA POBLACIÓN:")
#     # print(f"   {'Tamaño de población:':<35} {len(poblacion)} individuos")
#     # print(f"   {'Mejor error (Hall of Fame):':<35} {mejor_error:.10f}")
#     # print(f"   {'Error promedio:':<35} {np.mean(errores):.10f}")
#     # print(f"   {'Error mediana:':<35} {np.median(errores):.10f}")
#     # print(f"   {'Desviación estándar:':<35} {np.std(errores):.10f}")
#     # print(f"   {'Peor error:':<35} {max(errores):.10f}")
#     # print(f"   {'Rango (peor - mejor):':<35} {max(errores) - mejor_error:.10f}")
    
#     # Estadísticas
#     errores = [ind.fitness.values[0] for ind in poblacion]
#     print(f"\nEstadísticas:")
#     print(f"  Mejor:    {min(errores):.6f}")
#     print(f"  Peor:     {max(errores):.6f}")
#     print(f"  Media:    {np.mean(errores):.6f}")
#     print(f"  Std Dev:  {np.std(errores):.6f}")

#     if logbook and len(logbook) > 0:
#         gen_inicial = logbook[0]
#         gen_final = logbook[-1]
#         mejora_absoluta = gen_inicial['min'] - gen_final['min']
#         mejora_porcentual = (mejora_absoluta / gen_inicial['min'] * 100) if gen_inicial['min'] > 0 else 0
        
#         print(f"\n📈 EVOLUCIÓN DEL ALGORITMO:")
#         print(f"   {'Generaciones ejecutadas:':<35} {len(logbook)}")
#         print(f"   {'Error inicial (gen 0, min):':<35} {gen_inicial['min']:.10f}")
#         print(f"   {'Error final (gen {}, min):'.format(len(logbook)-1):<35} {gen_final['min']:.10f}")
#         print(f"   {'Mejora absoluta:':<35} {mejora_absoluta:.10f}")
#         print(f"   {'Mejora relativa:':<35} {mejora_porcentual:.4f}%")