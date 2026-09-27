// Panel de accesibilidad (templates/partials/accesibilidad.html).
// Guarda las preferencias en localStorage y las aplica como clases a11y-* en
// <html>. El script del <head> de base.html las aplica al cargar cada página
// para que no haya parpadeo; este archivo solo maneja los controles del panel.
(function () {
    var raiz = document.documentElement;
    var CLAVE = "accesibilidad";
    var ESCALA_MIN = 80;
    var ESCALA_MAX = 150;
    var PASO = 10;

    var panel = document.getElementById("panel-accesibilidad");
    if (!panel) {
        return;
    }

    var interruptores = panel.querySelectorAll("[data-a11y-opcion]");
    var valorEscala = document.getElementById("valor-escala");

    function leer() {
        try { return JSON.parse(localStorage.getItem(CLAVE)) || {}; } catch (e) { return {}; }
    }

    function guardar(preferencias) {
        try { localStorage.setItem(CLAVE, JSON.stringify(preferencias)); } catch (e) {}
    }

    function aplicar(preferencias) {
        var escala = preferencias.escala || 100;
        raiz.style.fontSize = escala === 100 ? "" : escala + "%";
        valorEscala.textContent = escala + " %";

        interruptores.forEach(function (interruptor) {
            var opcion = interruptor.dataset.a11yOpcion;
            var activa = Boolean(preferencias[opcion]);
            interruptor.checked = activa;
            raiz.classList.toggle("a11y-" + opcion, activa);
        });
    }

    var preferencias = leer();
    aplicar(preferencias);

    interruptores.forEach(function (interruptor) {
        interruptor.addEventListener("change", function () {
            preferencias[interruptor.dataset.a11yOpcion] = interruptor.checked;
            guardar(preferencias);
            aplicar(preferencias);
        });
    });

    panel.querySelectorAll("[data-a11y-escala]").forEach(function (boton) {
        boton.addEventListener("click", function () {
            var cambio = Number(boton.dataset.a11yEscala) * PASO;
            var escala = (preferencias.escala || 100) + cambio;
            preferencias.escala = Math.min(ESCALA_MAX, Math.max(ESCALA_MIN, escala));
            guardar(preferencias);
            aplicar(preferencias);
        });
    });

    panel.querySelector("[data-a11y-restablecer]").addEventListener("click", function () {
        preferencias = {};
        guardar(preferencias);
        aplicar(preferencias);
    });

    // "Saltar al contenido": mover también el foco del teclado, no solo el scroll.
    var saltar = document.querySelector(".saltar-contenido");
    var contenido = document.getElementById("contenido");
    if (saltar && contenido) {
        saltar.addEventListener("click", function (evento) {
            evento.preventDefault();
            contenido.focus({ preventScroll: true });
            contenido.scrollIntoView();
        });
    }
})();
