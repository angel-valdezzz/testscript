/* Approved language-map motion. Native MkDocs owns palette and locale navigation. */
(() => {
  'use strict';
  const root = document.querySelector('.ts-home');
  if (!root) return;
  const $ = selector => root.querySelector(selector);
  const concepts = [...root.querySelectorAll('.ts-concept')];
  const score = $('#ts-score');
  const pause = $('#ts-pause');
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  const language = root.dataset.lang;
  const copy = {
    es: {pause:'Pausar animación',resume:'Reanudar animación',reduced:'Movimiento reducido'},
    en: {pause:'Pause animation',resume:'Resume animation',reduced:'Reduced motion'}
  };
  let paused = false;
  let elapsed = 0;
  let last = null;
  let visible = true;
  let routes = [];
  const hold = 1500;
  const transfers = [1100, 1100, 1100, 1600];
  const cycle = hold * 4 + transfers.reduce((a, b) => a + b, 0);
  function updatePause() {
    pause.disabled = reduced.matches;
    pause.setAttribute('aria-pressed', String(paused));
    const state = reduced.matches ? 'reduced' : paused ? 'resume' : 'pause';
    pause.querySelector('span').textContent = copy[language][state];
    pause.querySelector('path').setAttribute('d', paused && !reduced.matches ? 'M5 3l7 5-7 5Z' : 'M5 3v10M11 3v10');
    root.classList.toggle('ts-paused', paused || reduced.matches);
  }
  pause.addEventListener('click', () => { if (!reduced.matches) { paused = !paused; updatePause(); } });
  document.addEventListener('visibilitychange', () => { last = null; });
  if (typeof IntersectionObserver !== 'undefined') new IntersectionObserver(entries => { visible = entries[0].isIntersecting; last = null; }, {threshold: 0}).observe(score);

  const lerp = (a, b, t) => a + (b - a) * t;
  const distance = (a, b) => Math.hypot(a.x - b.x, a.y - b.y);
  // Rounded polylines keep the light in the vacant connector lanes, never across the words.
  function rounded(points) {
    const samples = [{...points[0]}];
    let previous = points[0];
    function line(end) {
      const start = previous;
      const steps = Math.max(1, Math.ceil(distance(start, end) / 4));
      for (let i = 1; i <= steps; i++) samples.push({x: lerp(start.x, end.x, i / steps), y: lerp(start.y, end.y, i / steps)});
      previous = end;
    }
    for (let i = 1; i < points.length - 1; i++) {
      const before = points[i - 1], corner = points[i], after = points[i + 1];
      const radius = Math.min(23, distance(before, corner) * .3, distance(corner, after) * .3);
      const enter = {x: lerp(corner.x, before.x, radius / distance(before, corner)), y: lerp(corner.y, before.y, radius / distance(before, corner))};
      const leave = {x: lerp(corner.x, after.x, radius / distance(corner, after)), y: lerp(corner.y, after.y, radius / distance(corner, after))};
      line(enter);
      for (let j = 1; j <= 16; j++) {
        const t = j / 16, u = 1 - t;
        samples.push({x: u * u * enter.x + 2 * u * t * corner.x + t * t * leave.x, y: u * u * enter.y + 2 * u * t * corner.y + t * t * leave.y});
      }
      previous = leave;
    }
    line(points.at(-1));
    return samples;
  }
  function path(points) { return points.map((p, i) => `${i ? 'L' : 'M'}${p.x.toFixed(2)} ${p.y.toFixed(2)}`).join(' '); }
  function geometry() {
    let rect = score.getBoundingClientRect();
    if (rect.width <= 0 || rect.height <= 0) return;
    const contentBottom = Math.max(...concepts.map(el => el.getBoundingClientRect().bottom - rect.top));
    // Leave separate lanes for the return trace and the caption, even when translations wrap.
    score.style.minHeight = `${Math.ceil(contentBottom + 55)}px`;
    rect = score.getBoundingClientRect();
    $('.ts-connections').setAttribute('viewBox', `0 0 ${rect.width} ${rect.height}`);
    const pins = concepts.map(el => {
      const box = el.querySelector('.ts-pin i').getBoundingClientRect();
      return {x: box.left - rect.left + box.width / 2, y: box.top - rect.top + box.height / 2};
    });
    const mobile = pins[2].x < pins[1].x;
    const bottom = rect.height - 31;
    routes = pins.map((p, i) => {
      const next = pins[(i + 1) % 4];
      let points;
      if (i === 3) points = [p, {x: rect.width + 8, y: p.y}, {x: rect.width + 8, y: bottom}, {x: -8, y: bottom}, {x: -8, y: next.y}, next];
      else if (mobile && i === 1) {
        const upperBottom = Math.max(...ts-concepts.slice(0, 2).map(el => el.getBoundingClientRect().bottom - rect.top));
        const lane = (upperBottom + next.y) / 2;
        points = [p, {x: rect.width + 8, y: p.y}, {x: rect.width + 8, y: lane}, {x: -8, y: lane}, {x: -8, y: next.y}, next];
      } else points = [p, {x: next.x - 18, y: p.y}, {x: next.x - 18, y: next.y}, next];
      return rounded(points);
    });
    $('#ts-track').setAttribute('d', routes.map(path).join(' '));
    paint();
  }
  function energy(index, amount) {
    concepts[index].style.setProperty('--energy', amount.toFixed(3));
    concepts[index].style.setProperty('--lift', amount.toFixed(3));
  }
  function paint() {
    if (!routes.length) return;
    concepts.forEach((_, i) => energy(i, reduced.matches ? .8 : .12));
    if (reduced.matches) {
      $('#ts-trail').setAttribute('d', ''); $('#ts-halo').setAttribute('d', '');
      $('#ts-beam').style.opacity = '0'; $('#ts-orbit').style.opacity = '0';
      score.dataset.phase = 'reduced';
      return;
    }
    let t = elapsed % cycle, current = 0;
    while (t >= hold + transfers[current]) { t -= hold + transfers[current]; current++; }
    const moving = t >= hold;
    const progress = moving ? (t - hold) / transfers[current] : 0;
    const smooth = progress * progress * (3 - 2 * progress);
    const route = routes[current];
    const position = smooth * (route.length - 1);
    const low = Math.floor(position), high = Math.min(low + 1, route.length - 1);
    const dot = {x: lerp(route[low].x, route[high].x, position - low), y: lerp(route[low].y, route[high].y, position - low)};
    const trailLength = Math.max(2, Math.round(route.length * .16));
    const trailPoints = moving ? [...route.slice(Math.max(0, low - trailLength), low + 1), dot] : [];
    const d = trailPoints.length ? path(trailPoints) : '';
    $('#ts-trail').setAttribute('d', d); $('#ts-halo').setAttribute('d', d);
    $('#ts-beam').setAttribute('cx', dot.x); $('#ts-beam').setAttribute('cy', dot.y);
    $('#ts-beam').style.opacity = '1';
    const spin = elapsed / 260;
    $('#ts-orbit').setAttribute('cx', dot.x + Math.cos(spin) * 10);
    $('#ts-orbit').setAttribute('cy', dot.y + Math.sin(spin) * 10);
    $('#ts-orbit').style.opacity = moving ? '.3' : '.8';
    energy(current, moving ? 1 - .85 * smooth : .92 + .08 * Math.sin(t / 180));
    if (moving) energy((current + 1) % 4, .12 + .88 * smooth);
    score.dataset.active = String(current);
    score.dataset.phase = moving ? 'travel' : 'hold';
  }
  function animate(now) {
    if (last !== null && !paused && !reduced.matches && visible && !document.hidden) elapsed += Math.min(now - last, 80);
    last = now;
    paint();
    requestAnimationFrame(animate);
  }
  reduced.addEventListener('change', () => { last = null; updatePause(); paint(); });
  window.addEventListener('resize', geometry);
  if (typeof ResizeObserver !== 'undefined') new ResizeObserver(geometry).observe(score);
  updatePause(); geometry(); pause.hidden = false;
  const search = document.querySelector('.ts-search-trigger');
  search?.addEventListener('keydown', event => {
    if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); search.click(); }
  });
  root.querySelector('.ts-scroll-link').addEventListener('click', () => $('#ts-language-section').focus({preventScroll:true}));
  if (document.fonts) document.fonts.ready.then(geometry);
  requestAnimationFrame(animate);
})();
