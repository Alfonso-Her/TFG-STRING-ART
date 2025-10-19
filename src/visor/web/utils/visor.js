// VARIABLES GLOBALES
window.datosOriginales= [];
window.ejecucionesData = [];
window.paginaActual = 0;
window.elementosPorPagina = 20;
window.parametrosVisibles = [
    'imagen_original', 'funciones_usadas', 'numero_de_pines', 
    'distancia_minima', 'maximo_lineas', 'lineas_usadas', 
    'peso_de_linea', 'error_total', 'funcio_error', 
    'tiempo_ejecucion', 'verbose'
];

/**
 * Crea las tarjetas de ejecución (derecha) y especiales (izquierda)
 */
function crearTarjetas(item) {
    const contenedor_ejecuciones = document.querySelector(".contenedor-ejecuciones");
    const contenedor_imagen = document.querySelector(".contenedor-imagen");
    
    // Crear tarjeta de ejecución (derecha)
    const tarjeta = document.createElement("div");
    tarjeta.className = "tarjeta";

    // Contenedor de imagen
    const divImagen = document.createElement("div");
    divImagen.className = "Imagen";

    const img = document.createElement("img");
    img.src = item.ruta_resultado;
    img.alt = "Resultado";
    img.style.maxWidth = "100%";
    img.style.maxHeight = "100%";
    divImagen.appendChild(img);

    // Texto descriptivo
    const textoImagen = document.createElement("p");
    textoImagen.className = "nombreImagen";
    textoImagen.textContent = "Imagen: resultado";
    divImagen.appendChild(textoImagen);

    // Propiedades de ejecución (solo las visibles)
    const divPropiedadesEjecucion = document.createElement("div");
    divPropiedadesEjecucion.className = "propiedades-ejecucion";

    let propiedadesHTML = '';
    
    window.parametrosVisibles.forEach(param => {
        if (item.hasOwnProperty(param)) {
            const nombreFormateado = param.replace(/_/g, ' ')
                                         .replace(/\b\w/g, l => l.toUpperCase());
            
            let valor = item[param];
            
            // Formatear valores específicos
            if (param === 'error_total' && typeof valor === 'string') {
                // Convertir error_total a número para mejor ordenamiento
                valor = parseFloat(valor) || valor;
            }
            
            propiedadesHTML += `
                <p class="Propiedad" data-parametro="${param}">
                    ${nombreFormateado}: ${valor}
                </p>
            `;
        }
    });

    divPropiedadesEjecucion.innerHTML = propiedadesHTML;

    // Comportamiento de click para imágenes verbose
    if (item.verbose && item.verbose !== "False") {
        const imagenes = [
            { src: item.ruta_resultado, nombre: "resultado" },
            { src: item.ruta_imagen_preprocesada, nombre: "Preprocesada" },
            { src: item.ruta_imagen_error_preresolutor, nombre: "Error pre-resolución" },
            { src: item.ruta_imagen_error_post_resolutor, nombre: "Error post-resolución" }
        ].filter(obj => obj.src && obj.src !== "");
        
        if (imagenes.length > 1) { // Solo si hay más de una imagen
            let index = 0;

            img.style.cursor = "pointer";
            img.title = "Haz clic para alternar imágenes \n o pulsa click derecho para habilitar zoom";

            img.addEventListener("click", () => {
                index = (index + 1) % imagenes.length;
                const actual = imagenes[index];
                
                img.src = actual.src;
                textoImagen.textContent = `Imagen: ${actual.nombre}`;
            });
        }
    }

    // Configurar zoom
    img.classList.add("zoomable-img");

    // Montar tarjeta de ejecución
    tarjeta.appendChild(divImagen);
    tarjeta.appendChild(divPropiedadesEjecucion);

    // Crear tarjeta especial (izquierda) solo si no existe
    const imagenId = item.imagen_original;
    if (!document.getElementById(imagenId)) {
        const tarjetaEspecial = document.createElement("div");
        tarjetaEspecial.className = "tarjeta-especial";
        tarjetaEspecial.id = imagenId;

        const divImagenEspecial = document.createElement("div");
        divImagenEspecial.className = "imagen-especial";

        const imgEspecial = document.createElement("img");
        imgEspecial.src = item.imagen_original;
        imgEspecial.alt = "origen";
        imgEspecial.style.maxWidth = "100%";
        imgEspecial.style.maxHeight = "100%";
        imgEspecial.classList.add("zoomable-img");
        divImagenEspecial.appendChild(imgEspecial);

        const nombre = document.createElement("div");
        nombre.className = "texto-especial";
        
        // Mostrar solo el nombre del archivo
        const nombreArchivo = imagenId.split('/').pop() || imagenId.split('\\').pop() || imagenId;
        nombre.textContent = nombreArchivo;

        tarjetaEspecial.appendChild(divImagenEspecial);
        tarjetaEspecial.appendChild(nombre);
        contenedor_imagen.appendChild(tarjetaEspecial);
    }

    // Agregar al contenedor de ejecuciones
    contenedor_ejecuciones.appendChild(tarjeta);
}

/**
 * Carga una página específica de datos (virtual scrolling)
 */
function cargarPagina(pagina) {
    const inicio = pagina * window.elementosPorPagina;
    const fin = inicio + window.elementosPorPagina;
    const datosPagina = window.ejecucionesData.slice(inicio, fin);
    
    datosPagina.forEach(item => {
        crearTarjetas(item);
    });
}

/**
 * Configura el scroll infinito
 */
function configurarScrollInfinito() {
    const contenedor = document.querySelector(".ejecuciones");
    let cargando = false;

    contenedor.addEventListener("scroll", () => {
        const { scrollTop, scrollHeight, clientHeight } = contenedor;
        
        if (!cargando && scrollTop + clientHeight >= scrollHeight - 100) {
            cargando = true;
            window.paginaActual++;
            
            setTimeout(() => {
                cargarPagina(window.paginaActual);
                cargando = false;
            }, 100);
        }
    });
}

/**
 * Configura los filtros del menú superior
 */
function configurarFiltros() {
    const filtroGrupo = document.getElementById('filtro-grupo');
    const filtroOrden = document.getElementById('filtro-orden');
    const checkboxes = document.querySelectorAll('input[name="parametro"]');

    // Actualizar parámetros visibles cuando cambian los checkboxes
    checkboxes.forEach(checkbox => {
        checkbox.addEventListener('change', () => {
            window.parametrosVisibles = Array.from(document.querySelectorAll('input[name="parametro"]:checked'))
                .map(cb => cb.value);
            recargarVista();
        });
    });

    filtroGrupo.addEventListener('change', recargarVista);
    filtroOrden.addEventListener('change', recargarVista);
}

/**
 * Recarga la vista aplicando filtros y ordenamiento
 */
function recargarVista() {
    const grupo = document.getElementById('filtro-grupo').value;
    const orden = document.getElementById('filtro-orden').value;

    let datosFiltrados = [...window.ejecucionesData];

    // Aplicar ordenamiento
    if (orden) {
        datosFiltrados.sort((a, b) => {
            if (orden === 'error_total') return a.error_total - b.error_total;
            if (orden === 'tiempo_ejecucion') return a.tiempo_ejecucion - b.tiempo_ejecucion;
            if (orden === 'lineas_usadas') return a.lineas_usadas - b.lineas_usadas;
            return 0;
        });
    }

    // Limpiar contenedores
    document.querySelector(".contenedor-ejecuciones").innerHTML = "";
    document.querySelector(".contenedor-imagen").innerHTML = "";

    // Reiniciar paginación
    window.paginaActual = 0;

    // Aplicar agrupamiento
    if (grupo) {
        agruparYMostrar(datosFiltrados, grupo);
    } else {
        window.ejecucionesData = datosFiltrados;
        cargarPagina(0);
    }
}

/**
 * Agrupa y muestra los datos por criterio
 */
function agruparYMostrar(datos, grupo) {
    const grupos = {};
    
    // Agrupar datos
    datos.forEach(item => {
        const clave = item[grupo];
        if (!grupos[clave]) grupos[clave] = [];
        grupos[clave].push(item);
    });

    const contenedor = document.querySelector(".contenedor-ejecuciones");

    // Mostrar grupos
    Object.entries(grupos).forEach(([nombreGrupo, items]) => {
        // Crear header de grupo
        const header = document.createElement('div');
        header.className = 'grupo-header';
        header.innerHTML = `<h3>${grupo}: ${nombreGrupo} (${items.length} elementos)</h3>`;
        contenedor.appendChild(header);

        // Mostrar items del grupo
        items.forEach(item => crearTarjetas(item));
    });
}

/**
 * Configura el drag and drop
 */
function configurarDragAndDrop() {
    // Configurar Sortable.js para reordenamiento
    if (typeof Sortable !== 'undefined') {
        new Sortable(document.querySelector('.contenedor-ejecuciones'), {
            animation: 150,
            ghostClass: 'fantasma-arrastre',
            handle: '.tarjeta',
            onEnd: function(evt) {
                console.log('Elemento movido de posición', evt.oldIndex, '→', evt.newIndex);
            }
        });

        new Sortable(document.querySelector('.contenedor-imagen'), {
            animation: 150,
            ghostClass: 'fantasma-arrastre',
            handle: '.tarjeta-especial',
            onEnd: function(evt) {
                console.log('Imagen especial movida', evt.oldIndex, '→', evt.newIndex);
            }
        });
    }
}

/**
 * Carga ejecuciones desde datos.json
 */
async function cargarDatosDesdeJSON() {
    try {
        const respuesta = await fetch("datos.json", { cache: "no-store" });
        if (!respuesta.ok) {
            throw new Error(`Error HTTP ${respuesta.status}`);
        }

        const data = await respuesta.json();

        if (!Array.isArray(data)) {
            throw new Error("El contenido de datos.json no es una lista de ejecuciones.");
        }

        console.log(`✅ Cargadas ${data.length} ejecuciones desde datos.json`);
        
        window.ejecucionesData = data;
        window.paginaActual = 0;
        
        cargarPagina(0);
        configurarScrollInfinito();
        configurarFiltros();
        configurarDragAndDrop();
        
    } catch (error) {
        console.error("❌ Error al cargar datos.json:", error);
        const contenedor = document.querySelector(".contenedor-ejecuciones");
        contenedor.innerHTML = `
            <div style="color:white; text-align:center; padding:2em;">
                <h2>Error al cargar <code>datos.json</code></h2>
                <p>Verifica que estás sirviendo la carpeta con <code>python main.py</code>.</p>
                <p>Detalle del error: ${error.message}</p>
            </div>
        `;
    }
}

// Inicializar cuando el DOM esté listo
document.addEventListener("DOMContentLoaded", cargarDatosDesdeJSON);