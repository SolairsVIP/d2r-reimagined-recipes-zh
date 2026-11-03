import json
import re
import unittest
from pathlib import Path

DATA = Path(__file__).resolve().parents[1] / 'data' / 'recipes.json'


class RecipeDataTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if DATA.exists():
            cls.data = json.loads(DATA.read_text(encoding='utf-8'))
        else:
            cls.data = None

    def test_data_is_present_and_contains_all_three_systems(self):
        self.assertIsNotNone(self.data, '应生成中文配方数据')
        self.assertEqual({r['group'] for r in self.data['recipes']}, {'赫拉迪姆方块', '装备附魔', '物品制作'})
        # The 2026-11-02 source contains 690 recipe rows after table headers
        # and the two in-table section labels are excluded.
        self.assertEqual(len(self.data['recipes']), 690)

    def test_socketing_recipe_retains_material_and_result(self):
        self.assertIsNotNone(self.data, '应生成中文配方数据')
        rows = [r for r in self.data['recipes'] if r['section'] == '打孔']
        self.assertTrue(any('魔法珠宝' in ' '.join(r['inputs']) and '孔' in r['output'] for r in rows))

    def test_uber_upgrade_keeps_exact_bonus_and_limit(self):
        self.assertIsNotNone(self.data, '应生成中文配方数据')
        rows = [r for r in self.data['recipes'] if '火炬' in ' '.join(r['inputs'])]
        self.assertTrue(any('+2' in r['output'] and '6' in r['output'] for r in rows))

    def test_renewed_sunder_recipe_is_present(self):
        self.assertIsNotNone(self.data, '应生成中文配方数据')
        rows = [r for r in self.data['recipes'] if r['section'] == '破免护身符']
        self.assertTrue(any('潜藏' in ' '.join(r['inputs']) and '焕新' in r['output'] for r in rows))

    def test_visible_recipe_text_is_chinese(self):
        self.assertIsNotNone(self.data, '应生成中文配方数据')
        leaks = []
        for row in self.data['recipes']:
            text = ' '.join(row['inputs']) + ' ' + row['output']
            if re.search(r'[A-Za-z]', text):
                leaks.append(text)
        self.assertEqual(leaks[:10], [], '配方显示文字仍有未翻译内容')

    def test_browser_data_matches_downloadable_data(self):
        self.assertIsNotNone(self.data, '应生成中文配方数据')
        script = DATA.with_suffix('.js').read_text(encoding='utf-8')
        self.assertTrue(script.startswith('window.RECIPE_DATA = '))
        browser_data = json.loads(script.removeprefix('window.RECIPE_DATA = ').removesuffix(';\n'))
        self.assertEqual(browser_data, self.data)


if __name__ == '__main__':
    unittest.main()
