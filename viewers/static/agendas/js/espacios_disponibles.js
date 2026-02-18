async function loadAgendaCalendar(jsonUrl) {
    const response = await fetch(jsonUrl + `?t=${Date.now()}`);
    const data = await response.json();
    const items = data.tabla || [];
    const columnas = data.tabla_columnas || [];

    const events = items.map(row => {
        const servicio = row[columnas.indexOf("Servicio")] || "—";
        const colaborador = row[columnas.indexOf("Colaborador")] || "—";
        const duracionStr = row[columnas.indexOf("Duración")] || "30 min";
        const duracion = parseInt(duracionStr); // assume minutes
        const start = parseFechaHora(row[columnas.indexOf("Fecha y hora")]);
        const end = new Date(start.getTime() + duracion * 60000);

        return {
            title: `${servicio} - ${colaborador}`,
            start,
            end
        };
    });

    // Initialize FullCalendar
    const calendarEl = document.getElementById("agenda-calendar");
    const calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: "timeGridDay",
        slotMinTime: "07:00:00",
        slotMaxTime: "15:00:00",
        events: events,
        headerToolbar: false,
        allDaySlot: false,
        height: 'parent',
        nowIndicator: false,
        expandRows: true
    });
    calendar.render();
}

function startAgenda(jsonUrl) {
    loadAgendaCalendar(jsonUrl);
    setInterval(() => loadAgendaCalendar(jsonUrl), 300000); // refresh every 5 min
}
