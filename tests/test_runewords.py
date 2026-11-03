import importlib.util
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data' / 'runewords.json'
SPEC = importlib.util.spec_from_file_location('build_runewords', ROOT / 'tools' / 'build_runewords.py')
BUILDER = importlib.util.module_from_spec(SPEC) if SPEC and SPEC.loader else None
if BUILDER:
    SPEC.loader.exec_module(BUILDER)


class RunewordDataTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(DATA.read_text(encoding='utf-8')) if DATA.exists() else None

    def test_all_source_rows_are_kept_including_base_variants(self):
        self.assertIsNotNone(self.data, '应生成中文符文之语数据')
        self.assertEqual(len(self.data['runewords']), 220)
        leaf = [r for r in self.data['runewords'] if r['englishName'] == 'Leaf']
        self.assertEqual(len(leaf), 2)
        self.assertNotEqual(leaf[0]['types'], leaf[1]['types'])
        self.assertNotEqual(leaf[0]['properties'], leaf[1]['properties'])

    def test_spirit_keeps_order_level_and_allowed_bases(self):
        spirit = next(r for r in self.data['runewords'] if r['englishName'] == 'Spirit')
        self.assertEqual(spirit['name'], '精神')
        self.assertEqual(spirit['level'], 25)
        self.assertEqual([r['code'] for r in spirit['runes']], ['r07', 'r10', 'r09', 'r11'])
        self.assertEqual({t['code'] for t in spirit['types']}, {'sworitype', 'shlditype'})
        self.assertIn('+2 所有技能', spirit['properties'])

    def test_visible_text_has_no_untranslated_or_unfilled_tokens(self):
        for entry in self.data['runewords']:
            fields = [entry['name'], *(r['name'] for r in entry['runes']),
                      *(t['name'] for t in entry['types']), *entry['properties']]
            for value in fields:
                self.assertFalse(re.search(r'[A-Za-z]|%(?:[+]?d|[sSiD]|\d)', value), (entry['name'], value))

    def test_download_and_browser_payload_match(self):
        script = DATA.with_suffix('.js').read_text(encoding='utf-8')
        self.assertTrue(script.startswith('window.RUNEWORD_DATA = '))
        self.assertEqual(json.loads(script.removeprefix('window.RUNEWORD_DATA = ').removesuffix(';\n')), self.data)

    def test_localized_numeric_ranges_and_indexed_arguments(self):
        self.assertIsNotNone(BUILDER)
        self.assertEqual(BUILDER.format_template('施法速度 %+d%%', [25, 30]), '施法速度 +25-30%')
        self.assertEqual(BUILDER.format_template('每 %1 秒修复 %0 点耐久度', [1, 12]), '每 12 秒修复 1 点耐久度')
        self.assertEqual(BUILDER.format_template('附加 %d - %d 点火焰伤害', [5, 30]), '附加 5 - 30 点火焰伤害')


if __name__ == '__main__':
    unittest.main()
