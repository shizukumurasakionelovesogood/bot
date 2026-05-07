# DotaCoach Discord Bot

Discord bot without AI APIs. It answers from a local `knowledge_base.json` and can be taught with Discord commands.

## Setup

1. Create a Discord application and bot at <https://discord.com/developers/applications>.
2. Enable **Message Content Intent** for the bot.
3. Copy `.env.example` to `.env` and fill in `DISCORD_TOKEN`.
4. Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

5. Run:

```powershell
python bot.py
```

## Ask

```text
/coach играю TA мид против Viper и AA
!coach играю AM керри против Naga
@DotaCoach что брать на Huskar против Axe, AA, Drow
```

## Teach

```text
!learn Templar Assassin | mid | Viper, Ancient Apparition | **Templar Assassin vs Viper, AA — mid** ...
```

Quick teach after an unknown matchup:

```text
!teach **Huskar vs Viper, AA — mid**
Viper мешает стоять на линии, AA ломает весь отхил через Ice Blast.

**Starting items:** Bracer parts, Tango, Stick
**Core build:** Armlet → BKB → Satanic
**Situational:** Halberd (против физ. урона)

**Key tips:**
- Не прыгай Life Break, пока AA держит Ice Blast
- Держи Stick/Wand заряды под Viper spam
- BKB жми до Ice Blast
```

## Import OpenDota Base

Generate a local statistical knowledge base from OpenDota:

```powershell
python import_opendota.py --matchups-per-hero 5 --min-games 80 --sleep 1.5
```

The script creates a backup before replacing `knowledge_base.json`.

Useful options:

```powershell
python import_opendota.py --limit-heroes 20
python import_opendota.py --matchups-per-hero 8 --min-games 40 --sleep 2
```

OpenDota can rate-limit requests, so keep `--sleep` at `1.5` or higher for a full import.
