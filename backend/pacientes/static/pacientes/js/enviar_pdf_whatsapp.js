function activarEnvioWhatsApp(modal) {
    if (!modal) return;
    const formEnviarPDF = modal.querySelector("#form-enviar-pdf");
    if (!formEnviarPDF) return;

    formEnviarPDF.addEventListener("submit", async function (e) {
        e.preventDefault();
        const boton = formEnviarPDF.querySelector("button[type=submit]");
        if (!boton) return;

        const textoOriginal = boton.textContent;
        boton.textContent = "Enviando...";
        boton.disabled = true;

        const numero = formEnviarPDF.querySelector("input[name=numero]").value;
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
                mostrarMensajeEnvio(modal, "❌ Respuesta no válida del servidor.");
                boton.textContent = textoOriginal;
                boton.disabled = false;
                return;
            }

            if (data.status === "enviado") {
                mostrarMensajeEnvio(modal, "✅ PDF enviado correctamente.");
                boton.textContent = "Enviado";
            } else {
                mostrarMensajeEnvio(modal, "❌ Falló el envío.");
                boton.textContent = textoOriginal;
            }
        } catch (err) {
            console.error(err);
            mostrarMensajeEnvio(modal, "❌ Error al conectar con el servidor.");
            boton.textContent = textoOriginal;
        } finally {
            setTimeout(() => {
                boton.textContent = textoOriginal;
                boton.disabled = false;
            }, 4000);
        }
    });
}

function mostrarMensajeEnvio(modal, texto) {
    if (!modal) return;
    const mensajeDiv = modal.querySelector("#mensaje-envio");
    if (!mensajeDiv) return;

    mensajeDiv.textContent = texto;
    mensajeDiv.style.display = "block";

    setTimeout(() => {
        mensajeDiv.style.display = "none";
    }, 4000);
}

document.addEventListener("DOMContentLoaded", function () {
    // Intentamos activar para el modal inicial si existe
    const modalInicial = document.getElementById("modal-paciente");
    if (modalInicial) {
        activarEnvioWhatsApp(modalInicial);
    }
});
