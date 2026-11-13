"""Append the December plan to posts.csv/json and the Pinterest CSVs (idempotent)."""
import csv, json, os
from plan_dec import plan, ROOT

SERIES_BOARD = {"god": "Hindu Gods and Goddesses", "mantra": "Mantras and Their Meaning",
                "verse": "Bhagavad Gita and Vedic Verses", "vedanta": "Vedanta and Indian Philosophy"}
items = plan()
dates = {i["date"] for i in items}
FIELDS = ["date", "time", "format", "series", "topic", "files", "reel_cover", "caption"]

posts = json.load(open(os.path.join(ROOT, "posts.json"), encoding="utf-8"))
posts = [p for p in posts if p["date"] not in dates]
posts += [dict(date=i["date"], time=i["time"], format="Reel", series=i["series"], topic=i["topic"],
               files=i["video"], reel_cover=i["cover_png"], caption=i["caption"]) for i in items]
with open(os.path.join(ROOT, "posts.json"), "w", encoding="utf-8") as f:
    json.dump(posts, f, indent=1, ensure_ascii=False); f.write("\n")
with open(os.path.join(ROOT, "posts.csv"), "w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, FIELDS); w.writeheader(); w.writerows(posts)

PIN_FIELDS = ["nr", "date", "time", "ig_format", "series", "topic", "image", "pin_title", "pin_description", "link", "blog_article", "board_suggestion", "layout_check"]
path = os.path.join(ROOT, "pinterest", "pinterest-pins.csv")
rows = [r for r in csv.DictReader(open(path, encoding="utf-8")) if int(r["nr"]) < 151]
rows += [dict(nr=i["nr"], date=i["date"], time=i["time"], ig_format="Reel", series=i["series"], topic=i["topic"],
              image=os.path.basename(i["pin_en"]), pin_title=i["title_en"], pin_description=i["desc_en"], link=i["link_en"],
              blog_article=i["article_en"], board_suggestion=SERIES_BOARD[i["kind"]], layout_check="OK") for i in items]
with open(path, "w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, PIN_FIELDS); w.writeheader(); w.writerows(rows)

DE_FIELDS = ["nr", "date", "time", "series", "topic", "image", "pin_title", "pin_description", "link", "board_id"]
with open(os.path.join(ROOT, "pinterest", "pinterest-pins-de.csv"), "w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, DE_FIELDS); w.writeheader()
    w.writerows(dict(nr=i["nr"], date=i["date"], time=i["time"], series=i["series"], topic=i["topic"], image=os.path.basename(i["pin_de"]),
                     pin_title=i["title_de"], pin_description=i["desc_de"], link=i["link_de"], board_id=i["board_de"]) for i in items)
print(len(posts), "posts,", len(rows), "EN pins,", len(items), "DE pins")
