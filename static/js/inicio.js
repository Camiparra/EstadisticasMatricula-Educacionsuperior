// Mini gráfica de la matrícula nacional por año en la portada del inicio.
// Los datos llegan desde Flask en el atributo data-serie. Se dibuja en SVG,
// con guía vertical y tooltip al pasar el cursor o al usar las flechas del
// teclado. La tabla con los mismos valores está debajo ("Ver los datos").
(function () {
    var contenedor = document.getElementById("serie-nacional");
    if (!contenedor) {
        return;
    }

    var serie = JSON.parse(contenedor.dataset.serie);
    var formato = new Intl.NumberFormat("es-CO");
    var SVG = "http://www.w3.org/2000/svg";
    var MARGEN = 6;
    var yaAnimada = false;
    var seleccion = null;
    var puntos = [];
    var guia, marcador, tooltip;

    function crear(etiqueta, atributos) {
        var el = document.createElementNS(SVG, etiqueta);
        Object.keys(atributos).forEach(function (k) { el.setAttribute(k, atributos[k]); });
        return el;
    }

    function sinMovimiento() {
        return document.documentElement.classList.contains("a11y-sin-movimiento") ||
            window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    }

    function dibujar() {
        var ancho = contenedor.clientWidth;
        var alto = contenedor.clientHeight;
        var maximo = Math.max.apply(null, serie.map(function (p) { return p.matricula; }));

        // Eje Y desde cero para no exagerar el crecimiento.
        puntos = serie.map(function (p, i) {
            return {
                x: MARGEN + (i / (serie.length - 1)) * (ancho - MARGEN * 2),
                y: MARGEN + (1 - p.matricula / maximo) * (alto - MARGEN * 2),
                anio: p.anio,
                valor: p.matricula
            };
        });

        var trazo = puntos.map(function (p, i) { return (i ? "L" : "M") + p.x.toFixed(1) + " " + p.y.toFixed(1); }).join(" ");
        var ultimo = puntos[puntos.length - 1];
        var area = trazo + " L" + ultimo.x + " " + alto + " L" + puntos[0].x + " " + alto + " Z";

        var svg = crear("svg", { viewBox: "0 0 " + ancho + " " + alto, "aria-hidden": "true", focusable: "false" });
        svg.appendChild(crear("path", { d: area, "class": "area" }));
        var linea = crear("path", { d: trazo, "class": "linea" });
        svg.appendChild(linea);
        svg.appendChild(crear("circle", { cx: ultimo.x, cy: ultimo.y, r: 4, "class": "punto" }));

        guia = crear("line", { y1: 0, y2: alto, "class": "guia", visibility: "hidden" });
        marcador = crear("circle", { r: 5, "class": "punto", visibility: "hidden" });
        svg.appendChild(guia);
        svg.appendChild(marcador);

        contenedor.replaceChildren(svg);
        tooltip = document.createElement("div");
        tooltip.className = "sparkline-tooltip";
        tooltip.hidden = true;
        contenedor.appendChild(tooltip);

        if (!yaAnimada && !sinMovimiento()) {
            linea.style.setProperty("--largo", linea.getTotalLength());
            linea.classList.add("dibujar");
        }
        yaAnimada = true;
    }

    function mostrar(indice) {
        seleccion = indice;
        var p = puntos[indice];
        guia.setAttribute("x1", p.x);
        guia.setAttribute("x2", p.x);
        guia.setAttribute("visibility", "visible");
        marcador.setAttribute("cx", p.x);
        marcador.setAttribute("cy", p.y);
        marcador.setAttribute("visibility", "visible");

        var valor = document.createElement("strong");
        valor.textContent = formato.format(p.valor);
        var anio = document.createElement("span");
        anio.textContent = "Matrícula " + p.anio;
        tooltip.replaceChildren(valor, anio);
        tooltip.hidden = false;

        // Mantener el tooltip dentro de la tarjeta.
        var mitad = tooltip.offsetWidth / 2;
        var x = Math.min(Math.max(p.x, mitad), contenedor.clientWidth - mitad);
        tooltip.style.left = x + "px";
    }

    function ocultar() {
        seleccion = null;
        guia.setAttribute("visibility", "hidden");
        marcador.setAttribute("visibility", "hidden");
        tooltip.hidden = true;
    }

    function masCercano(clientX) {
        var x = clientX - contenedor.getBoundingClientRect().left;
        var mejor = 0;
        puntos.forEach(function (p, i) {
            if (Math.abs(p.x - x) < Math.abs(puntos[mejor].x - x)) { mejor = i; }
        });
        return mejor;
    }

    contenedor.tabIndex = 0;
    contenedor.addEventListener("pointermove", function (e) { mostrar(masCercano(e.clientX)); });
    contenedor.addEventListener("pointerleave", ocultar);
    contenedor.addEventListener("blur", ocultar);
    contenedor.addEventListener("keydown", function (e) {
        var ultimo = puntos.length - 1;
        var actual = seleccion === null ? ultimo : seleccion;
        var nuevo = null;
        if (e.key === "ArrowLeft") { nuevo = Math.max(0, actual - 1); }
        if (e.key === "ArrowRight") { nuevo = Math.min(ultimo, actual + 1); }
        if (e.key === "Home") { nuevo = 0; }
        if (e.key === "End") { nuevo = ultimo; }
        if (e.key === "Escape") { ocultar(); }
        if (nuevo !== null) {
            e.preventDefault();
            mostrar(nuevo);
        }
    });

    // Se dibuja cuando la página terminó de cargar (el CSS del tema llega por
    // JavaScript y los scripts no lo esperan, así que antes el tamaño del
    // contenedor puede ser incorrecto) y cada vez que cambia su ancho.
    function iniciar() {
        var anchoPrevio = 0;
        new ResizeObserver(function () {
            if (contenedor.clientWidth !== anchoPrevio) {
                anchoPrevio = contenedor.clientWidth;
                dibujar();
            }
        }).observe(contenedor);
    }

    if (document.readyState === "complete") {
        iniciar();
    } else {
        window.addEventListener("load", iniciar);
    }
})();
