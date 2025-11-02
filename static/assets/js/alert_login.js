document.addEventListener("DOMContentLoaded", function() {
    const alerts = document.querySelectorAll(".alert");
    alerts.forEach(alert => {
        // Espera 4 segundos e depois começa a desaparecer
        setTimeout(() => {
            alert.style.transition = "opacity 0.6s ease, transform 0.6s ease";
            alert.style.opacity = "0";
            alert.style.transform = "translateY(-10px)";
            
            // Remove do DOM após a animação
            setTimeout(() => alert.remove(), 600);
        }, 4000);
    });
});