async function initHomeCarousel(jsonUrl) {
    const carouselContainer = document.getElementById("espacios-carousel");
    if (!carouselContainer) return;

    try {
        const response = await fetch(jsonUrl + `?t=${Date.now()}`); // evitar caché
        const data = await response.json();
        const items = data.tabla || [];

        if (!items.length) {
            carouselContainer.innerHTML = "<p>No hay espacios disponibles por el momento.</p>";
            return;
        }

        // Crear los elementos del carrusel
        items.forEach(item => {
            const div = document.createElement("div");
            div.className = "carousel-item";
            div.textContent = `${item.nombre} — ${item.hora}`;
            carouselContainer.appendChild(div);
        });

        // Iniciar animación
        let index = 0;
        const slides = document.querySelectorAll(".carousel-item");
        slides[index].classList.add("active");

        setInterval(() => {
            slides[index].classList.remove("active");
            index = (index + 1) % slides.length;
            slides[index].classList.add("active");
        }, 5000); // cambia cada 5 segundos
    } catch (err) {
        carouselContainer.innerHTML = "<p>Error al cargar los datos.</p>";
        console.error("Error cargando carrusel:", err);
    }
}
