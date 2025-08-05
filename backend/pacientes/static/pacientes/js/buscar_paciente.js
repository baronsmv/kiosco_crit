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
    const anterior = document.getElementById("modal-paciente");
    if (anterior) anterior.remove();

    const form = document.getElementById("buscar-form");
    const modal = document.getElementById("modal-paciente");

    form.addEventListener("submit", async function (e) {
        e.preventDefault();

        const carnetInput = document.getElementById("carnet");
        const carnet = carnetInput.value.trim();
        if (!carnet) return;

        const csrfToken = document.querySelector("[name=csrfmiddlewaretoken]").value;

        try {
            const response = await fetch("", {
                method: "POST",
                headers: {
                    "X-CSRFToken": csrfToken,
                    "X-Requested-With": "XMLHttpRequest",
                    "Content-Type": "application/x-www-form-urlencoded",
                },
                body: new URLSearchParams({carnet}),
            });

            const html = await response.text();

            // Extrae el modal desde la respuesta y lo inserta
            const parser = new DOMParser();
            const doc = parser.parseFromString(html, "text/html");
            const modal = doc.getElementById("modal-paciente");

            if (modal) {
                document.body.appendChild(modal);
                setTimeout(() => {
                    modal.classList.add("show");
                    modal.focus();
                }, 20);
            } else {
                // Si no hay paciente, muestra el mensaje de error
                const container = document.querySelector(".container");
                const error = doc.querySelector(".error-message");
                if (error) {
                    container.querySelector(".error-message")?.remove(); // Elimina error anterior
                    container.insertAdjacentElement("beforeend", error);
                    mostrarErrorCampo("carnet");
                }
            }
        } catch (error) {
            console.error("Error al buscar paciente:", error);
        }
    });

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
