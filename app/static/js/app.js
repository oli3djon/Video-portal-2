// --- Темы и тосты ---
(function () {
  const key = 'vp-theme';
  const btn = document.getElementById('themeToggle');

  function applyTheme(val) {
    document.documentElement.setAttribute('data-bs-theme', val);
  }
  function current() {
    return localStorage.getItem(key) || 'auto';
  }

  // Инициализация
  applyTheme(current());

  // Переключение: auto -> dark -> light -> auto
  btn?.addEventListener('click', () => {
    const order = ['auto', 'dark', 'light'];
    const next = order[(order.indexOf(current()) + 1) % order.length];
    localStorage.setItem(key, next);
    applyTheme(next);
  });

  // Авто-показ bootstrap-тостов (если есть во вёрстке)
  const toasts = document.querySelectorAll('.toast');
  toasts.forEach(t => {
    const toast = new bootstrap.Toast(t, { delay: 3500 });
    toast.show();
  });
})();

// --- Превью видео при наведении ---
document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll(".preview-wrap").forEach(wrap => {
    const video = wrap.querySelector(".preview-video");
    const overlay = wrap.querySelector(".video-overlay");

    if (!video) return;

    // Наведение мышью — запуск
    wrap.addEventListener("mouseenter", () => {
      if (overlay) overlay.style.display = "none";
      try {
        video.muted = true;
        video.currentTime = 0;
        video.style.display = "block";
        video.play();
      } catch (err) {
        console.warn("Autoplay error:", err);
      }
    });

    // Уход мыши — стоп и возврат обложки
    wrap.addEventListener("mouseleave", () => {
      video.pause();
      video.currentTime = 0;
      video.style.display = "none";
      if (overlay) overlay.style.display = "block";
    });

    // Для мобилок: короткое касание = запуск, отпускание = стоп
    wrap.addEventListener("touchstart", () => {
      if (overlay) overlay.style.display = "none";
      video.style.display = "block";
      video.play();
    }, { passive: true });

    wrap.addEventListener("touchend", () => {
      video.pause();
      video.currentTime = 0;
      video.style.display = "none";
      if (overlay) overlay.style.display = "block";
    }, { passive: true });
  });
});



