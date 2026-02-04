function buildAgendaRow(hour, appointments, columnas) {
    const tr = document.createElement("tr");

    // Hour cell
    const hourCell = document.createElement("td");
    hourCell.textContent = `${hour}:00`;
    tr.appendChild(hourCell);

    // Appointments cell
    const apptCell = document.createElement("td");
    apptCell.className = "agenda-slot";

    if (!appointments.length) {
        apptCell.innerHTML = "<span class='no-appt'>—</span>";
    } else {
        appointments.forEach(row => {
            const servicio = row[columnas.indexOf("Servicio")] || "—";
            const colaborador = row[columnas.indexOf("Colaborador")] || "—";
            const duracion = row[columnas.indexOf("Duración")] || "—";
            const disponibles = row[columnas.indexOf("Disponibles")] || "—";

            const card = document.createElement("div");
            card.className = "agenda-card";
            card.innerHTML = `
                <h4>${servicio}</h4>
                <p><strong>Colaborador:</strong> ${colaborador}</p>
                <p><strong>Disponibles:</strong> ${disponibles}</p>
                <p><strong>Duración:</strong> ${duracion}</p>
            `;
            apptCell.appendChild(card);
        });
    }

    tr.appendChild(apptCell);
    return tr;
}

async function loadAgendaData(jsonUrl) {
    const tbody = document.getElementById("agenda-body");
    if (!tbody) return;

    try {
        const response = await fetch(jsonUrl + `?t=${Date.now()}`);
        const data = await response.json();
        const items = data.tabla || [];
        const columnas = data.tabla_columnas || [];

        const now = new Date();
        const futuros = items.filter(row => {
            const fechaHora = parseFechaHora(row[columnas.indexOf("Fecha y hora")]);
            return fechaHora && fechaHora.toDateString() === now.toDateString();
        });

        // Clear table
        tbody.innerHTML = "";

        // Build rows from 7 to 15
        for (let hour = 7; hour <= 15; hour++) {
            const appointments = futuros.filter(row => {
                const fechaHora = parseFechaHora(row[columnas.indexOf("Fecha y hora")]);
                return fechaHora && fechaHora.getHours() === hour;
            });
            tbody.appendChild(buildAgendaRow(hour, appointments, columnas));
        }
    } catch (err) {
        console.error("Error cargando agenda:", err);
    }
}

function startAgenda(jsonUrl) {
    loadAgendaData(jsonUrl);
    setInterval(() => loadAgendaData(jsonUrl), 300000); // refresh every 5 min
}
