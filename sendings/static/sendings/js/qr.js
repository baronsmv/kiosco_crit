function abrirQR(format) {
    abrirModal("modal-qr");

    const container = document.getElementById("qr-container");
    const qrImage = container.querySelector(".qr-image");
    qrImage.style.display = "none";
    container.querySelector("p")?.remove();

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
        })
        .catch(() => {
            container.innerHTML = "<p>Error al generar el QR.</p>";
        });
}
