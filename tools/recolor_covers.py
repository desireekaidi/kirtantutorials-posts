"""Give the reels from a start slot on a mixed cover colour (first slide), rebuild video and cover as *_v2 files.
Usage: recolor_covers.py FIRST_DATE FIRST_TIME"""
import os, sys, json
from render import build_reel
from plan_dec import plan, ROOT

CYCLE = ["cream", "bordeaux", "sand", "darkest", "cream", "dark"]

def recolored(items, first_date, first_time):
    out = []
    for n, item in enumerate(items):
        if (item["date"], item["time"]) < (first_date, first_time):
            continue
        slides = [dict(s) for s in item["slides"]]
        bg = CYCLE[n % len(CYCLE)]
        slides[0]["bg"] = bg
        if len(slides) > 1 and slides[1]["bg"] == bg:
            slides[1]["bg"] = "bordeaux" if bg in ("cream", "sand") else "cream"
        video = item["video"].replace(".mp4", "_v2.mp4")
        cover = item["cover_png"].replace("-cover.png", "_v2-cover.png")
        out.append(dict(item, slides=slides, video=video, cover_png=cover, cover_bg=bg))
    return out

if __name__ == "__main__":
    items = recolored(plan(), sys.argv[1], sys.argv[2])
    only = sys.argv[3] if len(sys.argv) > 3 else None
    for item in items:
        if only and item["date"] != only:
            continue
        build_reel(item["slides"], os.path.join(ROOT, item["video"]), os.path.join(ROOT, item["cover_png"]))
        print("built", item["date"], item["time"], item["cover_bg"], item["slug"], flush=True)
