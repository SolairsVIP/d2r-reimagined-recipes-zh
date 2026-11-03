const test = require('node:test');
const assert = require('node:assert/strict');
const { findRunewords } = require('../runewords-lib.js');

const entries = [
  { name: '精神', englishName: 'Spirit', level: 25, types: [{ code: 'sworitype', name: '剑' }], runes: [{ code: 'r07', name: '塔尔符文' }, { code: 'r10', name: '书尔符文' }], properties: ['所有技能 +2'] },
  { name: '奢求之愿', englishName: 'Desire', level: 13, types: [{ code: 'weapitype', name: '任意武器' }], runes: [{ code: 'r01', name: '艾尔符文' }, { code: 'r03', name: '特尔符文' }, { code: 'r01', name: '艾尔符文' }], properties: ['伤害强化 +30-50%'] },
  { name: '测试', englishName: 'Example', level: 20, types: [{ code: 'axeitype', name: '斧' }], runes: [{ code: 'r01', name: '艾尔符文' }, { code: 'r02', name: '艾德符文' }], properties: ['生命 +20'] },
];

test('搜索同时匹配中文、英文名称和词缀', () => {
  assert.deepEqual(findRunewords(entries, { query: '精神 书尔' }), [entries[0]]);
  assert.deepEqual(findRunewords(entries, { query: 'spirit 技能' }), [entries[0]]);
});

test('底材筛选包含上位通用类别，排除不相容的具体类别', () => {
  assert.deepEqual(findRunewords(entries, { type: 'sworitype' }), [entries[0], entries[1]]);
});

test('孔数和符文筛选可同时生效', () => {
  assert.deepEqual(findRunewords(entries, { sockets: 2, rune: 'r01' }), [entries[2]]);
});
