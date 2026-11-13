"""Render Kirtan Tutorials slides (1080x1350), reel frames (1080x1920) and reel videos.

A slide is a dict: {"bg": palette name, "label": str, "blocks": [...], "center": bool}
Blocks: ("deva", text) ("head", text) ("translit", text) ("body", text) ("rule",) ("table", [(left, right), ...]) ("gap", px)
"""
import os, subprocess, tempfile
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = os.path.join(HERE, "fonts")

PALETTE = {
    "bordeaux": (123, 46, 42),
    "dark": (69, 25, 23),
    "darkest": (46, 11, 15),
    "cream": (253, 241, 207),
    "sand": (243, 226, 180),
}
DARK_BACKGROUNDS = {"bordeaux", "dark", "darkest"}
GOLD = (192, 155, 88)
CREAM = (253, 241, 207)
INK = (74, 36, 32)
WINE = (123, 46, 42)

def font(name, size, variation=None):
    files = {
        "sansita": "Sansita-Bold.ttf",
        "lora": "Lora[wght].ttf",
        "cormorant": "CormorantGaramond-Italic[wght].ttf",
        "jost": "Jost[wght].ttf",
        "deva": "TiroDevanagariHindi-Regular.ttf",
    }
    loaded = ImageFont.truetype(os.path.join(FONT_DIR, files[name]), size, layout_engine=ImageFont.Layout.RAQM)
    if variation:
        loaded.set_variation_by_name(variation)
    return loaded

W, H = 1080, 1350
FRAME_INSET = 94
LEFT, RIGHT = 158, 922
TEXT_WIDTH = RIGHT - LEFT
CONTENT_TOP = 400

def colors(bg):
    if bg in DARK_BACKGROUNDS:
        return dict(label=CREAM, head=CREAM, body=(240, 222, 196), deva=(214, 178, 110), translit=(214, 178, 110), table_left=(240, 222, 196), table_right=(240, 222, 196), rule=GOLD, footer=(220, 200, 170))
    return dict(label=(110, 62, 50), head=WINE, body=INK, deva=WINE, translit=(150, 96, 70), table_left=INK, table_right=INK, rule=GOLD, footer=(110, 62, 50))

def spaced(draw, xy, text, fnt, fill, spacing_em=0.22, anchor_right=False):
    x, y = xy
    widths = [draw.textlength(ch, font=fnt) + fnt.size * spacing_em for ch in text]
    total = sum(widths) - fnt.size * spacing_em
    if anchor_right:
        x = x - total
    for ch, w in zip(text, widths):
        draw.text((x, y), ch, font=fnt, fill=fill)
        x += w
    return total

def wrap(draw, text, fnt, width):
    lines = []
    for paragraph in text.split("\n"):
        words, line = paragraph.split(), ""
        for word in words:
            candidate = (line + " " + word).strip()
            if draw.textlength(candidate, font=fnt) <= width:
                line = candidate
            else:
                lines.append(line)
                line = word
        lines.append(line)
    return lines

STYLES = {
    # name: (font, size, variation, line height)
    "deva": ("deva", 112, None, 140),
    "deva_small": ("deva", 68, None, 92),
    "head": ("sansita", 76, None, 86),
    "head_small": ("sansita", 66, None, 76),
    "translit": ("cormorant", 54, "Italic", 64),
    "body": ("lora", 43, "Regular", 69),
}

def table_right_lines(draw, left, right):
    """Wrap the right column of a table row. If the left word leaves too little room, put it on its own line below."""
    left_font, right_font = font("cormorant", 60, "Italic"), font("lora", 39, "Regular")
    room = TEXT_WIDTH - draw.textlength(left, font=left_font) - 40
    if room >= 300 or room >= draw.textlength(right, font=right_font):
        return wrap(draw, right, right_font, room), False
    return wrap(draw, right, right_font, TEXT_WIDTH), True

def render_slide(slide, page=None, pages=None):
    bg = slide["bg"]
    c = colors(bg)
    if bg == "bordeaux":
        c["deva"] = (247, 222, 184)
        c["translit"] = (232, 200, 160)
    image = Image.new("RGB", (W, H), PALETTE[bg])
    draw = ImageDraw.Draw(image)
    draw.rectangle([FRAME_INSET, FRAME_INSET, W - FRAME_INSET - 1, H - FRAME_INSET - 1], outline=GOLD, width=3)
    spaced(draw, (LEFT, 160), slide["label"].upper(), font("jost", 32, "Medium"), c["label"], 0.25)
    footer_font = font("jost", 30, "Regular")
    spaced(draw, (LEFT, 1176), "kirtantutorials.com", footer_font, c["footer"], 0.06)
    if page:
        spaced(draw, (RIGHT, 1176), f"{page} / {pages}", footer_font, c["footer"], 0.06, anchor_right=True)
    center = slide.get("center", False)

    # measure layout first so centered slides can be vertically centered
    ops, y = [], 0
    for block in slide["blocks"]:
        kind = block[0]
        if kind == "gap":
            y += block[1]; continue
        if kind == "rule":
            y += 14; ops.append(("rule", y)); y += 34; continue
        if kind == "table":
            for left, right in block[1]:
                lines, below = table_right_lines(draw, left, right)
                ops.append(("row", y, left, lines, below))
                y += 96 + 44 * (len(lines) - 1) + (56 if below else 0)
            continue
        style = kind
        if kind == "deva" and len(block[1]) > 14:
            style = "deva_small"
        if kind == "head" and len(block[1]) > 60:
            style = "head_small"
        fname, size, variation, line_height = STYLES[style]
        fnt = font(fname, size, variation)
        color = c["deva" if kind == "deva" else kind]
        for line in wrap(draw, block[1], fnt, TEXT_WIDTH):
            ops.append(("text", y, line, fnt, color))
            y += line_height
        y += {"deva": 26, "head": 30, "translit": 24, "body": 22}[kind]
    top = CONTENT_TOP if not center else max(330, (H - y) // 2)
    row_left_font = font("cormorant", 60, "Italic")
    row_right_font = font("lora", 39, "Regular")
    for op in ops:
        if op[0] == "rule":
            draw.line([(LEFT, top + op[1]), (RIGHT, top + op[1])], fill=c["rule"], width=2)
        elif op[0] == "row":
            _, oy, left, right_lines, below = op
            draw.text((LEFT, top + oy), left, font=row_left_font, fill=c["table_left"])
            start = oy + (70 if below else 14)
            for k, rl in enumerate(right_lines):
                draw.text((RIGHT, top + start + k * 44), rl, font=row_right_font, fill=c["table_right"], anchor="ra")
        else:
            _, oy, line, fnt, color = op
            if center:
                if fnt.size == 76:
                    fnt = font("sansita", 66)
                draw.text((W // 2, top + oy), line, font=fnt, fill=color, anchor="ma")
            else:
                draw.text((LEFT, top + oy), line, font=fnt, fill=color)
    return image

def to_reel_frame(slide_image, bg):
    frame = Image.new("RGB", (1080, 1920), PALETTE[bg])
    frame.paste(slide_image, (0, 285))
    return frame

def build_reel(slides, out_mp4, out_cover, seconds_per_slide=4.6, fade=0.5):
    pages = len(slides)
    with tempfile.TemporaryDirectory() as tmp:
        frames = []
        for i, slide in enumerate(slides, 1):
            frame = to_reel_frame(render_slide(slide, i, pages), slide["bg"])
            path = os.path.join(tmp, f"f{i}.png"); frame.save(path); frames.append(path)
            if i == 1:
                frame.save(out_cover)
        inputs = []
        for p in frames:
            inputs += ["-loop", "1", "-t", str(seconds_per_slide), "-i", p]
        chain, last = [], "0:v"
        for i in range(1, len(frames)):
            offset = i * (seconds_per_slide - fade)
            label = f"x{i}"
            chain.append(f"[{last}][{i}:v]xfade=transition=fade:duration={fade}:offset={offset:.2f}[{label}]")
            last = label
        chain.append(f"[{last}]format=yuv420p,fps=30[out]")
        cmd = ["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", ";".join(chain), "-map", "[out]",
               "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-movflags", "+faststart", out_mp4]
        subprocess.run(cmd, check=True)
