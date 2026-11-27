"""Hand-drawn (code-drawn) devotional symbols, owned outright, used in
place of deity photos. Each draw_* returns an RGBA image of size s x s."""
import math

from PIL import Image, ImageDraw, ImageFilter, ImageFont

GOLD = (246, 200, 107)
GOLD_D = (196, 140, 50)
GOLD_L = (255, 236, 180)


def _canvas(s):
    return Image.new('RGBA', (s, s), (0, 0, 0, 0))


def _bevel(img):
    """Adds a soft highlight and shadow so flat shapes read as metal."""
    a = img.split()[3]
    hi = Image.new('RGBA', img.size, GOLD_L + (0,))
    hi.putalpha(a.filter(ImageFilter.GaussianBlur(4)).point(lambda v: v // 3))
    out = img.copy()
    out.alpha_composite(hi, (-3, -3))
    out.putalpha(a)
    return out


def lotus(s, petal=(236, 92, 140), inner=(255, 170, 200)):
    img = _canvas(s)
    d = ImageDraw.Draw(img)
    cx, base = s / 2, s * 0.78

    def petal_poly(angle, length, width, col):
        pts = []
        for i in range(41):
            t = i / 40
            # Teardrop petal outline.
            w = width * math.sin(math.pi * t) * (1 - 0.35 * t)
            pts.append((t * length, w))
        pts += [(x, -y) for x, y in reversed(pts)]
        a = math.radians(angle)
        rot = [(cx + x * math.sin(a) + y * math.cos(a),
                base - x * math.cos(a) + y * math.sin(a)) for x, y in pts]
        d.polygon(rot, fill=col + (255,), outline=(150, 30, 70, 255))
        # Centre vein.
        d.line([(cx, base), (cx + length * 0.8 * math.sin(a),
                             base - length * 0.8 * math.cos(a))],
               fill=(170, 40, 90, 160), width=max(2, s // 200))

    for ang in (-78, 78):
        petal_poly(ang, s * 0.40, s * 0.10, (210, 70, 120))
    for ang in (-55, 55):
        petal_poly(ang, s * 0.46, s * 0.12, petal)
    for ang in (-28, 28):
        petal_poly(ang, s * 0.52, s * 0.13, inner)
    petal_poly(0, s * 0.56, s * 0.14, (255, 196, 216))
    # Leaves / water line.
    d.ellipse((s * 0.12, base - s * 0.03, s * 0.88, base + s * 0.09),
              fill=(46, 125, 80, 255))
    d.ellipse((s * 0.2, base - s * 0.01, s * 0.8, base + s * 0.06),
              fill=(70, 160, 100, 255))
    return img


def trishul(s):
    img = _canvas(s)
    d = ImageDraw.Draw(img)
    cx = s / 2
    w = s * 0.035
    c = GOLD + (255,)
    o = GOLD_D + (255,)
    # Shaft.
    d.rounded_rectangle((cx - w / 2, s * 0.30, cx + w / 2, s * 0.97), w / 2,
                        fill=c, outline=o, width=2)
    # Central prong.
    d.polygon([(cx, s * 0.03), (cx + w * 1.4, s * 0.20), (cx + w / 2, s * 0.32),
               (cx - w / 2, s * 0.32), (cx - w * 1.4, s * 0.20)],
              fill=c, outline=o)
    # Side prongs: curved blades.
    for sgn in (-1, 1):
        pts = []
        for i in range(30):
            t = i / 29
            x = cx + sgn * (s * 0.04 + s * 0.20 * math.sin(t * math.pi / 2))
            y = s * 0.36 - s * 0.26 * t ** 1.6
            pts.append((x, y))
        inner = []
        for i in range(30):
            t = i / 29
            x = cx + sgn * (s * 0.04 + s * 0.11 * math.sin(t * math.pi / 2))
            y = s * 0.36 - s * 0.16 * t ** 1.6
            inner.append((x, y))
        tip = (cx + sgn * s * 0.25, s * 0.06)
        d.polygon(pts + [tip] + list(reversed(inner)), fill=c, outline=o)
    # Crossbar.
    d.rounded_rectangle((cx - s * 0.20, s * 0.33, cx + s * 0.20, s * 0.37),
                        6, fill=c, outline=o, width=2)
    # Damru tied below the prongs.
    dy = s * 0.47
    dw, dh = s * 0.12, s * 0.10
    d.polygon([(cx - dw, dy - dh), (cx + dw, dy - dh), (cx + s * 0.02, dy),
               (cx + dw, dy + dh), (cx - dw, dy + dh), (cx - s * 0.02, dy)],
              fill=(150, 60, 30, 255), outline=o)
    d.ellipse((cx - dw, dy - dh - 8, cx + dw, dy - dh + 8),
              fill=(240, 220, 180, 255), outline=o)
    d.ellipse((cx - dw, dy + dh - 8, cx + dw, dy + dh + 8),
              fill=(240, 220, 180, 255), outline=o)
    # Ribbon.
    d.line([(cx, dy), (cx + s * 0.10, dy + s * 0.06), (cx + s * 0.07,
                                                     dy + s * 0.14)],
           fill=(220, 40, 40, 255), width=6)
    return _bevel(img)


def peacock_feather(s, angle=-20):
    f = _canvas(s)
    d = ImageDraw.Draw(f)
    cx = s / 2
    # Barbs: many thin green lines fanning out along the shaft.
    for i in range(140):
        t = i / 139
        y = s * 0.92 - t * s * 0.80
        spread = s * 0.18 * math.sin(math.pi * min(1, t * 1.15))
        for sgn in (-1, 1):
            d.line([(cx, y), (cx + sgn * spread, y - s * 0.05)],
                   fill=(40 + int(60 * t), 150, 90, 180), width=2)
    # Eye.
    ey = s * 0.27
    for r, col in [(0.15, (30, 140, 90)), (0.12, (220, 170, 40)),
                   (0.095, (20, 120, 150)), (0.07, (30, 60, 160)),
                   (0.04, (20, 20, 70))]:
        rx, ry = s * r * 0.85, s * r
        d.ellipse((cx - rx, ey - ry, cx + rx, ey + ry), fill=col + (255,))
    d.line([(cx, s * 0.97), (cx, s * 0.12)], fill=(240, 230, 200, 255),
           width=3)
    return f.rotate(angle, resample=Image.BICUBIC, center=(s / 2, s / 2))


def flute_and_feather(s):
    img = _canvas(s)
    fe = peacock_feather(int(s * 0.9), angle=18)
    img.alpha_composite(fe, (int(s * 0.12), 0))
    fl = _canvas(s)
    d = ImageDraw.Draw(fl)
    y = s * 0.62
    d.rounded_rectangle((s * 0.04, y - s * 0.028, s * 0.96, y + s * 0.028),
                        s * 0.028, fill=(200, 140, 60, 255),
                        outline=(120, 70, 20, 255), width=3)
    for i in range(7):
        x = s * 0.30 + i * s * 0.07
        d.ellipse((x - 7, y - 7, x + 7, y + 7), fill=(60, 30, 10, 255))
    for x in (s * 0.12, s * 0.86):
        d.rectangle((x - 6, y - s * 0.03, x + 6, y + s * 0.03),
                    fill=GOLD + (255,))
    # Tassel.
    d.line([(s * 0.86, y), (s * 0.90, y + s * 0.15)], fill=(220, 40, 40, 255),
           width=5)
    d.ellipse((s * 0.88, y + s * 0.14, s * 0.93, y + s * 0.20),
              fill=(220, 40, 40, 255))
    fl = fl.rotate(-14, resample=Image.BICUBIC, center=(s / 2, s / 2))
    img.alpha_composite(fl)
    return img


def gada(s):
    img = _canvas(s)
    d = ImageDraw.Draw(img)
    cx = s / 2
    c, o = GOLD + (255,), GOLD_D + (255,)
    d.rounded_rectangle((cx - s * 0.025, s * 0.45, cx + s * 0.025, s * 0.97),
                        8, fill=c, outline=o, width=2)
    for y in (s * 0.6, s * 0.75, s * 0.9):
        d.rounded_rectangle((cx - s * 0.04, y - 8, cx + s * 0.04, y + 8), 6,
                            fill=(210, 60, 30, 255))
    # Head: ribbed sphere.
    hy, r = s * 0.28, s * 0.22
    d.ellipse((cx - r, hy - r, cx + r, hy + r), fill=c, outline=o, width=4)
    for k in (-0.6, -0.2, 0.2, 0.6):
        d.arc((cx - r * abs(k) - 2, hy - r, cx + r * abs(k) + 2, hy + r),
              90 if k < 0 else 270, 270 if k < 0 else 90, fill=o, width=3)
    d.ellipse((cx - r * 0.3, hy - r * 1.25, cx + r * 0.3, hy - r * 0.85),
              fill=c, outline=o, width=3)
    d.rounded_rectangle((cx - r * 0.5, hy + r * 0.85, cx + r * 0.5,
                         hy + r * 1.15), 6, fill=(210, 60, 30, 255))
    return _bevel(img)


def kalash(s):
    img = _canvas(s)
    d = ImageDraw.Draw(img)
    cx = s / 2
    c, o = (214, 150, 60, 255), (140, 80, 20, 255)
    # Pot.
    d.ellipse((cx - s * 0.28, s * 0.45, cx + s * 0.28, s * 0.95), fill=c,
              outline=o, width=4)
    d.rectangle((cx - s * 0.14, s * 0.38, cx + s * 0.14, s * 0.52), fill=c,
                outline=o, width=3)
    d.ellipse((cx - s * 0.18, s * 0.35, cx + s * 0.18, s * 0.42), fill=c,
              outline=o, width=3)
    # Swastik on the pot, in red.
    sx, sy, k = cx, s * 0.70, s * 0.09
    red = (200, 30, 30, 255)
    w = max(4, s // 90)
    d.line([(sx, sy - k), (sx, sy + k)], fill=red, width=w)
    d.line([(sx - k, sy), (sx + k, sy)], fill=red, width=w)
    d.line([(sx, sy - k), (sx + k, sy - k)], fill=red, width=w)
    d.line([(sx + k, sy), (sx + k, sy + k)], fill=red, width=w)
    d.line([(sx, sy + k), (sx - k, sy + k)], fill=red, width=w)
    d.line([(sx - k, sy), (sx - k, sy - k)], fill=red, width=w)
    for px, py in [(sx + k / 2, sy - k / 2), (sx + k / 2, sy + k / 2),
                   (sx - k / 2, sy + k / 2), (sx - k / 2, sy - k / 2)]:
        d.ellipse((px - w, py - w, px + w, py + w), fill=red)
    # Mango leaves.
    for i, ang in enumerate([-60, -35, -12, 12, 35, 60]):
        a = math.radians(ang)
        L = s * 0.22
        x0, y0 = cx, s * 0.37
        x1, y1 = x0 + L * math.sin(a), y0 - L * math.cos(a) * 0.7
        d.polygon([(x0, y0), ((x0 + x1) / 2 + 12 * math.cos(a),
                               (y0 + y1) / 2 + 12 * math.sin(a)), (x1, y1),
                   ((x0 + x1) / 2 - 12 * math.cos(a),
                    (y0 + y1) / 2 - 12 * math.sin(a))],
                  fill=(50, 140, 60, 255), outline=(30, 90, 40, 255))
    # Coconut.
    d.ellipse((cx - s * 0.11, s * 0.13, cx + s * 0.11, s * 0.33),
              fill=(130, 80, 40, 255), outline=(80, 45, 20, 255), width=3)
    for i in range(6):
        y = s * 0.15 + i * s * 0.03
        d.line([(cx - s * 0.08, y), (cx + s * 0.08, y + 6)],
               fill=(90, 55, 25, 255), width=2)
    # Red thread.
    d.line([(cx - s * 0.14, s * 0.45), (cx + s * 0.14, s * 0.45)],
           fill=(220, 40, 40, 255), width=6)
    return img


def glyph(s, text, font_path, color=GOLD):
    """A large glyph like ॐ or श्री, gold with a soft glow."""
    img = _canvas(s)
    size = int(s * 0.75)
    while True:
        f = ImageFont.truetype(font_path, size,
                               layout_engine=ImageFont.Layout.RAQM)
        if f.getlength(text) <= s * 0.9 or size < 40:
            break
        size -= 8
    d = ImageDraw.Draw(img)
    d.text((s / 2, s / 2), text, font=f, fill=color + (255,), anchor='mm',
           stroke_width=max(2, s // 150), stroke_fill=GOLD_D + (255,))
    return _bevel(img)


def bow_arrow(s):
    img = _canvas(s)
    d = ImageDraw.Draw(img)
    c, o = GOLD + (255,), GOLD_D + (255,)
    # Bow: left half of a tall ellipse, opening to the right.
    box = (s * 0.18, s * 0.06, s * 0.62, s * 0.94)
    wdt = int(s * 0.04)
    d.arc(box, 95, 265, fill=o, width=wdt + 6)
    d.arc(box, 95, 265, fill=c, width=wdt)
    cx, cy, rx, ry = s * 0.40, s * 0.5, s * 0.22, s * 0.44
    top = (cx + rx * math.cos(math.radians(265)),
           cy + ry * math.sin(math.radians(265)))
    bot = (cx + rx * math.cos(math.radians(95)),
           cy + ry * math.sin(math.radians(95)))
    d.line([top, bot], fill=(250, 240, 220, 255), width=4)
    # Grip.
    d.rounded_rectangle((s * 0.16, s * 0.44, s * 0.24, s * 0.56), 6,
                        fill=(200, 40, 40, 255))
    # Arrow across.
    y = s * 0.5
    d.line([(top[0] - 6, y), (s * 0.92, y)], fill=c, width=9)
    d.polygon([(s * 0.99, y), (s * 0.88, y - 24), (s * 0.88, y + 24)],
              fill=c, outline=o)
    for k in range(3):
        x = top[0] + 4 + k * 20
        d.polygon([(x, y), (x - 18, y - 28), (x + 6, y - 28), (x + 22, y)],
                  fill=(220, 40, 40, 255))
        d.polygon([(x, y), (x - 18, y + 28), (x + 6, y + 28), (x + 22, y)],
                  fill=(220, 40, 40, 255))
    return _bevel(img)


def swastik(s):
    img = _canvas(s)
    d = ImageDraw.Draw(img)
    cx = cy = s / 2
    k = s * 0.32
    w = int(s * 0.07)
    red = (214, 40, 40, 255)
    segs = [((cx, cy - k), (cx, cy + k)), ((cx - k, cy), (cx + k, cy)),
            ((cx, cy - k), (cx + k, cy - k)), ((cx + k, cy), (cx + k, cy + k)),
            ((cx, cy + k), (cx - k, cy + k)), ((cx - k, cy), (cx - k, cy - k))]
    for col, ww in ((GOLD + (255,), w + 10), (red, w)):
        for a, b in segs:
            d.line([a, b], fill=col, width=ww)
        for a, b in segs:
            for p in (a, b):
                d.ellipse((p[0] - ww / 2, p[1] - ww / 2, p[0] + ww / 2,
                           p[1] + ww / 2), fill=col)
    for px, py in [(cx + k / 2, cy - k / 2), (cx + k / 2, cy + k / 2),
                   (cx - k / 2, cy + k / 2), (cx - k / 2, cy - k / 2)]:
        r = s * 0.035
        d.ellipse((px - r - 5, py - r - 5, px + r + 5, py + r + 5),
                  fill=GOLD + (255,))
        d.ellipse((px - r, py - r, px + r, py + r), fill=red)
    return img


def chakra(s):
    img = _canvas(s)
    d = ImageDraw.Draw(img)
    cx = cy = s / 2
    c, o = GOLD + (255,), GOLD_D + (255,)
    R = s * 0.44
    # Serrated rim.
    pts = []
    n = 48
    for i in range(n * 2):
        a = math.pi * i / n
        r = R if i % 2 == 0 else R * 0.90
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    d.polygon(pts, fill=c, outline=o)
    d.ellipse((cx - R * 0.80, cy - R * 0.80, cx + R * 0.80, cy + R * 0.80),
              fill=(0, 0, 0, 0), outline=o, width=3)
    inner = Image.new('L', img.size, 0)
    ImageDraw.Draw(inner).ellipse((cx - R * 0.78, cy - R * 0.78,
                                   cx + R * 0.78, cy + R * 0.78), fill=255)
    img.putalpha(Image.composite(Image.new('L', img.size, 0), img.split()[3],
                                 inner))
    d = ImageDraw.Draw(img)
    for i in range(12):
        a = 2 * math.pi * i / 12
        d.line([(cx + R * 0.2 * math.cos(a), cy + R * 0.2 * math.sin(a)),
                (cx + R * 0.79 * math.cos(a), cy + R * 0.79 * math.sin(a))],
               fill=c, width=int(s * 0.025))
    d.ellipse((cx - R * 0.24, cy - R * 0.24, cx + R * 0.24, cy + R * 0.24),
              fill=c, outline=o, width=3)
    d.ellipse((cx - R * 0.10, cy - R * 0.10, cx + R * 0.10, cy + R * 0.10),
              fill=(214, 40, 40, 255))
    return _bevel(img)
