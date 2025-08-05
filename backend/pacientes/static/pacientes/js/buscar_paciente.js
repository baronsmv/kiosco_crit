function cerrarModal() {
    const modal = document.getElementById("modal-paciente");
    if (!modal) return;

    modal.classList.remove("show");

    setTimeout(() => {
        modal.classList.remove("visible");

        const input = document.getElementById("carnet");
        if (input) {
            input.focus();
        }
    }, 300);
}

document.addEventListener("DOMContentLoaded", function () {
    const modal = document.getElementById("modal-paciente");

    if (modal && modal.classList.contains("visible")) {
        // Fuerza el reflow y luego aplica 'show' para activar transición
        setTimeout(() => {
            modal.classList.add("show");
            modal.focus();
        }, 20); // Delay pequeño para permitir pintar el estado inicial
    }

    if (modal && modal.classList.contains("show")) {
        // Dale foco al modal
        modal.focus();

        // Tecla Escape
        document.addEventListener("keydown", function (e) {
            if (e.key === "Escape") {
                cerrarModal();
            }

            // Loop de Tab
            if (e.key === "Tab") {
                const focusables = modal.querySelectorAll(
                    'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
                );
                const first = focusables[0];
                const last = focusables[focusables.length - 1];

                if (e.shiftKey) {
                    if (document.activeElement === first) {
                        e.preventDefault();
                        last.focus();
                    }
                } else {
                    if (document.activeElement === last) {
                        e.preventDefault();
                        first.focus();
                    }
                }
            }
        });

        // Cerrar al hacer clic fuera del contenido
        window.addEventListener("click", function (event) {
            if (event.target === modal) {
                cerrarModal();
            }
        });
    }
});
