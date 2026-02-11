let currentData = [];
let currentIndex = 0;
let slides = [];
let dotsContainer;
let carouselContainer;
let touchStartX = 0;
let touchEndX = 0;

function buildCard(row, columnas) {
    const getVal = (name) => {
        const idx = columnas.indexOf(name);
        return idx >= 0 ? row[idx] : "";
    };

    const servicio = getVal("Servicio");
    const fechaHora = getVal("Fecha y hora");
    const colaborador = getVal("Colaborador");
    const disponibles = getVal("Disponibles");
    const duracion = getVal("Duración");

    const div = document.createElement("div");
    div.className = "carousel-item";
    div.innerHTML = `
      <div class="espacio-card">
        <h4 class="servicio">${servicio || "—"}</h4>
        <p class="hora"><strong>Hora:</strong> ${fechaHora ? fechaHora.split(" ")[1] : "—"}</p>
        <p class="colaborador"><strong>Colaborador:</strong> ${colaborador || "—"}</p>
        <p class="disponibles"><strong>Disponibles:</strong> ${disponibles || "—"}</p>
        <p class="duracion"><strong>Duración:</strong> ${duracion || "—"}</p>
      </div>
    `;
    return div;
}

function renderDots() {
    if (!dotsContainer) return;
    dotsContainer.innerHTML = "";

    slides.forEach((_, i) => {
        const dot = document.createElement("span");
        dot.className = "dot" + (i === currentIndex ? " active" : "");
        dot.addEventListener("click", () => {
            // deactivate current slide
            slides[currentIndex].classList.remove("active");
            slides[currentIndex].classList.add("exit-left");

            // activate clicked slide
            currentIndex = i;
            slides[currentIndex].classList.remove("exit-left");
            slides[currentIndex].classList.add("active");

            // update dots
            dotsContainer.querySelectorAll(".dot").forEach(d => d.classList.remove("active"));
            dot.classList.add("active");

            // restart slideshow
            startSlideshow();
        });
        dotsContainer.appendChild(dot);
    });
}

async function loadCarouselData(jsonUrl) {
    carouselContainer = document.getElementById("espacios-carousel");
    dotsContainer = document.getElementById("carousel-dots");
    if (!carouselContainer) return;

    try {
        const response = await fetch(jsonUrl + `?t=${Date.now()}`);
        const data = await response.json();
        const items = data.tabla || [];
        const columnas = data.tabla_columnas || [];

        const bottomText = document.getElementById('bottom-text');
        const carouselRight = document.getElementById('carousel-right');

        const now = new Date();
        const futuros = items.filter(row => {
            const fechaHora = parseFechaHora(row[columnas.indexOf("Fecha y hora")]);
            return fechaHora && fechaHora > now;
        });

        carouselContainer.innerHTML = "";

        if (!futuros.length) {
            carouselContainer.innerHTML = "<p>No hay espacios disponibles para este día.</p>";
            slides = [];
            dotsContainer.innerHTML = "";
            if (bottomText) {
                bottomText.remove();
            }
            if (carouselRight) {
                carouselRight.style.minHeight = "auto";
            }

            return;
        }

        futuros.forEach(row => {
            carouselContainer.appendChild(buildCard(row, columnas));
        });

        slides = carouselContainer.querySelectorAll(".carousel-item");
        currentIndex = 0;
        slides[currentIndex].classList.add("active");

        renderDots();
    } catch (err) {
        console.error("Error cargando carrusel:", err);
        carouselContainer.innerHTML = "<p>Error cargando datos del carrusel.</p>";
    }
}

async function updateCarousel(jsonUrl) {
    if (!carouselContainer) return;

    try {
        const response = await fetch(jsonUrl + `?t=${Date.now()}`);
        const data = await response.json();
        const items = data.tabla || [];
        const columnas = data.tabla_columnas || [];

        const now = new Date();
        const futuros = items.filter(row => {
            const fechaHora = parseFechaHora(row[columnas.indexOf("Fecha y hora")]);
            return fechaHora && fechaHora > now;
        });

        const newData = JSON.stringify(futuros);
        if (newData === JSON.stringify(currentData)) return;
        currentData = futuros;

        carouselContainer.classList.add("fade-out");
        setTimeout(() => {
            carouselContainer.innerHTML = "";
            futuros.forEach(row => {
                carouselContainer.appendChild(buildCard(row, columnas));
            });

            slides = carouselContainer.querySelectorAll(".carousel-item");
            currentIndex = 0;
            if (slides.length) slides[currentIndex].classList.add("active");

            renderDots();

            carouselContainer.classList.remove("fade-out");
            carouselContainer.classList.add("fade-in");
        }, 500);
    } catch (err) {
        console.error("Error actualizando carrusel:", err);
    }
}

function startSlideshow() {
    if (!slides.length) return;
    if (carouselContainer._intervalId) clearInterval(carouselContainer._intervalId);

    carouselContainer._intervalId = setInterval(() => {
        const nextIndex = (currentIndex + 1) % slides.length;
        goToSlide(nextIndex);
    }, 5000);
}

function handleGesture() {
    const swipeThreshold = 50;
    if (touchEndX < touchStartX - swipeThreshold) {
        goToSlide((currentIndex + 1) % slides.length);
    }
    if (touchEndX > touchStartX + swipeThreshold) {
        goToSlide((currentIndex - 1 + slides.length) % slides.length);
    }
}

function goToSlide(index) {
    if (!slides.length) return;

    slides.forEach(slide => {
        slide.classList.remove("active", "exit-left", "exit-right");
    });

    const oldIndex = currentIndex;
    if (oldIndex !== index) {
        slides[oldIndex].classList.add(index > oldIndex ? "exit-left" : "exit-right");
    }

    currentIndex = index;
    slides[currentIndex].classList.add("active");

    dotsContainer.querySelectorAll(".dot").forEach(dot => dot.classList.remove("active"));
    if (dotsContainer.children[currentIndex]) {
        dotsContainer.children[currentIndex].classList.add("active");
    }
}

function enableSwipe() {
    if (!carouselContainer) return;
    carouselContainer.addEventListener("touchstart", e => {
        touchStartX = e.changedTouches[0].screenX;
    });
    carouselContainer.addEventListener("touchend", e => {
        touchEndX = e.changedTouches[0].screenX;
        handleGesture();
    });
}

function startCarousel(jsonUrl) {
    loadCarouselData(jsonUrl).then(() => {
        startSlideshow();
        enableSwipe();
    });
    setInterval(() => updateCarousel(jsonUrl), 300000); // refresh every 5 min
}
