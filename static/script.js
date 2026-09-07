// ==============================
// DARK / LIGHT MODE
// ==============================

const themeButton = document.getElementById("theme-toggle");

const savedTheme = localStorage.getItem("theme");

if (savedTheme === "dark") {
    document.body.classList.add("dark-mode");
}

function updateThemeIcon() {

    if (!themeButton) return;

    if (document.body.classList.contains("dark-mode")) {
        themeButton.innerHTML = "☀️";
        themeButton.title = "Switch to Light Mode";
    } else {
        themeButton.innerHTML = "🌙";
        themeButton.title = "Switch to Dark Mode";
    }
}

updateThemeIcon();


if (themeButton) {

    themeButton.addEventListener("click", function () {

        document.body.classList.toggle("dark-mode");

        if (document.body.classList.contains("dark-mode")) {

            localStorage.setItem("theme", "dark");

        } else {

            localStorage.setItem("theme", "light");

        }

        updateThemeIcon();

    });

}


// ==============================
// PAGE LOAD ANIMATION
// ==============================

document.addEventListener("DOMContentLoaded", function () {

    const cards = document.querySelectorAll(
        ".stat-card, .assignment-card, .welcome, .add-section"
    );

    cards.forEach(function (card, index) {

        card.style.animationDelay = `${index * 0.07}s`;

    });

});
// ==========================================
// PROFILE DROPDOWN
// ==========================================

const profileButton =
    document.getElementById("profile-menu-button");

const profileDropdown =
    document.getElementById("profile-dropdown");


if (profileButton && profileDropdown) {

    profileButton.addEventListener(
        "click",
        function (event) {

            event.stopPropagation();

            profileDropdown.classList.toggle("show");

        }
    );


    document.addEventListener(
        "click",
        function (event) {

            if (
                !profileDropdown.contains(event.target) &&
                !profileButton.contains(event.target)
            ) {

                profileDropdown.classList.remove(
                    "show"
                );

            }

        }
    );

}