function cerrarModal(id = "modal") {
    const modal = document.getElementById(id);
    if (!modal) return;

    modal.classList.remove("show");
    setTimeout(() => {
        modal.classList.remove("visible");
        const input = document.getElementById("id");
        input?.focus();
    }, 300);
}

function activarListenersModal(modal) {
    if (!modal) return;

    const onKeyDown = (e) => {
        if (!document.body.contains(modal)) {
            document.removeEventListener("keydown", onKeyDown);
            return;
        }

        if (e.key === "Escape") {
            cerrarModal(modal.id);
        }

        if (e.key === "Tab") {
            const focusables = modal.querySelectorAll(
                'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
            );
            if (focusables.length === 0) return;

            const first = focusables[0];
            const last = focusables[focusables.length - 1];

            if (e.shiftKey && document.activeElement === first) {
                e.preventDefault();
                last.focus();
            } else if (document.activeElement === last) {
                e.preventDefault();
                first.focus();
            }
        }
    };

    document.addEventListener("keydown", onKeyDown);

    modal.addEventListener("click", (event) => {
        if (event.target === modal) {
            cerrarModal(modal.id);
        }
    });
}

function mostrarErrorCampo(nombreCampo) {
    document.querySelector(`#${nombreCampo}`)?.closest(".input-group")?.classList.add("error");
}

function limpiarErrores() {
    document.querySelectorAll(".input-group").forEach(group => {
        group.classList.remove("error");
        group.querySelector(".icon-error")?.remove();
    });

    document.querySelector(".container .error-message")?.remove();
}

function toggleMensajeProcesando(visible) {
    const processingMessage = document.getElementById("processing-message");
    if (!processingMessage) return;

    processingMessage.classList.toggle("visible", visible);
    processingMessage.setAttribute("aria-hidden", visible ? "false" : "true");
}

function focusYSeleccionarInput(id) {
    const input = document.getElementById(id);
    if (input) {
        input.focus();
        input.select();
    }
}

function abrirVistaPrevia() {
    window.open(`/preview/pdf/?abrir=1`, "_blank");
}

function mostrarFormularioEmail() {
    const form = document.getElementById("send-email-pdf-form");
    form.style.display = "block";
    form.scrollIntoView({behavior: "smooth"});
}

document.addEventListener("DOMContentLoaded", () => {
    document.getElementById("modal")?.remove(); // limpia modal anterior

    const form = document.getElementById("buscar-form");

    const {
        idRequired = false,
        idPreserve = false,
        dateRequired = false,
        datePreserve = false
    } = window.FormConfig || {};

    form.addEventListener("submit", async (e) => {
        e.preventDefault();
        toggleMensajeProcesando(true);
        limpiarErrores();

        const idInput = document.getElementById("id");
        const fechaInput = document.getElementById("fecha");

        const id = idInput?.value.trim() ?? "";
        const fecha = fechaInput?.value.trim() ?? "";

        const validarCampo = (campo, valor) => {
            if (!valor) {
                toggleMensajeProcesando(false);
                mostrarErrorCampo(campo);
                focusYSeleccionarInput(campo);
                return false;
            }
            return true;
        };

        if (idRequired && !validarCampo("id", id)) return;
        if (dateRequired && !validarCampo("fecha", fecha)) return;

        const csrfToken = document.querySelector("[name=csrfmiddlewaretoken]")?.value;

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
            const doc = new DOMParser().parseFromString(html, "text/html");
            const nuevoModal = doc.getElementById("modal");

            document.getElementById("modal")?.remove(); // elimina viejo modal

            if (nuevoModal) {
                document.body.appendChild(nuevoModal);
                setTimeout(() => {
                    nuevoModal.classList.add("show");
                    nuevoModal.focus();
                    if (!idPreserve) idInput.value = "";
                    if (!datePreserve) fechaInput.value = "";
                }, 20);

                activarListenersModal(nuevoModal);
                activarEnvioWhatsApp(nuevoModal);
            } else {
                const error = doc.querySelector(".error-message");
                if (error) {
                    const container = document.querySelector(".container");
                    container.querySelector(".error-message")?.remove();
                    container.insertAdjacentElement("beforeend", error);

                    const target = error.getAttribute("data-error-target") || "id";
                    mostrarErrorCampo(target);
                    focusYSeleccionarInput(target);
                } else {
                    focusYSeleccionarInput("id");
                }
            }
        } catch (error) {
            console.error("Error al buscar:", error);
            focusYSeleccionarInput("id");
        } finally {
            toggleMensajeProcesando(false);
        }
    });

    const modalInicial = document.getElementById("modal");
    if (modalInicial) {
        activarListenersModal(modalInicial);
        setTimeout(() => {
            modalInicial.classList.add("show");
            modalInicial.focus();
        }, 20);
    }
});
