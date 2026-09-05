/**
 * EarthScape Climate Agency — GSAP Animation Engine
 * Minimalist, Corporate Monochrome Animation System
 * Compatible with GSAP 3.12.5 + ScrollTrigger
 */

(function () {
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    // =========================================================
    // 1. PAGE LOAD ENTRANCE ANIMATION
    // =========================================================
    function animatePageEntrance() {
        if (prefersReducedMotion || !window.gsap) return;

        const tl = gsap.timeline({ defaults: { ease: 'power2.out' } });

        // Header slide down
        if (document.querySelector('.hud-header')) {
            tl.from('.hud-header', { y: -25, opacity: 0, duration: 0.45 });
        }

        // HUD Chips micro-bounce
        if (document.querySelectorAll('.hud-chip').length) {
            tl.from('.hud-chip', { scale: 0.92, opacity: 0, duration: 0.3, stagger: 0.04 }, '-=0.25');
        }

        // Sidebar Navigation rail
        if (document.querySelector('.nav-rail')) {
            tl.from('.nav-rail', { x: -30, opacity: 0, duration: 0.4 }, '-=0.2');
        }
        if (document.querySelectorAll('.nav-item').length) {
            tl.from('.nav-item', { x: -15, opacity: 0, duration: 0.3, stagger: 0.05 }, '-=0.25');
        }

        // Anomaly Banner
        if (document.querySelector('.anomaly-banner')) {
            tl.from('.anomaly-banner', { y: 15, opacity: 0, duration: 0.4, ease: 'back.out(1.2)' }, '-=0.2');
        }

        // Cards Stagger Reveal
        if (document.querySelectorAll('.cyber-card, .card').length) {
            tl.from('.kpi-grid .cyber-card, .kpi-grid .card', {
                y: 20,
                opacity: 0,
                duration: 0.4,
                stagger: 0.07,
                ease: 'power2.out'
            }, '-=0.2');

            // Remaining cards on screen
            tl.from('.cyber-card:not(.kpi-grid .cyber-card), .card:not(.kpi-grid .card)', {
                y: 20,
                opacity: 0,
                duration: 0.45,
                stagger: 0.09,
                ease: 'power2.out'
            }, '-=0.2');
        }
    }

    // =========================================================
    // 2. NUMBER COUNT-UP ANIMATION
    // =========================================================
    function animateCountUp(elementId, targetValue, decimals = 0, suffix = '') {
        if (prefersReducedMotion || !window.gsap) {
            const el = document.getElementById(elementId);
            if (el) el.textContent = targetValue.toLocaleString() + suffix;
            return;
        }

        const el = document.getElementById(elementId);
        if (!el) return;

        const currentText = el.textContent.replace(/[^0-9.-]/g, '');
        const startValue = parseFloat(currentText) || 0;
        const target = parseFloat(targetValue);
        if (isNaN(target)) return;

        const counter = { val: startValue };
        gsap.to(counter, {
            val: target,
            duration: 0.8,
            ease: 'power2.out',
            onUpdate: function () {
                const formatted = decimals > 0 ? counter.val.toFixed(decimals) : Math.round(counter.val).toLocaleString();
                el.textContent = formatted + suffix;
            }
        });
    }

    // =========================================================
    // 3. BUTTON & CARD MICRO-INTERACTIONS
    // =========================================================
    function initMicroInteractions() {
        if (prefersReducedMotion || !window.gsap) return;

        // Button click press physics
        document.querySelectorAll('.btn').forEach(btn => {
            btn.addEventListener('mousedown', () => {
                gsap.to(btn, { scale: 0.97, duration: 0.1, ease: 'power1.out' });
            });
            btn.addEventListener('mouseup', () => {
                gsap.to(btn, { scale: 1.03, duration: 0.15, ease: 'power1.out' });
            });
            btn.addEventListener('mouseleave', () => {
                gsap.to(btn, { scale: 1.0, duration: 0.2, ease: 'power1.out' });
            });
        });
    }

    // =========================================================
    // 4. SCROLL REVEAL (SCROLLTRIGGER)
    // =========================================================
    function initScrollTriggerAnimations() {
        if (prefersReducedMotion || !window.gsap || !window.ScrollTrigger) return;

        gsap.registerPlugin(ScrollTrigger);

        const scrollCards = document.querySelectorAll('.scroll-reveal');
        if (scrollCards.length) {
            ScrollTrigger.batch('.scroll-reveal', {
                onEnter: batch => gsap.from(batch, {
                    y: 25,
                    opacity: 0,
                    stagger: 0.1,
                    duration: 0.5,
                    ease: 'power2.out',
                    overwrite: true
                }),
                once: true
            });
        }
    }

    // =========================================================
    // 5. TOAST ALERTS (MONOCHROME / MINIMAL)
    // =========================================================
    function showToast(message, isCritical = false) {
        let container = document.getElementById('toast-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'toast-container';
            container.style.cssText = 'position:fixed; top:20px; right:20px; z-index:9999; display:flex; flex-direction:column; gap:8px; pointer-events:none;';
            document.body.appendChild(container);
        }

        const toast = document.createElement('div');
        toast.style.cssText = `
            pointer-events: auto;
            background: ${isCritical ? '#FEF2F2' : '#FFFFFF'};
            color: ${isCritical ? '#EF4444' : '#111111'};
            border: 1px solid ${isCritical ? '#FCA5A5' : '#E5E5E5'};
            border-left: 4px solid ${isCritical ? '#EF4444' : '#111111'};
            padding: 12px 18px;
            border-radius: 8px;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.8rem;
            font-weight: 600;
            box-shadow: 0 4px 16px rgba(0,0,0,0.08);
            display: flex;
            align-items: center;
            gap: 10px;
        `;
        toast.innerHTML = `<span>${isCritical ? '⚠️' : 'ℹ️'}</span> <span>${message}</span>`;
        container.appendChild(toast);

        if (window.gsap) {
            gsap.from(toast, { x: 50, opacity: 0, duration: 0.35, ease: 'power2.out' });
            setTimeout(() => {
                gsap.to(toast, {
                    x: 50,
                    opacity: 0,
                    duration: 0.3,
                    ease: 'power2.in',
                    onComplete: () => toast.remove()
                });
            }, 3500);
        } else {
            setTimeout(() => toast.remove(), 3500);
        }
    }

    // =========================================================
    // 6. DARK / LIGHT THEME TOGGLE
    // =========================================================
    function initThemeToggle() {
        const savedTheme = localStorage.getItem('earthscape_theme') || 'light';
        document.documentElement.setAttribute('data-theme', savedTheme);

        window.toggleTheme = function () {
            const current = document.documentElement.getAttribute('data-theme') || 'light';
            const next = current === 'dark' ? 'light' : 'dark';
            document.documentElement.setAttribute('data-theme', next);
            localStorage.setItem('earthscape_theme', next);

            const btn = document.getElementById('theme-toggle-btn');
            if (btn) btn.textContent = next === 'dark' ? '☀️ LIGHT' : '🌙 DARK';
        };

        const btn = document.getElementById('theme-toggle-btn');
        if (btn) btn.textContent = savedTheme === 'dark' ? '☀️ LIGHT' : '🌙 DARK';
    }

    // Initialize on DOM ready
    document.addEventListener('DOMContentLoaded', () => {
        initThemeToggle();
        animatePageEntrance();
        initMicroInteractions();
        initScrollTriggerAnimations();
    });

    // Expose utility functions globally
    window.EarthScape = {
        animateCountUp: animateCountUp,
        showToast: showToast,
        animatePageEntrance: animatePageEntrance
    };
})();
