function abrirModal(id) {
    const modal = document.getElementById(id);
    if (!modal) return;

    modal.classList.add("visible");
    setTimeout(() => {
        modal.classList.add("show");
        modal.focus();
    }, 20);

    activarListenersModal(modal);
}

function cerrarModal(id = "modal", focusTarget = null) {
    const modal = document.getElementById(id);
    if (!modal) return;

    modal.classList.remove("show");
    setTimeout(() => {
        modal.classList.remove("visible");
        modal.dispatchEvent(new CustomEvent("modalClosed"));
        if (focusTarget) {
            const input = document.getElementById(focusTarget);
            input?.focus();
        }
    }, 300);
}

function activarListenersModal(modal) {
    if (!modal) return;

    const onKeyDown = (e) => {
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

    const onClose = () => {
        document.removeEventListener("keydown", onKeyDown);
        modal.removeEventListener("modalClosed", onClose);
    };
    modal.addEventListener("modalClosed", onClose);

    modal.addEventListener("click", (event) => {
        if (event.target === modal) {
            cerrarModal(modal.id);
        }
    });
}

function getCSRFToken() {
    const name = "csrftoken=";
    const decodedCookie = decodeURIComponent(document.cookie);
    const cookies = decodedCookie.split(";");

    for (let c of cookies) {
        c = c.trim();
        if (c.startsWith(name)) {
            return c.substring(name.length, c.length);
        }
    }
    return null;
}

function activarEnvioAjax(element) {
    const forms = element.querySelectorAll("form[data-ajax='true']");
    if (!forms.length) return;

    forms.forEach(form => {
        // Evitar múltiples listeners
        if (form.dataset.ajaxBound === "true") return;

        form.dataset.ajaxBound = "true"; // Marcar como enlazado
        console.log("Bound AJAX handler to", form.id);

        form.addEventListener("submit", async (e) => {
            e.preventDefault();
            limpiarErrores();
            toggleMensajeProcesando(true);

            const formData = new FormData(form);
            if (e.submitter && e.submitter.name) {
                formData.append(e.submitter.name, e.submitter.value);
            }

            const csrfToken = form.querySelector("[name='csrfmiddlewaretoken']")?.value;

            try {
                const response = await fetch(form.action || "", {
                    method: "POST",
                    headers: {
                        "X-CSRFToken": csrfToken,
                        "X-Requested-With": "XMLHttpRequest",
                    },
                    body: formData,
                });

                const html = await response.text();
                const doc = new DOMParser().parseFromString(html, "text/html");

                // Si hay un nuevo modal en la respuesta
                const nuevoModal = doc.getElementById("modal");
                if (nuevoModal) {
                    document.getElementById("modal")?.remove();
                    document.body.appendChild(nuevoModal);

                    setTimeout(() => {
                        nuevoModal.classList.add("show");
                        nuevoModal.focus();
                    }, 20);

                    activarListenersModal(nuevoModal);
                    activarEnvioAjax(nuevoModal);
                    // activarEnvioWhatsApp(nuevoModal);
                    toggleMensajeProcesando(false);
                    return;
                }

                // Mostrar mensajes inline (status.html)
                const container =
                    form.closest(".modal")?.querySelector(".ajax-response") ||
                    form.querySelector(".ajax-response");

                console.log("Submit handler triggered for", form.id);
                console.log("Response HTML:", html);
                console.log("Parsed mensaje:", doc.querySelector(".mensaje-flotante"));
                console.log("Target container:", container);

                if (container) {
                    const contenido = doc.querySelector(".mensaje-flotante");
                    container.innerHTML = contenido ? contenido.outerHTML : "";

                    const mensaje = container.querySelector(".mensaje-flotante");
                    if (mensaje) {
                        mensaje.scrollIntoView({behavior: "smooth", block: "center"});
                        setTimeout(() => {
                            mensaje.classList.add("fade-out");
                            mensaje.addEventListener("transitionend", () => mensaje.remove());
                        }, 5000);
                    }
                }
            } catch (error) {
                console.error("Error en envío AJAX:", error);
            } finally {
                toggleMensajeProcesando(false);
            }
        });
    });
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

function abrirVistaPreviaPDF() {
    window.open(`/preview/pdf/?abrir=1`, "_blank");
}

function abrirVistaPreviaExcel() {
    window.open(`/preview/excel/?abrir=1`, "_blank");
}

document.addEventListener("DOMContentLoaded", () => {
    document.getElementById("modal")?.remove();

    // Activar listeners globales para modales y formularios
    document.querySelectorAll("div.modal").forEach(modal => {
        activarListenersModal(modal);
        activarEnvioAjax(modal);
    });

    // Activar AJAX en toda la página (incluye #buscar-form inline)
    activarEnvioAjax(document);
});
