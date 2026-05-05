/**
 * SpendLog – main.js
 * Handles flash message auto-dismiss and minor UX enhancements.
 */

document.addEventListener("DOMContentLoaded", () => {

    // ── Auto-dismiss flash messages after 4 seconds ──
    const flashes = document.querySelectorAll(".flash");
    flashes.forEach((flash) => {
        setTimeout(() => {
            flash.style.transition = "opacity 0.5s ease";
            flash.style.opacity = "0";
            setTimeout(() => flash.remove(), 500);
        }, 4000);
    });

    // ── Confirm delete with expense title in message ──
    // (handled inline via onsubmit in the template)

});
