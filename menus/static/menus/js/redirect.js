function redirect_to(url, minutes_after = 5, countdownSeconds = 30) {
    let inactivityTimer;
    let countdownTimer;
    const timeout = minutes_after * 60 * 1000;
    const redirectUrl = window.INACTIVITY_REDIRECT_URL || url;

    const overlay = document.getElementById("redirection-message");
    const countdownEl = document.getElementById("countdown");
    const stayBtn = document.getElementById("stay-btn");

    function showWarning() {
        if (!overlay) return;
        overlay.classList.add("visible");

        let remaining = countdownSeconds;
        countdownEl.textContent = remaining;

        countdownTimer = setInterval(() => {
            remaining--;
            countdownEl.textContent = remaining;
            if (remaining <= 0) {
                clearInterval(countdownTimer);
                window.location.href = redirectUrl;
            }
        }, 1000);
    }

    function resetTimer() {
        clearTimeout(inactivityTimer);
        clearInterval(countdownTimer);
        if (overlay) overlay.classList.remove("visible");
        inactivityTimer = setTimeout(showWarning, timeout);
    }

    if (stayBtn) {
        stayBtn.addEventListener("click", () => {
            resetTimer();
        });
    }

    ["click", "mousemove", "keydown", "scroll", "touchstart"].forEach(evt => {
        document.addEventListener(evt, resetTimer, {passive: true});
    });

    resetTimer();
}
