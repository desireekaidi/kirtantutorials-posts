"""Contact sheet: one row per reel (5 slides) plus EN and DE pin. Usage: sheet_dec.py OUT FIRST_DAY LAST_DAY"""
import sys, datetime, os
from PIL import Image
from render import render_slide
from plan_dec import plan, ROOT, START
out, first, last = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
dates = {(START + datetime.timedelta(days=d)).isoformat() for d in range(first, last + 1)}
rows = [i for i in plan() if i["date"] in dates]
tw, th, pw = 216, 270, 180
sheet = Image.new("RGB", (tw * 5 + pw * 2, th * len(rows)), "white")
for r, item in enumerate(rows):
    for c, s in enumerate(item["slides"]):
        sheet.paste(render_slide(s, c + 1, 5).resize((tw, th)), (c * tw, r * th))
    for k, key in enumerate(("pin_en", "pin_de")):
        p = os.path.join(ROOT, item[key])
        if os.path.exists(p):
            sheet.paste(Image.open(p).resize((pw, th)), (5 * tw + k * pw, r * th))
sheet.save(out)
