"""Generates the daily status images for sanatan-frames.

Run:  python3 make_status.py <mantras repo> <output dir>
Writes <out>/status/<category>/<id>.jpg and <out>/frames.json.
Needs Pillow built with raqm (for Devanagari shaping).
"""
import json
import math
import os
import random
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont

REPO = sys.argv[1] if len(sys.argv) > 1 else '/home/user/mantras'
OUT = sys.argv[2] if len(sys.argv) > 2 else './out'
BASE_URL = 'https://raw.githubusercontent.com/hhmprodesign/sanatan-frames/main/'

W, H = 1080, 1920
FONTS = os.path.join(REPO, 'fonts')
IMAGES = os.path.join(REPO, 'assets/images')

GOLD = (246, 200, 107)
GOLD_LIGHT = (255, 230, 170)
CREAM = (255, 246, 228)

# Palettes: (top, bottom, glow, pattern colour)
PALETTES = {
    'saffron': ((214, 83, 18), (122, 22, 14), (255, 190, 90), (255, 214, 140)),
    'dawn': ((250, 160, 70), (190, 60, 40), (255, 236, 170), (255, 240, 200)),
    'maroon': ((128, 20, 36), (52, 6, 20), (240, 120, 60), (240, 170, 110)),
    'night': ((28, 30, 78), (8, 8, 30), (120, 120, 230), (180, 180, 255)),
    'peacock': ((10, 92, 110), (6, 34, 58), (90, 220, 210), (150, 230, 220)),
    'shiva': ((40, 64, 110), (12, 18, 40), (150, 190, 255), (190, 210, 255)),
    'green': ((40, 110, 50), (10, 46, 24), (200, 240, 120), (210, 240, 160)),
    'pink': ((200, 50, 110), (90, 14, 60), (255, 170, 200), (255, 200, 220)),
    'royal': ((90, 30, 120), (30, 8, 50), (220, 150, 255), (230, 190, 255)),
}


def font(name, size):
    path = {
        'tiro': 'TiroDevanagariHindi-Regular.ttf',
        'mukta': 'Mukta-SemiBold.ttf',
        'muktab': 'Mukta-Bold.ttf',
        'mukta-r': 'Mukta-Regular.ttf',
    }[name]
    return ImageFont.truetype(os.path.join(FONTS, path), size,
                              layout_engine=ImageFont.Layout.RAQM)


def gradient(top, bottom):
    col = Image.new('RGB', (1, H))
    for y in range(H):
        t = y / (H - 1)
        col.putpixel((0, y), tuple(int(top[i] + (bottom[i] - top[i]) * t)
                                   for i in range(3)))
    return col.resize((W, H))


def glow(img, cx, cy, r, color, strength=200):
    layer = Image.new('RGBA', img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=color + (strength,))
    layer = layer.filter(ImageFilter.GaussianBlur(r * 0.45))
    img.alpha_composite(layer)


def mandala(img, cx, cy, r, color, alpha=40, rings=6, petals=24):
    """Line-art mandala, drawn large and faint behind the deity."""
    layer = Image.new('RGBA', img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    c = color + (alpha,)
    for k in range(1, rings + 1):
        rr = r * k / rings
        d.ellipse((cx - rr, cy - rr, cx + rr, cy + rr), outline=c, width=3)
        n = petals if k % 2 == 0 else petals // 2
        inner = r * (k - 1) / rings
        for i in range(n):
            a0 = 2 * math.pi * i / n
            a1 = 2 * math.pi * (i + 1) / n
            am = (a0 + a1) / 2
            p0 = (cx + inner * math.cos(a0), cy + inner * math.sin(a0))
            p1 = (cx + rr * math.cos(am), cy + rr * math.sin(am))
            p2 = (cx + inner * math.cos(a1), cy + inner * math.sin(a1))
            d.line([p0, p1, p2], fill=c, width=3)
    # Dots on the outer ring.
    for i in range(petals * 2):
        a = 2 * math.pi * i / (petals * 2)
        x, y = cx + (r + 22) * math.cos(a), cy + (r + 22) * math.sin(a)
        d.ellipse((x - 5, y - 5, x + 5, y + 5), fill=c)
    img.alpha_composite(layer)


def sparkles(img, color, n=70, seed=1, top=0, bottom=H):
    rnd = random.Random(seed)
    layer = Image.new('RGBA', img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for _ in range(n):
        x, y = rnd.randint(40, W - 40), rnd.randint(top, bottom)
        s = rnd.choice([2, 3, 3, 4, 6])
        a = rnd.randint(70, 200)
        d.ellipse((x - s, y - s, x + s, y + s), fill=color + (a,))
    layer = layer.filter(ImageFilter.GaussianBlur(1))
    img.alpha_composite(layer)


def stars(img, n=120, seed=3):
    rnd = random.Random(seed)
    d = ImageDraw.Draw(img)
    for _ in range(n):
        x, y = rnd.randint(0, W), rnd.randint(0, int(H * 0.75))
        s = rnd.choice([1, 1, 2, 2, 3])
        d.ellipse((x - s, y - s, x + s, y + s),
                  fill=(255, 255, 255, rnd.randint(90, 230)))


def moon(img, cx, cy, r):
    glow(img, cx, cy, int(r * 2.2), (200, 200, 255), 90)
    layer = Image.new('RGBA', img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(255, 248, 220, 255))
    off = int(r * 0.45)
    d.ellipse((cx - r + off, cy - r - off // 3, cx + r + off, cy + r - off // 3),
              fill=(0, 0, 0, 0))
    img.alpha_composite(layer)


def sun(img, cx, cy, r):
    glow(img, cx, cy, int(r * 2.6), (255, 220, 120), 200)
    d = ImageDraw.Draw(img)
    for i in range(24):
        a = 2 * math.pi * i / 24
        x0, y0 = cx + r * 1.15 * math.cos(a), cy + r * 1.15 * math.sin(a)
        x1, y1 = cx + r * 1.6 * math.cos(a), cy + r * 1.6 * math.sin(a)
        d.line([(x0, y0), (x1, y1)], fill=(255, 230, 150, 160), width=6)
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(255, 214, 110, 255))


def border(img, color=GOLD):
    """Double gold border with lotus-dot corners."""
    d = ImageDraw.Draw(img)
    m1, m2 = 34, 52
    d.rounded_rectangle((m1, m1, W - m1, H - m1), 28, outline=color + (255,),
                        width=5)
    d.rounded_rectangle((m2, m2, W - m2, H - m2), 20, outline=color + (150,),
                        width=2)
    for cx, cy in [(m1, m1), (W - m1, m1), (m1, H - m1), (W - m1, H - m1)]:
        for r, a in [(22, 255), (12, 255)]:
            d.ellipse((cx - r, cy - r, cx + r, cy + r),
                      fill=(color if r == 12 else (90, 20, 10)) + (a,),
                      outline=color + (255,), width=4)
    # Small diamonds along the edges.
    for x in range(140, W - 100, 100):
        for y in (m1, H - m1):
            d.polygon([(x, y - 8), (x + 8, y), (x, y + 8), (x - 8, y)],
                      fill=color + (255,))


def toran(img, color=GOLD, y0=0):
    """A marigold toran hanging from the top edge."""
    d = ImageDraw.Draw(img)
    n = 9
    for i in range(n):
        x = 70 + i * (W - 140) / (n - 1)
        drop = 90 if i % 2 == 0 else 140
        for k in range(0, drop, 22):
            r = 13
            col = (255, 160, 20) if (k // 22) % 2 == 0 else (255, 205, 40)
            d.ellipse((x - r, y0 + 40 + k - r, x + r, y0 + 40 + k + r),
                      fill=col + (255,))
        d.polygon([(x, y0 + 40 + drop + 30), (x - 16, y0 + 40 + drop + 4),
                   (x + 16, y0 + 40 + drop + 4)], fill=(60, 150, 60, 255))
    # String of mango leaves between.
    for i in range(n * 3):
        x = 50 + i * (W - 100) / (n * 3 - 1)
        y = y0 + 40 + 18 * math.sin(i * 0.9)
        d.ellipse((x - 14, y - 7, x + 14, y + 7), fill=(46, 125, 50, 255))


def diya(img, cx, cy, s=1.0):
    d = ImageDraw.Draw(img)
    glow(img, cx, int(cy - 40 * s), int(60 * s), (255, 200, 80), 220)
    d.pieslice((cx - 70 * s, cy - 50 * s, cx + 70 * s, cy + 50 * s), 0, 180,
               fill=(196, 92, 30, 255))
    d.ellipse((cx - 70 * s, cy - 14 * s, cx + 70 * s, cy + 14 * s),
              fill=(226, 128, 50, 255))
    d.ellipse((cx - 14 * s, cy - 70 * s, cx + 14 * s, cy - 6 * s),
              fill=(255, 220, 90, 255))
    d.ellipse((cx - 7 * s, cy - 50 * s, cx + 7 * s, cy - 14 * s),
              fill=(255, 255, 230, 255))


def text(img, xy, s, f, fill=GOLD_LIGHT, anchor='mm', shadow=True,
         stroke=0, stroke_fill=(70, 10, 0)):
    d = ImageDraw.Draw(img)
    if shadow:
        layer = Image.new('RGBA', img.size, (0, 0, 0, 0))
        ImageDraw.Draw(layer).text((xy[0] + 3, xy[1] + 5), s, font=f,
                                   fill=(0, 0, 0, 150), anchor=anchor)
        layer = layer.filter(ImageFilter.GaussianBlur(6))
        img.alpha_composite(layer)
    d.text(xy, s, font=f, fill=fill + (255,), anchor=anchor,
           stroke_width=stroke, stroke_fill=stroke_fill)


def fit_font(name, s, max_w, start):
    size = start
    while size > 30:
        f = font(name, size)
        if f.getlength(s) <= max_w:
            return f
        size -= 4
    return font(name, size)


def wrap(s, f, max_w):
    words, lines, cur = s.split(), [], ''
    for w in words:
        t = (cur + ' ' + w).strip()
        if f.getlength(t) <= max_w:
            cur = t
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def deity(img, name, cx, bottom, max_w, max_h):
    im = Image.open(os.path.join(IMAGES, name)).convert('RGBA')
    k = min(max_w / im.width, max_h / im.height)
    im = im.resize((int(im.width * k), int(im.height * k)), Image.LANCZOS)
    # Soft shadow so the cut-out sits on the background.
    sh = Image.new('RGBA', img.size, (0, 0, 0, 0))
    a = im.split()[3].point(lambda v: v * 0.5)
    blk = Image.new('RGBA', im.size, (0, 0, 0, 255))
    blk.putalpha(a)
    sh.paste(blk, (cx - im.width // 2, bottom - im.height + 16), blk)
    sh = sh.filter(ImageFilter.GaussianBlur(14))
    img.alpha_composite(sh)
    img.alpha_composite(im, (cx - im.width // 2, bottom - im.height))
    return bottom - im.height


def ribbon(img, cy, s, f, color=(120, 20, 10), fg=GOLD_LIGHT):
    w = int(f.getlength(s)) + 120
    d = ImageDraw.Draw(img)
    x0, x1 = (W - w) // 2, (W + w) // 2
    h = 90
    d.polygon([(x0 - 40, cy - h // 2), (x0, cy), (x0 - 40, cy + h // 2),
               (x0 + 10, cy + h // 2), (x0 + 10, cy - h // 2)],
              fill=tuple(max(0, v - 30) for v in color) + (255,))
    d.polygon([(x1 + 40, cy - h // 2), (x1, cy), (x1 + 40, cy + h // 2),
               (x1 - 10, cy + h // 2), (x1 - 10, cy - h // 2)],
              fill=tuple(max(0, v - 30) for v in color) + (255,))
    d.rounded_rectangle((x0, cy - h // 2, x1, cy + h // 2), 14,
                        fill=color + (255,), outline=GOLD + (255,), width=3)
    text(img, (W // 2, cy + 2), s, f, fill=fg, shadow=False)


def divider(img, cy, color=GOLD):
    d = ImageDraw.Draw(img)
    d.line([(W // 2 - 260, cy), (W // 2 - 30, cy)], fill=color + (220,), width=3)
    d.line([(W // 2 + 30, cy), (W // 2 + 260, cy)], fill=color + (220,), width=3)
    d.polygon([(W // 2, cy - 14), (W // 2 + 14, cy), (W // 2, cy + 14),
               (W // 2 - 14, cy)], fill=color + (255,))


def photo_slot(img, cy, r=150):
    """A ring where the user's own photo goes. The app places it here."""
    d = ImageDraw.Draw(img)
    cx = W // 2
    glow(img, cx, cy, r + 30, (255, 220, 150), 120)
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(0, 0, 0, 60),
              outline=GOLD + (255,), width=8)
    # A faint person outline as a hint; the user's photo covers it.
    hint = GOLD + (110,)
    d.ellipse((cx - 42, cy - 80, cx + 42, cy + 4), outline=hint, width=6)
    d.arc((cx - 90, cy + 20, cx + 90, cy + 200), 200, 340, fill=hint, width=6)
    d.ellipse((cx - r - 18, cy - r - 18, cx + r + 18, cy + r + 18),
              outline=GOLD + (150,), width=3)
    return {'x': 0.5, 'y': round(cy / H, 4), 'size': round(2 * r / W, 4),
            'shape': 'circle'}


# ---------------------------------------------------------------- designs

def base(pal, seed=1, center_y=820, mandala_r=470, pattern=True):
    top, bottom, glow_c, pat = PALETTES[pal]
    img = gradient(top, bottom).convert('RGBA')
    if pattern:
        mandala(img, W // 2, center_y, mandala_r, pat, alpha=38)
    glow(img, W // 2, center_y, 360, glow_c, 170)
    sparkles(img, GOLD_LIGHT, n=60, seed=seed)
    return img


def deity_status(pal, deity_img, title, sub, mantra, seed=1, with_photo=False,
                 night=False, festive=False, sun_on=False):
    img = base(pal, seed=seed, center_y=860)
    if night:
        stars(img)
        moon(img, W - 150, 150, 48)
    if sun_on:
        sun(img, W // 2, 300, 70)
    if festive:
        toran(img)
    top_y = 330 if (festive or night) else 270
    if sun_on:
        top_y = 470
    f_title = fit_font('tiro', title, W - 200, 150)
    text(img, (W // 2, top_y), title, f_title, fill=GOLD_LIGHT, stroke=2)
    if sub:
        f_sub = fit_font('mukta', sub, W - 260, 64)
        text(img, (W // 2, top_y + 120), sub, f_sub, fill=CREAM)
    bottom = 1430 if not with_photo else 1250
    if deity_img == 'SUN':
        cy = bottom - (380 if not with_photo else 330)
        sun(img, W // 2, cy, 170 if not with_photo else 140)
    else:
        deity(img, deity_img, W // 2, bottom, 760,
              820 if not with_photo else 700)
    slot = None
    if with_photo:
        divider(img, 1300)
        slot = photo_slot(img, 1520, r=150)
    f_m = fit_font('tiro', mantra, W - 220, 84)
    ribbon(img, 1560 if not with_photo else 1760, mantra, f_m)
    if not with_photo:
        f_n = font('mukta-r', 40)
        text(img, (W // 2, 1690), '॥ जय सनातन ॥', f_n, fill=GOLD, shadow=False)
    for x in (170, W - 170):
        if not with_photo:
            diya(img, x, 1760, 0.8)
    border(img)
    return img.convert('RGB'), slot


def quote_status(pal, quote, source, seed=1):
    img = base(pal, seed=seed, center_y=960, mandala_r=500)
    om = Image.open(os.path.join(IMAGES, 'om1.webp')).convert('RGBA')
    om = om.resize((220, 220), Image.LANCZOS)
    # Recolour the Om to gold so it sits on any palette.
    gold = Image.new('RGBA', om.size, GOLD + (255,))
    gold.putalpha(om.split()[3])
    om = gold
    img.alpha_composite(om, (W // 2 - 110, 220))
    f = font('tiro', 92)
    lines = wrap(quote, f, W - 240)
    lh = 140
    y = 960 - (len(lines) - 1) * lh // 2
    text(img, (W // 2, 560), '“', font('tiro', 200), fill=GOLD, shadow=False)
    for ln in lines:
        text(img, (W // 2, y), ln, f, fill=CREAM)
        y += lh
    divider(img, y + 40)
    text(img, (W // 2, y + 130), source, font('mukta', 54), fill=GOLD_LIGHT)
    diya(img, W // 2, 1700, 1.0)
    border(img)
    return img.convert('RGB'), None


# ---------------------------------------------------------------- content

WEEK = [
    # id, palette, deity, day, mantra
    ('somvar', 'shiva', 'shiva_ji.webp', 'शुभ सोमवार', 'ॐ नमः शिवाय'),
    ('mangalvar', 'saffron', 'hanuman_ji.webp', 'शुभ मंगलवार', 'जय श्री हनुमान'),
    ('budhvar', 'green', 'ganesh_ji.webp', 'शुभ बुधवार', 'ॐ गं गणपतये नमः'),
    ('guruvar', 'royal', 'vishnuji.webp', 'शुभ गुरुवार',
     'ॐ नमो भगवते वासुदेवाय'),
    ('shukravar', 'pink', 'laxmi_ji.webp', 'शुभ शुक्रवार', 'जय माँ लक्ष्मी'),
    ('shanivar', 'night', 'shani_dev_ji.webp', 'शुभ शनिवार',
     'ॐ शं शनैश्चराय नमः'),
    ('ravivar', 'dawn', 'ram_ji.webp', 'शुभ रविवार', 'जय श्री राम'),
]

DEITIES = [
    ('shiv', 'shiva', 'shiva_ji.webp', 'हर हर महादेव', 'ॐ नमः शिवाय'),
    ('hanuman', 'saffron', 'hanuman_ji.webp', 'जय बजरंगबली', 'जय श्री राम'),
    ('ganesh', 'green', 'ganesh_ji.webp', 'गणपति बप्पा मोरया',
     'ॐ गं गणपतये नमः'),
    ('radhakrishna', 'peacock', 'radha_krishna_ji.webp', 'राधे राधे',
     'हरे कृष्ण हरे कृष्ण'),
    ('ram', 'dawn', 'ram_ji.webp', 'जय श्री राम', 'सियावर रामचंद्र की जय'),
    ('durga', 'maroon', 'durga_mata_ji.webp', 'जय माता दी', 'ॐ दुं दुर्गायै नमः'),
    ('laxmi', 'pink', 'laxmi_ji.webp', 'जय माँ लक्ष्मी', 'ॐ श्रीं महालक्ष्म्यै नमः'),
    ('saraswati', 'royal', 'saraswati_ji.webp', 'जय माँ सरस्वती',
     'ॐ ऐं सरस्वत्यै नमः'),
    ('khatushyam', 'peacock', 'khatu_shyam_ji.webp', 'जय श्री श्याम',
     'हारे का सहारा'),
    ('jagannath', 'saffron', 'jaggnath_ji.webp', 'जय जगन्नाथ',
     'जय जगन्नाथ स्वामी'),
    ('vishnu', 'royal', 'vishnuji.webp', 'ॐ नमो नारायणाय',
     'ॐ नमो भगवते वासुदेवाय'),
]

FESTIVALS = [
    # category id, en, hi, festivals (calendar names), designs
    ('makar_sankranti', 'Makar Sankranti', 'मकर संक्रांति',
     ['Makar Sankranti', 'मकर संक्रांति', 'Pongal', 'Lohri'],
     [('dawn', 'SUN', 'मकर संक्रांति', 'की हार्दिक शुभकामनाएँ',
       'ॐ सूर्याय नमः', {})]),
    ('vasant_panchami', 'Vasant Panchami', 'वसंत पंचमी',
     ['Vasant Panchami', 'Basant Panchami', 'वसंत पंचमी', 'बसंत पंचमी',
      'Saraswati Puja'],
     [('royal', 'saraswati_ji.webp', 'वसंत पंचमी', 'की हार्दिक शुभकामनाएँ',
       'ॐ ऐं सरस्वत्यै नमः', {})]),
    ('mahashivratri', 'Maha Shivratri', 'महाशिवरात्रि',
     ['Maha Shivaratri', 'Mahashivratri', 'महाशिवरात्रि', 'महा शिवरात्रि'],
     [('shiva', 'shiva_ji.webp', 'महाशिवरात्रि', 'की हार्दिक शुभकामनाएँ',
       'हर हर महादेव', dict(night=True))]),
    ('holi', 'Holi', 'होली', ['Holi', 'होली', 'Holika Dahan', 'होलिका दहन'],
     [('pink', 'radha_krishna_ji.webp', 'हैप्पी होली', 'रंगों के त्योहार की शुभकामनाएँ',
       'राधे राधे', dict(festive=True))]),
    ('navratri', 'Navratri', 'नवरात्रि',
     ['Navratri', 'नवरात्रि', 'Ghatasthapana', 'घटस्थापना'],
     [('maroon', 'durga_mata_ji.webp', 'शुभ नवरात्रि', 'माँ दुर्गा आपकी रक्षा करें',
       'जय माता दी', dict(festive=True))]),
    ('ram_navami', 'Ram Navami', 'राम नवमी', ['Rama Navami', 'Ram Navami',
                                             'राम नवमी'],
     [('dawn', 'ram_ji.webp', 'राम नवमी', 'की हार्दिक शुभकामनाएँ',
       'जय श्री राम', dict(festive=True))]),
    ('hanuman_jayanti', 'Hanuman Jayanti', 'हनुमान जयंती',
     ['Hanuman Jayanti', 'हनुमान जयंती'],
     [('saffron', 'hanuman_ji.webp', 'हनुमान जयंती', 'की हार्दिक शुभकामनाएँ',
       'जय बजरंगबली', dict(festive=True))]),
    ('janmashtami', 'Janmashtami', 'जन्माष्टमी',
     ['Janmashtami', 'जन्माष्टमी', 'Krishna Janmashtami'],
     [('peacock', 'radha_krishna_ji.webp', 'जन्माष्टमी', 'की हार्दिक शुभकामनाएँ',
       'नंद के आनंद भयो', dict(night=True))]),
    ('ganesh_chaturthi', 'Ganesh Chaturthi', 'गणेश चतुर्थी',
     ['Ganesh Chaturthi', 'गणेश चतुर्थी', 'Vinayaka Chaturthi'],
     [('green', 'ganesh_ji.webp', 'गणेश चतुर्थी', 'की हार्दिक शुभकामनाएँ',
       'गणपति बप्पा मोरया', dict(festive=True))]),
    ('diwali', 'Diwali', 'दीपावली', ['Diwali', 'दीपावली', 'Lakshmi Puja',
                                     'लक्ष्मी पूजा', 'Deepavali'],
     [('maroon', 'laxmi_ji.webp', 'शुभ दीपावली', 'माँ लक्ष्मी की कृपा बनी रहे',
       'ॐ श्रीं महालक्ष्म्यै नमः', dict(festive=True))]),
]

QUOTES = [
    ('कर्मण्येवाधिकारस्ते मा फलेषु कदाचन', 'श्रीमद्भगवद्गीता 2.47', 'maroon'),
    ('मन चंगा तो कठौती में गंगा', 'संत रविदास', 'peacock'),
    ('जो हुआ अच्छा हुआ, जो हो रहा है अच्छा हो रहा है, जो होगा वह भी अच्छा होगा',
     'श्रीमद्भगवद्गीता का सार', 'royal'),
    ('राम नाम की लूट है, लूट सके तो लूट', 'संत कबीर', 'saffron'),
    ('योगः कर्मसु कौशलम्', 'श्रीमद्भगवद्गीता 2.50', 'night'),
    ('धैर्य रखो, सब कुछ अपने समय पर होता है', 'सुविचार', 'green'),
]


def main():
    cats = []

    def save(cat, fid, img, tags, slot=None):
        d = os.path.join(OUT, 'status', cat)
        os.makedirs(d, exist_ok=True)
        path = os.path.join(d, fid + '.jpg')
        img.save(path, quality=86, optimize=True, progressive=True)
        item = {'id': fid,
                'imageUrl': BASE_URL + 'status/%s/%s.jpg' % (cat, fid),
                'tags': tags}
        if slot:
            item['photo'] = slot
        return item

    # Good morning, one per weekday. "weekday" lets the app show today's first.
    frames = []
    for i, (wid, pal, dimg, day, mantra) in enumerate(WEEK):
        img, _ = deity_status(pal, dimg, 'सुप्रभात', day, mantra, seed=i,
                              sun_on=False)
        it = save('suprabhat', 'suprabhat_' + wid, img,
                  ['suprabhat', 'good morning', 'सुप्रभात', day, mantra])
        it['weekday'] = i + 1  # Monday = 1, like Dart's DateTime.weekday
        frames.append(it)
        img, slot = deity_status(pal, dimg, day, 'आपका दिन मंगलमय हो', mantra,
                                 seed=i + 20, with_photo=True)
        it = save('suprabhat', 'photo_' + wid, img,
                  ['suprabhat', 'photo', 'फोटो', day, mantra], slot)
        it['weekday'] = i + 1
        frames.append(it)
    cats.append({'id': 'suprabhat', 'titleEnglish': 'Good Morning',
                 'titleHindi': 'सुप्रभात', 'frames': frames})

    # Good night.
    frames = []
    for i, (dimg, mantra) in enumerate([
            ('radha_krishna_ji.webp', 'राधे राधे'),
            ('shiva_ji.webp', 'ॐ नमः शिवाय'),
            ('ram_ji.webp', 'जय श्री राम')]):
        img, _ = deity_status('night', dimg, 'शुभ रात्रि', 'प्रभु आपकी रक्षा करें',
                              mantra, seed=40 + i, night=True)
        frames.append(save('shubh_ratri', 'shubh_ratri_%d' % (i + 1), img,
                           ['good night', 'shubh ratri', 'शुभ रात्रि']))
    cats.append({'id': 'shubh_ratri', 'titleEnglish': 'Good Night',
                 'titleHindi': 'शुभ रात्रि', 'frames': frames})

    # Deities.
    frames = []
    for i, (did, pal, dimg, title, mantra) in enumerate(DEITIES):
        img, _ = deity_status(pal, dimg, title, '', mantra, seed=60 + i)
        frames.append(save('bhagwan', did, img, [did, title, mantra]))
        if did in ('shiv', 'hanuman', 'radhakrishna', 'ganesh', 'durga'):
            img, slot = deity_status(pal, dimg, title, '', mantra,
                                     seed=80 + i, with_photo=True)
            frames.append(save('bhagwan', did + '_photo', img,
                               [did, title, 'photo', 'फोटो'], slot))
    cats.append({'id': 'bhagwan', 'titleEnglish': 'Deities',
                 'titleHindi': 'भगवान', 'frames': frames})

    # Quotes.
    frames = []
    for i, (q, src, pal) in enumerate(QUOTES):
        img, _ = quote_status(pal, q, src, seed=100 + i)
        frames.append(save('suvichar', 'suvichar_%d' % (i + 1), img,
                           ['quote', 'suvichar', 'सुविचार', src]))
    cats.append({'id': 'suvichar', 'titleEnglish': 'Quotes',
                 'titleHindi': 'सुविचार', 'frames': frames})

    # Festivals: one category each, so the Today tab can offer them on the day.
    for cid, en, hi, fest, designs in FESTIVALS:
        frames = []
        for j, (pal, dimg, title, sub, mantra, kw) in enumerate(designs):
            img, _ = deity_status(pal, dimg, title, sub, mantra, seed=200 + j,
                                  **kw)
            frames.append(save(cid, '%s_%d' % (cid, j + 1), img,
                               [en.lower(), hi, mantra]))
            img, slot = deity_status(pal, dimg, title, sub, mantra,
                                     seed=220 + j, with_photo=True,
                                     **{k: v for k, v in kw.items()
                                        if k != 'sun_on'})
            frames.append(save(cid, '%s_photo_%d' % (cid, j + 1), img,
                               [en.lower(), hi, 'photo', 'फोटो'], slot))
        cats.append({'id': cid, 'titleEnglish': en, 'titleHindi': hi,
                     'festivals': fest, 'frames': frames})

    with open(os.path.join(OUT, 'frames.json'), 'w') as f:
        json.dump({'categories': cats}, f, ensure_ascii=False, indent=2)
    print(sum(len(c['frames']) for c in cats), 'images')


if __name__ == '__main__':
    if len(sys.argv) > 3:  # quick preview of one design
        os.makedirs(OUT, exist_ok=True)
        img, _ = deity_status('shiva', 'shiva_ji.webp', 'सुप्रभात', 'शुभ सोमवार',
                              'ॐ नमः शिवाय')
        img.save(os.path.join(OUT, 'p1.jpg'))
        img, _ = deity_status('saffron', 'hanuman_ji.webp', 'शुभ मंगलवार',
                              'आपका दिन मंगलमय हो', 'जय श्री हनुमान',
                              with_photo=True)
        img.save(os.path.join(OUT, 'p2.jpg'))
        img, _ = quote_status('maroon', QUOTES[0][0], QUOTES[0][1])
        img.save(os.path.join(OUT, 'p3.jpg'))
        img, _ = deity_status('maroon', 'durga_mata_ji.webp', 'शुभ नवरात्रि',
                              'माँ दुर्गा आपकी रक्षा करें', 'जय माता दी',
                              festive=True)
        img.save(os.path.join(OUT, 'p4.jpg'))
    else:
        main()
