// VARIABLES GLOBALES
window.datosOriginales = []; // Mantenemos los datos originales intactos
window.ejecucionesData = []; // Datos filtrados/ordenados
window.paginaActual = 0;
window.elementosPorPagina = 20;
window.parametrosVisibles = [
    'imagen_original', 'numero_de_pines','distancia_minima', 
    'maximo_lineas', 'lineas_usadas','peso_de_linea',
    'error_total', 'funciones_usadas', 'tiempo_ejecucion',
    'tiempo_postOpt','iteraciones_postopimizacion'
];

/**
 * Actualiza los parámetros visibles basados en los checkboxes checked
 */
function actualizarParametrosVisibles() {
    const checkboxes = document.querySelectorAll('input[name="parametro"]:checked');
    window.parametrosVisibles = Array.from(checkboxes).map(cb => cb.value);
}

/**
 * Crea las tarjetas de ejecución (derecha) y especiales (izquierda)
 */
function crearTarjetas(item) {
    const contenedor_ejecuciones = document.querySelector(".contenedor-ejecuciones");
    const contenedor_imagen = document.querySelector(".contenedor-imagen");
    
    // Crear tarjeta de ejecución (derecha)
    const tarjeta = document.createElement("div");
    tarjeta.className = "tarjeta";

    // Detectar si es bioinspirado (basado en parámetros genéticos)
    if (item.Prob_mutar_gen > 0 || item.probabilidad_cruce > 0 || item.cantidad_toreno > 0 || item.Hall_Fama > 0) {
        tarjeta.classList.add('bioinspirado');
    } else {
        tarjeta.classList.add('normal');
    }

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

    // Propiedades de ejecución (solo las visibles) - Usando tabla como en Opción 3
    const divPropiedadesEjecucion = document.createElement("div");
    divPropiedadesEjecucion.className = "propiedades-ejecucion";

    let propiedadesHTML = '<table class="prop-table">';
    window.parametrosVisibles.forEach(param => {
        if (item.hasOwnProperty(param)) {
            const nombreFormateado = param.replace(/_/g, ' ')
                                         .replace(/\b\w/g, l => l.toUpperCase());
            
            let valor = item[param];
            
            // Formatear valores específicos
            if (param === 'error_total' && typeof valor === 'string') {
                valor = parseFloat(valor) || valor;
            }
            
            propiedadesHTML += `<tr><td>${nombreFormateado}:</td><td>${valor}</td></tr>`;
        }
    });
    propiedadesHTML += '</table>';

    divPropiedadesEjecucion.innerHTML = propiedadesHTML;

    // Comportamiento de click para imágenes verbose
    if (item.verbose && item.verbose !== "False") {
        const imagenes = [
            { src: item.ruta_resultado, nombre: "resultado" },
            { src: item.ruta_imagen_preprocesada, nombre: "Preprocesada" },
            { src: item.ruta_imagen_error_preresolutor, nombre: "Error pre-resolución" },
            { src: item.ruta_imagen_error_post_resolutor, nombre: "Error post-resolución" }
        ].filter(obj => obj.src && obj.src !== ""); // Filtra rutas vacías
        
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

    // Inicializar parámetros visibles
    actualizarParametrosVisibles();

    // Actualizar al cambiar cualquier checkbox
    checkboxes.forEach(checkbox => {
        checkbox.addEventListener('change', () => {
            actualizarParametrosVisibles();
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

    // Siempre trabajamos con los datos originales para filtros
    let datosFiltrados = [...window.datosOriginales];

    // Aplicar ordenamiento
    if (orden) {
        datosFiltrados.sort((a, b) => {
            let valorA = a[orden];
            let valorB = b[orden];
            
            // Convertir a número si es posible para ordenamiento correcto
            if (orden === 'error_total') {
                valorA = parseFloat(valorA) || 0;
                valorB = parseFloat(valorB) || 0;
                return valorA - valorB;
            }
            if (orden === 'tiempo_ejecucion') {
                valorA = parseFloat(valorA) || 0;
                valorB = parseFloat(valorB) || 0;
                return valorA - valorB;
            }
            if (orden === 'lineas_usadas') {
                valorA = parseInt(valorA) || 0;
                valorB = parseInt(valorB) || 0;
                return valorA - valorB;
            }
            if (orden === 'numero_de_pines') {
                valorA = parseInt(valorA) || 0;
                valorB = parseInt(valorB) || 0;
                return valorA - valorB;
            }
            
            // Ordenamiento por string para otros campos
            return String(valorA).localeCompare(String(valorB));
        });
    }

    // Actualizar datos de ejecución (sin perder los originales)
    window.ejecucionesData = datosFiltrados;

    // Limpiar contenedores
    document.querySelector(".contenedor-ejecuciones").innerHTML = "";
    document.querySelector(".contenedor-imagen").innerHTML = "";

    // Reiniciar paginación
    window.paginaActual = 0;

    // Aplicar agrupamiento
    if (grupo) {
        agruparYMostrar(datosFiltrados, grupo);
    } else {
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
        const claveNormalizada = String(clave || 'Sin valor'); // Manejar valores undefined/null
        
        if (!grupos[claveNormalizada]) grupos[claveNormalizada] = [];
        grupos[claveNormalizada].push(item);
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
 * Normaliza los datos cargados del JSON
 */
function normalizarDatos(data) {
    return data.map(item => {
        // Asegurar que las rutas de imágenes de error estén correctamente mapeadas
        const itemNormalizado = { ...item };
        
        // Corregir posibles inconsistencias en las rutas
        if (!itemNormalizado.ruta_imagen_error_post_resolutor && itemNormalizado.ruta_imagen_post_resolutor) {
            itemNormalizado.ruta_imagen_error_post_resolutor = itemNormalizado.ruta_imagen_post_resolutor;
        }
        
        // Convertir strings a booleanos para verbose
        if (typeof itemNormalizado.verbose === 'string') {
            itemNormalizado.verbose = itemNormalizado.verbose === 'True' || itemNormalizado.verbose === 'true';
        }
        
        // Convertir números almacenados como strings
        if (typeof itemNormalizado.error_total === 'string') {
            itemNormalizado.error_total = parseFloat(itemNormalizado.error_total) || itemNormalizado.error_total;
        }
        if (typeof itemNormalizado.tiempo_ejecucion === 'string') {
            itemNormalizado.tiempo_ejecucion = parseFloat(itemNormalizado.tiempo_ejecucion) || itemNormalizado.tiempo_ejecucion;
        }
        if (typeof itemNormalizado.lineas_usadas === 'string') {
            itemNormalizado.lineas_usadas = parseInt(itemNormalizado.lineas_usadas) || itemNormalizado.lineas_usadas;
        }
        
        // Normalizar valores booleanos
        ['pasar_a_grises', 'mascara_circular', 'marcar_bordes'].forEach(param => {
            if (typeof itemNormalizado[param] === 'string') {
                itemNormalizado[param] = itemNormalizado[param] === 'True';
            }
        });
        
        return itemNormalizado;
    });
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
        
        // Normalizar y guardar datos
        const datosNormalizados = normalizarDatos(data);
        window.datosOriginales = datosNormalizados;
        window.ejecucionesData = [...datosNormalizados]; // Copia para trabajar
        
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