import numpy as np
import matplotlib.pyplot as plt
from random import randint
import svgwrite
from matplotlib.patches import Circle

def draw_string_art_svg(coords, order, filename="string_art.svg",
                        size_px=3000,
                        nail_r=6,
                        thread_width=1,
                        nail_color="#929191",
                        thread_color='white',
                        padding_ratio=0.01,
                        background_color="black"):

    coords = np.asarray(coords)
    # Normaliza coords al rango 0..size_px con margen
    mn = coords.min(axis=0)
    mx = coords.max(axis=0)
    pad = padding_ratio * (mx - mn).max()
    mn -= pad
    mx += pad
    def map_pt(p):
        x = (p[0]-mn[0])/(mx[0]-mn[0]) * size_px
        y = (1 - (p[1]-mn[1])/(mx[1]-mn[1])) * size_px
        return (x,y)

    dwg = svgwrite.Drawing(filename, size=(size_px, size_px))
    
    # fondo (rectángulo que cubre todo el lienzo)
    dwg.add(dwg.rect(insert=(0, 0), size=(size_px, size_px), fill=background_color))
    # hilo
    path_pts = [map_pt(coords[i]) for i in order]
    dwg.add(dwg.polyline(points=path_pts, stroke=thread_color, fill='none',
                          stroke_width=thread_width, stroke_linecap='round',
                          stroke_linejoin="round"))
    # clavos
    for p in [map_pt(p) for p in coords]:
        dwg.add(dwg.circle(center=p, r=nail_r, fill=nail_color))
    dwg.save()

if __name__ == "__main__":

    t = np.linspace(0, 2*np.pi, 256, endpoint=False)
    coords = np.column_stack([np.cos(t), np.sin(t)])
    order = [0,125]
    draw_string_art_svg(coords, order, filename="string_art.svg")