// Botón "volver arriba" (templates/partials/volver_arriba.html).
// Aparece tras bajar un poco, su anillo muestra el avance de lectura y al
// pulsarlo lleva al inicio y pasa el foco al contenido principal.
(function () {
    var boton = document.getElementById("volver-arriba");
    var contenido = document.getElementById("contenido");
    if (!boton) {
        return;
    }

    var UMBRAL = 400;
    var pendiente = false;

    function actualizar() {
        pendiente = false;
        var desplazado = window.scrollY;
        var recorrido = document.documentElement.scrollHeight - window.innerHeight;
        var avance = recorrido > 0 ? Math.min(100, (desplazado / recorrido) * 100) : 0;

        boton.classList.toggle("visible", desplazado > UMBRAL);
        boton.style.setProperty("--avance", avance.toFixed(1));
    }

    window.addEventListener("scroll", function () {
        if (!pendiente) {
            pendiente = true;
            window.requestAnimationFrame(actualizar);
        }
    }, { passive: true });

    boton.addEventListener("click", function () {
        window.scrollTo({ top: 0 });
        if (contenido) {
            contenido.focus({ preventScroll: true });
        }
    });

    actualizar();
})();
