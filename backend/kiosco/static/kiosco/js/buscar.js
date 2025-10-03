function cerrarModal() {
    const modal = document.getElementById("modal");
    if (!modal) return;

    modal.classList.remove("show");

    setTimeout(() => {
        modal.classList.remove("visible");

        const input = document.getElementById("id");
        if (input) {
            input.focus();
        }
    }, 300);
}

function activarListenersModal(modal) {
    if (!modal) return;

    // Tecla Escape
    document.addEventListener("keydown", function onKeyDown(e) {
        if (!document.getElementById("modal")) {
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

function mostrarErrorCampo(nombreCampo) {
    const grupo = document.getElementById(nombreCampo)?.closest(".input-group");
    if (!grupo) return;

    grupo.classList.add("error");
}

function limpiarErrores() {
    // Quita clases e íconos de error
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

function abrirVistaPrevia(tipo, id) {
    const url = `/pdf/${tipo}/${id}/?abrir=1`;
    window.open(url, "_blank");
}

document.addEventListener("DOMContentLoaded", function () {
    const anterior = document.getElementById("modal");
    if (anterior) anterior.remove();

    const form = document.getElementById("buscar-form");
    console.log(window.FormConfig);

    const idRequired = window.FormConfig?.idRequired ?? false;
    const dateRequired = window.FormConfig?.dateRequired ?? false;
    const autoBorrado = window.FormConfig?.autoBorrado ?? false;

    form.addEventListener("submit", async function (e) {
        e.preventDefault();

        const processingMessage = document.getElementById("processing-message");
        if (processingMessage) {
            processingMessage.classList.add("visible");
            processingMessage.setAttribute("aria-hidden", "false");
        }

        limpiarErrores();

        const idInput = document.getElementById("id");
        const fechaInput = document.getElementById("fecha");

        const id = idInput?.value.trim() ?? "";
        const fecha = fechaInput?.value.trim() ?? "";

        if (idRequired && !id) {
            if (processingMessage) {
                processingMessage.classList.remove("visible");
                processingMessage.setAttribute("aria-hidden", "false");
            }
            mostrarErrorCampo("id");
            if (idInput) {
                idInput.focus();
                idInput.select();
            }
            return;
        }
        if (dateRequired && !fecha) {
            if (processingMessage) {
                processingMessage.classList.remove("visible");
                processingMessage.setAttribute("aria-hidden", "false");
            }
            mostrarErrorCampo("fecha");
            if (fechaInput) {
                fechaInput.focus();
                fechaInput.select();
            }
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
                body: new URLSearchParams({id, fecha}),
            });

            const html = await response.text();

            // Extrae el modal desde la respuesta y lo inserta
            const parser = new DOMParser();
            const doc = parser.parseFromString(html, "text/html");
            const nuevoModal = doc.getElementById("modal");

            // Elimina modal viejo
            const modalViejo = document.getElementById("modal");
            if (modalViejo) modalViejo.remove();

            if (nuevoModal) {
                document.body.appendChild(nuevoModal);
                setTimeout(() => {
                    nuevoModal.classList.add("show");
                    nuevoModal.focus();
                    if (autoBorrado) {
                        idInput.value = "";
                        fechaInput.value = "";
                    }
                }, 20);

                activarListenersModal(nuevoModal);
                activarEnvioWhatsApp(nuevoModal);
            } else {
                const container = document.querySelector(".container");
                const error = doc.querySelector(".error-message");
                if (error) {
                    container.querySelector(".error-message")?.remove(); // Elimina error anterior
                    container.insertAdjacentElement("beforeend", error);

                    const target = error.getAttribute("data-error-target") || "id";
                    mostrarErrorCampo(target);

                    const input = document.getElementById(target);
                    if (input) {
                        input.focus();
                        input.select();
                    }
                }
                if (idInput) {
                    idInput.focus();
                    idInput.select();
                }
            }
        } catch (error) {
            console.error("Error al buscar:", error);
            if (idInput) {
                idInput.focus();
                idInput.select();
            }
        } finally {
            if (processingMessage) {
                processingMessage.classList.remove("visible");
                processingMessage.setAttribute("aria-hidden", "true");
            }
        }
    });

    // Si en la carga inicial ya hay modal, activa listeners ahí
    const modalInicial = document.getElementById("modal");
    if (modalInicial) {
        activarListenersModal(modalInicial);

        setTimeout(() => {
            modalInicial.classList.add("show");
            modalInicial.focus();
        }, 20);
    }
});
