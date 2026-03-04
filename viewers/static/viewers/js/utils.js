function parseFechaHora(fechaHoraStr) {
    if (!fechaHoraStr) return null;
    try {
        const [fecha, hora] = fechaHoraStr.split(" ");
        const [day, month, year] = fecha.split("/").map(Number);
        const [hour, minute] = hora.split(":").map(Number);
        return new Date(year, month - 1, day, hour, minute);
    } catch {
        return null;
    }
}

async function fetchAgendaData(jsonUrl) {
    const response = await fetch(jsonUrl + `?t=${Date.now()}`);
    const data = await response.json();

    return {
        items: data.tabla || [],
        columnas: data.tabla_columnas || []
    };
}

function getColumnValue(row, columnas, name) {
    const idx = columnas.indexOf(name);
    return idx >= 0 ? row[idx] : "";
}

function parseRow(row, columnas) {
    const fechaHoraStr = getColumnValue(row, columnas, "Fecha y hora");
    const duracionStr = getColumnValue(row, columnas, "Duración");

    const start = parseFechaHora(fechaHoraStr);
    const duration = parseInt(duracionStr) || 30;
    const end = start ? new Date(start.getTime() + duration * 60000) : null;

    return {
        servicio: getColumnValue(row, columnas, "Servicio"),
        colaborador: getColumnValue(row, columnas, "Colaborador"),
        disponibles: getColumnValue(row, columnas, "Disponibles"),
        duracion: duracionStr,
        start,
        end
    };
}

function filterFutureAppointments(rows) {
    const now = new Date();
    return rows.filter(r => r.start && r.start > now);
}

function sortByStartTime(rows) {
    return rows.sort((a, b) => a.start - b.start);
}

async function loadAppointments(jsonUrl, renderCallback = null) {
    const {items, columnas} = await fetchAgendaData(jsonUrl);

    let parsed = items.map(row => parseRow(row, columnas));
    parsed = filterFutureAppointments(parsed);
    parsed = sortByStartTime(parsed);

    if (renderCallback) {
        renderCallback(parsed);
    }

    return parsed;
}

function formatTime(date) {
    if (!date) return "—";
    return date.toLocaleTimeString([], {
        hour: "2-digit",
        minute: "2-digit"
    });
}

function formatDate(date) {
    if (!date) return "—";
    return date.toLocaleDateString();
}
