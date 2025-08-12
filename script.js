/* Workout Worriers — Cinematic Scroll Script */

window.addEventListener('DOMContentLoaded', () => {
  const prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // Smooth scroll
  const lenis = new Lenis({
    duration: prefersReduced ? 0.6 : 1.2,
    easing: t => (t === 1 ? 1 : 1 - Math.pow(2, -10 * t)),
    smoothWheel: !prefersReduced,
    smoothTouch: !prefersReduced,
  });
  function raf(time) {
    lenis.raf(time);
    requestAnimationFrame(raf);
  }
  requestAnimationFrame(raf);

  // GSAP setup
  gsap.registerPlugin(ScrollTrigger);

  // Sync Lenis with ScrollTrigger
  lenis.on('scroll', ScrollTrigger.update);
  ScrollTrigger.scrollerProxy(document.documentElement, {
    scrollTop(value) {
      return arguments.length ? window.scrollTo(0, value) : window.pageYOffset;
    },
    getBoundingClientRect() {
      return { top: 0, left: 0, width: window.innerWidth, height: window.innerHeight };
    }
  });
  ScrollTrigger.addEventListener('refresh', () => lenis.update());
  ScrollTrigger.refresh();

  // Split headings
  const splitTargets = document.querySelectorAll('.heading-split');
  splitTargets.forEach(target => {
    const split = new SplitType(target, { types: 'words,chars' });
    gsap.fromTo(split.chars, { yPercent: 120, opacity: 0 }, {
      yPercent: 0, opacity: 1, stagger: 0.02, duration: 0.9,
      ease: 'power3.out',
      scrollTrigger: {
        trigger: target,
        start: 'top 85%',
        once: true,
      }
    });
  });

  // Reveal ups
  gsap.utils.toArray('.reveal-up').forEach(el => {
    gsap.to(el, {
      opacity: 1, y: 0, duration: 0.8, ease: 'power3.out',
      scrollTrigger: { trigger: el, start: 'top 85%', once: true }
    });
  });

  // Zoom-ins
  gsap.utils.toArray('.zoom-in').forEach(el => {
    gsap.to(el, {
      opacity: 1, scale: 1, duration: 0.9, ease: 'power3.out',
      scrollTrigger: { trigger: el, start: 'top 85%', once: true }
    });
  });

  // Parallax elements
  const parallaxEls = document.querySelectorAll('.parallax');
  parallaxEls.forEach(el => {
    const speed = parseFloat(el.getAttribute('data-speed') || '0.15');
    gsap.to(el, {
      yPercent: prefersReduced ? 0 : speed * -100,
      ease: 'none',
      scrollTrigger: {
        trigger: el.closest('.section') || el,
        start: 'top bottom',
        end: 'bottom top',
        scrub: true,
      }
    });
  });

  // Achievements counter animation
  const nums = document.querySelectorAll('.achieve-num');
  nums.forEach(el => {
    const raw = (el.getAttribute('data-count') || '').trim();
    // Extract leading number; keep suffix like + or k if provided
    const match = raw.match(/([\d.]+)(.*)/);
    const targetVal = match ? parseFloat(match[1]) : 0;
    const suffix = match ? match[2] : '';
    const isK = /k/i.test(suffix);
    const finalVal = isK ? targetVal * 1000 : targetVal;
    const pretty = v => {
      if (isK) return Math.round(v / 100) / 10 + 'k' + (suffix.includes('+') ? '+' : '');
      return Math.round(v) + (suffix || '');
    };
    ScrollTrigger.create({
      trigger: el,
      start: 'top 85%',
      once: true,
      onEnter: () => {
        gsap.fromTo({ val: 0 }, { val: finalVal, duration: 1.2, ease: 'power3.out', onUpdate: function() {
          el.textContent = pretty(this.targets()[0].val);
        }});
      }
    });
  });

  // Circular rings animation
  const circumference = 2 * Math.PI * 54;
  document.querySelectorAll('.ring').forEach(ring => {
    const progress = ring.querySelector('.progress');
    const numEl = ring.querySelector('.ring-num');
    const target = parseFloat(ring.getAttribute('data-target')) || 0; // negative for body fat
    const normalized = Math.max(Math.min(target, 100), -100);

    ScrollTrigger.create({
      trigger: ring,
      start: 'top 85%',
      once: true,
      onEnter: () => {
        const toValue = Math.abs(normalized);
        gsap.fromTo(progress, { strokeDashoffset: circumference }, {
          strokeDashoffset: circumference * (1 - toValue / 100), duration: 1.4, ease: 'power3.out'
        });
        gsap.fromTo({ val: 0 }, { val: target, duration: 1.4, ease: 'power3.out', onUpdate: function() {
          const v = Math.round(this.targets()[0].val);
          numEl.textContent = `${v > 0 ? v : v}%`;
        }});
      }
    });
  });

  // Before/After slider interactions
  const sliders = document.querySelectorAll('.ba-slider');
  sliders.forEach(slider => {
    const after = slider.querySelector('.after');
    const handle = slider.querySelector('.ba-handle');
    const setRatio = r => {
      const clamped = Math.max(0.05, Math.min(0.95, r));
      after.style.clipPath = `inset(0 0 0 ${clamped * 100}%)`;
      handle.setAttribute('aria-valuenow', Math.round(clamped * 100));
    };
    let active = false;
    const onMove = x => {
      const rect = slider.getBoundingClientRect();
      const ratio = (x - rect.left) / rect.width;
      setRatio(ratio);
    };
    slider.addEventListener('pointerdown', e => { active = true; onMove(e.clientX); slider.setPointerCapture(e.pointerId); });
    slider.addEventListener('pointermove', e => { if (active) onMove(e.clientX); });
    slider.addEventListener('pointerup', e => { active = false; slider.releasePointerCapture(e.pointerId); });
    slider.addEventListener('pointercancel', () => { active = false; });
    // Keyboard
    handle.addEventListener('keydown', e => {
      const current = parseInt(handle.getAttribute('aria-valuenow')) || 50;
      if (e.key === 'ArrowLeft') setRatio((current - 5) / 100);
      if (e.key === 'ArrowRight') setRatio((current + 5) / 100);
    });
  });

  // Horizontal scroll for Transform section (desktop)
  const track = document.querySelector('#transformTrack');
  if (track && window.matchMedia('(min-width: 901px)').matches) {
    const cards = track.querySelectorAll('.story-card');
    const totalWidth = Array.from(cards).reduce((acc, el) => acc + el.offsetWidth + 24, 0);
    const container = track.closest('.h-scroll-wrapper');
    const scrollLength = Math.max(0, totalWidth - window.innerWidth + 200);

    gsap.to(track, {
      x: () => -(scrollLength),
      ease: 'none',
      scrollTrigger: {
        trigger: container,
        start: 'top top',
        end: () => `+=${scrollLength}`,
        scrub: true,
        pin: true,
        anticipatePin: 1,
      }
    });
  }

  // Video controls
  const video = document.querySelector('.hero-video');
  const toggleBtn = document.querySelector('.video-toggle');
  if (video) {
    video.play().catch(() => {});
    if (toggleBtn) {
      const toggle = () => {
        if (video.paused) { video.play(); } else { video.pause(); }
      };
      toggleBtn.addEventListener('click', toggle);
      video.addEventListener('pointerenter', () => video.pause());
      video.addEventListener('pointerleave', () => video.play());
    }
  }

  // Footer year
  const yearEl = document.getElementById('year');
  if (yearEl) yearEl.textContent = new Date().getFullYear();
});