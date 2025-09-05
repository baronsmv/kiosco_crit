async function activarEnvioWhatsApp(modal) {
    if (!modal) return;

    const formEnviarPDF = modal.querySelector("#form-enviar-pdf");
    const input = formEnviarPDF.querySelector("input[name=numero]");
    const mensajeDiv = modal.querySelector("#mensaje-envio");

    // Verifica si el servicio de WhatsApp está listo
    try {
        const resp = await fetch("/whatsapp/status");
        const data = await resp.json();

        const noDisponible = !data || data.status !== "listo" || !data.connected;

        if (noDisponible && formEnviarPDF) {
            formEnviarPDF.classList.add("hidden");
            if (mensajeDiv) {
                mensajeDiv.textContent = "⚠️ Servicio de WhatsApp no disponible en este momento.";
                mensajeDiv.style.display = "block";
            }
            return;
        }
    } catch (err) {
        console.warn("No se pudo verificar el estado de WhatsApp:", err);
        if (formEnviarPDF) formEnviarPDF.classList.add("hidden");
        if (mensajeDiv) {
            mensajeDiv.textContent = "⚠️ Error al verificar el servicio de WhatsApp.";
            mensajeDiv.style.display = "block";
        }
        return;
    }

    if (!formEnviarPDF) return;

    formEnviarPDF.addEventListener("submit", async function (e) {
        e.preventDefault();

        const numero = input.value.trim();
        const regex = /^\d{10}$/;

        // Limpiar estado anterior
        input.classList.remove("input-error");
        if (mensajeDiv) {
            mensajeDiv.textContent = "";
            mensajeDiv.style.display = "none";
        }

        if (!regex.test(numero)) {
            if (mensajeDiv) {
                mensajeDiv.textContent = "❌ El número debe tener exactamente 10 dígitos.";
                mensajeDiv.style.display = "block";
            }
            input.classList.add("input-error");
            input.focus();
            return;
        }

        const boton = formEnviarPDF.querySelector("button[type=submit]");
        const textoOriginal = boton?.textContent || "Enviar";

        if (boton) {
            boton.textContent = "Enviando...";
            boton.disabled = true;
        }

        const csrfToken = formEnviarPDF.querySelector("[name=csrfmiddlewaretoken]").value;
        const actionUrl = formEnviarPDF.getAttribute("action") || window.location.pathname;

        try {
            const response = await fetch(actionUrl, {
                method: "POST",
                headers: {
                    "X-CSRFToken": csrfToken,
                    "X-Requested-With": "XMLHttpRequest",
                    "Content-Type": "application/x-www-form-urlencoded",
                },
                body: new URLSearchParams({numero}),
            });

            let data;
            try {
                data = await response.json();
            } catch {
                mostrarMensajeEnvio(mensajeDiv, "❌ Respuesta no válida del servidor.");
                return;
            }

            if (data.status === "enviado") {
                mostrarMensajeEnvio(mensajeDiv, "✅ PDF enviado correctamente.");
                if (boton) boton.textContent = "Enviado";
            } else {
                mostrarMensajeEnvio(mensajeDiv, "❌ Falló el envío.");
            }
        } catch (err) {
            console.error(err);
            mostrarMensajeEnvio(mensajeDiv, "❌ Error al conectar con el servidor.");
        } finally {
            if (boton) {
                setTimeout(() => {
                    boton.textContent = textoOriginal;
                    boton.disabled = false;
                }, 4000);
            }
        }
    });
}

function mostrarMensajeEnvio(elemento, texto) {
    if (!elemento) return;
    elemento.textContent = texto;
    elemento.style.display = "block";

    setTimeout(() => {
        elemento.style.display = "none";
    }, 4000);
}
