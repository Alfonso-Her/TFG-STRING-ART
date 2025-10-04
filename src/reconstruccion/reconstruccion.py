import numpy as np
import svgwrite

def hilar_secuencia_svg(posiciones_pines, secuencia_pines, ruta_a_resultado="string_art.svg",
                        tamano_lado_px=3000,
                        ancho_clavos=6,
                        ancho_de_hilo=1,
                        color_de_clavo="#929191",
                        color_de_hilo='#000000',
                        ratio_distancia=0.01,
                        color_de_fondo="#ffffff",
                        **kwargs):
    
    posiciones_pines = np.asarray(posiciones_pines)
    # Normaliza posiciones_pines al rango 0..tamano_lado_px con margen
    mn = posiciones_pines.min(axis=0)
    mx = posiciones_pines.max(axis=0)
    pad = ratio_distancia * (mx - mn).max()
    mn -= pad
    mx += pad
    def map_pt(p):
        x = (p[0]-mn[0])/(mx[0]-mn[0]) * tamano_lado_px
        y = (1 - (p[1]-mn[1])/(mx[1]-mn[1])) * tamano_lado_px
        return (x,y)
    
    centro_img= map_pt((0,0))
    dwg = svgwrite.Drawing(ruta_a_resultado, size=(tamano_lado_px, tamano_lado_px))
    
    # fondo (rectángulo que cubre todo el lienzo)
    dwg.add(dwg.rect(insert=(0, 0), size=(tamano_lado_px, tamano_lado_px), fill=color_de_fondo))
    # dwg.add(dwg.circle(center=(tamano_lado_px/2,tamano_lado_px/2), r=sum(mx), fill=color_de_fondo))
    # hilo
    path_pts = [map_pt(posiciones_pines[i]) for i in secuencia_pines]
    dwg.add(dwg.polyline(points=path_pts, stroke=color_de_hilo, fill='none',
                          stroke_width=ancho_de_hilo, stroke_linecap='round',
                          stroke_linejoin="round"))
    # clavos
    for p in [map_pt(p) for p in posiciones_pines]:
        dwg.add(dwg.circle(center=p, r=ancho_clavos, fill=color_de_clavo))
    dwg.save()

    return {"ruta_resultado":ruta_a_resultado}

##TESTING
if __name__ == "__main__":

    t = np.linspace(0, 2*np.pi, 256, endpoint=False)
    posiciones_pines = np.column_stack([np.cos(t), np.sin(t)])
    secuencia_pines = [0,125]
    hilar_secuencia_svg(posiciones_pines, secuencia_pines, ruta_a_resultado="string_art.svg")