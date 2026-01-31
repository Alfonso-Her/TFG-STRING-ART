import numpy as np
import cv2

def bresenham(x0: int, y0: int, x1: int, y1: int) :

    x0, y0, x1, y1 = int(x0), int(y0), int(x1), int(y1)
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy
    points_x, points_y = [], []

    while True:
        points_x.append(x0)
        points_y.append(y0)
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x0 += sx
        if e2 < dx:
            err += dx
            y0 += sy

    return list(zip(np.array(points_x, dtype=np.int64), np.array(points_y, dtype=np.int64)))

def _distancia_eu(x0,y0,x1,y1):
    return np.floor(np.sqrt(np.float64((x1-x0)*(x1-x0) + (y1-y0)*(y1-y0))))


def calculo_lineas_real(x0: int, y0: int, x1: int, y1: int):

    # Tomamos la distancia entre los pines para luego construir una "malla" de pixeles recorridos usando linspace
    distancia_entre_pines = _distancia_eu(x0,y0,x1,y1)
    #Convertimos a int para redondeo
    pasamos_por_xs = np.linspace(x0,x1,int(distancia_entre_pines),dtype=int).astype(np.int64)
    pasamos_por_ys = np.linspace(y0,y1,int(distancia_entre_pines),dtype=int).astype(np.int64)

    return list(zip(pasamos_por_xs, pasamos_por_ys))


def generar_comparativa_cv2(width: int, height: int, p0: tuple, p1: tuple):
    """
    Genera dos imágenes JPG usando OpenCV para comparar los algoritmos.
    """
    x0, y0 = p0
    x1, y1 = p1

    puntos_bresenham = bresenham(x0, y0, x1, y1)
    puntos_real = calculo_lineas_real(x0, y0, x1, y1)

    img_bresenham = np.zeros((height, width), dtype=np.uint8)
    img_real = np.zeros((height, width), dtype=np.uint8)

    for px, py in puntos_bresenham:
        if 0 <= px < width and 0 <= py < height:
            img_bresenham[py, px] = 255  


    for px, py in puntos_real:
        if 0 <= px < width and 0 <= py < height:
            img_real[py, px] = 255 

    cv2.imwrite("linea_bresenham_cv2.jpg", img_bresenham)
    cv2.imwrite("linea_real_cv2.jpg", img_real)
    
    print("Imágenes guardadas: 'linea_bresenham_cv2.jpg' y 'linea_real_cv2.jpg'")


if __name__ == "__main__":
    x0 = 0; y0 = 24
    x1 = 50; y1 = 0

    generar_comparativa_cv2(50, 50, (x0, y0), (x1, y1))
