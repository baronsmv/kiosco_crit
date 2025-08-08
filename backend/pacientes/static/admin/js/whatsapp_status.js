document.addEventListener("DOMContentLoaded", function () {
    const statusText = document.getElementById("status-text");
    const connectedText = document.getElementById("connected-text");
    const qrContainer = document.getElementById("qr-container");
    const alertsContainer = document.getElementById("dynamic-alerts");

    const STATUS_ENDPOINT = `${NODE_BASE_URL}/status`;
    const QR_ENDPOINT = `${NODE_BASE_URL}/qr`;

    async function fetchStatus() {
        try {
            const resp = await fetch(STATUS_ENDPOINT, {cache: "no-store"});
            if (!resp.ok) throw new Error(`Status ${resp.status}`);
            const data = await resp.json();

            statusText.innerText = data.status || "Desconocido";
            connectedText.innerText = data.connected ? "Sí" : "No";
            connectedText.style.color = data.connected ? "#2a9d8f" : "#e63946";

        } catch (err) {
            showError("No se pudo obtener el estado del cliente.");
            console.error("🔴 Error al obtener /status:", err);
        }
    }

    async function fetchQR() {
        try {
            const resp = await fetch(QR_ENDPOINT, {cache: "no-store"});
            if (!resp.ok) throw new Error(`Status ${resp.status}`);
            const data = await resp.json();

            if (data.qr) {
                qrContainer.innerHTML = `
                    <h2>Escanea este código QR</h2>
                    <img id="qr-image" alt="QR Code" src="${data.qr}">
                `;
            } else {
                qrContainer.innerHTML = `
                    <p id="no-qr">No hay QR disponible (probablemente el cliente ya está conectado).</p>
                `;
            }
        } catch (err) {
            showError("No se pudo obtener el código QR.");
            console.error("🔴 Error al obtener /qr:", err);
        }
    }

    function showError(message) {
        if (!alertsContainer) return;

        alertsContainer.innerHTML = `
            <div class="error">
                ⚠️ ${message}
            </div>
        `;
    }

    async function updateData() {
        await Promise.all([fetchStatus(), fetchQR()]);
    }

    // Primera carga
    updateData();

    // Polling cada 5 segundos
    setInterval(updateData, 5000);
});
