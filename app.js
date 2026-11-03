(function () {
  'use strict';
  const data = window.RECIPE_DATA;
  const $ = (id) => document.getElementById(id);
  const groups = [
    { name: '全部', label: '全部配方', icon: '✧' },
    { name: '赫拉迪姆方块', label: '方块合成', icon: '◇' },
    { name: '装备附魔', label: '装备附魔', icon: '✦' },
    { name: '物品制作', label: '物品制作', icon: '⚒' },
  ];
  const sectionNotes = {
    '打孔': '可用于武器、盾牌、盔甲和头盔；首饰、腰带、手套和靴子不能打孔。孔数受物品等级与底材上限限制；打孔宝珠也能重掷已有孔数。珠宝数量对应最终孔数。',
    '拆除镶嵌物': '符文钳用于符文之语，珠宝钳不能用于符文之语。拆除后孔数保留，取出的镶嵌物会返还；钳子可从各幕铁匠商人处购买。',
    '材料转换': '带星号的卷轴书会满格返还。变成白色底材的配方会重新生成物品，清除原有附魔与腐化效果。原表另有一项未明确对应配方的说明：物品升级为或保持精英级，并可能额外获得超强词缀，效果不再叠加；请核对原文。',
    '宝珠改变品质': '这些配方改变物品品质；单颗宝珠不属于重新生成配方。结果指定相同底材类型时会保留原底材类型。',
    '回收': '卷轴书会满格返还。五件装备须为同一部位或类型，例如五双手套；弹药指箭矢或弩箭。',
    '重掷': '卷轴书会满格返还。以角色等级为准表示结果等级按角色等级计算；以物品等级为准表示按输入物品等级计算。',
    '重新生成': '重新生成会重置现有属性，并移除腐化和升级。曾升级底材的物品可能变为该底材可生成的其他物品。',
    '火炬与遗物升级': '火炬最多升级六次。原资料列出的毁灭小护身符三宝珠附魔不再各自提供 1% 经验值。',
    '破免护身符': '同一元素的焕新破免护身符只能携带一个；制作前请将已有成品放入共享储物箱。\n焕新品可获得六组词缀：① 5–15% 元素技能伤害或元素穿抗、50–100% 增强武器伤害，或 +1 元素技能；② 20–30% 魔法装备获取几率或 40–60% 金币获取量；③ 20–50 生命、20–50 法力或 50–100 防御；④ 10–20% 跑步／行走速度、15–20% 打击恢复或 5–10 全属性；⑤ 移除或减半负抗惩罚；⑥ 5–15% 攻击速度或施法速度。',
  };
  const groupNotes = {
    '装备附魔': '每件物品最多附魔一次，并受属性数值上限限制，例如所有技能无法超过 +7。套装附魔前，请先将同套装的其他部件放入共享储物箱，保存退出并重新进入游戏，否则附魔可能只在套装加成生效时起作用。',
    '物品制作': '魔法、稀有和手工成品会在保底属性之外获得不同数量的随机词缀。除非另有说明，成品等级与制作角色等级相同。',
  };
  const state = { group: '全部', section: '全部', query: '', shown: 24 };
  const search = $('search-input');
  let matches = [];

  function element(tag, className, text) {
    const el = document.createElement(tag);
    if (className) el.className = className;
    if (text != null) el.textContent = text;
    return el;
  }
  function reset() {
    state.group = '全部'; state.section = '全部'; state.query = ''; state.shown = 24;
    search.value = '';
    render();
  }
  function renderGroups() {
    const box = $('group-list'); box.replaceChildren();
    groups.forEach((group) => {
      const count = group.name === '全部' ? data.recipes.length : data.recipes.filter((r) => r.group === group.name).length;
      const button = element('button', `group-button${state.group === group.name ? ' active' : ''}`);
      button.type = 'button'; button.setAttribute('aria-pressed', String(state.group === group.name));
      button.append(element('span', 'group-icon', group.icon), element('span', 'group-text', group.label), element('span', 'group-count', count));
      button.addEventListener('click', () => { state.group = group.name; state.section = '全部'; state.shown = 24; render(); });
      box.append(button);
    });
  }
  function renderSections() {
    const all = data.recipes.filter((r) => state.group === '全部' || r.group === state.group);
    const sections = ['全部', ...new Set(all.map((r) => r.section))];
    const box = $('section-list'); box.replaceChildren();
    sections.forEach((name) => {
      const button = element('button', `section-button${state.section === name ? ' active' : ''}`, name);
      button.type = 'button'; button.setAttribute('aria-pressed', String(state.section === name));
      button.addEventListener('click', () => { state.section = name; state.shown = 24; render(); });
      box.append(button);
    });
  }
  function renderNote() {
    const note = $('context-note');
    const text = sectionNotes[state.section] || groupNotes[state.group];
    note.hidden = !text; note.replaceChildren();
    if (text) note.append(element('strong', null, '使用提示'), element('p', null, text));
  }
  function recipeCard(recipe) {
    const card = element('article', 'recipe-card');
    const meta = element('div', 'recipe-meta');
    meta.append(element('span', 'recipe-number', `配方 ${String(recipe.id).padStart(3, '0')}`), element('span', 'recipe-section', recipe.section));
    const input = element('div'); input.append(element('span', 'recipe-label', '所需材料'));
    const ingredients = element('div', 'ingredients');
    recipe.inputs.forEach((item, index) => {
      if (index) ingredients.append(element('span', 'plus', '+'));
      ingredients.append(element('span', 'ingredient', item));
    });
    input.append(ingredients);
    const output = element('div'); output.append(element('span', 'recipe-label', '转化结果'), element('div', 'recipe-output', recipe.output));
    card.append(meta, input, element('div', 'recipe-arrow', '→'), output);
    return card;
  }
  function renderResults() {
    matches = window.RecipeSearch.findRecipes(data.recipes, state);
    const title = state.section !== '全部' ? state.section : (groups.find((g) => g.name === state.group) || groups[0]).label;
    $('result-title').textContent = title;
    $('result-count').textContent = `找到 ${matches.length} 条配方`;
    const box = $('recipe-list'); box.replaceChildren(...matches.slice(0, state.shown).map(recipeCard));
    $('empty-state').hidden = matches.length > 0;
    $('load-more').hidden = matches.length <= state.shown;
    $('load-more').firstChild.textContent = `加载更多配方（已显示 ${Math.min(matches.length, state.shown)} / ${matches.length}） `;
  }
  function render() {
    $('total-count').textContent = data.recipes.length;
    $('updated-date').textContent = `原始资料更新：${data.sourceUpdated.slice(0, 10)}（世界协调时）`;
    search.parentElement.classList.toggle('has-value', Boolean(search.value));
    renderGroups(); renderSections(); renderNote(); renderResults();
  }
  search.addEventListener('input', () => { state.query = search.value; state.shown = 24; render(); });
  $('clear-search').addEventListener('click', () => { search.value = ''; state.query = ''; state.shown = 24; render(); search.focus(); });
  $('reset-filters').addEventListener('click', reset);
  $('empty-reset').addEventListener('click', reset);
  $('load-more').addEventListener('click', () => { state.shown += 24; renderResults(); });
  document.addEventListener('keydown', (event) => {
    if (event.key === '/' && !event.ctrlKey && !event.metaKey && !event.altKey && !/INPUT|TEXTAREA/.test(document.activeElement.tagName)) {
      event.preventDefault(); search.focus();
    }
  });
  render();
})();
