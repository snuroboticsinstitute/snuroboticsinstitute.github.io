(() => {
  const theme = document.documentElement.dataset.theme;
  const here = new URL(location.href);
  document.querySelectorAll('[data-theme-choice]').forEach(link => {
    const url = new URL(here);
    url.searchParams.set('theme', link.dataset.themeChoice);
    link.href = url.href;
    link.setAttribute('aria-current', String(link.dataset.themeChoice === theme));
  });
  document.querySelectorAll('a[href]').forEach(link => {
    if (link.hasAttribute('data-theme-choice') || link.getAttribute('href').startsWith('#')) return;
    const url = new URL(link.href, location.href);
    if (url.origin === location.origin) {
      if (link.hasAttribute('hreflang')) url.hash = here.hash;
      url.searchParams.set('theme', theme);
      link.href = url.href;
    }
  });
  if (theme === 'light') {
    document.querySelectorAll('img.side-logo,img.mobile-logo').forEach(img => {
      img.src = img.src.replace('snu-official-crest-white.png', 'snu-official-crest.png');
    });
  }
  const language = document.documentElement.lang === 'en' ? 'en' : 'kr';
  document.querySelectorAll('img.nrl-header-mark,img.nrl-mark').forEach(img => {
    const logoVariant = theme === 'light' && !img.closest('.hero') ? 'color' : 'reversed';
    img.src = '/assets/nrl2-official-' + language + '-' + logoVariant + '.png';
    img.classList.toggle('nrl-en', language === 'en');
  });
})();
