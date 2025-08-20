function mostrarErrorCampo(inputId = "carnet") {
    const input = document.getElementById(inputId);
    if (!input) return;

    document.querySelectorAll(".input-group").forEach(group => {
        group.classList.remove("error");
        const existingIcon = group.querySelector(".icon-error");
        if (existingIcon) existingIcon.remove();
    });

    const group = input.closest(".input-group");
    if (!group) return;

    group.classList.add("error");

    if (!group.querySelector(".icon-error")) {
        const icon = document.createElement("span");
        icon.className = "icon-error";
        icon.title = "Error";
        icon.setAttribute("aria-hidden", "true");
        icon.innerHTML = `
            <svg height="20" width="20">
                <use href="#icon-error"></use>
            </svg>
        `;
        group.appendChild(icon);
    }
}
