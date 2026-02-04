function parseFechaHora(fechaHoraStr) {
    const [fecha, hora] = fechaHoraStr.split(" ");
    const [day, month, year] = fecha.split("/").map(Number);
    const [hour, minute] = hora.split(":").map(Number);
    return new Date(year, month - 1, day, hour, minute);
}

function groupByHour(items) {
    const byHour = {};

    items.forEach(item => {
        const date = parseFechaHora(item.fecha_cita);
        if (!date) return;

        const hour = date.getHours(); // 0–23
        if (hour < 7 || hour > 15) return;

        byHour[hour] ??= [];
        byHour[hour].push({
            ...item,
            _date: date,
        });
    });

    return byHour;
}
