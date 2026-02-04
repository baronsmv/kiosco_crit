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
