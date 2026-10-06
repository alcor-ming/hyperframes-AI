"""Procedural paper-theatre art; called by showcase_tools, with no Work dependency."""
import math
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy import ndimage as ndi

W, H = 1920, 1080
OPEN = (330, 128, 1590, 935)          # proscenium opening
ROOM_L = (16, 552, 266, 985)          # backstage cut-aways
ROOM_R = (1654, 552, 1904, 985)
BD = (1440, 880)                      # backdrop canvas
SS = 2                                # supersampling for shapes


# ---------------------------------------------------------------- helpers
def noise(h, w, sigma, seed, amp=1.0):
    r = np.random.default_rng(seed).standard_normal((h, w))
    n = ndi.gaussian_filter(r, sigma)
    n /= (n.std() + 1e-6)
    return n * amp


def paper_tex(h, w, seed, amp=7.0):
    """fine paper fibre texture, zero-mean"""
    return noise(h, w, 0.8, seed, amp * 0.5) + noise(h, w, 3.0, seed + 1, amp * 0.35) + \
        noise(h, w, (0.5, 6), seed + 2, amp * 0.4)


def rgb(hexs):
    hexs = hexs.lstrip("#")
    return np.array([int(hexs[i:i + 2], 16) for i in (0, 2, 4)], np.float32)


def rough(points, amp, seed, step=10):
    """perturb a polygon so cut edges look hand-cut"""
    rng = np.random.default_rng(seed)
    out = []
    pts = list(points) + [points[0]]
    for (x0, y0), (x1, y1) in zip(pts[:-1], pts[1:]):
        L = math.hypot(x1 - x0, y1 - y0)
        n = max(1, int(L / step))
        for i in range(n):
            t = i / n
            out.append((x0 + (x1 - x0) * t + rng.normal(0, amp), y0 + (y1 - y0) * t + rng.normal(0, amp)))
    return out


def mask_poly(h, w, polys, blur=0.6):
    im = Image.new("L", (w * SS, h * SS), 0)
    d = ImageDraw.Draw(im)
    for p in polys:
        d.polygon([(x * SS, y * SS) for x, y in p], fill=255)
    im = im.resize((w, h), Image.LANCZOS)
    if blur:
        im = im.filter(ImageFilter.GaussianBlur(blur))
    return np.asarray(im).astype(np.float32) / 255.0


def mask_ellipses(h, w, ells):
    im = Image.new("L", (w * SS, h * SS), 0)
    d = ImageDraw.Draw(im)
    for (cx, cy, rx, ry) in ells:
        d.ellipse([(cx - rx) * SS, (cy - ry) * SS, (cx + rx) * SS, (cy + ry) * SS], fill=255)
    im = im.resize((w, h), Image.LANCZOS)
    return np.asarray(im).astype(np.float32) / 255.0


class Canvas:
    """RGBA float canvas with paper-cut layering: each layer gets texture, an optional rim and a hard shadow."""

    def __init__(self, w, h, bg=None):
        self.w, self.h = w, h
        self.c = np.zeros((h, w, 3), np.float32)
        self.a = np.zeros((h, w), np.float32)
        if bg is not None:
            self.c[:] = bg
            self.a[:] = 1

    def layer(self, m, color, seed=0, tex=6.0, shadow=(5, 7, 0.28), rim=0, rim_col="#fffaf0", shade=None):
        h, w = self.h, self.w
        if shadow:
            dx, dy, sa = shadow
            sh = np.zeros_like(m)
            sh[max(0, dy):, max(0, dx):] = m[:h - max(0, dy), :w - max(0, dx)]
            sh = ndi.gaussian_filter(sh, 1.2) * sa
            self._over(np.zeros((h, w, 3), np.float32) + rgb("#1e1008"), sh)
        if rim:
            rm = np.clip(ndi.grey_dilation(m, size=(rim * 2 + 1, rim * 2 + 1)), 0, 1)
            rm = ndi.gaussian_filter(rm, 0.6)
            self._over(np.zeros((h, w, 3), np.float32) + rgb(rim_col), rm)
        col = np.zeros((h, w, 3), np.float32) + (rgb(color) if isinstance(color, str) else color)
        if shade is not None:
            col = col * shade[..., None]
        if tex:
            col = col + paper_tex(h, w, seed, tex)[..., None]
        self._over(col, m)

    def _over(self, col, m):
        m = np.clip(m, 0, 1)
        na = m + self.a * (1 - m)
        self.c = (col * m[..., None] + self.c * (self.a * (1 - m))[..., None]) / np.maximum(na, 1e-5)[..., None]
        self.a = na

    def vgrad(self, top, bottom, y0=0, y1=None):
        y1 = self.h if y1 is None else y1
        t = np.clip((np.arange(self.h) - y0) / max(1, (y1 - y0)), 0, 1)[:, None, None]
        return (rgb(top) * (1 - t) + rgb(bottom) * t) * np.ones((1, self.w, 1), np.float32)

    def save(self, path, jpg=False):
        c = np.clip(self.c, 0, 255).astype(np.uint8)
        if jpg:
            Image.fromarray(c, "RGB").save(path, quality=88, optimize=True)
        else:
            a = np.clip(self.a * 255, 0, 255).astype(np.uint8)
            Image.fromarray(np.dstack([c, a]), "RGBA").save(path, optimize=True)


def star_pts(cx, cy, r, k=5, inner=0.45, rot=-90):
    pts = []
    for i in range(k * 2):
        rr = r if i % 2 == 0 else r * inner
        ang = math.radians(rot + i * 180 / k)
        pts.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
    return pts


def cloud_pts(cx, cy, w, h, seed):
    rng = np.random.default_rng(seed)
    ells = []
    n = 5
    for i in range(n):
        t = i / (n - 1)
        x = cx - w / 2 + w * (0.12 + 0.76 * t)
        r = h * (0.36 + 0.28 * math.sin(math.pi * t)) * rng.uniform(0.9, 1.1)
        ells.append((x, cy - r * 0.35, r * 1.1, r))
    ells.append((cx, cy + h * 0.12, w * 0.48, h * 0.28))
    return ells


def hills(w, base, amp, waves, seed, h):
    rng = np.random.default_rng(seed)
    ph = rng.uniform(0, 6.28, len(waves))
    pts = [(0, h)]
    for x in range(0, w + 20, 20):
        y = base + sum(a * math.sin(x / l * 6.28 + p) for (a, l), p in zip(waves, ph)) * amp
        pts.append((x, y))
    pts.append((w, h))
    return pts


# ---------------------------------------------------------------- the house frame
def frame(output):
    cv = Canvas(W, H)
    # house wall: deep aubergine paper with a faint damask stencil
    wall = cv.vgrad("#3a1f2e", "#24131d")
    yy, xx = np.mgrid[0:H, 0:W]
    dam = (np.sin(xx / 22.0) * np.sin(yy / 22.0) > 0.55).astype(np.float32)
    dam = ndi.gaussian_filter(dam, 1.0)
    wall = wall + dam[..., None] * np.array([14, 6, 10]) + paper_tex(H, W, 3, 6)[..., None]
    full = np.ones((H, W), np.float32)
    cv._over(wall, full)
    # wainscot on the house walls at the backstage level
    for x0, x1 in ((0, 290), (1630, W)):
        m = mask_poly(H, W, [[(x0, 520), (x1, 520), (x1, 540), (x0, 540)]])
        cv.layer(m, "#7a4a2a", seed=11, shadow=(0, 4, 0.35))
    # proscenium pillars: cream paper with gold trim, fluting
    for (x0, x1) in ((272, 338), (1582, 1648)):
        m = mask_poly(H, W, [rough([(x0, 30), (x1, 30), (x1, 1000), (x0, 1000)], 0.8, x0)])
        fl = 1 - 0.10 * (np.sin((xx - x0) / (x1 - x0) * math.pi * 6) > 0.6)
        cv.layer(m, "#efe2c4", seed=x0, shade=fl, rim=3, rim_col="#c79a3c", shadow=(6, 0, 0.35))
        for yb in (56, 960):
            cap = mask_poly(H, W, [rough([(x0 - 14, yb - 18), (x1 + 14, yb - 18), (x1 + 14, yb + 18), (x0 - 14, yb + 18)], 0.8, yb + x0)])
            cv.layer(cap, "#d6a94a", seed=yb + x0, shadow=(4, 5, 0.35), rim=2)
    # header beam
    hb = mask_poly(H, W, [rough([(258, 26), (1662, 26), (1662, 130), (258, 130)], 0.8, 5)])
    cv.layer(hb, "#efe2c4", seed=21, rim=3, rim_col="#c79a3c", shadow=(0, 7, 0.35))
    # gold medallion in the header centre
    med = mask_ellipses(H, W, [(960, 78, 70, 36)])
    cv.layer(med, "#d6a94a", seed=22, rim=3, rim_col="#fff1c8", shadow=(3, 4, 0.3))
    # holes: stage opening and the two backstage rooms (rough hand-cut edge)
    hole = mask_poly(H, W, [rough([(OPEN[0], 130), (OPEN[2], 130), (OPEN[2], 936), (OPEN[0], 936)], 0.0, 9)], blur=0.5)
    rooms = mask_poly(H, W, [rough([(r[0], r[1]), (r[2], r[1]), (r[2], r[3]), (r[0], r[3])], 1.2, r[0], 8) for r in (ROOM_L, ROOM_R)], blur=0.6)
    cut = np.clip(hole + rooms, 0, 1)
    # rooms get a lighter paper rim and inner shadow
    rim = np.clip(ndi.grey_dilation(rooms, size=(9, 9)) - rooms, 0, 1)
    cv._over(np.zeros((H, W, 3), np.float32) + rgb("#f3e6c8"), rim)
    cv.a = cv.a * (1 - cut)
    cv.save(output / "frame.png")


def valance(output):
    w, h = OPEN[2] - OPEN[0] + 40, 120
    cv = Canvas(w, h)
    pts = [(0, 0), (w, 0)]
    n = 9
    sw = w / n
    edge = []
    for i in range(n + 1):
        x = w - i * sw
        edge.append((x, 62))
        if i < n:
            for k in range(1, 12):
                t = k / 12
                edge.append((x - sw * t, 62 + math.sin(math.pi * t) * 38))
    m = mask_poly(h, w, [pts + edge])
    xx = np.arange(w)[None, :]
    folds = 0.82 + 0.18 * np.cos(xx / sw * 2 * math.pi) * np.ones((h, 1))
    cv.layer(m, "#a8162a", seed=31, shade=folds, shadow=(0, 6, 0.4), tex=5)
    # gold fringe along the scallops
    fr = np.zeros((h, w), np.float32)
    for x, y in edge:
        xi, yi = int(x), int(y)
        if 0 <= xi < w:
            fr[max(0, yi - 4):min(h, yi + 9), max(0, xi - 3):min(w, xi + 3)] = 1
    fr = ndi.gaussian_filter(fr, 0.7)
    cv.layer(fr, "#e2b14c", seed=32, shadow=(0, 3, 0.3), tex=4)
    # gold braid at the top
    br = mask_poly(h, w, [[(0, 6), (w, 6), (w, 20), (0, 20)]])
    cv.layer(br, "#d6a94a", seed=33, shadow=(0, 3, 0.3))
    cv.save(output / "valance.png")


def velvet(w, h, seed, folds_n, hem=True, flip=False):
    cv = Canvas(w, h)
    m = mask_poly(h, w, [[(0, 0), (w, 0), (w, h), (0, h)]], blur=0)
    xx = np.arange(w, dtype=np.float32)[None, :]
    ph = np.random.default_rng(seed).uniform(0, 6.28, 3)
    f = (np.sin(xx / w * folds_n * 2 * math.pi + ph[0]) * 0.6 + np.sin(xx / w * folds_n * 4.3 * math.pi + ph[1]) * 0.25)
    shade = (0.78 + 0.22 * f) * np.ones((h, 1), np.float32)
    shade = shade * (0.92 + 0.08 * np.linspace(1, 0, h)[:, None])
    cv.layer(m, "#b0182c", seed=seed, shade=shade, shadow=None, tex=4)
    if hem:
        hm = mask_poly(h, w, [[(0, h - 30), (w, h - 30), (w, h - 8), (0, h - 8)]])
        cv.layer(hm, "#d6a94a", seed=seed + 1, shadow=(0, 3, 0.3), tex=4)
        fr = np.zeros((h, w), np.float32)
        for x in range(4, w, 9):
            fr[h - 9:h, x:x + 4] = 1
        cv.layer(ndi.gaussian_filter(fr, 0.6), "#e8bc5a", seed=seed + 2, shadow=None, tex=3)
    return cv


def curtains(output):
    w = (OPEN[2] - OPEN[0]) // 2 + 70
    h = OPEN[3] - 150 + 10
    for side, seed in (("l", 41), ("r", 42)):
        cv = velvet(w, h, seed, 7)
        # the meeting edge: a darker overlap fold
        xx = np.arange(w)[None, :]
        e = (xx > w - 26) if side == "l" else (xx < 26)
        cv.c = cv.c * np.where(e[..., None], 0.78, 1.0)
        cv.save(output / f"curtain-{side}.png")


def legs(output):
    w, h = 150, OPEN[3] - 150
    for side, seed in (("l", 51), ("r", 52)):
        cv = Canvas(w, h)
        # a drape tied back: wide at top, pinched at 62 %, flaring to the floor
        pts = []
        for y in range(0, h + 1, 10):
            t = y / h
            if t < 0.62:
                width = 150 - 92 * (t / 0.62) ** 1.4
            else:
                width = 58 + 70 * ((t - 0.62) / 0.38) ** 1.2
            pts.append((width, y))
        poly = [(0, 0)] + pts + [(0, h)]
        if side == "r":
            poly = [(w - x, y) for x, y in poly]
        m = mask_poly(h, w, [poly])
        xx = np.arange(w, dtype=np.float32)[None, :]
        shade = (0.8 + 0.2 * np.sin(xx / 14.0)) * np.ones((h, 1), np.float32)
        cv.layer(m, "#9c1428", seed=seed, shade=shade, shadow=(6 if side == "l" else -6, 4, 0.0), tex=4)
        tie = mask_poly(h, w, [[(0, h * 0.6), (90, h * 0.6 - 6), (90, h * 0.6 + 14), (0, h * 0.6 + 20)]])
        if side == "r":
            tie = tie[:, ::-1]
        cv.layer(tie, "#e2b14c", seed=seed + 3, shadow=(2, 3, 0.35))
        cv.save(output / f"leg-{side}.png")


def floor(output):
    w, h = OPEN[2] - OPEN[0], 190
    cv = Canvas(w, h)
    m = np.ones((h, w), np.float32)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    # perspective: plank seams converge to a vanishing point far above the centre
    vx, vy = w / 2, -900
    ang = np.arctan2(xx - vx, yy - vy)
    seams = np.abs(np.sin(ang * 70)) < 0.06
    rows = np.abs(np.sin(np.log(yy + 140) * 26)) < 0.05
    wood = 0.9 + 0.1 * np.sin(ang * 70 * 3 + noise(h, w, (2, 20), 61, 2))
    shade = wood * (0.78 + 0.22 * (yy / h)) * (1 - 0.35 * seams - 0.15 * rows)
    cv.layer(m, "#b07a48", seed=61, shade=shade, shadow=None, tex=5)
    # spike tape marks get drawn by the DOM; add scuffs
    sc = (noise(h, w, 6, 62) > 2.2).astype(np.float32)
    cv.c = cv.c * (1 - 0.12 * ndi.gaussian_filter(sc, 2)[..., None])
    cv.save(output / "floor.png")


def lip(output):
    """stage lip (front edge of the stage) with footlight hoods"""
    w, h = OPEN[2] - OPEN[0] + 120, 64
    cv = Canvas(w, h)
    m = mask_poly(h, w, [[(0, 6), (w, 6), (w, h), (0, h)]])
    yy = np.arange(h, dtype=np.float32)[:, None]
    cv.layer(m, "#5a3018", seed=71, shade=(0.8 + 0.2 * (yy / h)) * np.ones((1, w)), shadow=None)
    trim = mask_poly(h, w, [[(0, 0), (w, 0), (w, 9), (0, 9)]])
    cv.layer(trim, "#d6a94a", seed=72, shadow=(0, 3, 0.4))
    # hoods: half-shells every 90 px (the bulbs themselves are DOM so they can chase)
    hoods = []
    for x in range(60, w - 30, 90):
        hoods.append(rough([(x - 26, 14), (x + 26, 14), (x + 20, 34), (x - 20, 34)], 0.4, x, 6))
    cv.layer(mask_poly(h, w, hoods), "#2a1a10", seed=73, shadow=(0, 3, 0.3), rim=1, rim_col="#d6a94a")
    cv.save(output / "lip.png")


def band(output):
    w, h = W, 100
    cv = Canvas(w, h)
    m = np.ones((h, w), np.float32)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    panels = 1 - 0.12 * (np.abs(((xx + 60) % 240) - 120) > 112)
    cv.layer(m, "#3c2216", seed=81, shade=panels * (0.85 + 0.15 * (1 - yy / h)), shadow=None)
    trim = mask_poly(h, w, [[(0, 0), (w, 0), (w, 7), (0, 7)]])
    cv.layer(trim, "#d6a94a", seed=82, shadow=(0, 3, 0.45))
    cv.save(output / "band.png")


def room(side, output):
    x0, y0, x1, y1 = ROOM_L if side == "l" else ROOM_R
    w, h = x1 - x0 + 20, y1 - y0 + 20
    cv = Canvas(w, h, bg=rgb("#2c3442"))
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    # brick wall, dim and blue
    row = (yy // 22).astype(int)
    off = (row % 2) * 24
    mortar = ((yy % 22) < 2.5) | (((xx + off) % 48) < 2.5)
    shade = (0.85 + 0.15 * noise(h, w, 8, 91 if side == "l" else 92) * 0.5) * (1 - 0.22 * mortar)
    cv.layer(np.ones((h, w), np.float32), "#3a4558", seed=93, shade=shade, shadow=None, tex=5)
    # floor boards
    fl = mask_poly(h, w, [[(0, h - 78), (w, h - 78), (w, h), (0, h)]])
    cv.layer(fl, "#4a3526", seed=94, shade=1 - 0.2 * ((xx % 40) < 2), shadow=(0, -3, 0.4))
    # a pipe and a fuse box
    pipe = mask_poly(h, w, [[(w - 34, 0), (w - 24, 0), (w - 24, h - 78), (w - 34, h - 78)]]) if side == "l" else \
        mask_poly(h, w, [[(24, 0), (34, 0), (34, h - 78), (24, h - 78)]])
    cv.layer(pipe, "#6a7486", seed=95, shadow=(3, 0, 0.35))
    # vignette (work light pool is DOM)
    vg = 1 - 0.45 * (((xx - w / 2) / (w / 2)) ** 2 * 0.5 + ((yy - h * 0.55) / (h * 0.6)) ** 2 * 0.5)
    cv.c = cv.c * np.clip(vg, 0.4, 1)[..., None]
    cv.save(output / f"room-{side}.jpg", jpg=True)


def wing(side, output):
    w, h = 210, 760
    cv = Canvas(w, h)
    # a flat painted as a paper-cut tree trunk with leaves: reads as generic scenery under any gel
    trunk = rough([(70, h), (70, 260), (110, 200), (140, 260), (140, h)], 1.5, 101, 12)
    cv.layer(mask_poly(h, w, [trunk]), "#6b4a2e", seed=102, shadow=(6, 6, 0.3), rim=3)
    ells = [(105, 170, 100, 90), (60, 260, 70, 60), (160, 250, 60, 55), (110, 90, 70, 60)]
    cv.layer(mask_ellipses(h, w, ells), "#3f7a4a", seed=103, shadow=(6, 6, 0.3), rim=4)
    ells2 = [(90, 150, 50, 42), (140, 210, 40, 32), (70, 230, 30, 26)]
    cv.layer(mask_ellipses(h, w, ells2), "#5aa060", seed=104, shadow=(3, 4, 0.25))
    if side == "r":
        cv.c = cv.c[:, ::-1]
        cv.a = cv.a[:, ::-1]
    cv.save(output / f"wing-{side}.png")


# ---------------------------------------------------------------- backdrops
def bd_clouds(output):
    w, h = BD
    cv = Canvas(w, h)
    cv._over(cv.vgrad("#b7b2f2", "#f3d2ec", 0, h), np.ones((h, w), np.float32))
    for i, (cy, col, seed) in enumerate(((560, "#e9e1ff", 1), (650, "#d9ccff", 2), (740, "#fbf4ff", 3))):
        ells = []
        for k in range(7):
            ells += cloud_pts(80 + k * 230 + (i % 2) * 110, cy, 300, 120, seed * 10 + k)
        cv.layer(mask_ellipses(h, w, ells), col, seed=200 + i, rim=3, shadow=(5, 7, 0.22))
    rng = np.random.default_rng(7)
    stars = [star_pts(rng.uniform(60, w - 60), rng.uniform(40, 420), rng.uniform(10, 24), 4, 0.38) for _ in range(26)]
    cv.layer(mask_poly(h, w, stars), "#ffe08a", seed=210, rim=2, shadow=(3, 4, 0.22))
    cv.save(output / "bd-clouds.jpg", jpg=True)


def bd_night(output):
    w, h = BD
    cv = Canvas(w, h)
    cv._over(cv.vgrad("#141a44", "#33407a", 0, h), np.ones((h, w), np.float32))
    rng = np.random.default_rng(8)
    stars = [star_pts(rng.uniform(40, w - 40), rng.uniform(30, 520), rng.uniform(5, 14), 5, 0.45) for _ in range(60)]
    cv.layer(mask_poly(h, w, stars), "#fff1b0", seed=220, rim=1, shadow=(2, 3, 0.25))
    for i, (base, col) in enumerate(((620, "#2a3768"), (700, "#1f2a55"), (780, "#172045"))):
        cv.layer(mask_poly(h, w, [hills(w, base, 1, [(40, 520), (22, 260)], 300 + i, h)]), col, seed=230 + i, rim=2, rim_col="#8090c8", shadow=(4, 6, 0.3))
    cv.save(output / "bd-night.jpg", jpg=True)


def bd_market(output):
    w, h = BD
    cv = Canvas(w, h)
    cv._over(cv.vgrad("#ffb98a", "#ffe3b0", 0, h), np.ones((h, w), np.float32))
    # bunting string across the top
    flags = []
    for i in range(18):
        x = 30 + i * 78
        y = 70 + 40 * math.sin(i / 17 * math.pi)
        flags.append([(x, y), (x + 56, y + 4), (x + 28, y + 52)])
    cols = ["#e8505b", "#f9d56e", "#14b1ab", "#f3ecc2"]
    for k, c in enumerate(cols):
        cv.layer(mask_poly(h, w, flags[k::4]), c, seed=240 + k, rim=2, shadow=(3, 4, 0.25))
    # stall silhouettes with striped awnings
    for i, x in enumerate((40, 400, 760, 1100)):
        body = rough([(x, 470), (x + 300, 470), (x + 300, 800), (x, 800)], 1.0, 250 + i, 12)
        cv.layer(mask_poly(h, w, [body]), "#c98a5a", seed=251 + i, rim=3, shadow=(6, 7, 0.3))
        aw = [(x - 20, 400), (x + 320, 400), (x + 330, 480), (x - 30, 480)]
        stripes = []
        for s in range(0, 8, 2):
            sx0 = x - 20 + s * 42.5
            stripes.append([(sx0, 400), (sx0 + 42.5, 400), (sx0 + 42.5 + 1.25 * 4, 480), (sx0 + 1.25 * 4 - 10, 480)])
        cv.layer(mask_poly(h, w, [aw]), "#fffaf0", seed=260 + i, rim=0, shadow=(5, 7, 0.3))
        cv.layer(mask_poly(h, w, stripes), ["#e8505b", "#14b1ab", "#f2a541", "#7b6cd9"][i], seed=270 + i, shadow=None)
        win = rough([(x + 40, 530), (x + 260, 530), (x + 260, 690), (x + 40, 690)], 0.8, 280 + i)
        cv.layer(mask_poly(h, w, [win]), "#5a3a28", seed=281 + i, shadow=None)
    cv.save(output / "bd-market.jpg", jpg=True)


def bd_pasture(output):
    w, h = BD
    cv = Canvas(w, h)
    cv._over(cv.vgrad("#8fd0f5", "#e2f6ff", 0, h), np.ones((h, w), np.float32))
    ells = []
    for k, (x, y) in enumerate(((180, 160), (620, 110), (1080, 190), (1320, 90))):
        ells += cloud_pts(x, y, 260, 100, 400 + k)
    cv.layer(mask_ellipses(h, w, ells), "#ffffff", seed=410, rim=2, shadow=(4, 6, 0.18))
    for i, (base, col) in enumerate(((520, "#9fd36b"), (610, "#7cc05a"), (700, "#5fa84a"))):
        cv.layer(mask_poly(h, w, [hills(w, base, 1, [(50, 700), (25, 300)], 420 + i, h)]), col, seed=430 + i, rim=3, shadow=(5, 7, 0.28))
    # fence
    posts = [[(x, 610), (x + 16, 610), (x + 16, 720), (x, 720)] for x in range(40, w, 120)]
    rails = [[(0, 630), (w, 630), (w, 646), (0, 646)], [(0, 676), (w, 676), (w, 692), (0, 692)]]
    cv.layer(mask_poly(h, w, rails + posts), "#f6efe0", seed=440, rim=0, shadow=(4, 5, 0.3))
    rng = np.random.default_rng(9)
    fl = [(rng.uniform(20, w - 20), rng.uniform(740, 860), 9, 9) for _ in range(40)]
    cv.layer(mask_ellipses(h, w, fl), "#fff3a8", seed=450, rim=2, rim_col="#ffffff", shadow=(2, 3, 0.2))
    cv.save(output / "bd-pasture.jpg", jpg=True)


def bd_office(output):
    w, h = BD
    cv = Canvas(w, h)
    cv._over(cv.vgrad("#1b2236", "#283152", 0, h), np.ones((h, w), np.float32))
    # big window with a paper city at night
    win = [(300, 110), (1140, 110), (1140, 560), (300, 560)]
    cv.layer(mask_poly(h, w, [win]), "#0e1430", seed=500, rim=10, rim_col="#5b6480", shadow=(6, 8, 0.4))
    rng = np.random.default_rng(10)
    bldg, lit = [], []
    x = 300
    while x < 1140:
        bw = rng.uniform(60, 120)
        top = rng.uniform(260, 470)
        bldg.append([(x, top), (min(1140, x + bw), top), (min(1140, x + bw), 560), (x, 560)])
        for yy in np.arange(top + 16, 540, 30):
            for xx in np.arange(x + 10, min(1130, x + bw - 14), 24):
                if rng.uniform() < 0.45:
                    lit.append([(xx, yy), (xx + 12, yy), (xx + 12, yy + 14), (xx, yy + 14)])
        x += bw + rng.uniform(4, 16)
    cv.layer(mask_poly(h, w, bldg), "#222a4c", seed=501, shadow=None)
    cv.layer(mask_poly(h, w, lit), "#ffd77a", seed=502, shadow=None, tex=3)
    cross = [[(714, 110), (726, 110), (726, 560), (714, 560)], [(300, 330), (1140, 330), (1140, 342), (300, 342)]]
    cv.layer(mask_poly(h, w, cross), "#5b6480", seed=503, shadow=(3, 4, 0.35))
    # a paper moon in the window and a wainscot
    cv.layer(mask_ellipses(h, w, [(1010, 190, 40, 40)]), "#fff4c6", seed=504, shadow=None)
    ws = [(0, 640), (w, 640), (w, h), (0, h)]
    cv.layer(mask_poly(h, w, [ws]), "#3a2a3a", seed=505, rim=4, rim_col="#6a5060", shadow=(0, -4, 0.3))
    cv.save(output / "bd-office.jpg", jpg=True)


def bd_audition(output):
    w, h = BD
    cv = Canvas(w, h)
    cv._over(cv.vgrad("#f2d9b8", "#e8c49a", 0, h), np.ones((h, w), np.float32))
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    stripes = 1 - 0.06 * ((xx % 90) < 45)
    cv.c = cv.c * stripes[..., None]
    # mirror frame with bulbs (bulbs drawn as discs; glow is DOM)
    frame = [(330, 120), (1110, 120), (1110, 470), (330, 470)]
    cv.layer(mask_poly(h, w, [frame]), "#4a3326", seed=600, rim=4, rim_col="#d6a94a", shadow=(6, 8, 0.35))
    glass = [(360, 150), (1080, 150), (1080, 440), (360, 440)]
    cv.layer(mask_poly(h, w, [glass]), "#c8d6e0", seed=601, shadow=None, tex=3)
    sheen = mask_poly(h, w, [[(420, 150), (520, 150), (400, 440), (300, 440)], [(560, 150), (600, 150), (480, 440), (440, 440)]])
    cv.layer(sheen * 0.35, "#ffffff", seed=602, shadow=None, tex=0)
    bulbs = [(x, 135, 12, 12) for x in range(360, 1090, 60)] + [(x, 455, 12, 12) for x in range(360, 1090, 60)]
    cv.layer(mask_ellipses(h, w, bulbs), "#fff3c4", seed=603, shadow=(2, 3, 0.25), rim=2, rim_col="#d6a94a")
    ws = [(0, 600), (w, 600), (w, h), (0, h)]
    cv.layer(mask_poly(h, w, [ws]), "#7a4e34", seed=604, rim=4, rim_col="#d6a94a", shadow=(0, -4, 0.3))
    cv.save(output / "bd-audition.jpg", jpg=True)


def bd_finale(output):
    w, h = BD
    cv = Canvas(w, h)
    cv._over(cv.vgrad("#5c0f22", "#2c0614", 0, h), np.ones((h, w), np.float32))
    xx = np.arange(w, dtype=np.float32)[None, :]
    shade = (0.8 + 0.2 * np.sin(xx / 36.0)) * np.ones((h, 1), np.float32)
    cv.c = cv.c * shade[..., None]
    # swags
    sw = []
    for i in range(5):
        x0 = i * w / 5
        pts = [(x0, 0), (x0 + w / 5, 0)]
        for k in range(12, -1, -1):
            t = k / 12
            pts.append((x0 + w / 5 * t, 40 + math.sin(math.pi * t) * 110))
        sw.append(pts)
    cv.layer(mask_poly(h, w, sw), "#b0182c", seed=700, rim=3, rim_col="#e2b14c", shadow=(0, 8, 0.4))
    rng = np.random.default_rng(11)
    stars = [star_pts(rng.uniform(40, w - 40), rng.uniform(200, 700), rng.uniform(8, 18), 5, 0.45) for _ in range(34)]
    cv.layer(mask_poly(h, w, stars), "#f4c95d", seed=710, rim=2, shadow=(3, 4, 0.3))
    cv.save(output / "bd-finale.jpg", jpg=True)


def grain(output):
    s = 512
    n = paper_tex(s, s, 1000, 1.0)
    # tileable: blend with rolled copy
    n = (n + np.roll(n, s // 2, 0) + np.roll(n, s // 2, 1)) / 3
    v = np.clip(240 + n * 9, 200, 255).astype(np.uint8)
    Image.fromarray(np.dstack([v, v, v]), "RGB").save(output / "grain.png", optimize=True)



def generate(output: Path):
    """Generate the fixed 1920×1080 paper-theatre preset into an empty directory."""
    for draw in (frame, valance, curtains, legs, floor, lip, band, bd_clouds,
                 bd_night, bd_market, bd_pasture, bd_office, bd_audition, bd_finale, grain):
        draw(output)
    for side in ("l", "r"):
        room(side, output)
        wing(side, output)
