import os, sys
from PIL import Image
from render import render_slide, build_reel
import content_swap_nov as content
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHEET = sys.argv[1]
rows = []
for reel in sorted(content.REELS, key=lambda r: (r["date"], r["time"])):
    folder = os.path.join(ROOT, "media", reel["date"]); os.makedirs(folder, exist_ok=True)
    base = os.path.join(folder, f"{reel['time'].replace(':','')}_reel_{reel['slug']}")
    build_reel(reel["slides"], base + ".mp4", base + "-cover.png")
    thumbs = [render_slide(s, i, len(reel["slides"])).resize((216, 270)) for i, s in enumerate(reel["slides"], 1)]
    rows.append(thumbs)
    print("built", base)
sheet = Image.new("RGB", (216 * 5, 270 * len(rows)), "white")
for r, thumbs in enumerate(rows):
    for c, t in enumerate(thumbs):
        sheet.paste(t, (c * 216, r * 270))
sheet.save(SHEET)
