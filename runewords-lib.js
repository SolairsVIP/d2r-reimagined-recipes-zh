(function (root) {
  'use strict';

  // Item-type hierarchy used by the original catalog's applicability filter.
  const parents = {
    meleitype: ['weapitype'], missitype: ['weapitype'], shlditype: ['armoitype'],
    torsitype: ['armoitype'], helmitype: ['armoitype'], circitype: ['helmitype'],
    axeitype: ['meleitype'], clubitype: ['meleitype'], hammitype: ['meleitype'],
    maceitype: ['meleitype'], poleitype: ['meleitype'], scepitype: ['meleitype'],
    stafitype: ['meleitype'], speaitype: ['meleitype'], sworitype: ['meleitype'],
    wanditype: ['meleitype'], knifitype: ['meleitype'], bowitype: ['missitype'],
    abowitype: ['amazitype', 'bowitype'], aspeitype: ['amazitype', 'speaitype'],
    h2hitype: ['assnitype', 'meleitype'], orbitype: ['sorcitype', 'weapitype'],
    phlmitype: ['barbitype', 'helmitype'], peltitype: ['druiitype', 'helmitype'],
    headitype: ['necritype', 'shlditype'], ashditype: ['palaitype', 'shlditype'],
    grimitype: ['warlitype', 'shlditype'],
  };

  function typeChain(code, seen = new Set()) {
    if (!code || seen.has(code)) return seen;
    seen.add(code);
    (parents[code] || []).forEach((parent) => typeChain(parent, seen));
    return seen;
  }

  function matchesType(types, selected) {
    if (!selected) return true;
    const selectedChain = typeChain(selected);
    return types.some((type) => typeChain(type.code).has(selected) || selectedChain.has(type.code));
  }

  function normalize(value) {
    return String(value || '').normalize('NFKC').toLowerCase().trim();
  }

  function findRunewords(entries, options = {}) {
    const words = normalize(options.query).split(/\s+/).filter(Boolean);
    return entries.filter((entry) => {
      if (!matchesType(entry.types, options.type)) return false;
      if (options.sockets && entry.runes.length !== Number(options.sockets)) return false;
      if (options.rune && !entry.runes.some((rune) => rune.code === options.rune)) return false;
      if (options.origin === 'original' && !entry.original) return false;
      if (options.origin === 'reimagined' && entry.original) return false;
      const text = normalize([
        entry.name, entry.englishName, entry.level,
        ...entry.types.map((type) => type.name),
        ...entry.runes.flatMap((rune) => [rune.name, rune.code, rune.number]),
        ...entry.properties,
      ].join(' '));
      return words.every((word) => text.includes(word));
    });
  }

  const api = { findRunewords, matchesType };
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  if (root) root.RunewordSearch = api;
})(typeof window !== 'undefined' ? window : null);
