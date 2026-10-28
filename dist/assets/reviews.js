(() => {
  const board = document.querySelector('[data-reviews]');
  if (!board) return;
  const lang = document.documentElement.lang === 'en' ? 'en' : 'ko';
  const PAGE = 6;
  const ordinal = n => n + (n % 100 >= 11 && n % 100 <= 13 ? 'th' : ['th', 'st', 'nd', 'rd'][n % 10] || 'th');
  const T = {
    ko: { all: '전체', round: n => `제${n}회 로보콘`, more: '후기 더 보기', expand: '더보기', collapse: '접기', empty: '등록된 후기가 없습니다.' },
    en: { all: 'All', round: n => `${ordinal(n)} Robocon`, more: 'Show more reviews', expand: 'Read more', collapse: 'Show less', empty: 'No reviews yet.' }
  }[lang];
  const el = (tag, cls, text) => {
    const node = document.createElement(tag);
    if (cls) node.className = cls;
    if (text) node.textContent = text;
    return node;
  };

  fetch(board.dataset.reviews, { cache: 'no-cache' })
    .then(r => r.ok ? r.json() : Promise.reject(r.status))
    .then(data => {
      const reviews = (data.reviews || []).slice().sort((a, b) => b.year - a.year);
      const years = [...new Set(reviews.map(r => r.year))];
      let year = null, shown = PAGE;

      const filters = el('div', 'review-filters');
      filters.setAttribute('role', 'group');
      const list = el('div', 'voice-grid');
      const moreBtn = el('button', 'review-more', T.more);
      moreBtn.type = 'button';

      const options = [[null, T.all], ...years.map(y => {
        const r = reviews.find(x => x.year === y);
        return [y, `${y} · ${T.round(r.robocon)}`];
      })];
      options.forEach(([y, label]) => {
        const b = el('button', 'review-filter', label);
        b.type = 'button';
        b.addEventListener('click', () => { year = y; shown = PAGE; render(); });
        b.dataset.year = y === null ? '' : y;
        filters.append(b);
      });
      moreBtn.addEventListener('click', () => { shown += PAGE; render(); });

      const card = r => {
        const a = el('article', 'voice-card');
        a.id = 'review-' + r.id;
        const head = el('header');
        head.append(el('h4', '', r.team[lang]), el('p', 'voice-result', r.result[lang]));
        a.append(head);
        if (lang === 'ko' && r.members) a.append(el('p', 'voice-members', r.members));
        a.append(el('p', 'voice-meta', `${r.year} · ${T.round(r.robocon)}`));
        if (r.summary && r.summary[lang]) a.append(el('p', 'voice-desc', r.summary[lang]));
        const q = el('blockquote', 'is-clamped');
        q.append(el('p', '', r.text[lang]));
        a.append(q);
        const toggle = el('button', 'review-toggle', T.expand);
        toggle.type = 'button';
        toggle.setAttribute('aria-expanded', 'false');
        toggle.addEventListener('click', () => {
          const open = q.classList.toggle('is-clamped') === false;
          toggle.textContent = open ? T.collapse : T.expand;
          toggle.setAttribute('aria-expanded', String(open));
        });
        a.append(toggle);
        return a;
      };

      const render = () => {
        const items = reviews.filter(r => year === null || r.year === year);
        list.replaceChildren(...items.slice(0, shown).map(card));
        if (!items.length) list.append(el('p', 'member-empty', T.empty));
        moreBtn.hidden = items.length <= shown;
        filters.querySelectorAll('button').forEach(b => b.setAttribute('aria-pressed', String(b.dataset.year === (year === null ? '' : String(year)))));
        filters.hidden = years.length < 2;
        // Hide "read more" when the quote already fits in two lines
        requestAnimationFrame(() => list.querySelectorAll('.voice-card').forEach(c => {
          const t = c.querySelector('blockquote p');
          c.querySelector('.review-toggle').hidden = t.scrollHeight <= t.clientHeight + 1;
        }));
      };

      board.replaceChildren(filters, list, moreBtn);
      render();
    })
    .catch(() => {});
})();
