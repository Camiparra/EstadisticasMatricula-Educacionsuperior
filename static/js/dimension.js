// Menú lateral de las páginas de dimensión (templates/partials/menu_lateral.html):
// - resalta la sección que se está leyendo,
// - muestra una barra con el avance de lectura,
// - en celulares cierra el panel al elegir una sección.
(function () {
    var enlaces = Array.prototype.slice.call(document.querySelectorAll("#lista-secciones .enlace-seccion"));
    var barra = document.getElementById("progreso-dimension");
    var contenido = document.querySelector(".contenido-dimension");
    if (!enlaces.length || !contenido) {
        return;
    }

    var secciones = enlaces.map(function (enlace) {
        return document.querySelector(enlace.getAttribute("href"));
    });

    function activar(indice) {
        enlaces.forEach(function (enlace, i) {
            var activa = i === indice;
            enlace.classList.toggle("activa", activa);
            if (activa) {
                enlace.setAttribute("aria-current", "location");
            } else {
                enlace.removeAttribute("aria-current");
            }
        });
    }

    // La sección activa es la última cuyo inicio ya pasó la parte superior
    // de la ventana (debajo del menú fijo).
    var pendiente = false;
    function actualizar() {
        pendiente = false;
        var limite = window.innerHeight * 0.3;
        var indice = 0;
        secciones.forEach(function (seccion, i) {
            if (seccion && seccion.getBoundingClientRect().top <= limite) { indice = i; }
        });

        // Al llegar al final de la página, marcar la última sección.
        var alFinal = window.innerHeight + window.scrollY >= document.documentElement.scrollHeight - 4;
        activar(alFinal ? secciones.length - 1 : indice);

        if (barra) {
            var caja = contenido.getBoundingClientRect();
            var recorrido = caja.height - window.innerHeight;
            var avance = recorrido > 0 ? (-caja.top / recorrido) * 100 : 100;
            barra.style.width = Math.min(100, Math.max(0, avance)) + "%";
        }
    }

    window.addEventListener("scroll", function () {
        if (!pendiente) {
            pendiente = true;
            window.requestAnimationFrame(actualizar);
        }
    }, { passive: true });
    window.addEventListener("resize", actualizar);

    // En pantallas pequeñas el menú es un panel deslizable: cerrarlo al navegar.
    var panel = document.getElementById("menu-lateral");
    enlaces.forEach(function (enlace) {
        enlace.addEventListener("click", function () {
            var instancia = window.bootstrap && bootstrap.Offcanvas.getInstance(panel);
            if (instancia) { instancia.hide(); }
        });
    });

    actualizar();
})();
