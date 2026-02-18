function abrirQR(format) {
    abrirModal("modal-qr");

    const container = document.getElementById("qr-container");
    container.innerHTML = "<p>Generando QR…</p>";

    const qrImage = document.createElement("img");
    qrImage.className = "qr-image";
    qrImage.style.display = "none";

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
            container.innerHTML = "";

            const qrImage = document.createElement("img");
            qrImage.className = "qr-image";
            qrImage.src = data.qr_url;
            qrImage.style.display = "block";
            container.appendChild(qrImage);

            // Get the bottom text from the data attribute
            const bottomText = document.createElement("p");
            bottomText.textContent = document.getElementById("modal-qr").dataset.bottomText;
            container.appendChild(bottomText);
        })
        .catch(() => {
            container.innerHTML = "<p>Error al generar el QR.</p>";
        });
}
