/**
 * ASBJJ - Main JavaScript File
 * Funcionalidades principais do site
 */

// Inicialização quando o DOM estiver carregado
document.addEventListener('DOMContentLoaded', function() {
    // Inicializar componentes
    initializeComponents();
    
    // Configurar eventos
    setupEventListeners();
    
    // Configurar formulários
    setupForms();
    
    // Configurar animações
    setupAnimations();
});

/**
 * Inicializar componentes
 */
function initializeComponents() {
    // Inicializar tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Inicializar popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Configurar navbar scroll
    setupNavbarScroll();
    
    // Configurar lazy loading para imagens
    setupLazyLoading();
}

/**
 * Configurar eventos
 */
function setupEventListeners() {
    // Event listener para links suaves
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Event listener para botões de volta ao topo
    setupBackToTopButton();

    // Event listener para formulários de contato
    setupContactForms();

    // Event listener para galeria de imagens
    setupImageGallery();
}

/**
 * Configurar navbar com scroll
 */
function setupNavbarScroll() {
    const navbar = document.querySelector('.navbar');
    if (navbar) {
        window.addEventListener('scroll', function() {
            if (window.scrollY > 50) {
                navbar.classList.add('navbar-scrolled');
            } else {
                navbar.classList.remove('navbar-scrolled');
            }
        });
    }
}

/**
 * Configurar lazy loading para imagens
 */
function setupLazyLoading() {
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.classList.remove('lazy');
                    imageObserver.unobserve(img);
                }
            });
        });

        document.querySelectorAll('img[data-src]').forEach(img => {
            imageObserver.observe(img);
        });
    }
}

/**
 * Configurar botão de volta ao topo
 */
function setupBackToTopButton() {
    // Criar botão se não existir
    let backToTopBtn = document.querySelector('.back-to-top');
    if (!backToTopBtn) {
        backToTopBtn = document.createElement('button');
        backToTopBtn.className = 'back-to-top btn btn-primary rounded-circle position-fixed';
        backToTopBtn.innerHTML = '<i class="fas fa-arrow-up"></i>';
        backToTopBtn.style.cssText = 'bottom: 80px; right: 20px; width: 50px; height: 50px; z-index: 999; display: none;';
        backToTopBtn.setAttribute('aria-label', 'Voltar ao topo');
        document.body.appendChild(backToTopBtn);
    }

    // Mostrar/ocultar botão baseado no scroll
    window.addEventListener('scroll', function() {
        if (window.scrollY > 300) {
            backToTopBtn.style.display = 'block';
        } else {
            backToTopBtn.style.display = 'none';
        }
    });

    // Event listener para o botão
    backToTopBtn.addEventListener('click', function() {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });
}

/**
 * Configurar formulários
 */
function setupForms() {
    // Validação de formulários
    const forms = document.querySelectorAll('.needs-validation');
    Array.from(forms).forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });

    // Máscara para telefone
    const phoneInputs = document.querySelectorAll('input[type="tel"], input[name="phone"], input[name="whatsapp"]');
    phoneInputs.forEach(input => {
        input.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\D/g, '');
            if (value.length <= 11) {
                value = value.replace(/(\d{2})(\d{5})(\d{4})/, '($1) $2-$3');
                if (value.length < 14) {
                    value = value.replace(/(\d{2})(\d{4})(\d{4})/, '($1) $2-$3');
                }
            }
            e.target.value = value;
        });
    });

    // Máscara para CPF
    const cpfInputs = document.querySelectorAll('input[name="cpf"]');
    cpfInputs.forEach(input => {
        input.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\D/g, '');
            if (value.length <= 11) {
                value = value.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, '$1.$2.$3-$4');
            }
            e.target.value = value;
        });
        // Validação simples de comprimento
        input.addEventListener('blur', function(e) {
            const onlyDigits = e.target.value.replace(/\D/g, '');
            if (onlyDigits && onlyDigits.length !== 11) {
                e.target.classList.add('is-invalid');
            } else {
                e.target.classList.remove('is-invalid');
            }
        });
    });
}

/**
 * Configurar formulários de contato
 */
function setupContactForms() {
    const contactForms = document.querySelectorAll('form[action*="contato"], form[action*="contact"]');
    contactForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            // Adicionar loading state
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Enviando...';
            }
        });
    });
}

/**
 * Configurar galeria de imagens
 */
function setupImageGallery() {
    // Lightbox para imagens da galeria
    const galleryImages = document.querySelectorAll('[data-gallery="img-gallery"]');
    galleryImages.forEach(img => {
        img.addEventListener('click', function(e) {
            e.preventDefault();
            openLightbox(this.href, this.dataset.title || '');
        });
    });
}

/**
 * Abrir lightbox
 */
function openLightbox(src, title = '') {
    // Criar modal se não existir
    let modal = document.querySelector('#imageLightbox');
    if (!modal) {
        modal = document.createElement('div');
        modal.id = 'imageLightbox';
        modal.className = 'modal fade';
        modal.innerHTML = `
            <div class="modal-dialog modal-lg modal-dialog-centered">
                <div class="modal-content bg-transparent border-0">
                    <div class="modal-header border-0">
                        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body p-0">
                        <img src="" class="img-fluid" alt="${title}">
                    </div>
                </div>
            </div>
        `;
        document.body.appendChild(modal);
    }

    // Configurar imagem e título
    const img = modal.querySelector('img');
    img.src = src;
    img.alt = title;

    // Mostrar modal
    const bsModal = new bootstrap.Modal(modal);
    bsModal.show();
}

/**
 * Configurar animações
 */
function setupAnimations() {
    // Animações de entrada para elementos
    if ('IntersectionObserver' in window) {
        const animateObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animate-in');
                }
            });
        }, {
            threshold: 0.1
        });

        document.querySelectorAll('.animate-on-scroll').forEach(el => {
            animateObserver.observe(el);
        });
    }
}

/**
 * Utilitários
 */

// Função para mostrar toast
function showToast(message, type = 'info') {
    const toastContainer = document.querySelector('.toast-container') || createToastContainer();
    
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type} border-0`;
    toast.setAttribute('role', 'alert');
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    
    toastContainer.appendChild(toast);
    
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
    
    // Remover toast após ser ocultado
    toast.addEventListener('hidden.bs.toast', () => {
        toast.remove();
    });
}

// Criar container de toasts
function createToastContainer() {
    const container = document.createElement('div');
    container.className = 'toast-container position-fixed top-0 end-0 p-3';
    container.style.zIndex = '9999';
    document.body.appendChild(container);
    return container;
}

// Função para copiar texto para clipboard
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showToast('Copiado para a área de transferência!', 'success');
    }).catch(() => {
        showToast('Erro ao copiar texto', 'danger');
    });
}

// Função para formatar telefone
function formatPhone(phone) {
    const cleaned = phone.replace(/\D/g, '');
    if (cleaned.length === 11) {
        return cleaned.replace(/(\d{2})(\d{5})(\d{4})/, '($1) $2-$3');
    } else if (cleaned.length === 10) {
        return cleaned.replace(/(\d{2})(\d{4})(\d{4})/, '($1) $2-$3');
    }
    return phone;
}

// Função para validar email
function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

// Função para debounce
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Exportar funções para uso global
window.ASBJJ = {
    showToast,
    copyToClipboard,
    formatPhone,
    isValidEmail,
    debounce
};
