"""Build reels and pins for the December plan. Usage: build_dec.py FIRST_DAY LAST_DAY [--pins-only]"""
import os, sys
from render import build_reel
from pins import render_pin
from plan_dec import plan, ROOT, START
import datetime
first, last = int(sys.argv[1]), int(sys.argv[2])
pins_only = "--pins-only" in sys.argv
dates = {(START + datetime.timedelta(days=d)).isoformat() for d in range(first, last + 1)}
for item in plan():
    if item["date"] not in dates:
        continue
    for key, lang in (("pin_en", "en"), ("pin_de", "de")):
        path = os.path.join(ROOT, item[key]); os.makedirs(os.path.dirname(path), exist_ok=True)
        render_pin(item, lang).save(path, quality=92)
    if not pins_only:
        video = os.path.join(ROOT, item["video"]); os.makedirs(os.path.dirname(video), exist_ok=True)
        build_reel(item["slides"], video, os.path.join(ROOT, item["cover_png"]))
    print("built", item["date"], item["time"], item["slug"], flush=True)
