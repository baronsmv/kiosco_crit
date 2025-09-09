async function activarEnvioWhatsApp(modal) {
    if (!modal) return;

    const formEnviarPDF = modal.querySelector("#form-enviar-pdf");
    if (!formEnviarPDF) return;

    const input = formEnviarPDF.querySelector("input[name=numero]");
    const mensajeDiv = modal.querySelector("#mensaje-envio");

    // Obtener estado de WhatsApp desde el JSON embebido en el HTML
    let whatsappStatus;
    try {
        whatsappStatus = JSON.parse(document.getElementById('whatsapp-status').textContent);
    } catch (e) {
        console.warn("Error leyendo estado WhatsApp:", e);
        whatsappStatus = null;
    }

    if (!whatsappStatus || whatsappStatus.status !== "listo" || !whatsappStatus.connected) {
        formEnviarPDF.classList.add("hidden");
        if (mensajeDiv) {
            mensajeDiv.textContent = "⚠️ Servicio de WhatsApp no disponible en este momento.";
            mensajeDiv.style.display = "block";
        }
        return;
    } else {
        formEnviarPDF.classList.remove("hidden");
        if (mensajeDiv) {
            mensajeDiv.textContent = "";
            mensajeDiv.style.display = "none";
        }
    }

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
