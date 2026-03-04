let slides = [];
let currentIndex = 0;
let slideshowInterval = null;
let carouselContainer = null;
let dotsContainer = null;

let currentDataJSON = "";
let refreshIntervalId = null;

let touchStartX = 0;
let touchEndX = 0;

function renderCarousel(container, rows) {
    container.innerHTML = "";

    if (!rows.length) {
        container.innerHTML = "<p>No hay espacios disponibles para este día.</p>";
        return [];
    }

    rows.forEach(row => {
        container.appendChild(buildCarouselCard(row));
    });

    return Array.from(container.querySelectorAll(".carousel-item"));
}

function buildCarouselCard(data) {
    const div = document.createElement("div");
    div.className = "carousel-item";

    div.innerHTML = `
      <div class="espacio-card">
        <h4 class="servicio">${data.servicio || "—"}</h4>
        <p><strong>Hora:</strong> ${formatTime(data.start)}</p>
        <p><strong>Colaborador:</strong> ${data.colaborador || "—"}</p>
        <p><strong>Disponibles:</strong> ${data.disponibles || "—"}</p>
        <p><strong>Duración:</strong> ${data.duracion || "—"}</p>
      </div>
    `;

    return div;
}

function resetSlideshow() {
    if (slideshowInterval) {
        clearInterval(slideshowInterval);
    }
    startSlideshow();
}

function renderDots() {
    if (!dotsContainer) return;

    dotsContainer.innerHTML = "";

    slides.forEach((_, i) => {
        const dot = document.createElement("span");
        dot.className = "dot" + (i === currentIndex ? " active" : "");

        dot.addEventListener("click", () => {
            goToSlide(i);
        });

        dotsContainer.appendChild(dot);
    });
}

function goToSlide(index) {
    if (!slides.length) return;

    slides.forEach(slide => {
        slide.classList.remove("active", "exit-left", "exit-right");
    });

    const oldIndex = currentIndex;

    if (oldIndex !== index) {
        slides[oldIndex].classList.add(
            index > oldIndex ? "exit-left" : "exit-right"
        );
    }

    currentIndex = index;
    slides[currentIndex].classList.add("active");

    dotsContainer.querySelectorAll(".dot").forEach(dot =>
        dot.classList.remove("active")
    );

    if (dotsContainer.children[currentIndex]) {
        dotsContainer.children[currentIndex].classList.add("active");
    }

    resetSlideshow();
}

function startSlideshow() {
    if (!slides.length) return;

    if (slideshowInterval) {
        clearInterval(slideshowInterval);
    }

    slideshowInterval = setInterval(() => {
        const nextIndex = (currentIndex + 1) % slides.length;
        goToSlide(nextIndex);
    }, 5000);
}

async function rebuildCarousel(jsonUrl, firstLoad = false) {
    const parsedRows = await loadAppointments(jsonUrl);
    const newJSON = JSON.stringify(parsedRows);

    if (!firstLoad && newJSON === currentDataJSON) return;

    currentDataJSON = newJSON;

    if (slideshowInterval) {
        clearInterval(slideshowInterval);
    }

    carouselContainer.classList.remove("fade-in");
    carouselContainer.classList.add("fade-out");

    setTimeout(() => {
        slides = renderCarousel(carouselContainer, parsedRows);

        currentIndex = 0;

        if (slides.length) {
            slides[currentIndex].classList.add("active");
        }

        renderDots();
        startSlideshow();

        carouselContainer.classList.remove("fade-out");
        carouselContainer.classList.add("fade-in");

    }, firstLoad ? 0 : 400);
}

function handleGesture() {
    const swipeThreshold = 50;

    if (!slides.length) return;

    if (touchEndX < touchStartX - swipeThreshold) {
        goToSlide((currentIndex + 1) % slides.length);
    }

    if (touchEndX > touchStartX + swipeThreshold) {
        goToSlide((currentIndex - 1 + slides.length) % slides.length);
    }
}

function onTouchStart(e) {
    touchStartX = e.changedTouches[0].screenX;
}

function onTouchEnd(e) {
    touchEndX = e.changedTouches[0].screenX;
    handleGesture();
}

function enableSwipe() {
    if (!carouselContainer) return;

    carouselContainer.removeEventListener("touchstart", onTouchStart);
    carouselContainer.removeEventListener("touchend", onTouchEnd);

    carouselContainer.addEventListener("touchstart", onTouchStart);
    carouselContainer.addEventListener("touchend", onTouchEnd);
}

async function startCarousel(jsonUrl) {
    carouselContainer = document.getElementById("espacios-carousel");
    dotsContainer = document.getElementById("carousel-dots");

    if (!carouselContainer) return;

    await rebuildCarousel(jsonUrl, true);

    enableSwipe();

    refreshIntervalId = setInterval(() => {
        rebuildCarousel(jsonUrl, false);
    }, 300000);
}
