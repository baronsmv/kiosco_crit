function getMaxColumns(byHour) {
    return Math.max(
        1,
        ...Object.values(byHour).map(list => list.length)
    );
}

function buildAgenda(items) {
    const container = document.getElementById("agenda-container");
    if (!container) return;

    const byHour = groupByHour(items);
    const maxCols = getMaxColumns(byHour);

    const table = document.createElement("table");
    table.className = "agenda-table";

    // Header
    const thead = document.createElement("thead");
    const headRow = document.createElement("tr");

    headRow.innerHTML = `<th>Hora</th>`;
    for (let i = 1; i <= maxCols; i++) {
        headRow.innerHTML += `<th>Espacio ${i}</th>`;
    }

    thead.appendChild(headRow);
    table.appendChild(thead);

    // Body
    const tbody = document.createElement("tbody");

    for (let hour = 7; hour <= 15; hour++) {
        const row = document.createElement("tr");

        row.innerHTML = `<td class="hora-cell">${hour}:00</td>`;

        const slots = byHour[hour] || [];

        for (let i = 0; i < maxCols; i++) {
            const cell = document.createElement("td");

            if (slots[i]) {
                cell.appendChild(buildAgendaCard(slots[i]));
            } else {
                cell.innerHTML = `<div class="agenda-empty">—</div>`;
            }

            row.appendChild(cell);
        }

        tbody.appendChild(row);
    }

    table.appendChild(tbody);
    container.innerHTML = "";
    container.appendChild(table);
}

function buildAgendaCard(item) {
    const div = document.createElement("div");
    div.className = "espacio-card agenda-card";

    const hora = item._date.toTimeString().slice(0, 5);

    div.innerHTML = `
        <h4 class="servicio">${item.nombre_servicio}</h4>
        <p><strong>Hora:</strong> ${hora}</p>
        <p><strong>Colaborador:</strong> ${item.nombre_colaborador}</p>
        <p><strong>Disponibles:</strong> ${item.espacios_disponibles}</p>
        <p><strong>Duración:</strong> ${item.duracion_servicio}</p>
    `;

    return div;
}
