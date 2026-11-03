const test = require('node:test');
const assert = require('node:assert/strict');
const { findRecipes } = require('../lib.js');

const recipes = [
  { group: '赫拉迪姆方块', section: '打孔', inputs: ['魔法物品', '魔法珠宝'], output: '获得孔位' },
  { group: '装备附魔', section: '武器', inputs: ['武器', '红宝石'], output: '火焰伤害' },
  { group: '物品制作', section: '武器', inputs: ['魔法武器', '红宝石'], output: '新的手工武器' },
];

test('搜索可同时匹配材料与结果中的多个词', () => {
  assert.deepEqual(findRecipes(recipes, { query: '红宝石 火焰' }), [recipes[1]]);
});

test('分组和小类筛选同时生效', () => {
  assert.deepEqual(findRecipes(recipes, { group: '物品制作', section: '武器' }), [recipes[2]]);
});

test('空搜索显示所有配方，找不到时返回空列表', () => {
  assert.equal(findRecipes(recipes, {}).length, 3);
  assert.deepEqual(findRecipes(recipes, { query: '不存在的材料' }), []);
});
