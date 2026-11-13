"""Render Pinterest pins (1000x1500) in the Kirtan Tutorials pin design, English and German."""
from PIL import Image, ImageDraw
from render import font, wrap, spaced, PALETTE, GOLD, CREAM

PW, PH = 1000, 1500
INSET = 68
PLEFT, PRIGHT = 120, 880
WINE_TEXT = (69, 25, 23)
BG = {"god": "bordeaux", "mantra": "dark", "verse": "darkest", "vedanta": "bordeaux"}
LABEL = {"god": ("WHO IS...?", "WER IST...?"), "mantra": ("MANTRA MEANING", "MANTRA-BEDEUTUNG"),
         "vedanta": ("VEDANTA SIMPLY", "VEDANTA EINFACH")}
TAGLINE = {"god": ("HINDU DEITY · STORY · SYMBOLISM", "HINDU-GOTTHEIT · GESCHICHTE · SYMBOLIK"),
           "mantra": ("MANTRA · MEANING · TRANSLATION", "MANTRA · BEDEUTUNG · ÜBERSETZUNG"),
           "verse": ("BHAGAVAD GITA · SANSKRIT · MEANING", "BHAGAVAD GITA · SANSKRIT · BEDEUTUNG"),
           "vedanta": ("VEDANTA · SIMPLY · EXPLAINED", "VEDANTA · EINFACH · ERKLÄRT")}
BUTTON = ("READ THE FULL GUIDE", "ZUM GANZEN ARTIKEL")
DEVA_GOLD = (214, 178, 110)


def centered_spaced(draw, y, text, fnt, fill, spacing_em=0.22):
    widths = [draw.textlength(ch, font=fnt) + fnt.size * spacing_em for ch in text]
    total = sum(widths) - fnt.size * spacing_em
    spaced(draw, ((PW - total) / 2, y), text, fnt, fill, spacing_em)


def fit_lines(draw, text, name, sizes, width, max_lines, variation=None):
    for size in sizes:
        fnt = font(name, size, variation)
        lines = wrap(draw, text, fnt, width)
        if len(lines) <= max_lines:
            return fnt, lines
    return fnt, lines


def render_pin(item, lang):
    i = 0 if lang == "en" else 1
    kind = item["kind"]
    bg = BG[kind]
    img = Image.new("RGB", (PW, PH), PALETTE[bg])
    d = ImageDraw.Draw(img)
    d.rectangle([INSET, INSET, PW - INSET, PH - INSET], outline=GOLD, width=3)

    label = f"BHAGAVAD GITA {item['ref']}" if kind == "verse" else LABEL[kind][i]
    centered_spaced(d, 168, label, font("jost", 32, "Medium"), CREAM, 0.25)

    width = PRIGHT - PLEFT
    deva_fnt, deva_lines = fit_lines(d, item["deva"], "deva", [124, 100, 84, 72], width, 2)
    tr_fnt, tr_lines = fit_lines(d, item["translit"], "cormorant", [56, 48, 42], width, 2, "Italic")
    head = item["hook"] if lang == "en" else item["hook_de"]
    head_fnt, head_lines = fit_lines(d, head, "sansita", [80, 72, 64, 58], width, 4)

    blocks = [(deva_fnt, deva_lines, DEVA_GOLD, 1.18), (tr_fnt, tr_lines, DEVA_GOLD, 1.2), (head_fnt, head_lines, CREAM, 1.12)]
    gaps = [34, 52]
    heights = [len(lines) * int(f.size * lh) for f, lines, _, lh in blocks]
    total = sum(heights) + sum(gaps)
    top, bottom = 250, 1060
    y = top + max(0, (bottom - top - total) // 2)
    for n, (fnt, lines, color, lh) in enumerate(blocks):
        for line in lines:
            d.text((PLEFT, y), line, font=fnt, fill=color)
            y += int(fnt.size * lh)
        if n < len(gaps):
            y += gaps[n]

    tag_fnt = font("jost", 27, "Medium")
    centered_spaced(d, 1110, TAGLINE[kind][i], tag_fnt, DEVA_GOLD if bg != "bordeaux" else CREAM, 0.2)

    bw, bh, by = 630, 104, 1180
    bx = (PW - bw) // 2
    btn_fill = GOLD if bg != "bordeaux" else CREAM
    d.rounded_rectangle([bx, by, bx + bw, by + bh], radius=bh // 2, fill=btn_fill)
    btn_fnt = font("jost", 33, "Medium")
    centered_spaced(d, by + 30, BUTTON[i], btn_fnt, WINE_TEXT, 0.22)

    foot = font("jost", 30)
    w = d.textlength("kirtantutorials.com", font=foot)
    d.text(((PW - w) / 2, 1318), "kirtantutorials.com", font=foot, fill=DEVA_GOLD if bg != "bordeaux" else CREAM)
    return img
