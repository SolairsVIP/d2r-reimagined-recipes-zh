"""Build the static Chinese runeword data from the mod's keyed exports.

The templates and numerical arguments come from D2R Reimagined's public data.
Template handling follows the conventions of its website's format-template.ts.
"""
import argparse
import json
import math
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOKENS = re.compile(r'%(?:\+d|d|D|s|S|i|c\d|\d|%)')
NUMERIC = {'%d', '%D', '%i', '%+d'}
TYPE_LABELS = {
    'meleitype': '近战武器', 'barbitype': '野蛮人物品', 'druiitype': '德鲁伊物品',
    'necritype': '死灵法师物品', 'palaitype': '圣骑士物品',
}
CUSTOM_RUNES = {
    'Brak符文': '布拉克符文', 'Zeph符文': '泽弗符文', 'Myr符文': '米尔符文',
    'Grit符文': '格里特符文', 'Dem符文': '德姆符文', 'Hev符文': '赫夫符文',
}
SCOPE_KEYS = {'weapon': 'strRuneScopeWeapon', 'shield': 'strRuneScopeShield', 'armor': 'strRuneScopeArmor'}


def format_arg(value, token):
    if value is None:
        return ''
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        result = str(value) if isinstance(value, int) else format(value, '.15g')
        return ('+' if token == '%+d' and value >= 0 else '') + result
    return str(value)


def format_template(template, args):
    """Resolve D2R placeholders, including min/max pairs and indexed arguments."""
    tokens = TOKENS.findall(template)
    sequential = [t for t in tokens if t != '%%' and not re.fullmatch(r'%\d|%c\d', t)]
    numeric_count = sum(t in NUMERIC for t in sequential)
    pair_budget = max(0, min(len(args) - len(sequential), numeric_count))
    indexed = [int(t[1]) for t in tokens if re.fullmatch(r'%\d', t)]
    slots = max(indexed) + 1 if indexed else 0
    resolved = None
    if slots and len(args) > slots:
        resolved, pos, budget = [], 0, len(args) - slots
        for _ in range(slots):
            first = args[pos] if pos < len(args) else None
            second = args[pos + 1] if pos + 1 < len(args) else None
            if budget > 0 and isinstance(first, (int, float)) and isinstance(second, (int, float)):
                value = format_arg(first, '%d')
                if first != second:
                    value += '-' + format_arg(second, '%d')
                resolved.append(value)
                pos += 2
                budget -= 1
            else:
                resolved.append(format_arg(first, '%0'))
                pos += 1

    position = 0

    def replace(match):
        nonlocal position, pair_budget
        token = match.group()
        if token == '%%':
            return '%'
        if re.fullmatch(r'%c\d', token):
            return ''
        if re.fullmatch(r'%\d', token):
            index = int(token[1])
            return resolved[index] if resolved is not None and index < len(resolved) else format_arg(args[index] if index < len(args) else None, token)
        value = args[position] if position < len(args) else None
        position += 1
        if token in NUMERIC and pair_budget:
            pair_budget -= 1
            other = args[position] if position < len(args) else None
            position += 1
            text = format_arg(value, token)
            if isinstance(value, (int, float)) and isinstance(other, (int, float)) and math.isfinite(value) and math.isfinite(other) and value != other:
                text += '-' + format_arg(other, '%d' if token == '%+d' else token)
            return text
        return format_arg(value, token)

    return TOKENS.sub(replace, template)


def clean_label(value):
    if value.startswith('['):
        value = next((part for part in re.split(r'\[[a-z]{2}\]', value) if part), value)
    return value


def lookup(strings, key):
    if key in TYPE_LABELS:
        return TYPE_LABELS[key]
    if key not in strings:
        raise ValueError(f'缺少中文游戏文本：{key}')
    return clean_label(strings[key])


def localized_line(line, strings):
    key = line['key']
    template = lookup(strings, key)
    args = [lookup(strings, arg) if isinstance(arg, str) else arg for arg in line.get('args', [])]
    if key == 'healperhit' and args:
        template = '%d ' + template
    if key == 'strSkillRandomFromSkillClass' and len(args) >= 2:
        if isinstance(args[0], (int, float)) and isinstance(args[1], (int, float)):
            low, high, *rest = args
            value = str(math.trunc(low)) if math.trunc(low) == math.trunc(high) else f'{math.trunc(low)}-{math.trunc(high)}'
            template = re.sub(r'\s*%s\s*$', '', template) if len(rest) < 2 else template
            args = [value, *rest]
        elif len(args) < 3:
            template = re.sub(r'\s*%s\s*$', '', template)
    result = format_template(template, args)
    if line.get('perLevel'):
        result += lookup(strings, 'strPerCharacterLevelSuffix')
    if line.get('qualifier'):
        result += lookup(strings, SCOPE_KEYS[line['qualifier']])
    if line.get('classOnly'):
        result += ' ' + lookup(strings, line['classOnly'])
    return result


def extract(items, chinese, english, source_updated):
    entries = []
    for item in items:
        if not item.get('Enabled', True):
            continue
        runes = []
        for rune in item['Runes']:
            code = rune['NameKey']
            name = re.sub(r'\s*\(#\d+\)\s*$', '', lookup(chinese, code))
            name = CUSTOM_RUNES.get(name, name)
            runes.append({'code': code, 'name': name, 'number': int(code[1:])})
        entries.append({
            'id': len(entries) + 1,
            'key': item['Index'],
            'name': lookup(chinese, item['Index']),
            'englishName': english.get(item['Index'], item['Index']),
            'original': item['Vanilla'] == 'Y',
            'level': item['RequiredLevel'],
            'runes': runes,
            'types': [{'code': t['Index'], 'name': lookup(chinese, t['Index'])} for t in item['Types']],
            'properties': [localized_line(line, chinese) for line in item['Lines']],
        })
    return {
        'source': 'https://www.d2r-reimagined.com/data/runewords',
        'sourceUpdated': source_updated,
        'runewords': entries,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('runewords', type=Path)
    parser.add_argument('chinese', type=Path)
    parser.add_argument('english', type=Path)
    parser.add_argument('--source-updated', required=True, help='官网数据的更新时间（ISO 8601）')
    args = parser.parse_args()
    load = lambda path: json.loads(path.read_text(encoding='utf-8'))
    data = extract(load(args.runewords), load(args.chinese), load(args.english), args.source_updated)
    payload = json.dumps(data, ensure_ascii=False, indent=2) + '\n'
    target = ROOT / 'data'
    target.mkdir(exist_ok=True)
    (target / 'runewords.json').write_text(payload, encoding='utf-8', newline='\n')
    (target / 'runewords.js').write_text('window.RUNEWORD_DATA = ' + payload.rstrip() + ';\n', encoding='utf-8', newline='\n')
    print(f"Wrote {len(data['runewords'])} runewords")


if __name__ == '__main__':
    main()
