(function () {
  'use strict';
  const data = window.RUNEWORD_DATA;
  const $ = (id) => document.getElementById(id);
  const search = $('rw-search');
  const type = $('rw-type');
  const sockets = $('rw-sockets');
  const rune = $('rw-rune');
  const origin = $('rw-origin');
  const pageSize = 12;
  let shown = pageSize;
  let matches = [];

  function element(tag, className, text) {
    const el = document.createElement(tag);
    if (className) el.className = className;
    if (text != null) el.textContent = text;
    return el;
  }

  function buildOptions() {
    const types = new Map();
    const runes = new Map();
    data.runewords.forEach((entry) => {
      entry.types.forEach((item) => types.set(item.code, item.name));
      entry.runes.forEach((item) => runes.set(item.code, item));
    });
    [...types.entries()].sort((a, b) => a[1].localeCompare(b[1], 'zh-CN')).forEach(([code, name]) => {
      const option = element('option', '', name); option.value = code; type.append(option);
    });
    [...runes.values()].sort((a, b) => a.number - b.number).forEach((item) => {
      const option = element('option', '', `${item.number} 号 · ${item.name}`); option.value = item.code; rune.append(option);
    });
  }

  function card(entry) {
    const article = element('article', 'rw-card');
    const header = element('div', 'rw-card-header');
    const heading = element('div');
    heading.append(element('h3', '', entry.name), element('span', 'rw-origin', entry.original ? '原版词条' : '重构词条'));
    header.append(heading, element('span', 'rw-level', `需要等级 ${entry.level}`));

    const runes = element('div', 'rw-runes');
    entry.runes.forEach((item, index) => {
      if (index) runes.append(element('span', 'rw-rune-separator', '→'));
      const chip = element('span', 'rw-rune');
      chip.append(element('span', 'rw-rune-number', item.number), document.createTextNode(item.name));
      runes.append(chip);
    });

    const base = element('p', 'rw-base');
    base.append(element('span', '', '适用底材'), document.createTextNode(entry.types.map((item) => item.name).join(' / ')));
    const properties = element('ul', 'rw-properties');
    entry.properties.forEach((property) => properties.append(element('li', '', property)));
    article.append(header, element('div', 'rw-label', `${entry.runes.length} 个符文 · 按顺序镶入`), runes, base, properties);
    return article;
  }

  function renderResults() {
    $('rw-count').textContent = `找到 ${matches.length} 条记录`;
    $('rw-list').replaceChildren(...matches.slice(0, shown).map(card));
    $('rw-empty').hidden = matches.length > 0;
    const more = $('rw-more');
    more.hidden = matches.length <= shown;
    more.firstChild.textContent = `加载更多（已显示 ${Math.min(shown, matches.length)} / ${matches.length}） `;
  }

  function render() {
    search.parentElement.classList.toggle('has-value', Boolean(search.value));
    matches = window.RunewordSearch.findRunewords(data.runewords, {
      query: search.value, type: type.value, sockets: sockets.value, rune: rune.value, origin: origin.value,
    });
    renderResults();
  }

  function reset() {
    search.value = ''; type.value = ''; sockets.value = ''; rune.value = ''; origin.value = '';
    shown = pageSize; render();
  }

  buildOptions();
  $('rw-total').textContent = data.runewords.length;
  $('rw-updated').textContent = `原始资料更新：${data.sourceUpdated.slice(0, 10)}（世界协调时）`;
  [search, type, sockets, rune, origin].forEach((control) => {
    control.addEventListener(control === search ? 'input' : 'change', () => { shown = pageSize; render(); });
  });
  $('rw-clear-search').addEventListener('click', () => { search.value = ''; shown = pageSize; render(); search.focus(); });
  $('rw-reset').addEventListener('click', reset);
  $('rw-empty-reset').addEventListener('click', reset);
  $('rw-more').addEventListener('click', () => { shown += pageSize; renderResults(); });
  document.addEventListener('keydown', (event) => {
    if (event.key === '/' && !event.ctrlKey && !event.metaKey && !event.altKey && !/INPUT|TEXTAREA|SELECT/.test(document.activeElement.tagName)) {
      event.preventDefault(); search.focus();
    }
  });
  render();
})();
