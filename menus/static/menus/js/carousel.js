async function initHomeCarousel(jsonUrl) {
    const carouselContainer = document.getElementById("espacios-carousel");
    if (!carouselContainer) return;

    try {
        const response = await fetch(jsonUrl + `?t=${Date.now()}`); // evitar caché
        const data = await response.json();
        const items = data.tabla || [];
        const columnas = data.tabla_columnas || [];

        if (!items.length) {
            carouselContainer.innerHTML = "<p>No hay espacios disponibles por el momento.</p>";
            return;
        }

        // Identificar índices de columnas
        const idxServicio = columnas.indexOf("Servicio");
        const idxFechaHora = columnas.indexOf("Fecha y hora");
        const idxColaborador = columnas.indexOf("Colaborador");

        // Hora actual
        const now = new Date();

        // Filtrar solo eventos futuros
        const futuros = items.filter(row => {
            const fechaHoraStr = row[idxFechaHora]; // ej. "18/11/2025 09:05"
            // Parsear fecha/hora en formato dd/mm/yyyy HH:MM
            const [fecha, hora] = fechaHoraStr.split(" ");
            const [day, month, year] = fecha.split("/").map(Number);
            const [hour, minute] = hora.split(":").map(Number);
            const fechaHora = new Date(year, month - 1, day, hour, minute);
            return fechaHora > now;
        });

        if (!futuros.length) {
            carouselContainer.innerHTML = "<p>No hay espacios disponibles futuros.</p>";
            return;
        }

        // Crear elementos del carrusel
        futuros.forEach(row => {
            const servicio = row[idxServicio];
            const fechaHora = row[idxFechaHora];
            const colaborador = row[idxColaborador];

            const div = document.createElement("div");
            div.className = "carousel-item";
            div.textContent = `${servicio} — ${fechaHora} — ${colaborador}`;
            carouselContainer.appendChild(div);
        });

        // Iniciar animación
        const slides = carouselContainer.querySelectorAll(".carousel-item");
        let index = 0;
        slides[index].classList.add("active");

        setInterval(() => {
            slides[index].classList.remove("active");
            index = (index + 1) % slides.length;
            slides[index].classList.add("active");
        }, 5000);
    } catch (err) {
        carouselContainer.innerHTML = "<p>Error al cargar los datos.</p>";
        console.error("Error cargando carrusel:", err);
    }
}
