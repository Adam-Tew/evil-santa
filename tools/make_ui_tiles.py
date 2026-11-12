"""Generate placeholder UI textures for the Evil Santa theme.

Writes seamless tiles into static/spirit/ui/:
  navbar.svg      Christmas-jumper knit band for the navigation bar
  meter.svg       pine-branch band behind the Christmas Spirit meter
  coal.svg        faceted coal texture for unsolved challenges
  wrap-0..7.svg   wrapping papers for solved challenges

Replace any of them with your own art (same name, e.g. wrap-3.webp) and set
"spirit_ui_ext" in the theme settings.

usage: python make_ui_tiles.py <theme>/static/spirit/ui
"""
import math
import random
import sys
from pathlib import Path


def svg(w, h, body):
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">{body}</svg>'


def star(cx, cy, r, fill):
    pts = []
    for i in range(10):
        a = math.pi / 5 * i - math.pi / 2
        rr = r if i % 2 == 0 else r * 0.45
        pts.append(f"{cx + rr * math.cos(a):.1f},{cy + rr * math.sin(a):.1f}")
    return f'<polygon points="{" ".join(pts)}" fill="{fill}"/>'


def snowflake(cx, cy, r, stroke):
    arms = []
    for i in range(6):
        a = math.pi / 3 * i
        x, y = cx + r * math.cos(a), cy + r * math.sin(a)
        arms.append(f'<line x1="{cx}" y1="{cy}" x2="{x:.1f}" y2="{y:.1f}"/>')
        for s in (-1, 1):
            bx, by = cx + r * .55 * math.cos(a), cy + r * .55 * math.sin(a)
            ex, ey = bx + r * .3 * math.cos(a + s * .8), by + r * .3 * math.sin(a + s * .8)
            arms.append(f'<line x1="{bx:.1f}" y1="{by:.1f}" x2="{ex:.1f}" y2="{ey:.1f}"/>')
    return f'<g stroke="{stroke}" stroke-width="2.4" stroke-linecap="round">{"".join(arms)}</g>'


def tree(cx, cy, s, fill):
    return (f'<path d="M{cx} {cy - 20*s} L{cx + 13*s} {cy + 2*s} H{cx - 13*s} Z M{cx} {cy - 10*s} L{cx + 17*s} {cy + 14*s} H{cx - 17*s} Z" fill="{fill}"/>'
            f'<rect x="{cx - 3*s}" y="{cy + 14*s}" width="{6*s}" height="{6*s}" fill="#6b4421"/>')


def holly(cx, cy, s):
    leaf = "#1f7a3a"
    return (f'<path d="M{cx} {cy} q{-10*s} {-12*s} {-22*s} {-4*s} q{8*s} {2*s} {6*s} {10*s} q{8*s} {-4*s} {16*s} {-6*s}Z" fill="{leaf}"/>'
            f'<path d="M{cx} {cy} q{10*s} {-12*s} {22*s} {-4*s} q{-8*s} {2*s} {-6*s} {10*s} q{-8*s} {-4*s} {-16*s} {-6*s}Z" fill="{leaf}"/>'
            f'<circle cx="{cx - 3*s}" cy="{cy + 2*s}" r="{4*s}" fill="#d7263d"/><circle cx="{cx + 4*s}" cy="{cy + 3*s}" r="{4*s}" fill="#d7263d"/>')


def wrap_tiles():
    T = 120
    tiles = []
    # 0 candy cane stripes
    stripes = "".join(f'<path d="M{x} 0 L{x + 20} 0 L{x + 20 - T} {T} L{x - T} {T} Z" fill="#e3263a"/>' for x in range(0, 2 * T + 1, 40))
    tiles.append(svg(T, T, f'<rect width="{T}" height="{T}" fill="#fff6f0"/>{stripes}'))
    # 1 green polka dots
    dots = "".join(f'<circle cx="{x}" cy="{y}" r="9" fill="#f4f1ea"/>' for x, y in [(0, 0), (T, 0), (0, T), (T, T), (60, 60), (30, 90), (90, 30)])
    tiles.append(svg(T, T, f'<rect width="{T}" height="{T}" fill="#1f8a4c"/>{dots}'))
    # 2 blue snowflakes
    flakes = snowflake(30, 30, 18, "#ffffff") + snowflake(90, 90, 18, "#ffffff") + snowflake(90, 30, 9, "#bfe3ff") + snowflake(30, 90, 9, "#bfe3ff")
    tiles.append(svg(T, T, f'<rect width="{T}" height="{T}" fill="#1f5fae"/>{flakes}'))
    # 3 red with gold stars
    stars = star(30, 32, 16, "#ffcf3f") + star(90, 90, 16, "#ffcf3f") + star(92, 26, 7, "#fff1b8") + star(26, 94, 7, "#fff1b8")
    tiles.append(svg(T, T, f'<rect width="{T}" height="{T}" fill="#c4182f"/>{stars}'))
    # 4 gold with green trees
    trees = tree(30, 40, 1.1, "#1f7a3a") + tree(90, 100, 1.1, "#1f7a3a") + f'<circle cx="90" cy="30" r="4" fill="#d7263d"/><circle cx="30" cy="96" r="4" fill="#d7263d"/>'
    tiles.append(svg(T, T, f'<rect width="{T}" height="{T}" fill="#f2c14e"/>{trees}'))
    # 5 tartan plaid
    plaid = (f'<rect width="{T}" height="{T}" fill="#a3132a"/>'
             f'<rect x="0" y="40" width="{T}" height="30" fill="#14532d" opacity=".85"/><rect x="40" y="0" width="30" height="{T}" fill="#14532d" opacity=".7"/>'
             f'<rect x="0" y="52" width="{T}" height="5" fill="#ffcf3f" opacity=".8"/><rect x="52" y="0" width="5" height="{T}" fill="#ffcf3f" opacity=".8"/>'
             f'<rect x="0" y="100" width="{T}" height="3" fill="#ffffff" opacity=".5"/><rect x="100" y="0" width="3" height="{T}" fill="#ffffff" opacity=".5"/>')
    tiles.append(svg(T, T, plaid))
    # 6 purple with silver baubles
    baubles = "".join(f'<circle cx="{x}" cy="{y}" r="{r}" fill="none" stroke="#d9d4ff" stroke-width="3"/><circle cx="{x}" cy="{y}" r="{r/3:.0f}" fill="#d9d4ff"/>'
                      for x, y, r in [(30, 30, 14), (90, 90, 14), (90, 30, 7), (30, 90, 7)])
    tiles.append(svg(T, T, f'<rect width="{T}" height="{T}" fill="#5b2a86"/>{baubles}'))
    # 7 kraft paper with holly
    kraft = f'<rect width="{T}" height="{T}" fill="#c89b6d"/>' + holly(32, 34, 1) + holly(90, 92, 1) + '<circle cx="92" cy="28" r="3" fill="#7a4b1e"/><circle cx="28" cy="96" r="3" fill="#7a4b1e"/>'
    tiles.append(svg(T, T, kraft))
    return tiles


def coal_tile():
    """Faceted coal: a jittered triangle mesh that wraps around the edges."""
    T, N = 160, 6
    step = T / N
    random.seed(42)
    jit = {}
    for i in range(N + 1):
        for j in range(N + 1):
            key = (i % N, j % N)
            if key not in jit:
                jit[key] = (random.uniform(-.3, .3) * step, random.uniform(-.3, .3) * step)
    pt = lambda i, j: (i * step + jit[(i % N, j % N)][0], j * step + jit[(i % N, j % N)][1])
    out = [f'<rect width="{T}" height="{T}" fill="#141416"/>']
    for i in range(N):
        for j in range(N):
            a, b, c, d = pt(i, j), pt(i + 1, j), pt(i + 1, j + 1), pt(i, j + 1)
            for tri in ((a, b, c), (a, c, d)):
                l = random.randint(16, 46)
                shine = random.random() < .12
                col = f"#{l+30:02x}{l+30:02x}{l+34:02x}" if shine else f"#{l:02x}{l:02x}{l+3:02x}"
                pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in tri)
                out.append(f'<polygon points="{pts}" fill="{col}" stroke="#0a0a0b" stroke-width=".6"/>')
    # a few glints
    for _ in range(8):
        x, y = random.uniform(0, T), random.uniform(0, T)
        out.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="1.2" fill="#9aa0aa" opacity=".7"/>')
    return svg(T, T, "".join(out))


def navbar_tile():
    """Christmas-jumper knit band, 240x64, repeats horizontally."""
    W, H = 240, 64
    red, white, green = "#b3142b", "#f4efe6", "#1f7a3a"
    out = [f'<rect width="{W}" height="{H}" fill="{red}"/>']
    # knit stitch texture
    for y in range(0, H, 6):
        for x in range(0, W, 6):
            out.append(f'<path d="M{x} {y} l3 5 l3 -5" stroke="#000" stroke-opacity=".12" fill="none"/>')
    # zigzag bands top and bottom
    for yy in (6, H - 10):
        zz = " ".join(f"{x},{yy + (0 if (x // 8) % 2 == 0 else 6)}" for x in range(0, W + 1, 8))
        out.append(f'<polyline points="{zz}" stroke="{white}" stroke-width="3" fill="none"/>')
    # middle motif: tree, snowflake, tree, snowflake
    for i, x in enumerate(range(30, W, 60)):
        if i % 2 == 0:
            out.append(tree(x, 30, .9, green))
        else:
            out.append(snowflake(x, 32, 10, white))
    return svg(W, H, "".join(out))


def meter_tile():
    """Pine branch band, 220x60, repeats horizontally."""
    W, H = 220, 60
    random.seed(7)
    out = [f'<rect width="{W}" height="{H}" fill="#123a22"/>']
    for _ in range(260):
        x, y = random.uniform(-10, W + 10), random.uniform(0, H)
        a = random.uniform(-.9, .9) + (0 if random.random() < .5 else math.pi)
        l = random.uniform(8, 16)
        g = random.choice(["#1f6b3a", "#2a8048", "#18542e", "#3a9a58"])
        out.append(f'<line x1="{x:.1f}" y1="{y:.1f}" x2="{x + l*math.cos(a):.1f}" y2="{y + l*math.sin(a)*.4:.1f}" stroke="{g}" stroke-width="2" stroke-linecap="round"/>')
    for x in (40, 150):
        out.append(f'<circle cx="{x}" cy="18" r="4" fill="#d7263d"/><circle cx="{x+7}" cy="22" r="4" fill="#d7263d"/><circle cx="{x+2}" cy="25" r="4" fill="#e23a50"/>')
    for x in (95, 200):
        out.append(f'<path d="M{x} 40 l4 -6 l4 6 l-4 6z" fill="#ffcf3f" opacity=".8"/>')
    return svg(W, H, "".join(out))


if __name__ == "__main__":
    out = Path(sys.argv[1])
    out.mkdir(parents=True, exist_ok=True)
    for i, t in enumerate(wrap_tiles()):
        (out / f"wrap-{i}.svg").write_text(t)
    (out / "coal.svg").write_text(coal_tile())
    (out / "navbar.svg").write_text(navbar_tile())
    (out / "meter.svg").write_text(meter_tile())
    print("wrote UI tiles to", out)
