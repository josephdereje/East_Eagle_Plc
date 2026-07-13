/**
 * East Eagle Trading PLC — Main JavaScript
 * Handles: particle background, scroll animations, counters,
 *          navbar effects, and mobile navigation.
 */

(function () {
    'use strict';

    /* ==========================================================
       PARTICLE BACKGROUND — futuristic floating gold dots
       ========================================================== */
    function initParticles() {
        const canvas = document.getElementById('particle-canvas');
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        let particles = [];
        let animId;

        function resize() {
            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;
        }

        function createParticles(count) {
            particles = [];
            for (let i = 0; i < count; i++) {
                particles.push({
                    x: Math.random() * canvas.width,
                    y: Math.random() * canvas.height,
                    radius: Math.random() * 1.5 + 0.5,
                    speedX: (Math.random() - 0.5) * 0.3,
                    speedY: (Math.random() - 0.5) * 0.3,
                    opacity: Math.random() * 0.5 + 0.1,
                });
            }
        }

        function drawParticles() {
            const isLight = document.documentElement.getAttribute('data-theme') === 'light';
            const particleColor = isLight ? '168, 132, 26' : '212, 175, 55';
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            particles.forEach(function (p, i) {
                ctx.beginPath();
                ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
                ctx.fillStyle = 'rgba(' + particleColor + ', ' + p.opacity + ')';
                ctx.fill();

                particles.slice(i + 1).forEach(function (p2) {
                    const dx = p.x - p2.x;
                    const dy = p.y - p2.y;
                    const dist = Math.sqrt(dx * dx + dy * dy);
                    if (dist < 120) {
                        ctx.beginPath();
                        ctx.moveTo(p.x, p.y);
                        ctx.lineTo(p2.x, p2.y);
                        ctx.strokeStyle = 'rgba(' + particleColor + ', ' + (0.08 * (1 - dist / 120)) + ')';
                        ctx.lineWidth = 0.5;
                        ctx.stroke();
                    }
                });

                // Move particle
                p.x += p.speedX;
                p.y += p.speedY;

                // Wrap around edges
                if (p.x < 0) p.x = canvas.width;
                if (p.x > canvas.width) p.x = 0;
                if (p.y < 0) p.y = canvas.height;
                if (p.y > canvas.height) p.y = 0;
            });

            animId = requestAnimationFrame(drawParticles);
        }

        resize();
        createParticles(Math.min(80, Math.floor(window.innerWidth / 15)));
        drawParticles();

        window.addEventListener('resize', function () {
            resize();
            createParticles(Math.min(80, Math.floor(window.innerWidth / 15)));
        });
    }

    /* ==========================================================
       SCROLL REVEAL — fade-in elements on scroll
       ========================================================== */
    function initScrollReveal() {
        const reveals = document.querySelectorAll('.reveal');
        if (!reveals.length) return;

        const observer = new IntersectionObserver(
            function (entries) {
                entries.forEach(function (entry) {
                    if (entry.isIntersecting) {
                        entry.target.classList.add('visible');
                        observer.unobserve(entry.target);
                    }
                });
            },
            { threshold: 0.15, rootMargin: '0px 0px -40px 0px' }
        );

        reveals.forEach(function (el) { observer.observe(el); });
    }

    /* ==========================================================
       COUNTER ANIMATION — animate stat numbers in hero
       ========================================================== */
    function initCounters() {
        const counters = document.querySelectorAll('.stat-number[data-target]');
        if (!counters.length) return;

        const observer = new IntersectionObserver(
            function (entries) {
                entries.forEach(function (entry) {
                    if (!entry.isIntersecting) return;

                    const el = entry.target;
                    const target = parseInt(el.getAttribute('data-target'), 10);
                    const duration = 2000;
                    const start = performance.now();

                    function update(now) {
                        const elapsed = now - start;
                        const progress = Math.min(elapsed / duration, 1);
                        // Ease-out cubic
                        const eased = 1 - Math.pow(1 - progress, 3);
                        el.textContent = Math.floor(eased * target);
                        if (progress < 1) requestAnimationFrame(update);
                        else el.textContent = target;
                    }

                    requestAnimationFrame(update);
                    observer.unobserve(el);
                });
            },
            { threshold: 0.5 }
        );

        counters.forEach(function (el) { observer.observe(el); });
    }

    /* ==========================================================
       NAVBAR — scroll effect & mobile toggle
       ========================================================== */
    function initNavbar() {
        const navbar = document.getElementById('navbar');
        const toggle = document.getElementById('nav-toggle');
        const menu = document.getElementById('nav-menu');

        function closeMenu() {
            if (!menu || !toggle) return;
            menu.classList.remove('open');
            toggle.classList.remove('open');
            toggle.setAttribute('aria-expanded', 'false');
            document.body.classList.remove('nav-open');
        }

        // Add shadow on scroll
        window.addEventListener('scroll', function () {
            if (!navbar) return;
            navbar.classList.toggle('scrolled', window.scrollY > 50);
        });

        // Mobile menu toggle
        if (toggle && menu) {
            toggle.addEventListener('click', function (e) {
                e.stopPropagation();
                const isOpen = menu.classList.toggle('open');
                toggle.classList.toggle('open', isOpen);
                toggle.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
                document.body.classList.toggle('nav-open', isOpen);
            });

            // Close menu on link click
            menu.querySelectorAll('.nav-link').forEach(function (link) {
                link.addEventListener('click', closeMenu);
            });

            // Close when tapping the dimmed backdrop
            document.addEventListener('click', function (e) {
                if (!document.body.classList.contains('nav-open')) return;
                if (menu.contains(e.target) || toggle.contains(e.target)) return;
                closeMenu();
            });

            document.addEventListener('keydown', function (e) {
                if (e.key === 'Escape') closeMenu();
            });
        }
    }

    /* ==========================================================
       SMOOTH ANCHOR SCROLLING for in-page links
       ========================================================== */
    function initSmoothScroll() {
        document.querySelectorAll('a[href^="#"]').forEach(function (anchor) {
            anchor.addEventListener('click', function (e) {
                const targetId = this.getAttribute('href');
                if (targetId === '#') return;

                const target = document.querySelector(targetId);
                if (target) {
                    e.preventDefault();
                    target.scrollIntoView({ behavior: 'smooth' });
                }
            });
        });
    }

    /* ==========================================================
       GOLD SHIMMER on primary buttons (hover effect)
       ========================================================== */
    function initButtonShimmer() {
        document.querySelectorAll('.btn-primary').forEach(function (btn) {
            btn.addEventListener('mouseenter', function () {
                this.style.background = 'linear-gradient(135deg, #E2C685, #FFD700, #D4AF37, #8F6E35)';
                this.style.backgroundSize = '300% 300%';
                this.style.animation = 'shimmerBtn 1.5s ease infinite';
            });
            btn.addEventListener('mouseleave', function () {
                this.style.animation = '';
                this.style.background = '';
                this.style.backgroundSize = '';
            });
        });

        // Inject shimmer keyframes if not present
        if (!document.getElementById('shimmer-style')) {
            const style = document.createElement('style');
            style.id = 'shimmer-style';
            style.textContent = '@keyframes shimmerBtn { 0%{background-position:0% 50%} 50%{background-position:100% 50%} 100%{background-position:0% 50%} }';
            document.head.appendChild(style);
        }
    }

    /* ==========================================================
       HERO SHOWCASE — clean fade, 5 slides max
       ========================================================== */
    function initHomeAdSlider() {
        const track = document.getElementById('home-ad-track');
        if (!track) return;

        const slides = track.querySelectorAll('.hero-showcase-slide');
        const captions = document.querySelectorAll('.hero-showcase-caption');
        const pills = document.querySelectorAll('.hero-showcase-pill');
        const prevBtn = document.getElementById('slider-prev');
        const nextBtn = document.getElementById('slider-next');

        if (slides.length <= 1) return;

        let current = 0;
        let autoplayTimer;
        const INTERVAL = 5500;

        function resetPillProgress() {
            pills.forEach(function (pill, i) {
                pill.classList.remove('active');
                void pill.offsetWidth;
                if (i === current) pill.classList.add('active');
            });
        }

        function goTo(index) {
            slides[current].classList.remove('active');
            if (captions[current]) captions[current].classList.remove('active');
            if (pills[current]) pills[current].classList.remove('active');

            current = (index + slides.length) % slides.length;

            slides[current].classList.add('active');
            if (captions[current]) captions[current].classList.add('active');
            resetPillProgress();
        }

        function next() { goTo(current + 1); }
        function prev() { goTo(current - 1); }

        function startAutoplay() {
            stopAutoplay();
            resetPillProgress();
            autoplayTimer = setInterval(next, INTERVAL);
        }

        function stopAutoplay() {
            if (autoplayTimer) clearInterval(autoplayTimer);
        }

        if (nextBtn) nextBtn.addEventListener('click', function () { next(); startAutoplay(); });
        if (prevBtn) prevBtn.addEventListener('click', function () { prev(); startAutoplay(); });

        pills.forEach(function (pill) {
            pill.addEventListener('click', function () {
                goTo(parseInt(this.getAttribute('data-index'), 10));
                startAutoplay();
            });
        });

        const slider = document.getElementById('home-ad-slider');
        if (slider) {
            slider.addEventListener('mouseenter', stopAutoplay);
            slider.addEventListener('mouseleave', startAutoplay);

            let touchStartX = 0;
            let touchStartY = 0;

            slider.addEventListener('touchstart', function (e) {
                if (!e.changedTouches[0]) return;
                touchStartX = e.changedTouches[0].screenX;
                touchStartY = e.changedTouches[0].screenY;
                stopAutoplay();
            }, { passive: true });

            slider.addEventListener('touchend', function (e) {
                if (!e.changedTouches[0]) return;
                const deltaX = e.changedTouches[0].screenX - touchStartX;
                const deltaY = e.changedTouches[0].screenY - touchStartY;
                if (Math.abs(deltaX) > 50 && Math.abs(deltaX) > Math.abs(deltaY)) {
                    if (deltaX < 0) next();
                    else prev();
                }
                startAutoplay();
            }, { passive: true });
        }

        resetPillProgress();
        startAutoplay();
    }

    /* ==========================================================
       THEME TOGGLE — day / night mode with localStorage
       ========================================================== */
    function initThemeToggle() {
        const toggle = document.getElementById('theme-toggle');
        if (!toggle) return;

        function setTheme(theme) {
            document.documentElement.setAttribute('data-theme', theme);
            localStorage.setItem('ee-theme', theme);
            document.dispatchEvent(new CustomEvent('themechange', { detail: { theme: theme } }));
        }

        toggle.addEventListener('click', function () {
            const current = document.documentElement.getAttribute('data-theme') || 'dark';
            setTheme(current === 'dark' ? 'light' : 'dark');
        });
    }

    /* ==========================================================
       AUTO-DISMISS flash messages after 5 seconds
       ========================================================== */
    function initFlashDismiss() {
        document.querySelectorAll('.flash').forEach(function (flash) {
            setTimeout(function () {
                flash.style.transition = 'opacity 0.5s ease';
                flash.style.opacity = '0';
                setTimeout(function () { flash.remove(); }, 500);
            }, 5000);
        });
    }

    /* ==========================================================
       INITIALIZE ALL on DOM ready
       ========================================================== */
    document.addEventListener('DOMContentLoaded', function () {
        if ('ontouchstart' in window || navigator.maxTouchPoints > 0) {
            document.documentElement.classList.add('is-touch');
        }

        initParticles();
        initScrollReveal();
        initCounters();
        initNavbar();
        initSmoothScroll();
        initButtonShimmer();
        initThemeToggle();
        initHomeAdSlider();
        initFlashDismiss();
    });

})();
