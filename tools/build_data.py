"""Extract the factual recipe tables from a locally downloaded wiki Markdown file."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / 'source_recipes.tmp'

GROUPS = {
    'Cube Recipes': '赫拉迪姆方块',
    'Item Enchant System': '装备附魔',
    'Item Crafting System': '物品制作',
}
SECTIONS = {
    'Socket Recipes': '打孔', 'Unsocket Recipes': '拆除镶嵌物', 'Conversion Recipes': '材料转换',
    'Orb Quality Conversion Recipes': '宝珠改变品质', 'Recycle Recipes': '回收', 'Reroll Recipes': '重掷',
    'Regenerate (Divine Orb) Recipes': '重新生成', 'Armor & Weapon Base Upgrade Recipes': '底材升级',
    'Repair Recipes': '修理与补充', 'Uber Charm and Relic Upgrades': '火炬与遗物升级', 'Portal Recipes': '传送门',
    'Amulets': '项链', 'Rings': '戒指', 'Belts': '腰带', 'Boots': '靴子', 'Gloves': '手套',
    'Helms': '头盔', 'Shields': '盾牌', 'Body Armor': '盔甲', 'Weapons': '武器',
    'Charms': '护身小符', 'Sunder Charms': '破免护身符', 'Jewel Crafts': '宝石工艺',
}
RUNES = {
    'El':'艾尔', 'Eld':'艾德', 'Tir':'特尔', 'Nef':'那夫', 'Eth':'爱斯', 'Ith':'伊司', 'Tal':'塔尔',
    'Ral':'拉尔', 'Ort':'欧特', 'Thul':'书尔', 'Amn':'安姆', 'Sol':'索尔', 'Shael':'沙尔', 'Dol':'多尔',
    'Hel':'海尔', 'Io':'埃欧', 'Lum':'卢姆', 'Ko':'科', 'Fal':'法尔', 'Lem':'蓝姆', 'Pul':'普尔',
    'Um':'乌姆', 'Mal':'马尔', 'Ist':'伊司特', 'Gul':'古尔', 'Vex':'维克斯', 'Ohm':'欧姆', 'Lo':'罗',
    'Sur':'瑟', 'Ber':'贝', 'Jah':'乔', 'Cham':'查姆', 'Zod':'萨德', 'Brak':'布拉克', 'Zeph':'泽弗',
    'Myr':'米尔', 'Grit':'格里特', 'Dem':'德姆', 'Hev':'赫夫',
}

# Longer terms are applied first so game mechanics retain their meaning.
TERMS = {
    '100% drop from Ubers': '超级首领必定掉落', '1 of each': '每种各 1 个',
    '2 Hand': '双手', '1 Hand': '单手', '1H': '单手', '2H': '双手', 'Forced prefix': '固定前缀', 'Forced suffix': '固定后缀',
    'Random Skill Tab': '随机技能系', 'Enhanced Dmg': '增强伤害',
    'Life / Kill': '每击杀回复生命', 'Mana / Kill': '每击杀回复法力', 'FRW': '更快跑步／行走速度',
    'vs Melee': '对近战攻击', 'vs Missiles': '对远程攻击', 'Demon Heal': '击杀恶魔回复生命',
    'Replenish': '恢复', 'Seconds': '秒', 'per': '每', 'Savage': '野蛮',
    'Light': '闪电', 'Reduction': '减免', 'Increase': '提升', 'Adds': '附加',
    'Latent': '潜藏的', 'Runes': '符文', 'Rune': '符文', 'Base': '底材', 'Becomes': '变为',
    'Return': '返回', 'Rolls': '词缀', 'as': '为', 'and': '及', 'of': '的', 'Enhanced': '增强',
    "Upgrade the Torch: +2 to all Attributes and +2% to All Resistances (up to 6 upgrades, as reported by the new recipe export). A separate Obsidian Beacon outcome is also listed in the export.": '升级火炬：全属性 +2，所有抗性 +2%；最多升级 6 次。新配方导出中还列有独立的黑曜石信标结果。',
    "Relic gains +1 to your Class Skill Levels and +5% Increased Maximum Life.": '遗物获得 +1 本职业技能等级及 +5% 最大生命值。',
    "Relic gains +1 to your Class Skill Levels and +5% Magic Resistance.": '遗物获得 +1 本职业技能等级及 +5% 魔法抗性。',
    "Relic gains +1 to your Class Skill Levels and +5% to All Maximum Resistances.": '遗物获得 +1 本职业技能等级及 +5% 所有最大抗性。',
    "Item is upgraded to or remains Elite, and can gain superior modifiers in addition to the granted modifiers.": '物品升级为或保持精英底材，并可能在附加属性之外获得超强词缀。',
    "This recipe no longer stacks on items.": '此配方的效果不再叠加。',
    "Item is regenerated as a new white item.": '物品会重新生成为新的普通白色物品。',
    'Enchants/Corruption wiped.': '附魔和腐化效果将被清除。',
    'Selling this to any vendor spawns DClone': '出售给任意商人后会触发暗黑破坏神分身',
    'in place of next Super Unique monster': '取代下一个超级暗金怪物',
    'sells just like SOJ': '出售方式与乔丹之石相同',
    'DOES NOT WORK ON:': '不适用于：', 'Items without Durability': '没有耐久度的物品',
    'Bows or Crossbows': '弓或弩', 'Indestructible items': '无法破坏的物品',
    'Return Helm Base as White, Elite, Maximum Sockets, Superior Rolls and Enhanced Defense': '返回白色精英头盔底材，最大孔数，带超强词缀及增强防御',
    'Return Shield Base as White, Elite, Maximum Sockets, Superior Rolls and Enhanced Defense': '返回白色精英盾牌底材，最大孔数，带超强词缀及增强防御',
    'Return Torso Base as White, Elite, Maximum Sockets, Superior Rolls and Enhanced Defense': '返回白色精英盔甲底材，最大孔数，带超强词缀及增强防御',
    'Return Weapon Base as White, Elite, Maximum Sockets, Superior Rolls and Enhanced Damage': '返回白色精英武器底材，最大孔数，带超强词缀及增强伤害',
    'Mephisto’s Animus': '墨菲斯托之魂', "Mephisto's Animus": '墨菲斯托之魂', "Baal's Calamity": '巴尔之灾', "Diablo's Ire": '迪亚波罗之怒',
    "Korlic's Pain Statue": '科力克的痛苦雕像', "Talic's Anguish Statue": '塔力克的苦楚雕像',
    "Madawc's Ire Statue": '马道克的怒火雕像', "Bul-Kathos' Nightmare Statue": '布尔凯索的梦魇雕像', "Worusk's End Statue": '沃鲁斯克的终焉雕像',
    "Diablo's Horn": '迪亚波罗之角', "Baal's Eye": '巴尔之眼', "Mephisto's Brain": '墨菲斯托之脑',
    "Wirt's Leg": '维特之腿', "Matron's Den": '女族长之巢',
    'Portal to Tristram (Pandemonium Finale)': '通往崔斯特瑞姆的传送门（混沌终战）',
    'Portal to Colossal Summit (Colossal Ancients)': '通往巨人山巅的传送门（巨人先祖）',
    'Random Portal To:': '随机开启传送门，通往：', 'Forgotten Sands': '遗忘沙漠', 'Furnace of Pain': '痛苦熔炉', 'Cow Level': '奶牛关',
    'Latent Crack of the Heavens': '潜藏的天裂', 'Renewed Crack of the Heavens': '焕新的天裂',
    'Latent Cold Rupture': '潜藏的寒冰破裂', 'Renewed Cold Rupture': '焕新的寒冰破裂',
    'Latent Rotting Fissure': '潜藏的腐烂裂隙', 'Renewed Rotting Fissure': '焕新的腐烂裂隙',
    'Latent Flame Rift': '潜藏的烈焰裂隙', 'Renewed Flame Rift': '焕新的烈焰裂隙',
    'Latent Bone Break': '潜藏的断骨', 'Renewed Bone Break': '焕新的断骨',
    'Latent Black Cleft': '潜藏的黑色裂缝', 'Renewed Black Cleft': '焕新的黑色裂缝',
    'Latent Charm of the same type': '相同类型的潜藏护身符',
    'Western Worldstone Shard': '西方世界之石碎片', 'Eastern Worldstone Shard': '东方世界之石碎片',
    'Southern Worldstone Shard': '南方世界之石碎片', 'Northern Worldstone Shard': '北方世界之石碎片', 'Deep Worldstone Shard': '深层世界之石碎片',
    'Relic of the Ancients': '先祖遗物', 'Standard of Heroes': '英雄旗帜', 'Standard of Terror': '恐惧旗帜',
    'Hellfire Torch': '地狱火炬', 'Uber Spirits': '超级首领之魂', 'Obsidian Beacon': '黑曜石信标',
    'Key of Terror': '恐惧之钥', 'Key of Hate': '憎恨之钥', 'Key of Destruction': '毁灭之钥',
    'Orb of Socketing': '打孔宝珠', 'Orb of Assemblage': '套装宝珠', 'Orb of Conversion': '转换宝珠',
    'Orb of Corruption': '腐化宝珠', 'Orb of Infusion': '注入宝珠', 'Orb of Renewal': '更新宝珠',
    'Orb of Shadows': '暗影宝珠', 'Shadow Orb': '暗影宝珠', 'Conversion Orb': '转换宝珠',
    'Infusion Orb': '注入宝珠', 'Corruption Orb': '腐化宝珠',
    'Tome of Town Portal': '回城卷轴书', 'TP Tome': '回城卷轴书', 'ID Tome': '辨识卷轴书',
    'Rune Pliers': '符文钳', 'Jewel Pliers': '珠宝钳', 'Gem Cluster': '宝石簇', 'Gem Bag': '宝石袋',
    'Full Rejuvenation Potion': '全面回复药剂', 'Rejuvenation Potions': '回复药剂', 'Rejuvenation Potion': '回复药剂',
    'Healing Potions': '治疗药剂', 'Healing Potion': '治疗药剂', 'Exploding Potion': '爆炸药剂',
    'Thawing Potion': '解冻药剂', 'Antidote Potion': '解毒药剂', 'Chaos Onyx': '混沌缟玛瑙',
    'Prismatic Amulet': '棱彩项链', 'Garnet Ring': '石榴石戒指', 'Cobalt Ring': '钴蓝戒指',
    'Jade Ring': '翡翠戒指', 'Coral Ring': '珊瑚戒指', "Barilzar's Mazed Band": '巴利扎的迷乱之戒',
    'Winter Facet': '冬之刻面', 'Summer Facet': '夏之刻面', 'Spring Facet': '春之刻面', 'Autumn Facet': '秋之刻面',
    'Star Facet': '星之刻面', 'Jade Facet': '翡翠刻面', 'Heaven Facet': '天堂刻面',
    'Increased Chance of Blocking': '格挡几率提升', 'Chance Items Roll Magic or Better': '获得魔法或更高品质物品的几率',
    'Chance to cast level': '几率施放等级', 'CTC level': '几率施放等级', 'when you Level-Up': '在升级时', 'on level up': '在升级时',
    'when struck': '在受到攻击时', 'Battle Orders': '战斗体制', 'Battle Commands': '战斗指挥', 'Battle Command': '战斗指挥',
    'Frost Nova': '霜之新星', 'Frozen Armor': '冰封装甲', 'Burst of Speed': '速度爆发', 'Holy Shield': '神圣之盾',
    'Oak Sage': '橡木智者', 'Fade': '能量消解', 'Shout': '大叫',
    'Hits Cause Monsters to Flee': '命中使怪物逃跑', 'Attacker Takes Damage of': '攻击者受到伤害',
    'Extra Gold from Monsters': '怪物金币掉落增加', 'Life after each Demon Kill': '每击杀恶魔回复生命',
    'Life after each Kill': '每击杀回复生命', 'Mana after each Kill': '每击杀回复法力',
    'Damage Taken Added To Mana': '受到伤害转为法力', 'Damage to Mana': '伤害转为法力',
    'Life stolen per hit': '每次命中偷取生命', 'Mana stolen per hit': '每次命中偷取法力',
    'Physical Damage Reduced By': '物理伤害减少', 'Magic Damage Reduced By': '魔法伤害减少',
    'Physical Damage Reduction': '物理伤害减免', 'Magic Damage Reduced': '魔法伤害减少', 'Damage Reduced': '伤害减少',
    'Faster Run/Walk Speed': '更快跑步／行走速度', 'Faster Run/Walk': '更快跑步／行走', 'Faster Hit Recovery': '更快打击恢复',
    'Faster Attack Speed': '更快攻击速度', 'Increased Attack Speed': '攻击速度提升', 'Faster Cast Rate': '更快施法速度',
    'Increased Cast Rate': '施法速度提升', 'Faster Block Rate': '更快格挡速度',
    'Enhanced Weapon Damage': '增强武器伤害', 'Enhanced Defense': '增强防御', 'Enhanced Damage': '增强伤害',
    'Increased Maximum Life': '最大生命值提升', 'Increased Maximum Mana': '最大法力值提升',
    'Minimum Weapon Damage': '最小武器伤害', 'Maximum Weapon Damage': '最大武器伤害',
    'Mana Regeneration': '法力恢复速度', 'Mana Regen': '法力恢复速度', 'Attack Rating': '攻击准确率',
    'All Elemental Skill Damage': '所有元素技能伤害', 'All Enemy Elemental Resistances': '所有敌人元素抗性',
    'Enemy Physical Damage Resistance': '敌人物理伤害抗性', 'Enemy Magic Resistance': '敌人魔法抗性',
    'All Resistances': '所有抗性', 'All Resists': '所有抗性', 'All Res': '所有抗性', 'All-res': '所有抗性',
    'All Skills': '所有技能', 'Skill Levels': '技能等级', 'Skill Damage': '技能伤害', 'Skill Tab': '技能系',
    'Open Wounds': '撕开伤口', 'Deadly Strike': '致命攻击', 'Piercing Attack': '穿刺攻击',
    'Magic Find': '魔法装备获取几率', 'Gold Find': '金币获取量', 'Cannot Be Frozen': '无法冰冻',
    'Half Freeze Duration': '冰冻时间减半', 'Ignore Target\'s Defense': '忽略目标防御', 'Knockback': '击退',
    'Replenish Life': '生命恢复', 'Defense vs. Missile': '对远程攻击的防御', 'Defense vs. Melee': '对近战攻击的防御',
    'Current Class Skills': '当前职业技能', 'Random Class': '随机职业', 'current class': '当前职业',
    'Amazon': '亚马逊', 'Assassin': '刺客', 'Barbarian': '野蛮人', 'Druid': '德鲁伊', 'Necromancer': '死灵法师',
    'Paladin': '圣骑士', 'Sorceress': '法师', 'Warlock': '术士',
    'Ameythst': '紫宝石', 'Amethyst': '紫宝石', 'Sapphire': '蓝宝石', 'Emerald': '绿宝石', 'Ruby': '红宝石',
    'Topaz': '黄宝石', 'Diamond': '钻石', 'Skull': '骷髅宝石',
    'Bolt Case': '弩箭筒', 'Body Armor': '盔甲', 'Grand Charm': '超大型护身符', 'Sunder Charms': '破免护身符',
    'Sunder Charm': '破免护身符', 'Renewed Sunder': '焕新破免护身符', 'Runeword': '符文之语',
    'Socketed Items': '镶嵌物', 'Socketed Item': '镶孔物品', 'Socketed': '已镶孔', 'Unstacked': '未堆叠',
    'Stacked': '堆叠', 'Stack Qty': '堆叠数量', 'Qty': '数量', '1 Rune Higher': '高一级的符文 1 枚',
    '1 Rune Lower': '低一级的符文 1 枚', '1 Rune 3 Levels Higher': '高三级的符文 1 枚',
    'Base Item': '底材', 'Normal Quality': '普通品质', 'Repaired & Recharged': '已修理并补充充能',
    'Replenished Quantity': '补充数量', 'Indestructible': '无法破坏', 'Exceptional': '扩展级',
    'Ethereal': '无形', 'Superior': '超强', 'Elite': '精英级', 'Crafted': '手工', 'Rerolled': '重掷后的',
    'Regenerated': '重新生成的', 'Random Element': '随机元素', 'Random': '随机', 'New': '新的',
    'Unique': '暗金', 'Rare': '稀有', 'Magic': '魔法', 'White': '白色', 'Normal': '普通', 'Set': '套装',
    'Jewelry': '首饰', 'Jewels': '珠宝', 'Jewel': '珠宝', 'Gems': '宝石', 'Gem': '宝石',
    'Amulets': '项链', 'Amulet': '项链', 'Rings': '戒指', 'Ring': '戒指', 'Belts': '腰带', 'Belt': '腰带',
    'Boots': '靴子', 'Gloves': '手套', 'Helms': '头盔', 'Helm': '头盔', 'Shields': '盾牌', 'Shield': '盾牌',
    'Armors': '防具', 'Armor': '防具', 'Weapons': '武器', 'Weapon': '武器', 'Torso': '盔甲',
    'Charms': '护身符', 'Charm': '护身符', 'Arrows': '箭矢', 'Bolts': '弩箭', 'Quiver': '箭筒', 'Ammo': '弹药',
    'Non-Throwing': '非投掷类', 'Throwing Axe': '投掷斧', 'Axe': '斧', 'Dagger': '匕首', 'Knife': '小刀',
    'Javelins': '标枪', 'Spear': '长矛', 'Staff': '法杖', 'Polearm': '长柄武器', 'Sword of the Leech': '吸血之剑',
    'Item': '物品', 'Items': '物品', 'Sockets': '孔位', 'Socket': '孔位', 'Statue': '雕像',
    'Fire': '火焰', 'Cold': '冰冷', 'Lightning': '闪电', 'Poison': '毒素', 'Physical': '物理', 'Elemental': '元素',
    'Strength': '力量', 'Dexterity': '敏捷', 'Vitality': '体力', 'Energy': '精力', 'Attributes': '属性',
    'Life Steal': '偷取生命', 'Mana Steal': '偷取法力', 'Mana': '法力', 'Life': '生命', 'HP': '生命',
    'Resistances': '抗性', 'Resistance': '抗性', 'Resists': '抗性', 'Resist': '抗性', 'Res': '抗性',
    'Damage': '伤害', 'Dmg': '伤害', 'Defense': '防御', 'Def': '防御', 'AC': '防御', 'Thorns': '荆棘',
    'Regeneration': '恢复速度', 'Maximum': '最大', 'Minimum': '最小', 'Max': '最大', 'Min': '最小',
    'Chance': '几率', 'Skill': '技能', 'Skills': '技能', 'Levels': '等级', 'Level': '等级', 'lvl': '等级',
    'Speed': '速度', 'Attack': '攻击', 'Gold': '金币', 'Find': '获取', 'Block': '格挡',
    'Repaired': '已修理', 'Recharged': '已补充充能', 'Regen': '恢复速度', 'Exp': '经验值',
    'all elemental damage': '所有元素伤害', 'enemy elemental resist': '敌人元素抗性', 'magic damage': '魔法伤害',
    'enemy magic resist': '敌人魔法抗性', 'Enemy': '敌人', 'All': '所有', 'Any Type': '任意类型', 'Any': '任意',
    'same type': '相同类型', 'same size': '相同大小', 'each': '每次', 'per hit': '每次命中', 'per Kill': '每次击杀',
    'only': '专用', 'OR': '或', 'plvl': '角色等级', 'ilvl': '物品等级',
}

PATTERNS = [(re.compile(r'(?<![A-Za-z])' + re.escape(k) + r'(?![A-Za-z])', re.I), v)
            for k, v in sorted(TERMS.items(), key=lambda x: len(x[0]), reverse=True)]
RUNE_PATTERN = re.compile(r'\b(' + '|'.join(sorted(RUNES, key=len, reverse=True)) + r')\s+runes?\b', re.I)
RUNE_NAMES = {k.lower(): v for k, v in RUNES.items()}


def translate(text: str) -> str:
    text = re.sub(r'<br\s*/?>', '\n', text, flags=re.I)
    text = re.sub(r'<[^>]+>', '', text)
    text = text.replace('\\=', '=').replace('\\#', '#').replace('\\*', '*')
    text = text.replace('**', '').replace('__', '').replace('_', '')
    text = text.replace('\\[N\\]', '（普通级）').replace('[N]', '（普通级）')
    text = RUNE_PATTERN.sub(lambda m: RUNE_NAMES[m.group(1).lower()] + '符文', text)
    for pattern, replacement in PATTERNS:
        text = pattern.sub(lambda m, replacement=replacement: replacement, text)
    text = re.sub(r'\bto\b', '至', text, flags=re.I)
    text = re.sub(r'#-#', '随机数量', text)
    text = re.sub(r'#(?=\d)', '编号', text)
    text = text.replace('#', '相应数量')
    text = re.sub(r'(?<=[\u4e00-\u9fff]) +(?=[\u4e00-\u9fff])', '', text)
    text = re.sub(r'\s*\n\s*', '\n', text)
    return re.sub(r' {2,}', ' ', text).strip()


def extract(source: str) -> dict:
    group = section = subsection = None
    rows = []
    in_table = False
    for line_number, line in enumerate(source.splitlines(), start=1):
        if line.startswith('# '):
            group = GROUPS.get(line[2:])
            section = subsection = None
        elif line.startswith('## '):
            section = SECTIONS.get(line[3:]) if group else None
            subsection = None
        elif line.startswith('### '):
            subsection = {'Armor': '防具', 'Weapons': '武器'}.get(line[4:]) if section == '底材升级' else None
        if not line.startswith('|'):
            in_table = False
            continue
        if not group or not section:
            continue
        cells = [cell.strip() for cell in line.strip().strip('|').split('|')]
        if not in_table:
            in_table = True
            continue  # header
        if all(re.fullmatch(r':?-{3,}:?', c) for c in cells):
            continue
        clean = [c.replace('\\=', '=').strip() for c in cells]
        separator = next((i for i, c in enumerate(clean) if c == '='), None)
        if separator is None:
            if section not in ('宝珠改变品质', '重新生成', '火炬与遗物升级'):
                continue  # subsection labels inside a table
            separator = len(clean) - 1
        inputs = [translate(c) for c in clean[:separator] if c.strip()]
        output = translate('；'.join(c for c in clean[separator + (1 if clean[separator] == '=' else 0):] if c.strip()))
        if not inputs:
            if output and rows and rows[-1]['section'] == section:
                rows[-1]['output'] += '\n' + output
            continue
        if not output:
            continue
        rows.append({'id': len(rows) + 1, 'group': group, 'section': section + (' · ' + subsection if subsection else ''),
                     'inputs': inputs, 'output': output, 'sourceLine': line_number})
    return {'source': 'https://wiki.d2r-reimagined.com/en/recipes/recipes',
            'sourceUpdated': re.search(r'^date:\s*(.+)$', source, re.M).group(1), 'recipes': rows}


if __name__ == '__main__':
    data = extract(SOURCE.read_text(encoding='utf-8'))
    target = ROOT / 'data'
    target.mkdir(exist_ok=True)
    payload = json.dumps(data, ensure_ascii=False, indent=2) + '\n'
    (target / 'recipes.json').write_text(payload, encoding='utf-8')
    (target / 'recipes.js').write_text('window.RECIPE_DATA = ' + payload.rstrip() + ';\n', encoding='utf-8')
    print(f"Wrote {len(data['recipes'])} recipes")
