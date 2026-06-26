const hamburger = document.querySelector('.hamburger');
const nav = document.querySelector('.nav');
const header = document.querySelector('.header');
const pageTop = document.getElementById('pageTop');
const hero = document.querySelector('.hero');
const form = document.querySelector('.contact-form');
const fadeItems = document.querySelectorAll('.fade-up, .fade-left, .fade-right, .zoom');
const navLinks = document.querySelectorAll('.nav a[href^="#"]');
const sections = Array.from(document.querySelectorAll('main section[id]'));

const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

const closeMenu = () => {
    if (hamburger && nav) {
        hamburger.classList.remove('active');
        nav.classList.remove('active');
        document.body.classList.remove('menu-open');
        hamburger.setAttribute('aria-expanded', 'false');
    }
};

if (hamburger && nav) {
    hamburger.addEventListener('click', () => {
        const isExpanded = hamburger.getAttribute('aria-expanded') === 'true';
        hamburger.classList.toggle('active');
        nav.classList.toggle('active');
        document.body.classList.toggle('menu-open');
        hamburger.setAttribute('aria-expanded', String(!isExpanded));
    });

    document.addEventListener('keydown', (event) => {
        if (event.key === 'Escape') closeMenu();
    });

    document.addEventListener('click', (event) => {
        if (!nav.classList.contains('active')) return;
        if (event.target instanceof Node && !nav.contains(event.target) && !hamburger.contains(event.target)) {
            closeMenu();
        }
    });
}

document.querySelectorAll('.nav a').forEach((link) => {
    link.addEventListener('click', closeMenu);
});

let ticking = false;
const updateOnScroll = () => {
    const scrolled = window.scrollY > 20;

    if (header) {
        header.classList.toggle('scrolled', scrolled);
    }

    if (pageTop) {
        pageTop.classList.toggle('show', window.scrollY > 400);
    }

    ticking = false;
};

window.addEventListener('scroll', () => {
    if (!ticking) {
        window.requestAnimationFrame(updateOnScroll);
        ticking = true;
    }
}, { passive: true });
updateOnScroll();

const scrollLinks = document.querySelectorAll('a[href^="#"]');
scrollLinks.forEach((link) => {
    link.addEventListener('click', (event) => {
        const targetId = link.getAttribute('href');
        if (!targetId || targetId === '#') return;

        const target = document.querySelector(targetId);
        if (!target) return;

        event.preventDefault();
        target.scrollIntoView({ behavior: reduceMotion ? 'auto' : 'smooth', block: 'start' });
    });
});

if (pageTop) {
    pageTop.addEventListener('click', (event) => {
        event.preventDefault();
        window.scrollTo({ top: 0, behavior: reduceMotion ? 'auto' : 'smooth' });
    });
}

if (form) {
    const statusMessage = form.querySelector('.form-status');
    const submitButton = form.querySelector('button[type="submit"]');
    const defaultButtonText = submitButton ? submitButton.textContent : '';
    const getEndpoint = () => (form.dataset.formspreeEndpoint || form.getAttribute('action') || '').trim();

    const setStatus = (message, type = '') => {
        if (!statusMessage) return;
        statusMessage.textContent = message;
        statusMessage.classList.remove('success', 'error');
        if (type) statusMessage.classList.add(type);
    };

    const setSubmitting = (isSubmitting) => {
        if (!submitButton) return;
        form.classList.toggle('is-sending', isSubmitting);
        submitButton.disabled = isSubmitting;
        submitButton.setAttribute('aria-busy', String(isSubmitting));
        submitButton.textContent = isSubmitting ? '送信中...' : defaultButtonText;
    };

    form.querySelectorAll('input, textarea').forEach((field) => {
        field.addEventListener('input', () => {
            if (field.value.trim()) {
                field.closest('.input-field')?.classList.remove('error');
                field.removeAttribute('aria-invalid');
            }
        });
    });

    form.addEventListener('submit', async (event) => {
        event.preventDefault();

        const fields = form.querySelectorAll('input, textarea');
        let isValid = true;
        let firstInvalidField = null;

        fields.forEach((field) => {
            const parent = field.closest('.input-field');
            const isRequired = field.hasAttribute('required');
            const value = field.value.trim();

            if (isRequired && !value) {
                parent?.classList.add('error');
                field.setAttribute('aria-invalid', 'true');
                if (!firstInvalidField) firstInvalidField = field;
                isValid = false;
            } else {
                parent?.classList.remove('error');
                field.removeAttribute('aria-invalid');
            }
        });

        const emailField = form.querySelector('input[name="email"]');
        const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (emailField && emailField.value.trim() && !emailPattern.test(emailField.value.trim())) {
            emailField.closest('.input-field')?.classList.add('error');
            emailField.setAttribute('aria-invalid', 'true');
            if (!firstInvalidField) firstInvalidField = emailField;
            isValid = false;
        }

        if (!isValid) {
            setStatus('必須項目を正しく入力してください。', 'error');
            firstInvalidField?.focus();
            return;
        }

        const configuredEndpoint = getEndpoint();
        if (!configuredEndpoint || configuredEndpoint.includes('your-form-id')) {
            setStatus('Formspreeの送信先URLが未設定です。フォームのactionを設定してください。', 'error');
            return;
        }

        const company = form.querySelector('input[name="company"]').value.trim();
        const name = form.querySelector('input[name="name"]').value.trim();
        const email = form.querySelector('input[name="email"]').value.trim();
        const phone = form.querySelector('input[name="phone"]').value.trim();
        const message = form.querySelector('textarea[name="message"]').value.trim();

        setSubmitting(true);
        setStatus('送信中です。しばらくお待ちください。');

        try {
            const response = await fetch(configuredEndpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    Accept: 'application/json'
                },
                body: JSON.stringify({
                    company,
                    name,
                    email,
                    phone,
                    message,
                    _subject: 'お問い合わせフォームからの送信'
                })
            });

            if (!response.ok) {
                let errorMessage = '送信に失敗しました。時間をおいて再度お試しください。';
                try {
                    const errorData = await response.json();
                    if (errorData?.errors?.length) {
                        errorMessage = errorData.errors.map((item) => item.message).join(' ');
                    }
                } catch (_error) {
                    // Keep fallback message when response body is not JSON.
                }
                throw new Error(errorMessage);
            }

            setStatus('お問い合わせありがとうございます。内容を送信しました。', 'success');
            form.reset();
        } catch (error) {
            setStatus(error.message || '送信に失敗しました。通信環境をご確認ください。', 'error');
        } finally {
            setSubmitting(false);
        }
    });
}

const fadeObserver = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
        if (entry.isIntersecting) {
            entry.target.classList.add('show');
            fadeObserver.unobserve(entry.target);
        }
    });
}, { threshold: 0.16, rootMargin: '0px 0px -8% 0px' });

if (reduceMotion) {
    fadeItems.forEach((item) => item.classList.add('show'));
} else {
    fadeItems.forEach((item) => fadeObserver.observe(item));
}

const sectionObserver = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
        if (entry.isIntersecting) {
            const id = entry.target.id;
            navLinks.forEach((link) => {
                link.classList.toggle('active', link.getAttribute('href') === `#${id}`);
            });
        }
    });
}, { threshold: 0.35 });

sections.forEach((section) => sectionObserver.observe(section));