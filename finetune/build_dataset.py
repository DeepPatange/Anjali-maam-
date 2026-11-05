"""
Build the fine-tuning dataset for the custom story model.

Source: "Thousand Stories, Hundred Genres" (FareedKhan/1k_stories_100_genre on
Hugging Face, CC-BY-2.0): 1,000 short stories, each with a title and a genre.

Each story is turned into training samples in the exact format the application
uses at run time:

  1. The story is back-labelled with answers to the application's own 17
     questions (setting, character, theme, plot) using keyword rules.
  2. A question budget (4, 8, 12 or 17) is sampled and the first N answers are
     passed through the application's ContextExtractionEngine and
     PromptEngineeringLayer, so the system and user prompts are identical to
     the ones produced by the running system.
  3. The story is cut into segments. The opening becomes the target of the
     "story init" prompt; later segments become targets of the continuation,
     climax and resolution prompts.

Output: data/train.jsonl, data/valid.jsonl, data/test.jsonl (chat format, one
{"messages": [...]} object per line) and data/stats.json.

Usage:  python finetune/build_dataset.py
"""

import argparse
import collections
import csv
import json
import random
import re
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app.modules.context_extraction import ContextExtractionEngine  # noqa: E402
from app.modules.prompt_engineering import PromptEngineeringLayer  # noqa: E402

DATA_DIR = Path(__file__).resolve().parent / "data"
RAW_CSV = DATA_DIR / "raw" / "1k_stories_100_genre.csv"
SOURCE_URL = ("https://huggingface.co/datasets/FareedKhan/1k_stories_100_genre/"
              "resolve/main/1k_stories_100_genre.csv")

# Order in which the front end presents questions; a budget of N uses the first N.
QUESTION_ORDER = [
    "setting_1", "setting_2", "setting_3", "setting_4",
    "char_1", "char_2", "char_3", "char_4", "char_5",
    "theme_1", "theme_2", "theme_3", "theme_4",
    "plot_1", "plot_2", "plot_3", "plot_4",
]
BUDGETS = [(17, 0.50), (12, 0.25), (8, 0.15), (4, 0.10)]

CHOICE_SYSTEM = "Generate 4 brief story choices as numbered options. Be creative and engaging."


# --------------------------------------------------------------------------
# Back-labelling rules
# --------------------------------------------------------------------------
def count(text, words):
    return sum(len(re.findall(r"\b" + w, text)) for w in words)


def pick(text, table, default):
    """Return the option whose keyword list scores highest in `text`."""
    best, best_score = default, 0
    for option, words in table:
        score = count(text, words)
        if score > best_score:
            best, best_score = option, score
    return best


GENRE_RULES = [
    ("Science Fiction (technology, space)",
     ["sci", "cyber", "space", "dystop", "steampunk", "time travel", "apocal", "alien", "futur", "robot", "techno"]),
    ("Fantasy (magic, mythical creatures)",
     ["fantasy", "fairy", "myth", "magic", "legend", "fable", "folk", "sword", "superhero", "paranormal", "supernatural"]),
    ("Mystery (puzzles, detective work)", ["mystery", "detective", "crime", "noir", "whodunit", "heist"]),
    ("Romance (love stories, relationships)", ["roman", "love", "chick"]),
    ("Thriller (suspense, action)", ["thriller", "horror", "suspense", "spy", "espionage", "gothic", "war", "military", "action"]),
    ("Adventure (quests, exploration)", ["adventure", "quest", "western", "pirate", "survival", "travel", "explor"]),
]

SETTING_RULES = [
    ("A futuristic sci-fi world with advanced technology",
     ["spaceship", "robot", "android", "galaxy", "starship", "cyber", "hologram", "colony", "planet", "laser", "futuristic"]),
    ("A magical fantasy realm with castles and dragons",
     ["magic", "dragon", "wizard", "castle", "kingdom", "sorcer", "elf", "elves", "enchanted", "spell", "witch"]),
    ("A historical setting from the past",
     ["century", "medieval", "victorian", "sultan", "pharaoh", "knight", "samurai", "colonial", "musket", "carriage"]),
    ("A mysterious supernatural dimension",
     ["ghost", "spirit", "haunted", "demon", "vampire", "werewolf", "curse", "supernatural", "paranormal", "otherworld"]),
    ("The real modern world we live in",
     ["phone", "internet", "office", "car ", "apartment", "coffee", "email", "police", "detective", "computer", "college"]),
]

LOCATION_RULES = [
    ("Bustling cities and urban environments", ["city", "street", "town", "market", "apartment", "building", "alley"]),
    ("Enchanted forests and natural landscapes", ["forest", "woods", "jungle", "river", "meadow", "valley", "tree"]),
    ("Space stations or alien planets", ["space", "planet", "station", "galaxy", "ship's", "orbit", "alien"]),
    ("Underwater kingdoms or oceanic adventures", ["ocean", "sea ", "underwater", "island", "ship", "waves", "sail"]),
    ("Mountains, caves, or underground realms", ["mountain", "cave", "underground", "cavern", "tunnel", "peak", "cliff"]),
]

TRAIT_RULES = [
    ("Brave and courageous", ["brave", "courage", "fearless", "bold", "valiant", "hero"]),
    ("Clever and witty", ["clever", "wit", "intelligen", "smart", "brilliant", "cunning", "genius"]),
    ("Kind and compassionate", ["kind", "compassion", "caring", "gentle", "generous", "warm"]),
    ("Mysterious and secretive", ["mysterious", "secret", "enigma", "quiet", "shadow", "hidden"]),
    ("Rebellious and independent", ["rebel", "independen", "defian", "stubborn", "free spirit", "outlaw"]),
]

MOTIVE_RULES = [
    ("Love and relationships", ["love", "heart", "beloved", "romance", "marry", "family"]),
    ("Revenge or justice", ["revenge", "justice", "avenge", "vengeance", "crime", "guilty"]),
    ("Curiosity and discovery", ["discover", "curio", "explor", "secret", "mystery", "learn", "truth"]),
    ("Duty and responsibility", ["duty", "responsib", "mission", "honor", "oath", "sworn", "serve"]),
    ("Survival and protection", ["surviv", "protect", "escape", "danger", "defend", "save"]),
    ("Redemption and forgiveness", ["redemption", "forgive", "redeem", "regret", "atone", "guilt"]),
]

ALLY_RULES = [
    ("A loyal best friend", ["friend", "best friend", "companion", "partner"]),
    ("A wise mentor figure", ["mentor", "teacher", "master", "elder", "old man", "wise"]),
    ("A group of diverse companions", ["crew", "team", "group", "companions", "band of", "allies"]),
    ("A mysterious stranger who helps", ["stranger", "hooded", "unknown figure"]),
    ("A magical creature or pet", ["creature", "dragon", "dog", "cat ", "horse", "wolf", "pet "]),
    ("The character journeys alone", ["alone", "lonely", "solitary", "by himself", "by herself"]),
]

ANTAGONIST_RULES = [
    ("A powerful villain with dark motives", ["villain", "evil", "dark lord", "tyrant", "sorcerer", "warlord", "killer", "murderer"]),
    ("A corrupt organization or government", ["corporation", "government", "regime", "council", "empire", "company", "corrupt", "agency"]),
    ("Forces of nature or supernatural threats", ["storm", "monster", "beast", "ghost", "demon", "plague", "flood", "wilderness"]),
    ("Internal struggles and personal demons", ["fear", "doubt", "guilt", "grief", "anxiety", "lonel", "himself", "herself"]),
    ("A rival with conflicting goals", ["rival", "competitor", "opponent", "enemy", "nemesis"]),
    ("An ancient evil awakening", ["ancient", "curse", "awaken", "prophecy", "forgotten", "sealed"]),
]

THEME_RULES = [
    ("Friendship and loyalty", ["friend", "loyal", "together", "trust", "bond"]),
    ("Sacrifice and heroism", ["sacrifice", "hero", "brave", "courage", "save"]),
    ("Identity and self-discovery", ["identity", "who he was", "who she was", "herself", "himself", "true self", "destiny"]),
    ("Power and corruption", ["power", "corrupt", "control", "greed", "throne", "rule"]),
    ("Nature and environment", ["nature", "forest", "earth", "environment", "river", "animal"]),
    ("Technology and humanity", ["technology", "machine", "robot", "artificial", "human", "computer"]),
]

ENDING_RULES = [
    ("Happy ending where everything works out", ["happy", "smile", "peace", "joy", "celebrat", "ever after", "hope", "laugh"]),
    ("Bittersweet with some sacrifice", ["sacrifice", "loss", "tears", "farewell", "memory", "never forget", "bittersweet", "grief"]),
    ("Ambiguous, leaving some mystery", ["mystery", "unknown", "wonder", "perhaps", "never knew", "question"]),
    ("Open-ended for continuation", ["next adventure", "another journey", "only the beginning", "new chapter", "to be continued"]),
    ("Unexpected twist ending", ["twist", "all along", "realized", "revealed", "truth was", "never expected"]),
]

# Derived directly from the mapped genre (index into GENRE_RULES order).
BY_GENRE = {
    "Science Fiction (technology, space)": dict(
        time="Distant future (space age, post-apocalyptic)", atmosphere="Thrilling and suspenseful",
        journey="Thought-provoking and philosophical", tone="Serious and dramatic",
        style="A balanced mix of both"),
    "Fantasy (magic, mythical creatures)": dict(
        time="Ancient times (medieval, mythological)", atmosphere="Bright and adventurous",
        journey="Uplifting and inspiring", tone="Serious and dramatic", style="A balanced mix of both"),
    "Mystery (puzzles, detective work)": dict(
        time="Present day (contemporary)", atmosphere="Dark and mysterious",
        journey="Thrilling and exciting", tone="Dark and intense", style="Mystery-focused with puzzles to solve"),
    "Romance (love stories, relationships)": dict(
        time="Present day (contemporary)", atmosphere="Romantic and emotional",
        journey="Heartwarming and comforting", tone="Lighthearted and fun",
        style="Character-driven with deep emotions"),
    "Thriller (suspense, action)": dict(
        time="Present day (contemporary)", atmosphere="Thrilling and suspenseful",
        journey="Thrilling and exciting", tone="Dark and intense", style="Action-heavy with lots of excitement"),
    "Adventure (quests, exploration)": dict(
        time="Historical past (Victorian, Renaissance, etc.)", atmosphere="Bright and adventurous",
        journey="Uplifting and inspiring", tone="Lighthearted and fun", style="Action-heavy with lots of excitement"),
}

CONFLICT_BY_ANTAGONIST = {
    "A powerful villain with dark motives": "Person vs. Person (battles, rivalries)",
    "A corrupt organization or government": "Person vs. Society (rebellion, justice)",
    "Forces of nature or supernatural threats": "Person vs. Nature (survival, disasters)",
    "Internal struggles and personal demons": "Person vs. Self (inner struggles)",
    "A rival with conflicting goals": "Person vs. Person (battles, rivalries)",
    "An ancient evil awakening": "Person vs. Supernatural (magic, gods)",
}

NOT_NAMES = set("""The A An In On At It He She They We I You His Her Their Its But And Or As With For From When While
After Before Then There This That These Those If So Yet Now One Once Every Each All Some Many No Not What Why How Who
Where Mr Mrs Ms Dr Sir Lady Lord King Queen Prince Princess Captain Professor Doctor Detective Sultan Emperor General
Monday Tuesday Wednesday Thursday Friday Saturday Sunday January February March April May June July August September
October November December God Earth English French American British Chapter Suddenly Finally However Meanwhile
Together Without Inside Outside Despite Although Though Just Even Still Only Perhaps Maybe Yes Oh Well Here
North South East West New Old Great Little Dear Thank Please Let Could Would Should Did Do Does Was Were Is Are
Have Has Had Will Can May Might Must Upon Over Under Into Through During Since Until Because Something Nothing
Everyone Someone Anyone Nobody Everything Time Day Night Years Year Long Far Deep High Eye City Tech
Chapter Part Prologue Epilogue Order World Resistance""".split())


def find_protagonist(story):
    """Most frequent personal name: a capitalised word that is not sentence-initial
    filler, is not used as a group or place ("the Resistance", "Aetherians")."""
    tokens = re.findall(r"(?<![.!?\"“]\s)(?<!^)\b([A-Z][a-z]{2,})\b", story)
    counts = collections.Counter(t for t in tokens if t not in NOT_NAMES)
    for name in re.findall(r"\b(?:named|name was|name is) ([A-Z][a-z]{2,})\b", story):
        if name not in NOT_NAMES:
            counts[name] += 3
    for name, n in counts.most_common(6):
        if n < 3:
            break
        after_the = len(re.findall(r"\b[Tt]he " + name + r"\b", story))
        plural = len(re.findall(r"\b" + name + r"s\b", story))
        place = len(re.findall(r"\b(?:in|at|to|from|of) " + name + r"\b", story))
        if after_the + plural + place > 0.34 * n:
            continue
        return name
    return None


def map_genre(genre_label, story_lower):
    label = genre_label.lower()
    for option, words in GENRE_RULES:
        if any(w in label for w in words):
            return option
    return pick(story_lower, GENRE_RULES, "Adventure (quests, exploration)")


def map_setting(label, story_lower):
    """Setting type: the dataset genre decides when it is explicit, keywords otherwise."""
    by_label = [
        ("A futuristic sci-fi world with advanced technology",
         ["sci", "cyber", "space", "dystop", "apocal", "steampunk", "time travel", "alien", "futur"]),
        ("A magical fantasy realm with castles and dragons",
         ["fantasy", "fairy", "myth", "magic", "sword", "legend", "fable", "folk"]),
        ("A historical setting from the past", ["histor", "western", "medieval", "period", "pirate"]),
        ("A mysterious supernatural dimension", ["paranormal", "supernatural", "ghost", "gothic", "occult"]),
    ]
    for option, words in by_label:
        if any(w in label for w in words):
            return option
    return pick(story_lower, SETTING_RULES, "The real modern world we live in")


def label_story(row):
    """Answer the application's 17 questions for one story."""
    story = row["story"]
    low = story.lower()
    genre = map_genre(row["genre"], low)
    g = BY_GENRE[genre]
    label = row["genre"].lower()

    tone = g["tone"]
    if any(w in label for w in ["comedy", "humor", "satire", "parody"]):
        tone = "Humorous with witty dialogue"
    elif any(w in label for w in ["horror", "noir", "gothic", "dystop", "dark"]):
        tone = "Dark and intense"
    elif any(w in label for w in ["philosoph", "literary"]):
        tone = "Philosophical and reflective"

    time_period = g["time"]
    if any(w in label for w in ["histor", "western", "medieval", "war"]):
        time_period = "Historical past (Victorian, Renaissance, etc.)"

    antagonist = pick(low, ANTAGONIST_RULES, "A rival with conflicting goals")
    ending_text = " ".join(story.split()[-140:]).lower()
    answers = {
        "setting_1": map_setting(label, low),
        "setting_2": time_period,
        "setting_3": "Comedic and lighthearted" if tone.startswith("Humorous") else g["atmosphere"],
        "setting_4": pick(low, LOCATION_RULES, "Bustling cities and urban environments"),
        "char_2": pick(low, TRAIT_RULES, "Brave and courageous"),
        "char_3": pick(low, MOTIVE_RULES, "Curiosity and discovery"),
        "char_4": pick(low, ALLY_RULES, "A loyal best friend"),
        "char_5": antagonist,
        "theme_1": genre,
        "theme_2": g["journey"],
        "theme_3": pick(low, THEME_RULES, "Friendship and loyalty"),
        "theme_4": tone,
        "plot_1": CONFLICT_BY_ANTAGONIST[antagonist],
        "plot_2": g["style"],
        "plot_3": "Moderately complex with some twists",
        "plot_4": pick(ending_text, ENDING_RULES, "Happy ending where everything works out"),
    }
    name = find_protagonist(story)
    if name:
        answers["char_1"] = name
    return answers


# --------------------------------------------------------------------------
# Story segmentation and prompt construction
# --------------------------------------------------------------------------
def segment(story, first=(280, 430), rest=(230, 360)):
    """Cut a story into an opening and follow-up segments at paragraph breaks."""
    paras = [p.strip() for p in re.split(r"\n\s*\n|\n", story) if p.strip()]
    segments, cur, cur_words = [], [], 0
    lo, hi = first
    for p in paras:
        n = len(p.split())
        if cur and cur_words + n > hi:
            segments.append("\n\n".join(cur))
            cur, cur_words = [], 0
            lo, hi = rest
        cur.append(p)
        cur_words += n
        if cur_words >= lo:
            segments.append("\n\n".join(cur))
            cur, cur_words = [], 0
            lo, hi = rest
    if cur:
        if segments and cur_words < 120:
            segments[-1] += "\n\n" + "\n\n".join(cur)
        else:
            segments.append("\n\n".join(cur))
    return segments


def direction_for(seg, position):
    """Pick the continuation option that best describes what `seg` does."""
    low = seg.lower()
    words = max(1, len(seg.split()))
    quotes = (seg.count('"') + seg.count("“")) / words
    if position >= 0.6:
        return "Move towards the climax and resolution"
    if count(low, ["suddenly", "unexpected", "to his surprise", "to her surprise", "little did", "without warning"]) >= 2:
        return "Add a surprising twist"
    if count(low, ["mystery", "strange", "secret", "discovered", "hidden", "clue", "puzzle"]) >= 2:
        return "Introduce a new challenge or mystery"
    if quotes > 0.02:
        return "Develop the characters and relationships"
    return "Continue with more action and adventure"


def tail_words(text, n):
    words = text.split()
    return text if len(words) <= n else "... " + " ".join(words[-n:])


def clean_story(story):
    """Drop chapter headings and stray indentation; the UI adds its own chapter titles."""
    lines = [ln.strip() for ln in story.replace("\r", "").split("\n")]
    lines = [ln for ln in lines if not re.match(r"^(chapter|part|prologue|epilogue)\b[^.!?]{0,60}$", ln, re.I)]
    return "\n".join(lines).strip()


def build_examples(row, rng, prev_words):
    row = dict(row, story=clean_story(row["story"]))
    answers = label_story(row)
    budget = rng.choices([b for b, _ in BUDGETS], [w for _, w in BUDGETS])[0]
    responses = {q: answers[q] for q in QUESTION_ORDER[:budget] if q in answers}
    # Half of the samples also carry the fine-grained genre as a user-added question,
    # which exercises the custom_elements channel.
    if rng.random() < 0.5:
        responses["custom_q_1"] = f"What sub-genre should the story be? -> {row['genre']}"

    context = ContextExtractionEngine().extract_from_responses(responses)
    layer = PromptEngineeringLayer()
    system = layer.build_system_prompt(context)

    segs = segment(row["story"])
    if not segs or len(segs[0].split()) < 120:
        return []

    def sample(kind, user, target):
        return {
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
                {"role": "assistant", "content": target},
            ],
            "meta": {"story_id": row["id"], "kind": kind, "budget": budget, "genre": row["genre"]},
        }

    out = [sample("init", layer.build_story_init_prompt(context), segs[0])]
    last = len(segs) - 1
    for i in range(1, len(segs)):
        recent = "\n\n".join(segs[max(0, i - 2):i])  # the app passes the last two segments
        if i == last and last >= 1:
            user = layer.build_resolution_prompt(context, tail_words(recent, prev_words))
            kind = "resolution"
        elif i == last - 1 and last >= 3:
            user = layer.build_climax_prompt(context, recent)
            kind = "climax"
        else:
            user = layer.build_continuation_prompt(
                context, tail_words(recent, prev_words), direction_for(segs[i], i / max(1, last)))
            kind = "continuation"
        out.append(sample(kind, user, segs[i]))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--prev-words", type=int, default=350,
                    help="words of earlier story kept in continuation/resolution prompts")
    ap.add_argument("--max-words", type=int, default=1150,
                    help="drop samples whose prompt + target exceed this many words")
    args = ap.parse_args()

    RAW_CSV.parent.mkdir(parents=True, exist_ok=True)
    if not RAW_CSV.exists():
        print("downloading", SOURCE_URL)
        urllib.request.urlretrieve(SOURCE_URL, RAW_CSV)

    rows = list(csv.DictReader(open(RAW_CSV, encoding="utf-8")))
    rng = random.Random(args.seed)
    rng.shuffle(rows)
    n = len(rows)
    splits = {"train": rows[: int(n * 0.90)], "valid": rows[int(n * 0.90): int(n * 0.95)],
              "test": rows[int(n * 0.95):]}

    stats = {"source": "FareedKhan/1k_stories_100_genre (CC-BY-2.0)", "stories": n, "splits": {}}
    for name, split_rows in splits.items():
        samples, dropped = [], 0
        for row in split_rows:
            for ex in build_examples(row, rng, args.prev_words):
                total = sum(len(m["content"].split()) for m in ex["messages"])
                if total > args.max_words:
                    dropped += 1
                    continue
                samples.append(ex)
        rng.shuffle(samples)
        with open(DATA_DIR / f"{name}.jsonl", "w", encoding="utf-8") as f:
            for ex in samples:
                f.write(json.dumps({"messages": ex["messages"]}, ensure_ascii=False) + "\n")
        with open(DATA_DIR / f"{name}_meta.jsonl", "w", encoding="utf-8") as f:
            for ex in samples:
                f.write(json.dumps(ex["meta"], ensure_ascii=False) + "\n")
        kinds = collections.Counter(ex["meta"]["kind"] for ex in samples)
        budgets = collections.Counter(ex["meta"]["budget"] for ex in samples if ex["meta"]["kind"] == "init")
        words = [sum(len(m["content"].split()) for m in ex["messages"]) for ex in samples]
        target = [len(ex["messages"][-1]["content"].split()) for ex in samples]
        stats["splits"][name] = {
            "stories": len(split_rows), "samples": len(samples), "dropped_too_long": dropped,
            "by_kind": dict(kinds), "init_by_budget": {str(k): v for k, v in sorted(budgets.items())},
            "mean_words_per_sample": round(sum(words) / max(1, len(words)), 1),
            "max_words_per_sample": max(words) if words else 0,
            "mean_target_words": round(sum(target) / max(1, len(target)), 1),
        }
        print(name, stats["splits"][name])
    json.dump(stats, open(DATA_DIR / "stats.json", "w"), indent=2)


if __name__ == "__main__":
    main()
