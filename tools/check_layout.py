"""Flag slides whose text would run into the footer."""
from PIL import Image, ImageDraw
from render import font, wrap, STYLES, TEXT_WIDTH, CONTENT_TOP, H, table_right_lines
from plan_dec import plan
d = ImageDraw.Draw(Image.new("RGB", (10, 10)))
bad = 0
for item in plan():
    for n, s in enumerate(item["slides"], 1):
        y = 0
        for b in s["blocks"]:
            k = b[0]
            if k == "rule": y += 48; continue
            if k == "table":
                for l, r in b[1]:
                    lines, below = table_right_lines(d, l, r)
                    y += 96 + 44 * (len(lines) - 1) + (56 if below else 0)
                continue
            st = k
            if k == "deva" and len(b[1]) > 14: st = "deva_small"
            if k == "head" and len(b[1]) > 60: st = "head_small"
            fn, size, var, lh = STYLES[st]
            y += len(wrap(d, b[1], font(fn, size, var), TEXT_WIDTH)) * lh + {"deva": 26, "head": 30, "translit": 24, "body": 22}[k]
        top = CONTENT_TOP if not s.get("center") else max(330, (H - y) // 2)
        if top + y > 1160:
            print(f"OVERFLOW {item['slug']} s{n}: {top + y}"); bad += 1
print("overflow:", bad)
