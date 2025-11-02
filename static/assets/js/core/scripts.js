
// Toggle Sidebar
function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    const mainWrapper = document.getElementById('mainWrapper');
    const icon = document.querySelector('.sidebar-toggle i');

    sidebar.classList.toggle('collapsed');
    mainWrapper.classList.toggle('expanded');

    if (sidebar.classList.contains('collapsed')) {
        icon.classList.remove('fa-chevron-left');
        icon.classList.add('fa-chevron-right');
        localStorage.setItem('sidebarCollapsed', 'true');
    } else {
        icon.classList.remove('fa-chevron-right');
        icon.classList.add('fa-chevron-left');
        localStorage.setItem('sidebarCollapsed', 'false');
    }
}

// Restaurar estado da sidebar
window.addEventListener('DOMContentLoaded', () => {
    const collapsed = localStorage.getItem('sidebarCollapsed');
    if (collapsed === 'true') {
        toggleSidebar();
    }
});

// Toggle Mobile Sidebar
function toggleMobileSidebar() {
    const sidebar = document.getElementById('sidebar');
    sidebar.classList.toggle('active');
}

// Toggle Collapse
function toggleCollapse(id) {
    const element = document.getElementById(id);
    const allCollapses = document.querySelectorAll('.collapse');

    allCollapses.forEach(collapse => {
        if (collapse.id !== id) {
            collapse.classList.remove('show');
        }
    });

    element.classList.toggle('show');
}

// Show Alert Global
function showAlert(type, message, duration = 5000) {
    const container = document.getElementById('alert-container');

    const iconMap = {
        'success': 'fas fa-check-circle',
        'error': 'fas fa-times-circle',
        'danger': 'fas fa-times-circle',
        'warning': 'fas fa-exclamation-triangle',
        'info': 'fas fa-info-circle'
    };

    const alertDiv = document.createElement('div');
    alertDiv.className = `custom-alert alert-${type}`;
    alertDiv.innerHTML = `
                <div class="alert-content">
                    <i class="${iconMap[type]} alert-icon"></i>
                    <div class="alert-message">${message}</div>
                    <button class="alert-close" onclick="this.closest('.custom-alert').remove()">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
                <div class="alert-progress">
                    <div class="alert-progress-bar" id="progress-${Date.now()}"></div>
                </div>
            `;

    container.appendChild(alertDiv);

    const progressBar = alertDiv.querySelector('.alert-progress-bar');
    setTimeout(() => {
        progressBar.style.transition = `width ${duration}ms linear`;
        progressBar.style.width = '0%';
    }, 10);

    setTimeout(() => {
        alertDiv.style.animation = 'slideOutRight 0.4s ease forwards';
        setTimeout(() => alertDiv.remove(), 400);
    }, duration);
}

// Animação de saída
const style = document.createElement('style');
style.textContent = `
            @keyframes slideOutRight {
                to {
                    transform: translateX(400px);
                    opacity: 0;
                }
            }
        `;
document.head.appendChild(style);

// Fechar sidebar ao clicar fora (mobile)
document.addEventListener('click', (e) => {
    if (window.innerWidth <= 768) {
        const sidebar = document.getElementById('sidebar');
        const mobileToggle = document.querySelector('.mobile-toggle');

        if (!sidebar.contains(e.target) && !mobileToggle.contains(e.target)) {
            sidebar.classList.remove('active');
        }
    }
});

// Prevenir fechamento ao clicar dentro da sidebar
document.getElementById('sidebar').addEventListener('click', (e) => {
    e.stopPropagation();
});

