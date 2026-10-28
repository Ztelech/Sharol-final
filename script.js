/* ==========================================================================
   UNIVERSO COLDY - SCRIPT CÓSMICO INTERACTIVO
   Canvas de estrellas, nebulosas, estrellas fugaces y efectos estelares
   ========================================================================== */

document.addEventListener('DOMContentLoaded', () => {
  initCosmicCanvas();
  initVideoControls();
});

function initCosmicCanvas() {
  const canvas = document.getElementById('space-canvas');
  if (!canvas) return;

  const ctx = canvas.getContext('2d');
  let width = (canvas.width = window.innerWidth);
  let height = (canvas.height = window.innerHeight);

  // Redimensionar al cambiar tamaño de ventana
  window.addEventListener('resize', () => {
    width = canvas.width = window.innerWidth;
    height = canvas.height = window.innerHeight;
    initStars();
  });

  // Parallax suave con el ratón
  let mouseX = 0;
  let mouseY = 0;
  let targetMouseX = 0;
  let targetMouseY = 0;

  window.addEventListener('mousemove', (e) => {
    targetMouseX = (e.clientX - width / 2) * 0.03;
    targetMouseY = (e.clientY - height / 2) * 0.03;
  });

  // Sistema de Estrellas
  const STAR_COUNT = Math.min(260, Math.floor((width * height) / 4500));
  let stars = [];

  const starColors = [
    'rgba(255, 255, 255, ',
    'rgba(216, 180, 254, ', // violeta
    'rgba(147, 197, 253, ', // azul celeste
    'rgba(254, 205, 211, ', // rosa suave
    'rgba(253, 230, 138, '  // dorado suave
  ];

  function initStars() {
    stars = [];
    for (let i = 0; i < STAR_COUNT; i++) {
      stars.push({
        x: Math.random() * width,
        y: Math.random() * height,
        baseSize: Math.random() * 1.8 + 0.4,
        alpha: Math.random(),
        twinkleSpeed: Math.random() * 0.02 + 0.005,
        twinkleDir: Math.random() > 0.5 ? 1 : -1,
        colorPrefix: starColors[Math.floor(Math.random() * starColors.length)],
        parallaxFactor: Math.random() * 0.8 + 0.2
      });
    }
  }

  initStars();

  // Sistema de Estrellas Fugaces (Shooting Stars)
  let shootingStars = [];

  function maybeCreateShootingStar() {
    if (shootingStars.length < 2 && Math.random() < 0.015) {
      const startX = Math.random() * width * 0.9;
      const startY = Math.random() * height * 0.4;
      const length = Math.random() * 100 + 70;
      const speed = Math.random() * 9 + 7;
      const angle = (Math.PI / 4) + (Math.random() - 0.5) * 0.3; // alrededor de 45 grados

      shootingStars.push({
        x: startX,
        y: startY,
        length: length,
        speed: speed,
        dx: Math.cos(angle) * speed,
        dy: Math.sin(angle) * speed,
        opacity: 1,
        fadeSpeed: Math.random() * 0.015 + 0.01,
        color: Math.random() > 0.4 ? '#f472b6' : '#38bdf8'
      });
    }
  }

  // Bucle de animación
  function animate() {
    // Parallax easing
    mouseX += (targetMouseX - mouseX) * 0.05;
    mouseY += (targetMouseY - mouseY) * 0.05;

    ctx.clearRect(0, 0, width, height);

    // Dibujar y animar estrellas que brillan y se apagan (Requirement #9)
    for (let i = 0; i < stars.length; i++) {
      const s = stars[i];

      // Twinkle calculation
      s.alpha += s.twinkleSpeed * s.twinkleDir;
      if (s.alpha >= 1) {
        s.alpha = 1;
        s.twinkleDir = -1;
      } else if (s.alpha <= 0.15) {
        s.alpha = 0.15;
        s.twinkleDir = 1;
      }

      // Parallax coordinate
      const renderX = s.x + mouseX * s.parallaxFactor;
      const renderY = s.y + mouseY * s.parallaxFactor;

      ctx.beginPath();
      ctx.arc(renderX, renderY, s.baseSize * (0.8 + s.alpha * 0.4), 0, Math.PI * 2);
      ctx.fillStyle = s.colorPrefix + s.alpha + ')';

      // Añadir resplandor para estrellas más brillantes
      if (s.alpha > 0.7 && s.baseSize > 1.2) {
        ctx.shadowBlur = 6;
        ctx.shadowColor = s.colorPrefix + '0.8)';
      } else {
        ctx.shadowBlur = 0;
      }

      ctx.fill();
    }
    ctx.shadowBlur = 0;

    // Actualizar y dibujar estrellas fugaces
    maybeCreateShootingStar();

    for (let i = shootingStars.length - 1; i >= 0; i--) {
      const ss = shootingStars[i];
      ss.x += ss.dx;
      ss.y += ss.dy;
      ss.opacity -= ss.fadeSpeed;

      if (ss.opacity <= 0 || ss.x > width || ss.y > height) {
        shootingStars.splice(i, 1);
        continue;
      }

      const tailX = ss.x - (ss.dx / ss.speed) * ss.length;
      const tailY = ss.y - (ss.dy / ss.speed) * ss.length;

      const grad = ctx.createLinearGradient(tailX, tailY, ss.x, ss.y);
      grad.addColorStop(0, 'rgba(255, 255, 255, 0)');
      grad.addColorStop(1, ss.color);

      ctx.beginPath();
      ctx.moveTo(tailX, tailY);
      ctx.lineTo(ss.x, ss.y);
      ctx.strokeStyle = grad;
      ctx.lineWidth = 2;
      ctx.stroke();

      // Cabeza brillante de la estrella fugaz
      ctx.beginPath();
      ctx.arc(ss.x, ss.y, 1.8, 0, Math.PI * 2);
      ctx.fillStyle = '#ffffff';
      ctx.shadowBlur = 8;
      ctx.shadowColor = ss.color;
      ctx.fill();
      ctx.shadowBlur = 0;
    }

    requestAnimationFrame(animate);
  }

  animate();
}

function initVideoControls() {
  const toggleSoundBtn = document.getElementById('toggle-yt-sound');
  const ytIframe = document.getElementById('featured-yt-iframe');

  if (toggleSoundBtn && ytIframe) {
    let isMuted = true;
    toggleSoundBtn.addEventListener('click', () => {
      // Intentar alternar comando postMessage a YouTube API
      if (isMuted) {
        ytIframe.contentWindow.postMessage('{"event":"command","func":"unMute","args":""}', '*');
        ytIframe.contentWindow.postMessage('{"event":"command","func":"playVideo","args":""}', '*');
        toggleSoundBtn.innerHTML = `
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon><path d="M19.07 4.93a10 10 0 0 1 0 14.14M15.54 8.46a5 5 0 0 1 0 7.07"></path></svg>
          Sonido Activado
        `;
        isMuted = false;
      } else {
        ytIframe.contentWindow.postMessage('{"event":"command","func":"mute","args":""}', '*');
        toggleSoundBtn.innerHTML = `
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon><line x1="23" y1="9" x2="17" y2="15"></line><line x1="17" y1="9" x2="23" y2="15"></line></svg>
          Activar Sonido
        `;
        isMuted = true;
      }
    });
  }
}
