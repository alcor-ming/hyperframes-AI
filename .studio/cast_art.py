"""Near-white three-view sheets and transparent poses with paper rim and shadow."""
import numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage as ndi

PAPER = np.array([255, 251, 241], np.float32)
RIM = np.array([214, 196, 160], np.float32)
SHADOW = (7, 9, 0.30)   # dx, dy, alpha of the baked hard shadow


def disk(r):
    y, x = np.ogrid[-r:r + 1, -r:r + 1]
    return x * x + y * y <= r * r


def figure_masks(rgb):
    """Background = near-white pixels connected to the sheet border (plus large flat white holes)."""
    mn = rgb.min(axis=2)
    mx = rgb.max(axis=2)
    whiteish = (mn > 236) & ((mx - mn) < 16)
    edges = np.concatenate([whiteish[0], whiteish[-1], whiteish[:, 0], whiteish[:, -1]])
    if edges.mean() < 0.95:
        raise ValueError("sheet requires a near-white background and clear outer margins")
    lab, n = ndi.label(whiteish)
    edge = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
    bg = np.isin(lab, list(edge))
    # enclosed holes (between arm and body, between legs): very flat, very white, reasonably large
    flat = (mn > 249) & ((mx - mn) < 6)
    hl, hn = ndi.label(flat & ~bg)
    holes = np.zeros_like(bg)
    if hn:
        sizes = ndi.sum(np.ones_like(hl), hl, index=np.arange(1, hn + 1))
        for i, s in enumerate(sizes, start=1):
            if s > 1500:
                holes |= hl == i
    fg = ~(bg | holes)
    fg = ndi.binary_opening(fg, structure=disk(1))
    fg = ndi.binary_closing(fg, structure=disk(2))
    fg = ndi.binary_fill_holes(fg) & ~holes
    lab, n = ndi.label(fg)
    sizes = ndi.sum(np.ones_like(lab), lab, index=np.arange(1, n + 1))
    objs = ndi.find_objects(lab)
    H = fg.shape[0]
    # figures are tall; labels ("Front", "Back") and sparkles are not
    tall = [i + 1 for i, sl in enumerate(objs) if sl is not None and (sl[0].stop - sl[0].start) > 0.4 * H]
    parts = [lab == i for i in tall]
    if not 1 <= len(parts) <= 3:
        raise ValueError("sheet requires three tall, horizontally arranged figures")
    while len(parts) < 3:
        # two views whose hair touches: split the widest blob at its thinnest column
        parts.sort(key=lambda m: -np.ptp(np.nonzero(m)[1]))
        m = parts.pop(0)
        xs = np.nonzero(m)[1]
        x0, x1 = xs.min(), xs.max()
        cols = m.sum(axis=0)
        lo, hi = x0 + int(0.3 * (x1 - x0)), x0 + int(0.7 * (x1 - x0))
        if hi <= lo:
            raise ValueError("sheet figures are too narrow to separate")
        cut = lo + int(np.argmin(cols[lo:hi]))
        # ponytail: retain the existing valley split; complex touching poses require separate alpha inputs.
        if cut <= x0 or cut >= x1 or cols[cut] > min(cols[x0:cut].max(), cols[cut + 1:x1 + 1].max()) * 0.25:
            raise ValueError("sheet layout is unsupported: cannot separate three views")
        left, right = m.copy(), m.copy()
        left[:, cut:] = False
        right[:, :cut] = False
        parts += [left, right]
    parts.sort(key=lambda m: np.nonzero(m)[1].mean())
    spans = [(np.nonzero(m)[1].min(), np.nonzero(m)[1].max()) for m in parts]
    if any(left[1] >= right[0] for left, right in zip(spans, spans[1:])):
        raise ValueError("sheet views must be arranged horizontally without overlap")
    out = []
    for m in parts[:3]:
        ys, xs = np.nonzero(m)
        x0, x1, y0, y1 = xs.min(), xs.max(), ys.min(), ys.max()
        for i, sl in enumerate(objs):
            if sl is None or (i + 1) in tall or sizes[i] < 3000:
                continue
            cy = (sl[0].start + sl[0].stop) / 2
            cx = (sl[1].start + sl[1].stop) / 2
            if x0 <= cx <= x1 and y0 <= cy <= y1:
                m |= lab == i + 1
        out.append(m)
    return out


def diecut(rgba, scale, border=9):
    """rgba float array (h,w,4) 0..255 → die-cut PIL image with rim and baked hard shadow."""
    h, w = rgba.shape[:2]
    im = Image.fromarray(rgba.astype(np.uint8), "RGBA")
    if scale != 1:
        im = im.resize((max(1, round(w * scale)), max(1, round(h * scale))), Image.LANCZOS)
    a = np.asarray(im).astype(np.float32)
    pad = border + 16
    H, W = a.shape[0] + 2 * pad, a.shape[1] + 2 * pad
    big = np.zeros((H, W, 4), np.float32)
    big[pad:pad + a.shape[0], pad:pad + a.shape[1]] = a
    alpha = big[..., 3] / 255.0
    solid = alpha > 0.45
    if not solid.any():
        raise ValueError("Figure disappears at the requested scale")
    rim = ndi.binary_dilation(solid, structure=disk(border))
    rim_soft = np.asarray(Image.fromarray((rim * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.8))) / 255.0
    edge = rim_soft * (1 - np.asarray(Image.fromarray((ndi.binary_erosion(rim, structure=disk(2)) * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.8))) / 255.0)
    col = np.zeros((H, W, 3), np.float32)
    col[:] = PAPER
    col = col * (1 - edge[..., None] * 0.55) + RIM * (edge[..., None] * 0.55)
    col = col * (1 - alpha[..., None]) + big[..., :3] * alpha[..., None]
    out_a = np.maximum(rim_soft, alpha)
    # hard shadow underneath
    dx, dy, sa = SHADOW
    sh = np.zeros_like(out_a)
    sh[dy:, dx:] = rim_soft[:-dy, :-dx]
    sh_a = sh * sa * (1 - out_a)
    res_a = out_a + sh_a
    res_c = (col * out_a[..., None] + np.array([42, 24, 8], np.float32) * sh_a[..., None]) / np.maximum(res_a, 1e-4)[..., None]
    res = np.dstack([res_c, res_a * 255]).clip(0, 255).astype(np.uint8)
    img = Image.fromarray(res, "RGBA")
    return img.crop(img.getbbox())


def kraft(img, seed):
    """Mirrored cardboard back in the shape of the die-cut board."""
    a = np.asarray(img).astype(np.float32)[..., 3] / 255.0
    h, w = a.shape
    rng = np.random.default_rng(seed)
    base = np.array([196, 154, 104], np.float32)
    n = ndi.gaussian_filter(rng.standard_normal((h, w)), 1.2) * 10
    fib = ndi.gaussian_filter(rng.standard_normal((h, w)), (0.6, 9)) * 14
    flute = (np.sin(np.arange(w) / 3.2) * 4)[None, :]
    c = base[None, None, :] + (n + fib + flute)[..., None] * np.array([1, 0.85, 0.6])
    edge = a - ndi.grey_erosion(a, size=(9, 9))
    c = c * (1 - 0.25 * edge[..., None])
    out = np.dstack([c.clip(0, 255), (a * 255)]).astype(np.uint8)
    return Image.fromarray(out[:, ::-1], "RGBA")


def silhouette(img):
    a = np.asarray(img).astype(np.float32)[..., 3]
    out = np.zeros(a.shape + (4,), np.uint8)
    out[..., :3] = (40, 26, 18)
    out[..., 3] = a.astype(np.uint8)
    im = Image.fromarray(out, "RGBA")
    return im.resize((max(1, im.width // 2), max(1, im.height // 2)), Image.LANCZOS)


def gray(img):
    a = np.asarray(img).astype(np.float32)
    lum = a[..., :3] @ np.array([0.3, 0.59, 0.11], np.float32)
    g = lum[..., None] * 0.92 + 8
    tint = np.array([0.97, 0.98, 1.02], np.float32)
    out = np.dstack([(g * tint).clip(0, 255), a[..., 3]])
    return Image.fromarray(out.astype(np.uint8), "RGBA")
