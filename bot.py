import json
import os
import re
from pathlib import Path
from typing import Any

import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv


load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
DATA_FILE = Path(os.getenv("DATA_FILE", "knowledge_base.json"))

if not DISCORD_TOKEN:
    raise RuntimeError("DISCORD_TOKEN is not set")


SHORT_ALIASES = {
    "Anti-Mage": ["am", "antimage", "антимаг", "ам"],
    "Templar Assassin": ["ta", "темпларка", "темплар", "та"],
    "Ancient Apparition": ["aa", "аппарат", "апарат", "аа"],
    "Shadow Fiend": ["sf", "сф", "сфыч"],
    "Storm Spirit": ["storm", "шторм"],
    "Phantom Assassin": ["pa", "па", "фантомка"],
    "Queen of Pain": ["qop", "квопа", "квоп"],
    "Crystal Maiden": ["cm", "цм", "кристалка"],
    "Naga Siren": ["naga", "нага"],
    "Drow Ranger": ["drow", "дровка", "дров"],
    "Nature's Prophet": ["np", "furion", "фурион"],
    "Outworld Destroyer": ["od", "од"],
    "Keeper of the Light": ["kotl", "котл"],
    "Wraith King": ["wk", "вк", "скелет"],
    "Dragon Knight": ["dk", "дк"],
    "Bounty Hunter": ["bh", "бх"],
    "Spirit Breaker": ["bara", "бара"],
}

PLAYER_ALIASES = {
    "Abaddon": ["абаддон", "абба", "аба"],
    "Alchemist": ["алхимик", "алхим", "алх"],
    "Ancient Apparition": ["аппарат", "апарат", "аа", "aa"],
    "Anti-Mage": ["антимаг", "ам", "am", "анти маг"],
    "Arc Warden": ["арк", "арк варден", "зет"],
    "Axe": ["акс", "топор"],
    "Bane": ["бейн"],
    "Batrider": ["батрайдер", "бат", "бэт"],
    "Beastmaster": ["бистмастер", "бист", "зверь"],
    "Bloodseeker": ["бладсикер", "бс", "блад"],
    "Bounty Hunter": ["баунти", "бх", "bh", "гондар"],
    "Brewmaster": ["брюмастер", "брю", "панда"],
    "Bristleback": ["бристлбек", "бристл", "ёж", "еж"],
    "Broodmother": ["бруда", "брумать", "паучиха"],
    "Centaur Warrunner": ["центавр", "кент", "цент"],
    "Chaos Knight": ["хаос", "цк", "ck"],
    "Chen": ["чен"],
    "Clinkz": ["клинкз", "клинкс", "кость"],
    "Clockwerk": ["клокверк", "клок"],
    "Crystal Maiden": ["кристалка", "цм", "cm"],
    "Dark Seer": ["дарксир", "дс", "ds"],
    "Dark Willow": ["виллоу", "дарк виллоу", "фея"],
    "Dawnbreaker": ["даунбрейкер", "донбрейкер", "донка"],
    "Dazzle": ["дазл", "даззл"],
    "Death Prophet": ["дп", "dp", "кроба"],
    "Disruptor": ["дизраптор", "диз", "дизруптор"],
    "Doom": ["дум"],
    "Dragon Knight": ["дк", "dk", "драгон кнайт"],
    "Drow Ranger": ["дровка", "дров", "траха", "тракса"],
    "Earth Spirit": ["земеля", "земля", "ес", "earth spirit"],
    "Earthshaker": ["шейкер", "еш", "earthshaker"],
    "Elder Titan": ["титан", "элдер", "ет"],
    "Ember Spirit": ["эмбер", "ember"],
    "Enchantress": ["энча", "энчантрес", "коза"],
    "Enigma": ["энигма"],
    "Faceless Void": ["войлд", "воид", "фв", "fv"],
    "Grimstroke": ["грим", "гримстрок"],
    "Gyrocopter": ["гиро", "гирокоптер"],
    "Hoodwink": ["худвинк", "белка"],
    "Huskar": ["хускар", "хуск"],
    "Invoker": ["инвокер", "инвок", "инв"],
    "Io": ["ио", "висп", "виспер"],
    "Jakiro": ["джакиро", "жакиро", "джакир"],
    "Juggernaut": ["джагер", "джаг", "jugg"],
    "Keeper of the Light": ["котл", "kotl", "кипер"],
    "Kez": ["кез"],
    "Kunkka": ["кунка", "кункка", "адмирал"],
    "Legion Commander": ["легионка", "лега", "лк", "lc"],
    "Leshrac": ["лешрак", "леший", "леш"],
    "Lich": ["лич"],
    "Lifestealer": ["лайфстилер", "найкс", "naix", "гуля"],
    "Lina": ["лина"],
    "Lion": ["лион"],
    "Lone Druid": ["друид", "лд", "ld", "медведь"],
    "Luna": ["луна"],
    "Lycan": ["ликан", "волк"],
    "Magnus": ["магнус"],
    "Marci": ["марси"],
    "Mars": ["марс"],
    "Medusa": ["медуза", "дуза"],
    "Meepo": ["мипо"],
    "Mirana": ["мирана", "потма", "потм"],
    "Monkey King": ["мк", "mk", "манки", "обезьяна"],
    "Morphling": ["морф", "морфлинг"],
    "Muerta": ["муэрта", "муерта"],
    "Naga Siren": ["нага", "naga"],
    "Nature's Prophet": ["фурион", "фура", "нп", "np"],
    "Necrophos": ["некр", "некрофос", "некрич"],
    "Night Stalker": ["баланар", "нс", "night stalker"],
    "Nyx Assassin": ["никс", "nyx"],
    "Ogre Magi": ["огр", "огр маг", "огрмаг"],
    "Omniknight": ["омник", "омни"],
    "Oracle": ["оракл"],
    "Outworld Destroyer": ["од", "od", "одешник"],
    "Pangolier": ["пангольер", "панго"],
    "Phantom Assassin": ["па", "pa", "фантомка", "мортира"],
    "Phantom Lancer": ["пл", "pl", "лансер"],
    "Phoenix": ["феникс", "птица"],
    "Primal Beast": ["праймал", "бист"],
    "Puck": ["пак"],
    "Pudge": ["пудж", "падж", "мясо"],
    "Pugna": ["пугна"],
    "Queen of Pain": ["квопа", "квоп", "qop", "акаша"],
    "Razor": ["рейзор", "разор"],
    "Riki": ["рики", "рикки"],
    "Ringmaster": ["рингмастер", "ринг"],
    "Rubick": ["рубик"],
    "Sand King": ["ск", "sand king", "скорп"],
    "Shadow Demon": ["шд", "sd", "демон"],
    "Shadow Fiend": ["сф", "sf", "сфыч", "фиенд"],
    "Shadow Shaman": ["раста", "шаман"],
    "Silencer": ["сало", "сайленсер", "сайл", "сайленс"],
    "Skywrath Mage": ["скаймаг", "скай маг", "скай", "петух", "курица"],
    "Slardar": ["слардар", "селедка"],
    "Slark": ["сларк"],
    "Snapfire": ["снапка", "бабка", "снап"],
    "Sniper": ["снайпер", "снайп"],
    "Spectre": ["спектра", "спектр"],
    "Spirit Breaker": ["бара", "баратрум", "сб", "sb"],
    "Storm Spirit": ["шторм", "storm"],
    "Sven": ["свен"],
    "Techies": ["течис", "течка", "минер"],
    "Templar Assassin": ["темпларка", "темплар", "та", "ta"],
    "Terrorblade": ["террор", "тб", "tb"],
    "Tidehunter": ["тайд", "тайдхантер", "арбуз"],
    "Timbersaw": ["тимбер", "пила"],
    "Tinker": ["тинкер"],
    "Tiny": ["тини"],
    "Treant Protector": ["трент", "дерево"],
    "Troll Warlord": ["тролль", "троль"],
    "Tusk": ["туск", "бивень"],
    "Underlord": ["андерлорд", "питлорд"],
    "Undying": ["андаинг", "зомби", "томба"],
    "Ursa": ["урса", "мишка"],
    "Vengeful Spirit": ["венга", "венж"],
    "Venomancer": ["веник", "веном", "веник"], 
    "Viper": ["вайпер", "гадюка"],
    "Visage": ["висаж", "визаж"],
    "Void Spirit": ["воид спирит", "вс", "void spirit"],
    "Warlock": ["варлок"],
    "Weaver": ["вивер", "жук"],
    "Windranger": ["врка", "вр", "windranger", "виндрейнджер"],
    "Winter Wyvern": ["виверна", "виверна зимняя", "ww"],
    "Witch Doctor": ["вд", "wd", "доктор"],
    "Wraith King": ["вк", "wk", "скелет", "леорик"],
    "Zeus": ["зевс"],
}

ROLE_ALIASES = {
    "mid": ["mid", "middle", "мид", "миде"],
    "carry": ["carry", "керри", "кери", "pos1", "1 поз", "easy line", "safe lane", "safelane", "изи лайн", "лёгкая", "легкая"],
    "offlane": ["offlane", "оффлейн", "хард", "pos3", "3 поз"],
    "support": ["support", "hard support", "soft support", "саппорт", "сап", "pos4", "pos5", "4 поз", "5 поз"],
}

ROLE_ALIASES["mid"].extend(["мид", "миде", "центр"])
ROLE_ALIASES["carry"].extend(["керри", "кери", "изилайн", "изи лайн", "лёгкая", "легкая", "сейфлейн", "safe lane"])
ROLE_ALIASES["offlane"].extend(["оффлейн", "хард", "тройка", "3 позиция"])
ROLE_ALIASES["support"].extend(["саппорт", "сапорт", "сап", "хард саппорт", "хард сап", "пятерка", "четверка", "4 позиция", "5 позиция"])

ROLE_BUILDS = {
    "mid": {
        "starting": "Bottle rush, Branches, Tango, Faerie Fire",
        "core": "Bottle → Boots → Blink/Force Staff → BKB",
        "situational": "Aghanim's/Shard (если герой хорошо скейлится от спеллов)",
        "tips": [
            "Контроль руны важнее лишнего range creep: заранее пушь wave перед 2/4/6 минутой.",
            "Если враг сильнее стоит линию, быстро добивай wave и забирай ближайший camp.",
        ],
    },
    "carry": {
        "starting": "Quelling Blade, Tango, Branches, stats item",
        "core": "Power Treads/Phase Boots → farming/damage item → BKB",
        "situational": "Satanic/Skadi/Linken's (если надо пережить первый прокаст)",
        "tips": [
            "Не дерись до первого большого слота: забирай safe wave и ближайший camp.",
            "Держи TP на ответную драку, но не прилетай первым под контроль.",
        ],
    },
    "offlane": {
        "starting": "Bracer parts, Tango, Stick, Ring of Protection",
        "core": "Phase Boots → Vanguard/Blade Mail → Blink/Pipe",
        "situational": "Lotus Orb/Crimson Guard (под тип урона врага)",
        "tips": [
            "Перед ротацией запушь wave под башню, чтобы враг терял крипов.",
            "Начинай драку только когда видишь ключевой disable или можешь пережить его.",
        ],
    },
    "support": {
        "starting": "Observer Ward, Sentry, Blood Grenade, Tango, Wind Lace",
        "core": "Boots → Wand → Force Staff/Glimmer Cape → Shard",
        "situational": "Ghost Scepter/Lotus Orb (если тебя быстро фокусят)",
        "tips": [
            "Ставь вижен на подход к драке, а не на очевидный клифф в лоб.",
            "Играй за спиной кора: сначала save/disable, потом добор урона.",
        ],
    },
}

HERO_ROLE_BUILDS = {
    ("Pudge", "mid"): {
        "starting": "Bottle rush, Branches, Tango, Faerie Fire",
        "core": "Bottle → Phase Boots → Blink Dagger → Aghanim's Scepter → BKB",
        "situational": "Eternal Shroud (против магического прокаста)",
    },
    ("Pudge", "support"): {
        "starting": "Observer Ward, Sentry, Blood Grenade, Tango, Wind Lace",
        "core": "Tranquil Boots → Wand → Blink/Force Staff → Aghanim's Shard",
        "situational": "Glimmer Cape (сейв после hook/initiation)",
    },
    ("Pudge", "carry"): {
        "starting": "Quelling Blade, Tango, Bracer parts, Magic Stick",
        "core": "Phase Boots → Aghanim's Scepter → BKB → Heart",
        "situational": "Harpoon (если нужно цепляться за дальников)",
    },
    ("Skywrath Mage", "support"): {
        "starting": "Observer Ward, Sentry, Blood Grenade, Tango, Mango, Wind Lace",
        "core": "Arcane Boots → Rod of Atos → Aghanim's Shard → Force Staff/Glimmer Cape",
        "situational": "Eul's Scepter (снять silence и подготовить Mystic Flare setup)",
    },
    ("Phantom Assassin", "carry"): {
        "starting": "Quelling Blade, Tango, Slippers/Circlet, Branches",
        "core": "Battle Fury/Desolator → Power Treads → BKB → Basher → Abyssal Blade → Nullifier",
        "situational": "Skadi/Satanic поздно; Manta только niche, если нужен dispel и нет лучшего ответа",
    },
}

HERO_ITEM_POOLS = {
    ("Phantom Assassin", "carry"): [
        ("Black King Bar", "почти обязательно против Sky/QoP/SD/Centaur: жми до silence/stun, а не после"),
        ("Basher → Abyssal Blade", "чтобы удержать TB/QoP после Blink Strike и убить цель до save"),
        ("Nullifier", "против Shadow Demon save, Force/Glimmer/Eul/Ghost и сейв-саппортов"),
        ("Eye of Skadi", "против Terrorblade: режет lifesteal/regen, даёт плотность и помогает держать ranged core"),
        ("Satanic", "поздний слот после BKB/Abyssal/Nullifier, если драки долгие и тебя не убивают в контроле"),
        ("Linken's Sphere", "situational против Duel/Hex/targeted setup, если BKB не решает первый catch"),
        ("Monkey King Bar", "только если враг купил evasion/Butterfly или есть миссы, не автопокупка"),
    ],
}

HERO_ITEM_BANS = {
    ("Phantom Assassin", "carry"): {
        "Manta Style",
        "Crimson Guard",
        "Shiva's Guard",
        "Shiva's Guard/Skadi",
        "Pipe of Insight",
        "Spirit Vessel",
        "Solar Crest",
        "Force Staff",
        "Glimmer Cape",
        "Ghost Scepter",
        "Blade Mail",
    },
}

ROLE_ITEM_POOLS = {
    "mid": [
        ("BKB", "если враг ловит тебя первым станом/сайленсом и без BKB ты не нажимаешь кнопки"),
        ("Blink Dagger", "если нужно самому начинать в дальнюю цель или наказывать ошибку позиции"),
        ("Force Staff", "против кайта, замедлений и героев, которые держат дистанцию"),
        ("Eul's Scepter", "снять silence/slow, сбить tp или пережить первый фокус"),
        ("Linken's Sphere", "против одиночного ключевого таргет-спелла: Duel, Doom, Hex, Fiend's Grip"),
        ("Scythe of Vyse", "если нужен гарантированный catch на мобильного кора"),
    ],
    "carry": [
        ("BKB", "когда в драке тебя убивают контролем раньше, чем ты успеваешь бить"),
        ("Satanic", "против долгих драк и физического фокуса после BKB"),
        ("Eye of Skadi", "против сильного отхила, lifesteal и мобильных ranged cores"),
        ("Manta Style", "против silence/root/DoT, если иллюзии не умирают мгновенно"),
        ("Nullifier", "против Ghost Scepter, Glimmer, Force Staff, Eul и save-саппортов"),
        ("Linken's Sphere", "если тебя ловят одним таргет-спеллом до BKB"),
    ],
    "offlane": [
        ("Pipe of Insight", "против массового магического прокаста"),
        ("Crimson Guard", "против иллюзий, summons и частого физического урона"),
        ("Lotus Orb", "против Hex, Orchid, Duel, single-target disables и дебаффов на кора"),
        ("Blink Dagger", "если команде нужен первый старт драки"),
        ("Blade Mail", "против героев, которые вынуждены бить тебя в фокусе"),
        ("Shiva's Guard", "против отхила, lifesteal и плотных melee heroes"),
    ],
    "support": [
        ("Force Staff", "против slows, Clockwerk/Pudge-style catch и чтобы вытаскивать кора"),
        ("Glimmer Cape", "против магического burst и для сейва после initiation"),
        ("Ghost Scepter", "если тебя убивает физический кор без Nullifier"),
        ("Lotus Orb", "снять silence/root/Hex с кора и наказать single-target spells"),
        ("Solar Crest", "если твой кор дерётся рано и ему нужны armor/attack speed"),
        ("Aeon Disk", "если тебя всегда убивают первым до нажатия сейва"),
    ],
}

ENEMY_ITEM_RULES = {
    "Invoker": [
        ("BKB", "против Tornado/EMP + chain control; жми до потери маны"),
        ("Orchid/Bloodthorn", "если можешь первым находить Invoker до BKB/Linken"),
        ("Lotus Orb", "снять Cold Snap/Orchid и отразить targeted setup"),
        ("Dust/Sentry", "если Invoker играет через Ghost Walk и уходит после прокаста"),
    ],
    "Sniper": [
        ("Blink/Shadow Blade", "чтобы заходить сбоку и не бежать через Shrapnel"),
        ("Force Staff/Hurricane Pike", "разорвать дистанцию после Pike или Assassinate setup"),
        ("Blade Mail", "если Sniper вынужден бить тебя в фокусе"),
        ("Nullifier", "против Pike, Force Staff, Ghost/Glimmer сейвов"),
    ],
    "Huskar": [
        ("Spirit Vessel", "обязателен в команде против Berserker's Blood и Satanic"),
        ("Silver Edge", "сломать пассивку перед фокусом"),
        ("Halberd", "выключить урон Huskar после прыжка"),
        ("Shiva's Guard/Skadi", "резать отхил и lifesteal в затяжной драке"),
    ],
    "Phantom Assassin": [
        ("MKB", "если твой герой бьёт с руки и PA уже имеет Blur/evasion"),
        ("Ghost Scepter", "на саппорте до Nullifier"),
        ("Abyssal Blade", "если нужно удержать PA после BKB"),
        ("Butterfly", "если PA без MKB и ты играешь right-click core"),
    ],
    "Anti-Mage": [
        ("Scythe of Vyse", "лучший catch после Manta/BKB timings"),
        ("Orchid/Bloodthorn", "до Manta или если можно сбить Blink первым"),
        ("Abyssal Blade", "для кора, которому нужно удержать AM в BKB"),
        ("Linken's Sphere", "если AM ловит через Abyssal + team follow-up"),
    ],
    "Viper": [
        ("Magic Wand", "ранний value против Poison Attack/Nethertoxin spam"),
        ("Force Staff/Hurricane Pike", "выйти из Nethertoxin и разорвать slow"),
        ("BKB", "когда Viper мешает нажать ключевые spells в драке"),
        ("Manta/Dispel", "если герой страдает от Corrosive Skin/slow debuffs"),
    ],
    "Ancient Apparition": [
        ("BKB", "жать до Ice Blast, если драка начинается в тебя"),
        ("Lotus Orb", "снять Cold Feet и помочь кору пережить setup"),
        ("Pipe/Glimmer", "снизить магический burst до Ice Blast"),
        ("Blink/Shadow Blade", "быстро находить AA на задней линии"),
    ],
    "Silencer": [
        ("Eul's Scepter", "снять Global Silence/Last Word и сразу дать ответный прокаст"),
        ("Lotus Orb", "снимать silence с себя или кора; хорошо против Last Word/Curse"),
        ("Glimmer Cape", "пережить магический фокус после Global Silence"),
        ("Force Staff", "выйти из плохой позиции, когда после Global Silence враг идёт вперёд"),
        ("BKB", "если ты core и Silencer ломает весь spell rotation"),
    ],
    "Terrorblade": [
        ("Eye of Skadi", "для carry против TB: режет sustain, даёт плотность и помогает держать его после Meta"),
        ("Abyssal Blade", "зафиксировать TB до Sunder или после его BKB"),
        ("Satanic", "поздний слот, если драки долгие и нужно пережить физический урон"),
    ],
    "Shadow Demon": [
        ("Nullifier", "снять Disruption follow-up сейвы, Force/Glimmer/Eul и добить цель"),
        ("BKB", "чтобы не умереть в Soul Catcher + chain control до прыжка"),
        ("Linken's Sphere", "если SD начинает драку через targeted setup по тебе"),
    ],
    "Skywrath Mage": [
        ("BKB", "против Ancient Seal/Atos/Mystic Flare: жать до silence"),
        ("Linken's Sphere", "если Sky ловит через Atos/Hex setup до BKB"),
        ("Nullifier", "если Sky выживает через Ghost/Glimmer/Force"),
    ],
    "Queen of Pain": [
        ("Abyssal Blade", "удержать QoP после Blink и убить до повторного escape"),
        ("BKB", "пережить Orchid/Sonic Wave и дать свой урон"),
        ("Nullifier", "против Eul/Ghost/Linken-save вариантов"),
    ],
    "Centaur Warrunner": [
        ("BKB", "не получить Hoof Stomp/chain stun в момент прыжка"),
        ("Linken's Sphere", "situational, если Centaur + команда ловят одним targeted setup"),
        ("Satanic", "поздно, если переживаешь первый stun и нужна вторая жизнь в драке"),
    ],
}

last_query_by_channel: dict[int, dict[str, Any]] = {}

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)


def make_help_embed() -> discord.Embed:
    embed = discord.Embed(
        title="DotaCoach — команды",
        description="Пиши матчап свободным текстом или открой форму через `/form`.",
        color=discord.Color.blurple(),
    )
    embed.add_field(
        name="Спросить",
        value=(
            "`!coach играю скай маг против сало саппорт`\n"
            "`!coach я Pudge mid vs Invoker`\n"
            "`/coach question: играю веник против петух хард`"
        ),
        inline=False,
    )
    embed.add_field(
        name="Форма",
        value=(
            "`/form` или `!form` — форма для 1v1/линии\n"
            "`/draft` или `!draft` — форма для полного 5v5 драфта"
        ),
        inline=False,
    )
    embed.add_field(
        name="Обучить",
        value=(
            "`!teach ответ` — запомнить ответ для последнего неизвестного матчапа\n"
            "`!learn герой | роль | враги | ответ` — добавить запись вручную"
        ),
        inline=False,
    )
    embed.add_field(
        name="Сленг",
        value="Понимаю `петух/скай маг`, `сало`, `веник`, `фура`, `цм`, `сф`, `лега`, `пудж/мясо` и другие популярные названия.",
        inline=False,
    )
    embed.set_footer(text="Пример: !coach играю Skywrath Mage vs Silencer - support")
    return embed


class CoachModal(discord.ui.Modal, title="DotaCoach вопрос"):
    hero = discord.ui.TextInput(
        label="Твой герой",
        placeholder="Например: скай маг, Pudge, веник",
        max_length=80,
    )
    role = discord.ui.TextInput(
        label="Твоя роль/линия",
        placeholder="mid / carry / support / offlane / easy line",
        max_length=40,
        required=False,
    )
    enemies = discord.ui.TextInput(
        label="Враги",
        placeholder="Например: сало, Invoker, Huskar",
        max_length=160,
    )
    enemy_role = discord.ui.TextInput(
        label="Роль/позиция врага",
        placeholder="Например: mid, carry, offlane, тройка",
        max_length=60,
        required=False,
    )
    details = discord.ui.TextInput(
        label="Дополнительно",
        placeholder="Например: нет станов, проиграл лайн, что брать после Atos?",
        style=discord.TextStyle.paragraph,
        max_length=400,
        required=False,
    )

    async def on_submit(self, interaction: discord.Interaction) -> None:
        query = parse_form_fields(
            self.hero.value,
            self.role.value,
            self.enemies.value,
            self.details.value,
            self.enemy_role.value,
        )
        if interaction.channel_id:
            last_query_by_channel[interaction.channel_id] = query
        embed = lookup_embed(query)
        if embed:
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message(lookup_answer(query))


class CoachFormView(discord.ui.View):
    def __init__(self) -> None:
        super().__init__(timeout=180)

    @discord.ui.button(label="Открыть форму", style=discord.ButtonStyle.primary)
    async def open_form(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await interaction.response.send_modal(CoachModal())


class DraftModal(discord.ui.Modal, title="DotaCoach 5v5 драфт"):
    hero_role = discord.ui.TextInput(
        label="Ты: герой + роль",
        placeholder="Например: чен hard support / Pudge mid / веник offlane",
        max_length=120,
    )
    allies = discord.ui.TextInput(
        label="Союзники",
        placeholder="4 героя через запятую: морф, магнус, рубик, цм",
        max_length=220,
        required=False,
    )
    enemies = discord.ui.TextInput(
        label="Враги",
        placeholder="5 героев через запятую: лега, сало, снайпер, урса, лич",
        max_length=260,
    )
    enemy_roles = discord.ui.TextInput(
        label="Роли врагов",
        placeholder="Например: лега 3, сало 5, снайпер mid, урса carry",
        max_length=260,
        required=False,
    )
    question = discord.ui.TextInput(
        label="Что разобрать?",
        placeholder="Например: что собирать, как играть линии, кого фокусить, план на драки",
        style=discord.TextStyle.paragraph,
        max_length=500,
        required=False,
    )

    async def on_submit(self, interaction: discord.Interaction) -> None:
        query = parse_draft_fields(
            self.hero_role.value,
            self.allies.value,
            self.enemies.value,
            self.enemy_roles.value,
            self.question.value,
        )
        if interaction.channel_id:
            last_query_by_channel[interaction.channel_id] = {
                "hero": query["hero"],
                "role": query["role"],
                "enemies": query["enemies"],
                "raw": query["raw"],
            }
        await interaction.response.send_message(embed=render_draft_embed(query))


class DraftFormView(discord.ui.View):
    def __init__(self) -> None:
        super().__init__(timeout=180)

    @discord.ui.button(label="Открыть 5v5 форму", style=discord.ButtonStyle.success)
    async def open_draft_form(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await interaction.response.send_modal(DraftModal())


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()


def read_json_file(path: Path) -> Any:
    raw = path.read_bytes()
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        text = raw.decode("utf-16")
    return json.loads(text)


def load_data() -> list[dict[str, Any]]:
    if not DATA_FILE.exists():
        return []
    data = read_json_file(DATA_FILE)
    if not isinstance(data, list):
        return []
    return data


def save_data(entries: list[dict[str, Any]]) -> None:
    DATA_FILE.write_text(json.dumps(entries, ensure_ascii=False, indent=2), encoding="utf-8")


def hero_aliases_from_name(hero: str) -> list[str]:
    aliases = {hero.lower(), hero.replace("-", " ").lower(), hero.replace("'", "").lower()}
    words = re.findall(r"[A-Za-z]+", hero)
    if len(words) > 1:
        aliases.add(" ".join(word.lower() for word in words))
    aliases.update(alias.lower() for alias in SHORT_ALIASES.get(hero, []))
    aliases.update(alias.lower() for alias in PLAYER_ALIASES.get(hero, []))
    return sorted(aliases, key=len, reverse=True)


def build_hero_aliases() -> dict[str, list[str]]:
    heroes = set(SHORT_ALIASES)
    for entry in load_data():
        if entry.get("hero"):
            heroes.add(entry["hero"])
        heroes.update(entry.get("enemies", []))
    return {hero: hero_aliases_from_name(hero) for hero in sorted(heroes)}


def find_heroes(text: str) -> list[str]:
    haystack = f" {normalize(text)} "
    found = []
    candidates = []
    for hero, aliases in build_hero_aliases().items():
        for alias in aliases:
            candidates.append((hero, alias))
    for hero, alias in sorted(candidates, key=lambda item: len(item[1]), reverse=True):
        if hero in found:
            continue
        pattern = r"(?<![a-zа-я0-9])" + re.escape(alias.lower()) + r"(?![a-zа-я0-9])"
        if re.search(pattern, haystack):
            found.append(hero)
    return found


def find_role(text: str) -> str:
    haystack = normalize(text)
    for role, aliases in ROLE_ALIASES.items():
        if any(alias in haystack for alias in aliases):
            return role
    return "unknown role"


def parse_query(text: str) -> dict[str, Any]:
    split = re.split(r"\b(?:против|противник|vs|against|versus|контра|на\s+линии\s+против)\b", text, maxsplit=1, flags=re.IGNORECASE)
    role = find_role(text)

    if len(split) == 2:
        hero_text, enemy_text = split[0], split[1]
        hero_role = find_role(hero_text)
        if hero_role != "unknown role":
            role = hero_role
        hero_candidates = find_heroes(hero_text)
        enemy_candidates = find_heroes(enemy_text)
        all_candidates = find_heroes(text)
        hero = hero_candidates[0] if hero_candidates else (all_candidates[0] if all_candidates else "")
        enemies = [enemy for enemy in enemy_candidates if enemy != hero]
        if not enemies and len(all_candidates) > 1:
            enemies = [enemy for enemy in all_candidates if enemy != hero]
        return {"hero": hero, "role": role, "enemies": enemies, "raw": text}

    heroes = find_heroes(text)
    hero = heroes[0] if heroes else ""
    enemy_text = text

    enemies = [enemy for enemy in find_heroes(enemy_text) if enemy != hero]
    if len(heroes) > 1:
        enemies = [enemy for enemy in heroes[1:] if enemy != hero]

    return {"hero": hero, "role": role, "enemies": enemies, "raw": text}


def parse_form_fields(
    hero_text: str,
    role_text: str,
    enemies_text: str,
    details_text: str = "",
    enemy_role_text: str = "",
) -> dict[str, Any]:
    hero_candidates = find_heroes(hero_text)
    enemy_candidates = find_heroes(enemies_text)
    role = find_role(role_text)
    if role == "unknown role":
        role = find_role(f"{hero_text} {details_text}")

    hero = hero_candidates[0] if hero_candidates else ""
    enemies = [enemy for enemy in enemy_candidates if enemy != hero]
    return {
        "hero": hero,
        "role": role,
        "enemies": enemies,
        "enemy_role": find_role(enemy_role_text),
        "raw": f"{hero_text} {role_text} vs {enemies_text} {enemy_role_text}. {details_text}".strip(),
    }


def parse_draft_fields(
    hero_role_text: str,
    allies_text: str,
    enemies_text: str,
    enemy_roles_text: str = "",
    question_text: str = "",
) -> dict[str, Any]:
    hero_candidates = find_heroes(hero_role_text)
    hero = hero_candidates[0] if hero_candidates else ""
    role = find_role(hero_role_text)
    allies = [ally for ally in find_heroes(allies_text) if ally != hero]
    enemies = [enemy for enemy in find_heroes(f"{enemies_text} {enemy_roles_text}") if enemy != hero]
    return {
        "hero": hero,
        "role": role,
        "allies": allies[:4],
        "enemies": enemies[:5],
        "enemy_roles_text": enemy_roles_text.strip(),
        "question": question_text.strip(),
        "raw": f"{hero_role_text} | allies: {allies_text} | enemies: {enemies_text} | {enemy_roles_text} | {question_text}",
    }


def entry_score(query: dict[str, Any], entry: dict[str, Any]) -> int:
    score = 0
    if query["hero"] and query["hero"] == entry.get("hero"):
        score += 8
    if query["role"] != "unknown role" and query["role"] == entry.get("role"):
        score += 2
    query_enemies = set(query["enemies"])
    entry_enemies = set(entry.get("enemies", []))
    score += len(query_enemies & entry_enemies) * 4
    if query_enemies and query_enemies <= entry_enemies:
        score += 2
    return score


def role_build(hero: str, role: str) -> dict[str, Any]:
    build = dict(ROLE_BUILDS.get(role, ROLE_BUILDS["mid"]))
    build.update(HERO_ROLE_BUILDS.get((hero, role), {}))
    return build


def matchup_tip(hero: str, enemy: str, role: str) -> str:
    if hero == "Pudge" and enemy == "Invoker":
        if role == "mid":
            return "Против Invoker: держи Meat Hook до Tornado/EMP или когда он стоит без Forge Spirits перед собой."
        if role == "support":
            return "Против Invoker: не показывайся первым, жди Tornado/EMP и хукай после потраченного контроля."
        if role == "carry":
            return "Против Invoker: BKB жми до Tornado/EMP, а не после потери маны."
    if hero == "Skywrath Mage" and enemy == "Silencer":
        return "Против Silencer: не отдавай Ancient Seal до Global Silence; держи Eul/Lotus план и бей после его ульта."
    if enemy == "Sniper":
        return "Против Sniper: заходи сбоку с вижена и не трать gap-close, пока он держит Pike."
    if enemy == "Huskar":
        return "Против Huskar: не принимай all-in без контроля/BKB, разрывай дистанцию после Life Break."
    if enemy == "Invoker":
        return "Против Invoker: считай Tornado/EMP и не начинай драку без вижена на его позицию."
    if enemy == "Silencer":
        return "Против Silencer: держи dispel/save под Global Silence и не начинай драку, если вся команда без BKB/диспела."
    return f"Против {enemy}: не начинай драку вслепую, сначала найди его позицию или ключевой spell."


def situational_items(hero: str, enemies: list[str], role: str) -> list[tuple[str, str]]:
    items: list[tuple[str, str]] = []
    items.extend(HERO_ITEM_POOLS.get((hero, role), []))
    for enemy in enemies:
        items.extend(ENEMY_ITEM_RULES.get(enemy, []))
    items.extend(ROLE_ITEM_POOLS.get(role, ROLE_ITEM_POOLS["mid"]))

    deduped = []
    seen = set()
    hero_bans = HERO_ITEM_BANS.get((hero, role), set())
    support_skip = {
        "BKB",
        "Orchid/Bloodthorn",
        "Abyssal Blade",
        "MKB",
        "Butterfly",
        "Satanic",
        "Eye of Skadi",
        "Blink/Shadow Blade",
        "Force Staff/Hurricane Pike",
        "Blade Mail",
        "Nullifier",
        "Silver Edge",
        "Halberd",
        "Shiva's Guard/Skadi",
    }
    carry_skip = {"Observer Ward", "Sentry", "Dust/Sentry", "Glimmer Cape", "Ghost Scepter", "Solar Crest", "Aeon Disk"}
    for item, reason in items:
        if item in hero_bans:
            continue
        if role == "support" and item in support_skip:
            continue
        if role == "carry" and item in carry_skip:
            continue
        if item in seen:
            continue
        seen.add(item)
        deduped.append((item, reason))
    return deduped[:7]


def lane_plan(hero: str, enemy: str, role: str) -> str:
    if role == "mid":
        return (
            "Первые 4 минуты играй вокруг creep equilibrium: не отдавай free deny, пушь wave перед руной, "
            "и не разменивайся без creep advantage. Если враг сильнее по харассу, быстро добей wave и забери small camp."
        )
    if role == "carry":
        return (
            "Твоя линия про стабильный CS: держи wave ближе к своей башне, проси саппорта блочить pull врага, "
            "и уходи в лес только после boots/первого farming-компонента."
        )
    if role == "offlane":
        return (
            "Твоя задача не умереть до первого utility timing: режь wave только с виженом, бей саппорта когда кор добивает крипов, "
            "и перед ротацией запушь lane под башню."
        )
    return (
        "Играй от вижена и ресурсов кора: разменивай HP за regen врага, блочь camp против pull, "
        "и не показывайся первым, если у врага есть instant disable."
    )


def fight_plan(hero: str, enemy: str, role: str) -> str:
    if role == "support":
        return (
            "В драке стой вторым экраном: сначала дождись прыжка/прокаста врага, потом дай save или disable. "
            "Если тебя видят первым, твой Force/Glimmer не успеет спасти кора."
        )
    if role == "carry":
        return (
            "Не входи первым. Жди, пока враг потратит главный disable, затем жми BKB и бей ближайшую цель, "
            "не ныряя за саппортом под buyback/TP."
        )
    if role == "offlane":
        return (
            "Стартуй только по цели, за которой команда успевает дать урон. Если ключевой enemy save не виден, "
            "лучше вынуди его первым коротким заходом, а потом перезайди."
        )
    return (
        "На миде решает первый spell rotation: заходи с high ground/смока, не показывайся на wave перед дракой, "
        "и держи escape до ответа врага."
    )


def find_best_match(query: dict[str, Any]) -> dict[str, Any] | None:
    entries = load_data()
    query_enemies = set(query["enemies"])
    matches = [
        entry
        for entry in entries
        if entry.get("hero") == query["hero"] and query_enemies & set(entry.get("enemies", []))
    ]
    matches = sorted(matches, key=lambda entry: entry_score(query, entry), reverse=True)
    if not matches or entry_score(query, matches[0]) < 10:
        return None
    return matches[0]


def render_stat_embed(entry: dict[str, Any], query: dict[str, Any]) -> discord.Embed:
    hero = entry.get("hero", query["hero"])
    enemies = entry.get("enemies", query["enemies"])
    enemy = enemies[0] if enemies else query["enemies"][0]
    role = query["role"] if query["role"] != "unknown role" else entry.get("role", "mid")
    enemy_role = query.get("enemy_role", "unknown role")
    enemy_label = f"{enemy} {enemy_role}" if enemy_role != "unknown role" else enemy
    build = role_build(hero, role)
    stats = entry.get("stats", {})
    games = stats.get("games_played", "?")
    winrate = stats.get("winrate")
    if isinstance(winrate, (int, float)):
        description = f"OpenDota: **{winrate:.1f}% winrate** на **{games}** играх. План ниже адаптирован под роль **{role}**."
    else:
        description = f"Статистический матчап из локальной базы. План адаптирован под роль **{role}**."

    embed = discord.Embed(
        title=f"{hero} — {role} vs {enemy_label}",
        description=description,
        color=discord.Color.dark_gold(),
    )
    embed.add_field(name="Линия", value=lane_plan(hero, enemy, role), inline=False)
    embed.add_field(name="Starting", value=build["starting"], inline=False)
    embed.add_field(name="Core", value=build["core"], inline=False)

    sit = "\n".join(f"**{item}** — {reason}" for item, reason in situational_items(hero, [enemy], role))
    embed.add_field(name="Situational items", value=sit[:1024], inline=False)

    tips = [
        build["tips"][0],
        build["tips"][1],
        matchup_tip(hero, enemy, role),
        fight_plan(hero, enemy, role),
    ]
    embed.add_field(name="Как играть", value="\n".join(f"• {tip}" for tip in tips)[:1024], inline=False)
    embed.set_footer(text="Источник: OpenDota stats + локальные правила DotaCoach. Ручные !teach ответы имеют приоритет.")
    return embed


def draft_threats(enemies: list[str], hero: str = "", role: str = "") -> list[str]:
    threats = []
    for enemy in enemies:
        if hero == "Phantom Assassin" and role == "carry" and enemy == "Terrorblade":
            threats.append("**Terrorblade** — не бей в Metamorphosis без BKB/контроля; Skadi/Abyssal помогают добить после Sunder window.")
        elif hero == "Phantom Assassin" and role == "carry" and enemy == "Shadow Demon":
            threats.append("**Shadow Demon** — главный save против PA: не прыгай в core, пока Disruption готов; Nullifier обязателен.")
        elif hero == "Phantom Assassin" and role == "carry" and enemy == "Skywrath Mage":
            threats.append("**Skywrath Mage** — silence/Atos убивает PA до BKB; прыгай после его прокаста или сразу под BKB.")
        elif hero == "Phantom Assassin" and role == "carry" and enemy == "Queen of Pain":
            threats.append("**Queen of Pain** — Orchid/Hex + kite; Abyssal нужен, чтобы удержать её после Blink.")
        elif hero == "Phantom Assassin" and role == "carry" and enemy == "Centaur Warrunner":
            threats.append("**Centaur** — Hoof Stomp + Stampede ломают фокус; жди stun/Stampede или бей другую цель.")
        if hero == "Phantom Assassin" and role == "carry" and enemy in {
            "Terrorblade",
            "Shadow Demon",
            "Skywrath Mage",
            "Queen of Pain",
            "Centaur Warrunner",
        }:
            continue
        if enemy in {"Silencer", "Doom", "Legion Commander", "Bane", "Lion", "Shadow Shaman"}:
            threats.append(f"**{enemy}** — опасный single-target контроль: нужен dispel/save или позиция вне первого прыжка.")
        elif enemy in {"Sniper", "Drow Ranger", "Arc Warden"}:
            threats.append(f"**{enemy}** — дальний урон: нужен заход сбоку, gap-close или Force/Pike план.")
        elif enemy in {"Huskar", "Necrophos", "Alchemist", "Bristleback"}:
            threats.append(f"**{enemy}** — живучесть/отхил: нужен Vessel, Shiva, Skadi или Silver Edge по ситуации.")
        elif enemy in {"Phantom Assassin", "Ursa", "Sven", "Troll Warlord"}:
            threats.append(f"**{enemy}** — физический burst: armor, Ghost/Force на саппортах, kite до конца BKB.")
        elif enemy in {"Naga Siren", "Phantom Lancer", "Chaos Knight", "Terrorblade"}:
            if role == "carry":
                threats.append(f"**{enemy}** — иллюзии/сильный carry: тебе нужны BKB timing, правильный target priority и помощь команды с wave clear.")
            else:
                threats.append(f"**{enemy}** — иллюзии: команде нужны wave clear, Crimson/Shiva и не драться в узком choke.")
        else:
            threats.append(f"**{enemy}** — следи за его ключевым cooldown и не отдавай первый контакт без вижена.")
    return threats[:5]


def draft_game_plan(hero: str, role: str, allies: list[str], enemies: list[str]) -> list[str]:
    plan = []
    if hero == "Phantom Assassin" and role == "carry":
        plan.append("Твой вход — контр-инициация: жди Shadow Demon save, Centaur stun/Stampede, Sky silence/Atos или QoP control, потом прыгай.")
        plan.append("Приоритет слотов: BF/Deso по игре → BKB → Basher/Abyssal → Nullifier; Skadi/Satanic уже после ключевого контроля.")
        if "Shadow Demon" in enemies:
            plan.append("Не коммить Coup de Grace в первую цель, пока SD держит Disruption: сначала вынуди save или купи Nullifier.")
        if "Terrorblade" in enemies:
            plan.append("Против TB не дерись в лоб под Metamorphosis: лови саппортов/мидера, а TB добивай с Abyssal + Skadi после его BKB/Sunder window.")
        return plan

    if role == "support":
        plan.append("Ты не первый герой в драке: держи save/disable до вражеского jump, особенно если есть Duel/Hex/Silence.")
        plan.append("Вижен ставь на подходы к объекту, а не на очевидный cliff: против 5 героев важнее увидеть smoke-route.")
    elif role == "carry":
        plan.append("До BKB/ключевого слота играй от безопасных wave + camps; в драку заходи после первого enemy disable.")
        plan.append("Если у врагов много kite/save, заранее планируй Nullifier/Skadi/Abyssal вместо чистого урона.")
    elif role == "offlane":
        plan.append("Твоя работа — начать драку так, чтобы команда успела дать урон, либо вынудить save и перезайти.")
        plan.append("Если у врагов много магии/иллюзий, utility timing важнее жадного личного урона.")
    else:
        plan.append("На миде играй от рун и первого power spike: твой rotation должен ломать сайд, а не просто стоять 1v1.")
        plan.append("Перед fight не показывайся на wave: для мидера важен первый spell rotation с fog/highground.")

    if allies:
        plan.append(f"Союзники: {', '.join(allies)}. Играй рядом с тем, кто даёт первый контроль или сейвит твой вход.")
    if enemies:
        plan.append(f"Главная цель первого фокуса: обычно самый дальний/тонкий герой из {', '.join(enemies)}, если он без BKB/save.")
    return plan


def render_draft_embed(query: dict[str, Any]) -> discord.Embed:
    hero = query["hero"] or "Твой герой не распознан"
    role = query["role"] if query["role"] != "unknown role" else "роль не указана"
    allies = query["allies"]
    enemies = query["enemies"]

    embed = discord.Embed(
        title=f"5v5 план — {hero} ({role})",
        description="Разбор по форме: твоя роль, союзники, враги, предметы и план драки.",
        color=discord.Color.green(),
    )
    embed.add_field(name="Союзники", value=", ".join(allies) if allies else "Не указаны", inline=False)
    embed.add_field(name="Враги", value=", ".join(enemies) if enemies else "Не распознаны", inline=False)
    if query.get("enemy_roles_text"):
        embed.add_field(name="Позиции врагов", value=query["enemy_roles_text"][:1024], inline=False)

    if query["hero"] and query["role"] != "unknown role":
        build = role_build(query["hero"], query["role"])
        embed.add_field(
            name="Личный билд",
            value=(
                f"**Starting:** {build['starting']}\n"
                f"**Core:** {build['core']}\n"
                f"**Late/option:** {build['situational']}"
            )[:1024],
            inline=False,
        )

    if enemies:
        sit = "\n".join(f"**{item}** — {reason}" for item, reason in situational_items(hero, enemies, query["role"]))
        embed.add_field(name="Situational items", value=sit[:1024], inline=False)
        embed.add_field(name="Главные угрозы", value="\n".join(draft_threats(enemies, query["hero"], query["role"]))[:1024], inline=False)
    else:
        embed.add_field(name="Нужно уточнить", value="Не понял врагов. Напиши 5 героев через запятую или сленгом.", inline=False)

    plan = "\n".join(f"• {tip}" for tip in draft_game_plan(hero, query["role"], allies, enemies))
    embed.add_field(name="План игры", value=plan[:1024], inline=False)
    if query.get("question"):
        embed.add_field(name="Твой вопрос", value=query["question"][:1024], inline=False)
    embed.set_footer(text="5v5 форма использует локальные правила + OpenDota-базу предметов/матчапов.")
    return embed


def render_stat_answer(entry: dict[str, Any], query: dict[str, Any]) -> str:
    hero = entry.get("hero", query["hero"])
    enemies = entry.get("enemies", query["enemies"])
    enemy = enemies[0] if enemies else query["enemies"][0]
    role = query["role"] if query["role"] != "unknown role" else entry.get("role", "mid")
    build = role_build(hero, role)
    stats = entry.get("stats", {})
    games = stats.get("games_played", "?")
    winrate = stats.get("winrate")
    if isinstance(winrate, (int, float)):
        summary = f"По OpenDota матчап около {winrate:.1f}% winrate на {games} играх."
    else:
        summary = "По OpenDota это статистический матчап из публичной базы."

    return (
        f"**{hero} vs {enemy} — {role}**\n"
        f"{summary} План меняется от роли: предметы и позиционирование ниже собраны под `{role}`.\n\n"
        f"**Starting items:** {build['starting']}\n"
        f"**Core build:** {build['core']}\n"
        f"**Situational:** {build['situational']}\n\n"
        "**Key tips:**\n"
        f"- {build['tips'][0]}\n"
        f"- {build['tips'][1]}\n"
        f"- {matchup_tip(hero, enemy, role)}"
    )


def lookup_answer(query: dict[str, Any]) -> str:
    if not query["hero"]:
        return "Кого играешь? Напиши героя, роль и врагов."
    if not query["enemies"]:
        return "Кто враги?"

    match = find_best_match(query)
    if not match:
        last = f"{query['hero']} | {query['role']} | {', '.join(query['enemies'])}"
        return (
            f"Я пока не знаю этот матчап: `{last}`.\n"
            "Научи меня: `!teach Starting items: ... Core build: ... Key tips: ...`"
        )
    if match.get("source") == "OpenDota":
        return render_stat_answer(match, query)[:1900]

    answer = match["answer"]
    entry_role = match.get("role")
    if query["role"] != "unknown role" and entry_role and entry_role != query["role"]:
        answer = answer.replace(f"— {entry_role}", f"— {query['role']}", 1)
    return answer[:1900]


def lookup_embed(query: dict[str, Any]) -> discord.Embed | None:
    if not query["hero"] or not query["enemies"]:
        return None
    match = find_best_match(query)
    if not match or match.get("source") != "OpenDota":
        return None
    return render_stat_embed(match, query)


def add_entry(hero: str, role: str, enemies: str, answer: str) -> None:
    entries = load_data()
    enemy_list = [enemy.strip() for enemy in enemies.split(",") if enemy.strip()]
    entries.append({"hero": hero.strip(), "role": role.strip(), "enemies": enemy_list, "answer": answer.strip()})
    save_data(entries)


async def answer_message(message: discord.Message, question: str) -> None:
    query = parse_query(question)
    last_query_by_channel[message.channel.id] = query
    embed = lookup_embed(query)
    if embed:
        await message.reply(embed=embed, mention_author=False)
    else:
        await message.reply(lookup_answer(query), mention_author=False)


@bot.event
async def on_ready() -> None:
    synced = await bot.tree.sync()
    print(f"Logged in as {bot.user} | synced {len(synced)} slash commands")


@bot.tree.command(name="coach", description="Ask local DotaCoach for matchup, build, or strategy advice.")
@app_commands.describe(question="Например: играю TA мид против Viper и AA")
async def coach_slash(interaction: discord.Interaction, question: str) -> None:
    query = parse_query(question)
    if interaction.channel_id:
        last_query_by_channel[interaction.channel_id] = query
    embed = lookup_embed(query)
    if embed:
        await interaction.response.send_message(embed=embed)
    else:
        await interaction.response.send_message(lookup_answer(query))


@bot.tree.command(name="form", description="Open a DotaCoach question form.")
async def form_slash(interaction: discord.Interaction) -> None:
    await interaction.response.send_modal(CoachModal())


@bot.tree.command(name="draft", description="Open a 5v5 DotaCoach draft form.")
async def draft_slash(interaction: discord.Interaction) -> None:
    await interaction.response.send_modal(DraftModal())


@bot.tree.command(name="help", description="Show DotaCoach commands and examples.")
async def help_slash(interaction: discord.Interaction) -> None:
    await interaction.response.send_message(embed=make_help_embed(), ephemeral=True)


@bot.tree.command(name="learn", description="Teach DotaCoach a matchup answer.")
@app_commands.describe(
    hero="Hero name, e.g. Templar Assassin",
    role="mid/carry/offlane/support",
    enemies="Comma-separated enemies, e.g. Viper, Ancient Apparition",
    answer="Full answer that bot should return",
)
async def learn_slash(interaction: discord.Interaction, hero: str, role: str, enemies: str, answer: str) -> None:
    add_entry(hero, role, enemies, answer)
    await interaction.response.send_message("Запомнил матчап.", ephemeral=True)


@bot.event
async def on_message(message: discord.Message) -> None:
    if message.author.bot:
        return

    content = message.content.strip()
    lowered = content.lower()

    if lowered in {"!help", "!coach help", "!coach помощь", "!помощь"}:
        await message.reply(embed=make_help_embed(), mention_author=False)
        return

    if lowered in {"!form", "!coach form", "!форма"}:
        await message.reply(
            "Нажми кнопку, чтобы открыть форму DotaCoach.",
            view=CoachFormView(),
            mention_author=False,
        )
        return

    if lowered in {"!draft", "!5v5", "!драфт", "!coach draft"}:
        await message.reply(
            "Нажми кнопку, чтобы открыть 5v5 форму DotaCoach.",
            view=DraftFormView(),
            mention_author=False,
        )
        return

    if lowered.startswith("!learn"):
        payload = content[len("!learn"):].strip()
        parts = [part.strip() for part in payload.split("|", 3)]
        if len(parts) != 4:
            await message.reply("Формат: `!learn герой | роль | враги через запятую | ответ`", mention_author=False)
            return
        add_entry(parts[0], parts[1], parts[2], parts[3])
        await message.reply("Запомнил матчап.", mention_author=False)
        return

    if lowered.startswith("!teach"):
        answer = content[len("!teach"):].strip()
        query = last_query_by_channel.get(message.channel.id)
        if not query:
            await message.reply("Сначала спроси матчап, потом отправь `!teach ответ`.", mention_author=False)
            return
        if not answer:
            await message.reply("Добавь текст ответа после `!teach`.", mention_author=False)
            return
        add_entry(query["hero"], query["role"], ", ".join(query["enemies"]), answer)
        await message.reply("Запомнил ответ для последнего матчапа.", mention_author=False)
        return

    if lowered.startswith("!coach"):
        question = content[len("!coach"):].strip()
        if not question:
            await message.reply("Напиши героя, роль и врагов. Например: `!coach играю TA мид против Viper и AA`")
            return
        await answer_message(message, question)
        return

    if bot.user and bot.user in message.mentions:
        question = clean_mention(content)
        if not question:
            await message.reply("Напиши героя, роль и врагов. Например: `играю TA мид против Viper и AA`")
            return
        await answer_message(message, question)


def clean_mention(text: str) -> str:
    if bot.user:
        return text.replace(f"<@{bot.user.id}>", "").replace(f"<@!{bot.user.id}>", "").strip()
    return text.strip()


bot.run(DISCORD_TOKEN)
