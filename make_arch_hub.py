from PIL import Image, ImageDraw, ImageFont
import math

w, h = 1000, 520
canvas = Image.new('RGBA', (w, h), (255, 255, 255, 0))
draw = ImageDraw.Draw(canvas)

try:
    font_main = ImageFont.truetype('arialbd.ttf', 20)
    font_sub = ImageFont.truetype('arial.ttf', 14)
except:
    font_main = font_sub = None

cx, cy = w // 2, h // 2

# Draw dashed bounding rectangle
draw.rounded_rectangle((10, 10, w - 10, h - 10), radius=16, outline=(100, 116, 139, 255), width=2)

badge = Image.open('sih26102_badge.png').resize((130, 130), Image.Resampling.LANCZOS)
bw, bh = badge.size

capsules = [
    # (dx, dy, title, sub, bg_color, border_color)
    (-260, -140, "1. MoSPI Data Ingestion", "105,000 Authenticated Works", (239, 246, 255, 255), (59, 130, 246, 255)),
    (260, -140, "2. Dual Hybrid ML", "Isolation Forest + LOF + PCA", (240, 253, 244, 255), (34, 197, 94, 255)),
    (290, 0, "3. 5 Codified CAG Rules", "GFR 149 & 45-Day Sanction SLA", (255, 247, 237, 255), (249, 115, 22, 255)),
    (260, 140, "4. Official CAG Dossier", "One-Click Formatted Dossier", (238, 242, 255, 255), (79, 70, 229, 255)),
    (-260, 140, "5. Officer Case Queue", "Under Review / Inspection / Pass", (254, 252, 232, 255), (234, 179, 8, 255)),
    (-290, 0, "6. Temporal Forensics", "'March Rush' & Dormancy Radar", (250, 245, 255, 255), (168, 85, 247, 255))
]

for dx, dy, title, sub, bg_c, b_c in capsules:
    nx, ny = cx + dx, cy + dy
    # Connecting line to center
    draw.line([(cx, cy), (nx, ny)], fill=b_c, width=3)
    
    # Capsule rounded box
    cw, ch = 270, 60
    x1, y1 = nx - cw // 2, ny - ch // 2
    x2, y2 = nx + cw // 2, ny + ch // 2
    draw.rounded_rectangle((x1, y1, x2, y2), radius=14, fill=bg_c, outline=b_c, width=3)
    
    if font_main:
        tb = draw.textbbox((0, 0), title, font=font_main)
        draw.text((nx - (tb[2] - tb[0]) // 2, y1 + 10), title, fill=(15, 23, 42, 255), font=font_main)
    if font_sub:
        sb = draw.textbbox((0, 0), sub, font=font_sub)
        draw.text((nx - (sb[2] - sb[0]) // 2, y1 + 34), sub, fill=(71, 85, 105, 255), font=font_sub)

# Center badge
draw.ellipse((cx - bw//2 - 6, cy - bh//2 - 6, cx + bw//2 + 6, cy + bh//2 + 6), fill=(15, 23, 42, 255), outline=(56, 189, 248, 255), width=4)
canvas.paste(badge, (cx - bw // 2, cy - bh // 2), badge)

canvas.save('arch_hub.png')
print('SUCCESS: Created arch_hub.png')
