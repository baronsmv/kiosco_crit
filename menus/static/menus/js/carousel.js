let currentData = [];
let currentIndex = 0;
let slides = [];
let dotsContainer;
let carouselContainer;

async function loadCarouselData(jsonUrl) {
    carouselContainer = document.getElementById("espacios-carousel");
    dotsContainer = document.getElementById("carousel-dots");
    if (!carouselContainer) return;

    try {
        const response = await fetch(jsonUrl + `?t=${Date.now()}`); // cache bust
        const data = await response.json();
        const items = data.tabla || [];
        const columnas = data.tabla_columnas || [];

        // Identify column indices
        const idxServicio = columnas.indexOf("Servicio");
        const idxFechaHora = columnas.indexOf("Fecha y hora");
        const idxColaborador = columnas.indexOf("Colaborador");

        // Current time
        const now = new Date();

        // Filter future events
        const futuros = items.filter(row => {
            const fechaHoraStr = row[idxFechaHora]; // "dd/mm/yyyy HH:MM"
            const [fecha, hora] = fechaHoraStr.split(" ");
            const [day, month, year] = fecha.split("/").map(Number);
            const [hour, minute] = hora.split(":").map(Number);
            const fechaHora = new Date(year, month - 1, day, hour, minute);
            return fechaHora > now;
        });

        // Clear old content
        carouselContainer.innerHTML = "";

        if (!futuros.length) {
            carouselContainer.innerHTML = "<p>No hay espacios disponibles para este día.</p>";
            return;
        }

        // Build carousel items
        futuros.forEach(row => {
            const servicio = row[idxServicio];
            const fechaHora = row[idxFechaHora];
            const colaborador = row[idxColaborador];
            const disponibles = row[columnas.indexOf("Disponibles")];
            const duracion = row[columnas.indexOf("Duración")];

            const div = document.createElement("div");
            div.className = "carousel-item";

            // Build a card with all info
            div.innerHTML = `
              <div class="espacio-card">
                <h4 class="servicio">${servicio}</h4>
                <p class="hora"><strong>Hora:</strong> ${fechaHora.split(" ")[1]}</p>
                <p class="colaborador"><strong>Colaborador:</strong> ${colaborador}</p>
                <p class="disponibles"><strong>Disponibles:</strong> ${disponibles}</p>
                <p class="duracion"><strong>Duración:</strong> ${duracion}</p>
              </div>
            `;

            carouselContainer.appendChild(div);
        });

        slides = carouselContainer.querySelectorAll(".carousel-item");
        currentIndex = 0;
        slides[currentIndex].classList.add("active");

        animateDots();
    } catch (err) {
        carouselContainer.innerHTML = "<p>No hay espacios disponibles para este día.</p>";
        console.error("Error cargando carrusel:", err);
    }
}

async function updateCarousel(jsonUrl) {
    carouselContainer = document.getElementById("espacios-carousel");
    if (!carouselContainer) return;

    const response = await fetch(jsonUrl + `?t=${Date.now()}`);
    const data = await response.json();
    const items = data.tabla || [];
    const columnas = data.tabla_columnas || [];

    const idxServicio = columnas.indexOf("Servicio");
    const idxFechaHora = columnas.indexOf("Fecha y hora");
    const idxColaborador = columnas.indexOf("Colaborador");

    const now = new Date();
    const futuros = items.filter(row => {
        const [fecha, hora] = row[idxFechaHora].split(" ");
        const [day, month, year] = fecha.split("/").map(Number);
        const [hour, minute] = hora.split(":").map(Number);
        const fechaHora = new Date(year, month - 1, day, hour, minute);
        return fechaHora > now;
    });

    // Compare with currentData
    const newData = JSON.stringify(futuros);
    if (newData === JSON.stringify(currentData)) return;
    currentData = futuros;

    // Smooth update: fade out, replace, fade in
    carouselContainer.classList.add("fade-out");
    setTimeout(() => {
        carouselContainer.innerHTML = "";
        futuros.forEach(row => {
            const div = document.createElement("div");
            div.className = "carousel-item";
            div.innerHTML = `
              <div class="espacio-card">
                <h4 class="servicio">${servicio}</h4>
                <p class="hora"><strong>Hora:</strong> ${fechaHora.split(" ")[1]}</p>
                <p class="colaborador"><strong>Colaborador:</strong> ${colaborador}</p>
                <p class="disponibles"><strong>Disponibles:</strong> ${disponibles}</p>
                <p class="duracion"><strong>Duración:</strong> ${duracion}</p>
              </div>
            `;
            carouselContainer.appendChild(div);
        });

        slides = carouselContainer.querySelectorAll(".carousel-item");
        currentIndex = 0;
        slides[currentIndex].classList.add("active");

        animateDots();

        carouselContainer.classList.remove("fade-out");
        carouselContainer.classList.add("fade-in");
    }, 500);
}

function animateDots() {
    if (!dotsContainer) return;
    dotsContainer.innerHTML = "";

    slides.forEach((_, i) => {
        const dot = document.createElement("span");
        dot.className = "dot" + (i === currentIndex ? " active" : "");
        dotsContainer.appendChild(dot);
    });
}

function startSlideshow() {
    if (slides.length === 0) return;

    if (carouselContainer._intervalId) {
        clearInterval(carouselContainer._intervalId);
    }

    carouselContainer._intervalId = setInterval(() => {
        slides[currentIndex].classList.remove("active");
        slides[currentIndex].classList.add("exit-left");

        currentIndex = (currentIndex + 1) % slides.length;

        slides[currentIndex].classList.remove("exit-left");
        slides[currentIndex].classList.add("active");

        dotsContainer.querySelectorAll(".dot").forEach(dot => dot.classList.remove("active"));
        dotsContainer.children[currentIndex].classList.add("active");
    }, 5000);

}


function startCarousel(jsonUrl) {
    loadCarouselData(jsonUrl).then(() => {
        startSlideshow();
    });
    setInterval(() => updateCarousel(jsonUrl), 300000); // refresh every 5 min
}
