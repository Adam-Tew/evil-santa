"""Generate placeholder stage scenes for the Evil Santa CTFd theme.

Each scene is a simple, flat SVG that mirrors the intended composition:
kids + converted allies on the LEFT, evil forces on the RIGHT, colour
returning as the stage rises. Replace with final art of the same name.

usage: python make_placeholders.py <output_dir>
"""
import math
import random
import sys
from pathlib import Path

W, H = 1600, 900
STAGES = [
    (0, "town", "A Coal-Black Christmas"),
    (10, "town", "A Spark in the Snow"),
    (20, "road", "The Brave Brigade"),
    (30, "road", "Cookies for the Scouts"),
    (40, "gate", "The Coal Gate"),
    (50, "gate", "Gumdrop Breach"),
    (60, "hall", "The Hall of Antlers"),
    (70, "throne", "The Throne Room"),
    (80, "throne", "The Spirit Strikes"),
    (90, "square", "Christmas Is Saved!"),
    (100, "multiverse", "The Multiverse Milk & Cookies Club"),
]


def mix(a, b, t):
    a = [int(a[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(b[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(x + (y - x) * t):02x}" for x, y in zip(a, b))


def grey(c, t):
    """Desaturate colour c by (1-t)."""
    r, g, b = (int(c[i:i + 2], 16) for i in (1, 3, 5))
    l = round(0.3 * r + 0.59 * g + 0.11 * b)
    return mix(f"#{l:02x}{l:02x}{l:02x}", c, t)


# ---------- figures ----------
def kid(x, y, t, shirt, weapon, s=1.0):
    skin = grey("#f2c9a0", max(t, .6))
    p = [f'<g transform="translate({x} {y}) scale({s})">',
         f'<rect x="-16" y="-55" width="32" height="48" rx="12" fill="{grey(shirt, max(t,.5))}"/>',
         f'<rect x="-13" y="-10" width="10" height="22" rx="4" fill="#2d2f3a"/><rect x="3" y="-10" width="10" height="22" rx="4" fill="#2d2f3a"/>',
         f'<circle cx="0" cy="-74" r="20" fill="{skin}"/>',
         f'<path d="M-20 -80 Q0 -108 20 -80 Z" fill="{grey("#c0392b", max(t,.5))}"/><circle cx="0" cy="-104" r="5" fill="#fff"/>',
         '<circle cx="-7" cy="-74" r="2.5" fill="#222"/><circle cx="7" cy="-74" r="2.5" fill="#222"/>',
         '<path d="M-7 -65 Q0 -59 7 -65" stroke="#222" stroke-width="2.5" fill="none"/>']
    if weapon == "cane":
        p.append('<g transform="translate(18 -40) rotate(30)"><path d="M0 0 V-60 A12 12 0 0 1 24 -60" stroke="#fff" stroke-width="7" fill="none" stroke-linecap="round"/>'
                 '<path d="M0 0 V-60 A12 12 0 0 1 24 -60" stroke="#e3263a" stroke-width="7" fill="none" stroke-dasharray="7 7" stroke-linecap="round"/></g>')
    elif weapon == "star":
        p.append('<g transform="translate(26 -50)"><path d="M0 -14 L4 -4 L14 -4 L6 3 L9 13 L0 7 L-9 13 L-6 3 L-14 -4 L-4 -4Z" fill="#c98a4b" stroke="#7a4b1e" stroke-width="2"/></g>')
    elif weapon == "toy":
        p.append('<g transform="translate(26 -78)"><circle r="16" fill="#ffd447"/><circle r="9" fill="#e3263a"/><circle r="4" fill="#fff"/></g>')
    p.append("</g>")
    return "".join(p)


def elf(x, y, good, t, s=1.0, flip=False):
    body = "#1f9d55" if good else "#3a3b40"
    hat = "#d7263d" if good else "#26272b"
    face = "#f5d0a9" if good else "#a7a9ad"
    mouth = '<path d="M-6 -50 Q0 -44 6 -50" stroke="#222" stroke-width="2" fill="none"/>' if good else '<path d="M-6 -46 Q0 -52 6 -46" stroke="#222" stroke-width="2" fill="none"/>'
    brows = "" if good else '<path d="M-10 -64 L-3 -60 M10 -64 L3 -60" stroke="#111" stroke-width="2.5"/>'
    weapon = "" if good else '<rect x="16" y="-70" width="6" height="60" rx="2" fill="#4b3a2a" transform="rotate(20 19 -40)"/>'
    sc = f"scale({-s if flip else s} {s})"
    return (f'<g transform="translate({x} {y}) {sc}">'
            f'<path d="M-16 0 L-12 -40 H12 L16 0 Z" fill="{body}"/>'
            f'<circle cx="0" cy="-56" r="15" fill="{face}"/>'
            f'<path d="M-15 -62 L0 -100 L15 -62 Z" fill="{hat}"/><circle cx="0" cy="-100" r="4" fill="{"#fff" if good else "#555"}"/>'
            f'<path d="M-15 -58 L-24 -66 L-14 -52 Z M15 -58 L24 -66 L14 -52 Z" fill="{face}"/>'
            f'<circle cx="-5" cy="-57" r="2" fill="#111"/><circle cx="5" cy="-57" r="2" fill="#111"/>{brows}{mouth}{weapon}</g>')


def reindeer(x, y, good, s=1.0, nose=False):
    body = "#8b5a2b" if good else "#3b3c40"
    n = "#ff2b2b" if (good and nose) else ("#111" if not nose else "#552222")
    eye = "#111" if good else "#ff5555"
    return (f'<g transform="translate({x} {y}) scale({s})">'
            f'<ellipse cx="0" cy="-40" rx="46" ry="22" fill="{body}"/>'
            f'<rect x="-36" y="-26" width="8" height="30" fill="{body}"/><rect x="26" y="-26" width="8" height="30" fill="{body}"/>'
            f'<ellipse cx="-50" cy="-70" rx="16" ry="14" fill="{body}"/>'
            f'<path d="M-56 -82 L-66 -112 M-62 -100 L-76 -104 M-46 -82 L-38 -112 M-41 -100 L-28 -106" stroke="{("#d9c39a" if good else "#1d1e21")}" stroke-width="4" stroke-linecap="round"/>'
            f'<circle cx="-64" cy="-66" r="6" fill="{n}"/><circle cx="-48" cy="-74" r="2.5" fill="{eye}"/></g>')


def santa(x, y, good, s=1.0, sitting=False):
    coat = "#d7263d" if good else "#2b2c31"
    trim = "#ffffff" if good else "#5d5f66"
    face = "#f5cfa7" if good else "#9c9ea3"
    mouth = '<path d="M-14 -128 Q0 -114 14 -128" stroke="#222" stroke-width="3" fill="none"/>' if good else '<path d="M-14 -120 Q0 -132 14 -120" stroke="#222" stroke-width="3" fill="none"/>'
    brows = "" if good else '<path d="M-20 -158 L-6 -150 M20 -158 L6 -150" stroke="#111" stroke-width="4"/>'
    return (f'<g transform="translate({x} {y}) scale({s})">'
            f'<ellipse cx="0" cy="-60" rx="62" ry="66" fill="{coat}"/>'
            f'<rect x="-62" y="-70" width="124" height="14" fill="{"#222" if good else "#111"}"/><rect x="-10" y="-72" width="20" height="18" fill="{"#ffd447" if good else "#444"}"/>'
            f'<circle cx="0" cy="-145" r="32" fill="{face}"/>'
            f'<path d="M-32 -140 Q0 -70 32 -140 Q0 -120 -32 -140Z" fill="{trim}"/>'
            f'<path d="M-34 -160 Q0 -220 40 -170 L34 -158 Z" fill="{coat}"/><rect x="-36" y="-166" width="72" height="12" rx="6" fill="{trim}"/><circle cx="44" cy="-176" r="9" fill="{trim}"/>'
            f'<circle cx="-11" cy="-148" r="3.5" fill="#111"/><circle cx="11" cy="-148" r="3.5" fill="#111"/>{brows}{mouth}</g>')


def present(x, y, w, h, c, ribbon, t):
    return (f'<g><rect x="{x}" y="{y-h}" width="{w}" height="{h}" fill="{grey(c, t)}" rx="3"/>'
            f'<rect x="{x + w/2 - 5}" y="{y-h}" width="10" height="{h}" fill="{grey(ribbon, t)}"/>'
            f'<rect x="{x}" y="{y-h/2-5}" width="{w}" height="10" fill="{grey(ribbon, t)}"/></g>')


def castle(x, y, s, t):
    stone = mix("#2a2b30", "#5a4f6e", t * .6)
    win = "#ffcf3f" if t > .5 else "#551111"
    parts = [f'<g transform="translate({x} {y}) scale({s})" opacity=".95">',
             f'<rect x="-120" y="-200" width="240" height="200" fill="{stone}"/>']
    for tx in (-160, 120):
        parts.append(f'<rect x="{tx}" y="-300" width="40" height="300" fill="{stone}"/><path d="M{tx-10} -300 L{tx+20} -360 L{tx+50} -300Z" fill="{mix("#18191c", "#7a1f2b", t)}"/>')
    parts.append(f'<rect x="-40" y="-380" width="80" height="180" fill="{stone}"/><path d="M-55 -380 L0 -460 L55 -380Z" fill="{mix("#18191c", "#7a1f2b", t)}"/>')
    for i in range(-110, 120, 40):
        parts.append(f'<rect x="{i}" y="-216" width="22" height="16" fill="{stone}"/>')
    parts.append(f'<rect x="-14" y="-340" width="28" height="40" rx="14" fill="{win}"/>')
    parts.append('<path d="M-40 0 V-90 A40 40 0 0 1 40 -90 V0Z" fill="#111"/></g>')
    return "".join(parts)


def house(x, y, w, h, t, lit):
    wall = grey("#b5654a", t)
    roof = grey("#5b2a1e", t)
    windows = "#ffcf3f" if lit else "#2a2b2f"
    out = [f'<rect x="{x}" y="{y-h}" width="{w}" height="{h}" fill="{wall}"/>',
           f'<path d="M{x-12} {y-h} L{x+w/2} {y-h-70} L{x+w+12} {y-h}Z" fill="{roof}"/>',
           f'<path d="M{x-12} {y-h} L{x+w/2} {y-h-70} L{x+w+12} {y-h}" stroke="#f4f6f8" stroke-width="7" fill="none"/>',
           f'<rect x="{x+18}" y="{y-h+30}" width="30" height="30" fill="{windows}"/><rect x="{x+w-48}" y="{y-h+30}" width="30" height="30" fill="{windows}"/>']
    if lit:
        cols = ["#ff3b3b", "#ffd447", "#3ddc6b", "#4cc3ff"]
        for i in range(9):
            px = x - 8 + (w + 16) * i / 8
            out.append(f'<circle cx="{px:.0f}" cy="{y-h+6}" r="5" fill="{cols[i%4]}"/>')
    return "".join(out)


def tree(x, y, s, t, lit):
    g = mix("#3a3c3f", "#1f7a3a", t)
    parts = [f'<g transform="translate({x} {y}) scale({s})"><rect x="-10" y="-30" width="20" height="30" fill="#4b3a2a"/>']
    for i, (w, yy) in enumerate([(90, -30), (70, -90), (50, -145)]):
        parts.append(f'<path d="M{-w} {yy} L0 {yy-90} L{w} {yy}Z" fill="{g}"/>')
    if lit:
        cols = ["#ff3b3b", "#ffd447", "#4cc3ff", "#ff8ad8"]
        random.seed(int(x))
        for i in range(16):
            parts.append(f'<circle cx="{random.randint(-60,60)}" cy="{random.randint(-200,-40)}" r="6" fill="{cols[i%4]}"/>')
        parts.append('<path d="M0 -258 L8 -238 L28 -238 L12 -226 L18 -206 L0 -218 L-18 -206 L-12 -226 L-28 -238 L-8 -238Z" fill="#ffd447"/>')
    else:
        parts.append('<path d="M0 -258 L8 -238 L28 -238 L12 -226 L18 -206 L0 -218 L-18 -206 L-12 -226 L-28 -238 L-8 -238Z" fill="#3a3b3f"/>')
    parts.append("</g>")
    return "".join(parts)


def snow(t, n=120, seed=1):
    random.seed(seed)
    return "".join(f'<circle cx="{random.randint(0,W)}" cy="{random.randint(0,H)}" r="{random.uniform(1.5,4):.1f}" fill="#fff" opacity="{random.uniform(.3,.9):.2f}"/>' for _ in range(n))


def cookie_shot(x1, y1, x2, y2):
    return (f'<path d="M{x1} {y1} Q{(x1+x2)/2} {min(y1,y2)-120} {x2} {y2}" stroke="#ffd447" stroke-width="3" stroke-dasharray="4 10" fill="none" opacity=".8"/>'
            f'<circle cx="{x2}" cy="{y2}" r="12" fill="#c98a4b" stroke="#7a4b1e" stroke-width="2"/>')


def sparkle(x, y, r=40):
    return (f'<g transform="translate({x} {y})" opacity=".9">'
            f'<path d="M0 {-r} L{r*.15} {-r*.15} L{r} 0 L{r*.15} {r*.15} L0 {r} L{-r*.15} {r*.15} L{-r} 0 L{-r*.15} {-r*.15}Z" fill="#fff6c8"/></g>')


# ---------- scenes ----------
def scene(at, place, title):
    t = min(1.0, at / 90)
    sky_top = mix("#0b0c0f", "#0f2350", t)
    sky_bot = mix("#2a2b30", "#4b3a78", t)
    ground = mix("#6d7075", "#eef3f8", t)
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" preserveAspectRatio="xMidYMax slice">',
         f'<defs><linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{sky_top}"/><stop offset="1" stop-color="{sky_bot}"/></linearGradient>'
         f'<linearGradient id="hope" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#ffcf3f" stop-opacity="{.35*t+.08:.2f}"/><stop offset=".55" stop-color="#ffcf3f" stop-opacity="0"/></linearGradient></defs>']
    indoor = place in ("hall", "throne")
    if indoor:
        wall = mix("#1a1b1f", "#3b1f2e", t)
        s.append(f'<rect width="{W}" height="{H}" fill="{wall}"/>')
        for px in range(80, W, 260):
            s.append(f'<rect x="{px}" y="0" width="70" height="{H}" fill="{mix("#24252a", "#4a2a3a", t)}"/>')
        s.append(f'<rect y="{H-160}" width="{W}" height="160" fill="{mix("#2b2c30", "#6b1d2a", t)}"/>')
    else:
        s.append(f'<rect width="{W}" height="{H}" fill="url(#sky)"/>')
        s.append(f'<circle cx="1380" cy="140" r="60" fill="{mix("#5a5c60", "#fdf6d8", t)}"/>')
        s.append(f'<path d="M0 {H-200} Q400 {H-280} 800 {H-210} T1600 {H-230} V{H} H0Z" fill="{mix("#3a3c40", "#c9d6e6", t)}"/>')
        s.append(f'<rect y="{H-150}" width="{W}" height="150" fill="{ground}"/>')
    s.append(f'<rect width="{W}" height="{H}" fill="url(#hope)"/>')

    gy = H - 70  # ground line for characters
    kids_weapons = ["cane", "star", "cane", "star", "toy"]
    shirts = ["#2e86de", "#16a085", "#8e44ad", "#e67e22", "#e84393"]

    if place == "town":
        s.append(castle(1300, H - 230, .55, t))
        for i, hx in enumerate((120, 360, 1020)):
            s.append(house(hx, H - 150, 170, 150, t, False))
        s.append(tree(800, H - 150, 1.0, t, False))
        # sad families holding coal
        random.seed(3)
        for i in range(9):
            x = 260 + i * 110
            s.append(f'<g transform="translate({x} {gy})"><rect x="-14" y="-60" width="28" height="60" rx="10" fill="{grey("#555566", 0)}"/>'
                     f'<circle cx="0" cy="-74" r="15" fill="#9a9a9a"/><path d="M-6 -66 Q0 -72 6 -66" stroke="#222" stroke-width="2" fill="none"/>'
                     f'<circle cx="18" cy="-34" r="7" fill="#111"/></g>')
        if at >= 10:
            s.append(kid(170, gy, t, shirts[0], "cane", 1.1))
            s.append(sparkle(200, gy - 150, 34))
    elif place == "road":
        s.append(castle(1250, H - 200, .8, t))
        n_kids = 4 if at == 20 else 5
        for i in range(n_kids):
            s.append(kid(120 + i * 90, gy - (i % 2) * 18, t, shirts[i], kids_weapons[i], 1.15))
        # gumdrop cannon
        s.append(f'<g transform="translate({110 + n_kids*90} {gy})"><rect x="-40" y="-40" width="90" height="34" rx="16" fill="#e84393" transform="rotate(-15)"/>'
                 '<circle cx="-20" cy="-6" r="16" fill="#6c3a1e"/><circle cx="30" cy="-6" r="16" fill="#6c3a1e"/></g>')
        if at >= 30:
            s.append(elf(700, gy, True, t, 1.1))
            s.append(cookie_shot(390, gy - 120, 960, gy - 50))
            for i in range(3):
                s.append(elf(1000 + i * 120, gy, False, t, 1.1))
        else:
            for i in range(3):
                s.append(elf(1300 + i * 90, gy - 150, False, t, .55))
    elif place == "gate":
        wall = mix("#2a2b30", "#5a4f6e", t * .6)
        s.append(f'<rect x="900" y="120" width="700" height="{H-190}" fill="{wall}"/>')
        for bx in range(900, 1600, 60):
            s.append(f'<rect x="{bx}" y="90" width="36" height="34" fill="{wall}"/>')
        if at >= 50:
            s.append('<path d="M1080 830 L1080 520 Q1180 430 1300 520 L1300 830Z" fill="#0b0b0d"/>')
            random.seed(5)
            cols = ["#ff3b3b", "#ffd447", "#3ddc6b", "#4cc3ff", "#ff8ad8"]
            for i in range(40):
                s.append(f'<circle cx="{random.randint(1000,1400)}" cy="{random.randint(380,800)}" r="{random.randint(6,14)}" fill="{cols[i%5]}"/>')
        else:
            s.append(f'<path d="M1080 830 L1080 520 Q1190 430 1300 520 L1300 830Z" fill="#3b2a1e" stroke="#111" stroke-width="8"/>')
        for i in range(4):
            s.append(elf(980 + i * 160, 125, False, t, .7))
            s.append(f'<rect x="{995 + i*160}" y="70" width="46" height="18" rx="8" fill="#111"/>')
        for i in range(5):
            s.append(kid(100 + i * 90, gy - (i % 2) * 16, t, shirts[i], kids_weapons[i], 1.1))
        s.append('<g transform="translate(600 820)"><rect x="-50" y="-50" width="120" height="44" rx="20" fill="#e84393" transform="rotate(-20)"/>'
                 '<circle cx="-20" cy="-6" r="20" fill="#6c3a1e"/><circle cx="40" cy="-6" r="20" fill="#6c3a1e"/></g>')
        if at >= 50:
            for i in range(3):
                s.append(elf(760 + i * 70, gy, True, t, .95))
            s.append(cookie_shot(320, gy - 120, 1450, gy - 40))
            s.append(elf(1450, gy, False, t, 1.0))
    elif place == "hall":
        for i in range(5):
            s.append(kid(100 + i * 85, gy - (i % 2) * 16, t, shirts[i], kids_weapons[i], 1.1))
        for i in range(4):
            s.append(elf(560 + i * 60, gy, True, t, .9))
        s.append(reindeer(860, gy, True, 1.1))
        s.append(f'<path d="M520 {gy-150} Q700 {gy-260} 840 {gy-110}" stroke="#ffd447" stroke-width="5" fill="none" stroke-dasharray="2 6"/>')
        for i in range(3):
            s.append(reindeer(1150 + i * 150, gy, False, 1.1))
    elif place == "throne":
        # throne + dark hoard
        random.seed(7)
        for i in range(30):
            x = random.randint(1040, 1580); y = random.randint(470, 760)
            s.append(present(x, y, random.randint(40, 80), random.randint(40, 70), "#d7263d" if at >= 80 and i % 3 == 0 else "#2a2b30", "#4a4b50", t if at >= 80 else 0))
        s.append(f'<path d="M1180 {gy} V420 Q1290 330 1400 420 V{gy}Z" fill="{mix("#111214", "#7a1f2b", t*.7)}"/>')
        good = at >= 80
        s.append(santa(1290, gy, good, 1.25))
        s.append(reindeer(1520, gy, good, 1.0, nose=True))
        for i in range(5):
            s.append(kid(100 + i * 85, gy - (i % 2) * 16, t, shirts[i], kids_weapons[i], 1.1))
        for i in range(4):
            s.append(elf(560 + i * 60, gy, True, t, .9))
        s.append(reindeer(860, gy, True, 1.0))
        if good:
            s.append(sparkle(1290, gy - 200, 140))
            s.append(cookie_shot(470, gy - 140, 1290, gy - 210).replace("#c98a4b", "#ffd447"))
        else:
            for i in range(2):
                s.append(elf(1000 + i * 90, gy, False, t, .95))
    elif place in ("square", "multiverse"):
        for hx in (60, 1360):
            s.append(house(hx, H - 150, 190, 150, 1, True))
        s.append(tree(800, H - 140, 1.4, 1, True))
        random.seed(11)
        for i in range(10):
            s.append(present(620 + i * 34, H - 120, 30, 26, ["#d7263d", "#1f9d55", "#2e86de", "#ffd447"][i % 4], "#ffffff", 1))
        if place == "square":
            s.append(santa(1060, gy, True, 1.1))
            s.append(f'<g transform="translate(1180 {gy})"><path d="M-36 0 Q-30 -110 0 -110 Q30 -110 36 0Z" fill="#d7263d"/><circle cx="0" cy="-128" r="22" fill="#f5cfa7"/>'
                     '<path d="M-22 -136 Q0 -165 22 -136" fill="#dcdcdc"/><path d="M-36 0 H36" stroke="#fff" stroke-width="10"/></g>')
            s.append(reindeer(1300, gy, True, 1.0, nose=True))
            for i in range(5):
                s.append(kid(120 + i * 90, gy - (i % 2) * 16, 1, shirts[i], "", 1.1))
            for i in range(3):
                s.append(elf(940 + i * 50, gy - 160, True, 1, .7))
        else:
            # table of Santas from across the multiverse
            s.append(f'<rect x="300" y="{gy-90}" width="1000" height="20" rx="8" fill="#8b5a2b"/><rect x="330" y="{gy-70}" width="16" height="70" fill="#6b4421"/><rect x="1254" y="{gy-70}" width="16" height="70" fill="#6b4421"/>')
            looks = [("#d7263d", "#fff"), ("#00f0ff", "#ff2bd6"), ("#2e7d32", "#ffd447"), ("#6a1b9a", "#e1bee7"), ("#ff9800", "#fff")]
            for i, (coat, trim) in enumerate(looks):
                x = 420 + i * 190
                svg = santa(x, gy - 90, True, .8)
                svg = svg.replace("#d7263d", coat).replace('fill="#ffffff"', f'fill="{trim}"')
                if i == 1:  # cyber santa visor
                    svg = svg.replace("</g>", f'<rect x="-34" y="-162" width="68" height="14" rx="4" fill="#ff2bd6"/></g>', 1)
                s.append(svg)
                s.append(f'<rect x="{x+38}" y="{gy-130}" width="18" height="34" rx="3" fill="#fff"/><circle cx="{x-50}" cy="{gy-100}" r="11" fill="#c98a4b"/>')
            s.append(f'<text x="800" y="120" text-anchor="middle" font-family="sans-serif" font-size="44" fill="#ffd447" font-weight="bold">★ Multiverse Milk &amp; Cookies Club ★</text>')

    s.append(snow(t, 110, seed=at + 1))
    s.append("</svg>")
    return "\n".join(s)


if __name__ == "__main__":
    out = Path(sys.argv[1])
    out.mkdir(parents=True, exist_ok=True)
    for at, place, title in STAGES:
        (out / f"stage-{at:03d}.svg").write_text(scene(at, place, title))
    print("wrote", len(STAGES), "scenes to", out)
