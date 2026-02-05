function abrirQR(format) {
    abrirModal("modal-qr");

    const container = document.getElementById("qr-container");
    container.innerHTML = "<p>Generando QR…</p>";

    fetch("/qr/", {
        method: "POST",
        headers: {
            "X-Requested-With": "XMLHttpRequest",
            "X-CSRFToken": getCSRFToken(),
            "Content-Type": "application/x-www-form-urlencoded",
        },
        body: new URLSearchParams({format}),
    })
        .then(response => response.text())
        .then(html => {
            // Your ajax_response already returns rendered HTML
            container.innerHTML = html;
        })
        .catch(() => {
            container.innerHTML = "<p>Error al generar el QR.</p>";
        });
}
