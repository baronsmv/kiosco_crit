function abrirQR(format) {
    abrirModal("modal-qr");

    const container = document.getElementById("qr-container");
    container.innerHTML = "<p>Generando QR…</p>";

    const qrImage = document.createElement("img");
    qrImage.className = "qr-image";
    qrImage.style.display = "none";
    container.appendChild(qrImage);

    fetch(QR_URL, {
        method: "POST",
        headers: {
            "X-Requested-With": "XMLHttpRequest",
            "X-CSRFToken": getCSRFToken(),
            "Content-Type": "application/x-www-form-urlencoded",
        },
        body: new URLSearchParams({format}),
    })
        .then(response => response.json())
        .then(data => {
            qrImage.src = data.qr_url;
            qrImage.style.display = "block";

            // Remove the loading text
            const p = container.querySelector("p");
            if (p) p.remove();
        })
        .catch(() => {
            container.innerHTML = "<p>Error al generar el QR.</p>";
        });
}
