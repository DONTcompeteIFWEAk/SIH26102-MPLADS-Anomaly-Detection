from PIL import Image, ImageDraw, ImageFont
import math

w, h = 1000, 650
canvas = Image.new('RGBA', (w, h), (255, 255, 255, 0))
draw = ImageDraw.Draw(canvas)

try:
    font_pill = ImageFont.truetype('arialbd.ttf', 20)
    font_sub = ImageFont.truetype('arial.ttf', 14)
except:
    font_pill = font_sub = None

cx, cy = w // 2, h // 2

# Center badge
badge = Image.open('sih26102_badge.png').resize((130, 130), Image.Resampling.LANCZOS)
bw, bh = badge.size

tech_nodes = [
    (0, -220, "Python 3.12", "AI / ML Core Engine"),
    (240, -170, "Scikit-Learn", "IF 45% • LOF 35% • PCA 20%"),
    (320, 0, "FastAPI", "Async High-Throughput REST"),
    (240, 170, "PostgreSQL 16", "105,000 Works Database"),
    (0, 220, "React 18 & Vite", "Responsive SPA Dashboard"),
    (-240, 170, "Leaflet GIS", "All-India Heatmap Radar"),
    (-320, 0, "Recharts", "Dynamic Data Analytics"),
    (-240, -170, "Bilingual NLP", "Hindi + English Legal Directives")
]

for dx, dy, title, desc in tech_nodes:
    nx, ny = cx + dx, cy + dy
    # Draw arrow line from center to node
    # line start at border of center circle (radius 75)
    angle = math.atan2(dy, dx)
    sx = cx + int(75 * math.cos(angle))
    sy = cy + int(75 * math.sin(angle))
    
    ex = nx - int(70 * math.cos(angle))
    ey = ny - int(30 * math.sin(angle))
    
    draw.line([(sx, sy), (ex, ey)], fill=(30, 41, 59, 255), width=3)
    # arrow head at (ex, ey)
    arrow_len = 12
    a1 = angle + math.pi - 0.35
    a2 = angle + math.pi + 0.35
    draw.polygon([
        (ex, ey),
        (ex + int(arrow_len * math.cos(a1)), ey + int(arrow_len * math.sin(a1))),
        (ex + int(arrow_len * math.cos(a2)), ey + int(arrow_len * math.sin(a2)))
    ], fill=(30, 41, 59, 255))
    
    # Draw pill box
    pw, ph = 210, 52
    px1, py1 = nx - pw // 2, ny - ph // 2
    px2, py2 = nx + pw // 2, ny + ph // 2
    draw.rounded_rectangle((px1, py1, px2, py2), radius=10, fill=(255, 255, 255, 255), outline=(15, 23, 42, 255), width=2)
    
    if font_pill:
        tb = draw.textbbox((0, 0), title, font=font_pill)
        tw = tb[2] - tb[0]
        draw.text((nx - tw // 2, py1 + 8), title, fill=(15, 23, 42, 255), font=font_pill)
    if font_sub:
        sb = draw.textbbox((0, 0), desc, font=font_sub)
        sw = sb[2] - sb[0]
        draw.text((nx - sw // 2, py1 + 30), desc, fill=(71, 85, 105, 255), font=font_sub)

# Draw center badge with glowing ring
draw.ellipse((cx - bw//2 - 6, cy - bh//2 - 6, cx + bw//2 + 6, cy + bh//2 + 6), fill=(15, 23, 42, 255), outline=(56, 189, 248, 255), width=3)
canvas.paste(badge, (cx - bw // 2, cy - bh // 2), badge)

canvas.save('tech_stack_hub.png')
print('SUCCESS: Created tech_stack_hub.png')
