import argparse
import json
import time
import urllib.error
import urllib.request
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any


API_BASE = "https://api.opendota.com/api"

ROLE_MAP = {
    "Carry": "carry",
    "Nuker": "mid",
    "Initiator": "offlane",
    "Disabler": "support",
    "Durable": "offlane",
    "Escape": "mid",
    "Support": "support",
    "Pusher": "carry",
    "Jungler": "offlane",
}

GENERIC_RU_TIPS = {
    "mid": [
        "Проверь power rune заранее: против тяжёлого матчапа руна часто важнее лишнего крипа.",
        "Если линия плохая, добивай wave быстро и уходи в ближайший camp, не стой под бесплатный харасс.",
        "Перед дракой поставь вижен/контроль на подход: тебе нужно начать первым, а не отвечать после стана.",
    ],
    "carry": [
        "Не приходи в драку без ключевого слота: сначала забери безопасную линию и ближайший camp.",
        "Держи TP на ответную драку, но не телепортируйся первым, если враг ещё держит контроль.",
        "Фарми сторону карты, где видны два-три врага: так ты не отдашь тайминг под smoke.",
    ],
    "offlane": [
        "Дави wave под башню перед ротацией, чтобы враг терял крипов, пока ты дерёшься.",
        "Начинай драку только когда видишь главную контр-способность врага или можешь её пережить.",
        "Если вас кайтят, купи utility раньше урона: Force/Blade Mail/Pipe часто важнее жадного слота.",
    ],
    "support": [
        "Ставь вижен не на клифф в лоб, а на подход к драке, чтобы не умереть первым.",
        "Держи сейв-скилл/предмет под ключевой прокаст врага, не трать его на случайный харасс.",
        "Играй за спиной кора: твоя задача дать disable и save, а не начинать драку лицом.",
    ],
}


def fetch_json(path: str, retries: int = 5) -> Any:
    url = f"{API_BASE}{path}"
    req = urllib.request.Request(url, headers={"User-Agent": "DotaCoachLocalBot/1.0"})
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            if exc.code != 429 or attempt == retries - 1:
                raise
            wait = 20 + attempt * 20
            print(f"  rate limited, waiting {wait}s")
            time.sleep(wait)
    raise RuntimeError(f"Failed to fetch {url}")


def load_item_names() -> dict[int, str]:
    data = fetch_json("/constants/items")
    result = {}
    for key, item in data.items():
        if not isinstance(item, dict) or "id" not in item:
            continue
        name = item.get("dname") or item.get("hint") or key.replace("_", " ").title()
        result[int(item["id"])] = str(name)
    return result


def top_items(item_bucket: dict[str, int] | None, item_names: dict[int, str], limit: int) -> list[str]:
    if not item_bucket:
        return []
    counts = Counter({int(item_id): count for item_id, count in item_bucket.items()})
    names = []
    for item_id, _ in counts.most_common(limit * 3):
        name = item_names.get(item_id)
        if name and name not in names:
            names.append(name)
        if len(names) >= limit:
            break
    return names


def choose_role(hero: dict[str, Any]) -> str:
    for role in hero.get("roles", []):
        if role in ROLE_MAP:
            return ROLE_MAP[role]
    return "mid"


def winrate(matchup: dict[str, Any]) -> float:
    games = matchup.get("games_played", 0) or 1
    return matchup.get("wins", 0) / games


def make_answer(
    hero: str,
    role: str,
    enemies: list[str],
    start_items: list[str],
    core_items: list[str],
    situational: str,
    bad_wr: float,
    games: int,
) -> str:
    enemy_text = ", ".join(enemies)
    start_text = ", ".join(start_items) if start_items else "Tango, Stick, stats по линии"
    core_text = " → ".join(core_items) if core_items else "ранний слот на выживание → BKB → damage/utility"
    situational_text = situational or "BKB/Linken's (если у врага много контроля)"
    tips = GENERIC_RU_TIPS.get(role, GENERIC_RU_TIPS["mid"])
    counter_tip = f"Против {enemy_text}: не начинай драку, пока не видишь их ключевой disable/ульт, или заходи с вижена первым."

    return (
        f"**{hero} vs {enemy_text} — {role}**\n"
        f"По OpenDota это тяжёлый матчап: около {bad_wr:.1f}% winrate на {games} играх. "
        "Играй от таймингов предметов и не отдавай первый контакт без вижена.\n\n"
        f"**Starting items:** {start_text}\n"
        f"**Core build:** {core_text}\n"
        f"**Situational:** {situational_text}\n\n"
        "**Key tips:**\n"
        f"- {tips[0]}\n"
        f"- {tips[1]}\n"
        f"- {counter_tip}"
    )


def backup_output(path: Path) -> None:
    if not path.exists():
        return
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = path.with_name(f"{path.stem}.backup_{stamp}{path.suffix}")
    path.replace(backup)
    print(f"Backup saved: {backup}")


def load_existing_manual_entries(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
    except UnicodeDecodeError:
        data = json.loads(path.read_text(encoding="utf-16"))
    if not isinstance(data, list):
        return []
    return [entry for entry in data if entry.get("source") == "manual"]


def main() -> None:
    parser = argparse.ArgumentParser(description="Build DotaCoach knowledge_base.json from OpenDota.")
    parser.add_argument("--output", default="knowledge_base.json")
    parser.add_argument("--matchups-per-hero", type=int, default=5)
    parser.add_argument("--min-games", type=int, default=80)
    parser.add_argument("--limit-heroes", type=int, default=0)
    parser.add_argument("--sleep", type=float, default=1.5)
    args = parser.parse_args()

    output = Path(args.output)
    manual_entries = load_existing_manual_entries(output)
    heroes = fetch_json("/heroes")
    hero_by_id = {hero["id"]: hero for hero in heroes}
    item_names = load_item_names()
    entries = []

    selected_heroes = heroes[: args.limit_heroes] if args.limit_heroes else heroes

    for index, hero in enumerate(selected_heroes, start=1):
        hero_id = hero["id"]
        hero_name = hero["localized_name"]
        role = choose_role(hero)
        print(f"[{index}/{len(selected_heroes)}] {hero_name}")

        try:
            matchups = fetch_json(f"/heroes/{hero_id}/matchups")
            item_popularity = fetch_json(f"/heroes/{hero_id}/itemPopularity")
        except Exception as exc:
            print(f"  skip: {exc}")
            time.sleep(args.sleep)
            continue

        bad_matchups = [
            matchup
            for matchup in matchups
            if matchup.get("games_played", 0) >= args.min_games and matchup["hero_id"] in hero_by_id
        ]
        bad_matchups.sort(key=winrate)

        start_items = top_items(item_popularity.get("start_game_items"), item_names, 4)
        early_items = top_items(item_popularity.get("early_game_items"), item_names, 2)
        mid_items = top_items(item_popularity.get("mid_game_items"), item_names, 3)
        late_items = top_items(item_popularity.get("late_game_items"), item_names, 1)
        core_items = (early_items + mid_items + late_items)[:4]
        situational = core_items[-1] if core_items else "BKB"

        for matchup in bad_matchups[: args.matchups_per_hero]:
            enemy = hero_by_id[matchup["hero_id"]]["localized_name"]
            games = matchup.get("games_played", 0)
            wr = winrate(matchup) * 100
            entries.append(
                {
                    "hero": hero_name,
                    "role": role,
                    "enemies": [enemy],
                    "answer": make_answer(hero_name, role, [enemy], start_items, core_items, situational, wr, games),
                    "source": "OpenDota",
                    "stats": {"games_played": games, "winrate": round(wr, 2)},
                }
            )
        time.sleep(args.sleep)

    existing_keys = {
        (entry.get("hero"), entry.get("role"), tuple(entry.get("enemies", [])))
        for entry in entries
    }
    for entry in reversed(manual_entries):
        key = (entry.get("hero"), entry.get("role"), tuple(entry.get("enemies", [])))
        if key not in existing_keys:
            entries.insert(0, entry)
            existing_keys.add(key)

    backup_output(output)
    output.write_text(json.dumps(entries, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Done: wrote {len(entries)} entries to {output} ({len(manual_entries)} manual preserved)")


if __name__ == "__main__":
    main()
