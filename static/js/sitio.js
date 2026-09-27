// Comportamientos generales de todas las páginas:
// - sombra en el menú al desplazarse,
// - aparición de elementos .aparecer al entrar en pantalla,
// - contadores animados [data-contador].
(function () {
    var raiz = document.documentElement;

    function sinMovimiento() {
        return raiz.classList.contains("a11y-sin-movimiento") ||
            window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    }

    // Menú principal con sombra cuando la página no está arriba.
    var menu = document.querySelector(".barra-principal");
    if (menu) {
        var marcarMenu = function () {
            menu.classList.toggle("desplazada", window.scrollY > 8);
        };
        window.addEventListener("scroll", marcarMenu, { passive: true });
        marcarMenu();
    }

    // Contadores: animan de 0 al valor final, con formato colombiano (2.448.271).
    var formato = new Intl.NumberFormat("es-CO");

    function animarContador(elemento) {
        var final = Number(elemento.dataset.contador);
        if (!isFinite(final) || sinMovimiento()) {
            return;
        }
        var duracion = 1400;
        var inicio = null;

        function paso(tiempo) {
            if (inicio === null) { inicio = tiempo; }
            var t = Math.min(1, (tiempo - inicio) / duracion);
            var suavizado = 1 - Math.pow(1 - t, 3);
            elemento.textContent = formato.format(Math.round(final * suavizado));
            if (t < 1) { window.requestAnimationFrame(paso); }
        }
        window.requestAnimationFrame(paso);
    }

    var elementos = document.querySelectorAll(".aparecer, [data-contador]");

    if (!("IntersectionObserver" in window)) {
        elementos.forEach(function (el) { el.classList.add("visible"); });
        return;
    }

    var observador = new IntersectionObserver(function (entradas) {
        entradas.forEach(function (entrada) {
            if (!entrada.isIntersecting) { return; }
            var el = entrada.target;
            el.classList.add("visible");
            if (el.dataset.contador) { animarContador(el); }
            observador.unobserve(el);
        });
    }, { rootMargin: "0px 0px -8% 0px", threshold: 0.1 });

    elementos.forEach(function (el) { observador.observe(el); });
})();
