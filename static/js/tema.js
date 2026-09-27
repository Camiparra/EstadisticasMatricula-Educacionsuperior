// Cambio entre modo claro (Bootswatch Flatly) y oscuro (Bootswatch Darkly).
// El tema inicial lo fija el script del <head> en base.html; este archivo solo
// maneja el botón del menú y los cambios de preferencia del sistema.
(function () {
    var raiz = document.documentElement;
    var enlace = document.getElementById("tema-bootswatch");
    var boton = document.getElementById("boton-tema");
    var consultaOscuro = window.matchMedia("(prefers-color-scheme: dark)");

    if (!enlace || !boton) {
        return;
    }

    function aplicarTema(tema) {
        enlace.href = tema === "oscuro" ? raiz.dataset.temaOscuro : raiz.dataset.temaClaro;
        raiz.dataset.tema = tema;

        // El botón muestra el modo al que se va a cambiar.
        var siguiente = tema === "oscuro" ? "claro" : "oscuro";
        var texto = "Cambiar a modo " + siguiente;
        boton.innerHTML = '<i class="bi ' + (tema === "oscuro" ? "bi-sun-fill" : "bi-moon-stars-fill") + '" aria-hidden="true"></i>';
        boton.setAttribute("aria-label", texto);
        boton.title = texto;
    }

    function temaGuardado() {
        try { return localStorage.getItem("tema"); } catch (e) { return null; }
    }

    boton.addEventListener("click", function () {
        var nuevo = raiz.dataset.tema === "oscuro" ? "claro" : "oscuro";
        try { localStorage.setItem("tema", nuevo); } catch (e) {}
        aplicarTema(nuevo);
    });

    // Si el usuario nunca eligió un tema, seguir los cambios del sistema operativo.
    consultaOscuro.addEventListener("change", function (evento) {
        if (!temaGuardado()) {
            aplicarTema(evento.matches ? "oscuro" : "claro");
        }
    });

    aplicarTema(raiz.dataset.tema || "claro");
})();
