"""Render the lock-screen wallpaper and check that its QR code decodes to the contact page.

Usage: wallpaper.py <width> <height> <fonts-dir> [out.png]
iPhone layout: top 35 % left free for the clock, bottom 12 % for flashlight and camera.
"""
import sys
from pathlib import Path

import segno
from PIL import Image, ImageDraw, ImageFont
from pyzbar.pyzbar import decode

URL = "https://a-jl.github.io/kontakt/"
NAME = "Adrian Jean-Ludwig Leutner"
ROLE = ("Co-Founder · ", "Spayz AG")
BG, ACCENT, TEXT, MUTED = "#081522", "#FF743D", "#F5F2EC", "#9AA7B4"

W, H, fonts = int(sys.argv[1]), int(sys.argv[2]), Path(sys.argv[3])
out = sys.argv[4] if len(sys.argv) > 4 else f"wallpaper-{W}x{H}.png"

img = Image.new("RGB", (W, H), BG)
d = ImageDraw.Draw(img)

top, bottom = int(H * 0.35), int(H * 0.88)
qr_w = W // 2
card_pad = qr_w // 14

# Name: largest size that fits 86 % of the width, capped.
size = int(W * 0.075)
while True:
    f_name = ImageFont.truetype(str(fonts / "Poppins-Bold.ttf"), size)
    if d.textlength(NAME, font=f_name) <= W * 0.86:
        break
    size -= 2
f_role = ImageFont.truetype(str(fonts / "Poppins-Medium.ttf"), int(size * 0.62))

name_h = f_name.getbbox(NAME)[3]
role_h = f_role.getbbox("Ag")[3]
rule_h, gap = max(6, W // 200), int(H * 0.018)
card = qr_w + 2 * card_pad
block = rule_h + gap + name_h + gap // 2 + role_h + 2 * gap + card
y = top + (bottom - top - block) // 2

rule_w = W // 12
d.rounded_rectangle([(W - rule_w) // 2, y, (W + rule_w) // 2, y + rule_h], radius=rule_h // 2, fill=ACCENT)
y += rule_h + gap
d.text((W / 2, y), NAME, font=f_name, fill=TEXT, anchor="mt")
y += name_h + gap // 2
role_w = d.textlength(ROLE[0] + ROLE[1], font=f_role)
x = (W - role_w) / 2
d.text((x, y), ROLE[0], font=f_role, fill=MUTED)
d.text((x + d.textlength(ROLE[0], font=f_role), y), ROLE[1], font=f_role, fill=ACCENT)
y += role_h + 2 * gap

# White card with the QR code, dark modules, quiet zone inside the card.
cx = (W - card) // 2
d.rounded_rectangle([cx, y, cx + card, y + card], radius=card // 12, fill="#FFFFFF", outline=ACCENT, width=max(4, W // 250))
qr = segno.make(URL, error="m")
modules = qr.symbol_size(border=0)[0]
scale = qr_w // modules
tmp = Path(out).with_suffix(".qr.png")
qr.save(tmp, scale=scale, border=0, dark=BG, light="#FFFFFF")
qr_img = Image.open(tmp).convert("RGB")
tmp.unlink()
off = (card - qr_img.width) // 2
img.paste(qr_img, (cx + off, y + off))

img.save(out)

# Read the code back, full size and scaled down.
for f in (1, 0.5, 0.25):
    test = img if f == 1 else img.resize((int(W * f), int(H * f)), Image.LANCZOS)
    got = [r.data.decode() for r in decode(test)]
    assert got == [URL], f"scale {f}: decoded {got}"
    print(f"scale {f}: {got[0]}")
print(f"wrote {out} ({W}x{H}), content {top}..{bottom}px, card {card}px")
