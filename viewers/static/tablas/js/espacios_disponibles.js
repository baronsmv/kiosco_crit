function renderTable(tbody, rows) {
    tbody.innerHTML = "";

    if (!rows.length) {
        tbody.innerHTML = `
            <tr>
                <td colspan="6">No hay espacios disponibles para este día.</td>
            </tr>
        `;
        return;
    }

    rows.forEach(row => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
            <td data-label="Servicio">${row.servicio || "—"}</td>
            <td data-label="Hora">${formatTime(row.start)}</td>
            <td data-label="Colaborador">${row.colaborador || "—"}</td>
            <td data-label="Disponibles">${row.disponibles}</td>
            <td data-label="Duración">${row.duracion || "—"}</td>
        `;
        tbody.appendChild(tr);
    });
}

function startTable(jsonUrl) {
    const tbody = document.querySelector("#espacios-table tbody");
    if (!tbody) return;

    loadAppointments(jsonUrl, (parsedRows) => {
        renderTable(tbody, parsedRows);
    });

    setInterval(() => {
        loadAppointments(jsonUrl, (parsedRows) => {
            renderTable(tbody, parsedRows);
        });
    }, 300000);
}
