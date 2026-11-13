"""Posting plan 25 November to 22 December 2026: 5 trial reels per day plus 5 EN and 5 DE pins.

Slots: 07:30 mantra, 10:00 god, 12:30 Gita verse or Vedanta question (alternating), 16:00 mantra, 19:30 god.
Each reel gets one English and one German pin on the matching board, linking to an existing page.
"""
import csv, datetime, os
from content_dec_gods import GODS
from content_dec_mantras import MANTRAS
from content_dec_other import VERSES, VEDANTA

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
START = datetime.date(2026, 11, 25)
DAYS = 28
SLOTS = ["07:30", "10:00", "12:30", "16:00", "19:30"]
SITE = "https://kirtantutorials.com"
PAGES_CSV = "/mnt/project-files/kirtantutorials-website/plan/bestand_zuordnung.csv"

BOARDS = {
    "god": ("1133429499911451634", "1133429499911454101"),
    "mantra": ("1133429499911451636", "1133429499911454109"),
    "verse": ("1133429499911451631", "1133429499911454100"),
    "vedanta": ("1133429499911451638", "1133429499911454105"),
}
AUDIO = {"om": "1803923983802801", "vaishnav": "1744694772899065"}
PLURAL = {"Ashvins": ("the Ashvins", "die Ashvins"), "Nara-Narayana": ("Nara and Narayana", "Nara und Narayana"),
          "Ashta Lakshmi": ("the Ashta Lakshmi", "die Ashta Lakshmi"), "Rahu and Ketu": ("Rahu and Ketu", "Rahu und Ketu")}
LINE_EN = {"god": "Story, symbols and mantra for devotees and kirtan singers.",
           "mantra": "Sanskrit text, transliteration and word-by-word meaning for kirtan and chanting practice.",
           "verse": "Sanskrit verse with English translation and a plain explanation.",
           "vedanta": "Indian philosophy for beginners, simply explained."}
LINE_DE = {"god": "Geschichte, Symbolik und Mantra für Gläubige und Kirtan-Singende.",
           "mantra": "Sanskrit-Text, Umschrift und Bedeutung Wort für Wort für Kirtan und Mantra-Praxis.",
           "verse": "Sanskrit-Vers mit deutscher Übersetzung und klarer Erklärung.",
           "vedanta": "Indische Philosophie für Anfänger, einfach erklärt."}


def load_pages():
    pages = {}
    with open(PAGES_CSV, encoding="utf-8") as f:
        for row in csv.DictReader(f, delimiter=";"):
            pages[row["Bestand"]] = (row["Titel alt"], SITE + row["Adresse EN alt"], SITE + row["Adresse DE alt"])
    return pages


def first_sentence(text):
    return text.split(". ")[0].rstrip(".") + "."


def pin_texts(item, pages):
    kind, topic = item["kind"], item["topic"]
    title_en_article, link_en, link_de = pages[item["page"]]
    tags = item["caption"].rsplit("\n\n", 1)[1]
    if kind == "god":
        if topic in PLURAL:
            en, de = PLURAL[topic]
            t_en, t_de = f"Who Are {en}? Hindu Deities, Story, Symbolism and Meaning", f"Wer sind {de}? Hindu-Gottheiten, Geschichte, Symbolik und Bedeutung"
        elif topic == "Sudarshana":
            t_en, t_de = "What Is Sudarshana? Vishnu's Discus, Story, Symbolism and Meaning", "Was ist Sudarshana? Vishnus Diskus, Geschichte, Symbolik und Bedeutung"
        else:
            t_en, t_de = f"Who Is {topic}? Hindu Deity, Story, Symbolism and Meaning", f"Wer ist {topic}? Hindu-Gottheit, Geschichte, Symbolik und Bedeutung"
    elif kind == "mantra":
        t_en, t_de = f"{topic}: Meaning, Sanskrit Text and English Translation", f"{topic}: Bedeutung, Sanskrit-Text und deutsche Übersetzung"
    elif kind == "verse":
        t_en, t_de = f"Bhagavad Gita {item['ref']} Meaning: Sanskrit Verse with English Translation", f"Bhagavad Gita {item['ref']} Bedeutung: Sanskrit-Vers mit deutscher Übersetzung"
    else:
        t_en, t_de = f"{item['hook']} Vedanta Simply Explained", f"{item['hook_de']} Vedanta einfach erklärt"
    d_en = f"{first_sentence(item['cap_en'])} {LINE_EN[kind]} Read the full guide: {title_en_article}.\n\n{tags}"
    d_de = f"{first_sentence(item['cap_de'])} {LINE_DE[kind]} Zum ganzen Artikel auf kirtantutorials.com.\n\n{tags}"
    return dict(title_en=t_en, title_de=t_de, desc_en=d_en, desc_de=d_de, link_en=link_en, link_de=link_de,
                board_en=BOARDS[kind][0], board_de=BOARDS[kind][1], article_en=title_en_article)


def plan():
    pages = load_pages()
    assert len(GODS) == 2 * DAYS and len(MANTRAS) == 2 * DAYS and len(VERSES) == DAYS // 2 and len(VEDANTA) == DAYS // 2
    items, nr = [], 151
    for d in range(DAYS):
        date = (START + datetime.timedelta(days=d)).isoformat()
        middle = VERSES[d // 2] if d % 2 == 0 else VEDANTA[d // 2]
        for time, item in zip(SLOTS, [MANTRAS[2 * d], GODS[2 * d], middle, MANTRAS[2 * d + 1], GODS[2 * d + 1]]):
            item = dict(item, date=date, time=time, nr=nr, audio_id=AUDIO[item.get("audio", "om")])
            hhmm = time.replace(":", "")
            item["video"] = f"media/{date}/{hhmm}_reel_{item['slug']}.mp4"
            item["cover_png"] = f"media/{date}/{hhmm}_reel_{item['slug']}-cover.png"
            item["pin_en"] = f"pinterest/images/pin-{nr:03d}-{date}-{item['slug']}.jpg"
            item["pin_de"] = f"pinterest/images-de/pin-de-{nr:03d}-{date}-{item['slug']}.jpg"
            item.update(pin_texts(item, pages))
            items.append(item)
            nr += 1
    return items


if __name__ == "__main__":
    import collections
    items = plan()
    print(len(items), "items")
    seen = collections.Counter(i["slug"] for i in items)
    print("duplicate slugs:", [s for s, c in seen.items() if c > 1])
    for i in items[:5]:
        print(i["date"], i["time"], i["kind"], i["topic"], "|", i["title_en"], "|", i["link_de"])
