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

function activarListenersModal(modal) {
    if (!modal) return;

    // Tecla Escape
    document.addEventListener("keydown", function onKeyDown(e) {
        if (!document.getElementById("modal-paciente")) {
            // Si modal ya no está en DOM, quita listener para evitar fugas
            document.removeEventListener("keydown", onKeyDown);
            return;
        }

        if (e.key === "Escape") {
            cerrarModal();
        }

        // Loop de Tab
        if (e.key === "Tab") {
            const focusables = modal.querySelectorAll(
                'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
            );
            if (focusables.length === 0) return;

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
    modal.addEventListener("click", function (event) {
        if (event.target === modal) {
            cerrarModal();
        }
    });
}

function limpiarErrores() {
    // Quita clases y íconos de error
    document.querySelectorAll(".input-group").forEach(group => {
        group.classList.remove("error");
        const existingIcon = group.querySelector(".icon-error");
        if (existingIcon) existingIcon.remove();
    });

    // Quita mensajes de error visibles en el DOM
    const container = document.querySelector(".container");
    const error = container.querySelector(".error-message");
    if (error) {
        error.remove();
    }
}

document.addEventListener("DOMContentLoaded", function () {
    const anterior = document.getElementById("modal-paciente");
    if (anterior) anterior.remove();

    const form = document.getElementById("buscar-form");

    form.addEventListener("submit", async function (e) {
        e.preventDefault();

        limpiarErrores();

        const carnetInput = document.getElementById("carnet");
        const carnet = carnetInput.value.trim();
        if (!carnet) {
            carnetInput.focus();
            return;
        }

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
            const nuevoModal = doc.getElementById("modal-paciente");

            // Elimina modal viejo
            const modalViejo = document.getElementById("modal-paciente");
            if (modalViejo) modalViejo.remove();

            if (nuevoModal) {
                document.body.appendChild(nuevoModal);
                setTimeout(() => {
                    nuevoModal.classList.add("show");
                    nuevoModal.focus();
                    carnetInput.value = "";
                }, 20);

                activarListenersModal(nuevoModal);
            } else {
                // Si no hay paciente, muestra el mensaje de error
                const container = document.querySelector(".container");
                const error = doc.querySelector(".error-message");
                if (error) {
                    container.querySelector(".error-message")?.remove(); // Elimina error anterior
                    container.insertAdjacentElement("beforeend", error);
                    mostrarErrorCampo("carnet");
                }
                carnetInput.focus();
            }
        } catch (error) {
            console.error("Error al buscar paciente:", error);
            carnetInput.focus();
        }
    });

    // Si en la carga inicial ya hay modal, activa listeners ahí
    const modalInicial = document.getElementById("modal-paciente");
    if (modalInicial) {
        activarListenersModal(modalInicial);

        setTimeout(() => {
            modalInicial.classList.add("show");
            modalInicial.focus();
        }, 20);
    }
});
