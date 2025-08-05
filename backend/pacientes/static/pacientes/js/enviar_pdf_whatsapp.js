function activarEnvioWhatsApp(modal) {
    if (!modal) return;
    const formEnviarPDF = modal.querySelector("#form-enviar-pdf");
    if (!formEnviarPDF) return;

    formEnviarPDF.addEventListener("submit", async function (e) {
        e.preventDefault();
        console.log("Submit interceptado");

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

            // Intenta parsear JSON, si falla muestra error
            let data;
            try {
                data = await response.json();
            } catch {
                mostrarMensajeEnvio(modal, "❌ Respuesta no válida del servidor.");
                return;
            }

            mostrarMensajeEnvio(modal, data.status === "enviado" ? "✅ PDF enviado correctamente." : "❌ Falló el envío.");
        } catch (err) {
            console.error(err);
            mostrarMensajeEnvio(modal, "❌ Error al conectar con el servidor.");
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
