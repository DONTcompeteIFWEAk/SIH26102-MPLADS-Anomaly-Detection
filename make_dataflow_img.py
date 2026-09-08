from PIL import Image, ImageDraw, ImageFont

w, h = 1800, 1060
canvas = Image.new('RGBA', (w, h), (255, 255, 255, 255))
draw = ImageDraw.Draw(canvas)

try:
    font_lg = ImageFont.truetype('arialbd.ttf', 30)
    font_md = ImageFont.truetype('arialbd.ttf', 24)
    font_sm = ImageFont.truetype('arialbd.ttf', 20)
except:
    font_lg = font_md = font_sm = None

def draw_pill(box, fill_c, text, font, border_c=None):
    draw.rounded_rectangle(box, radius=12, fill=fill_c, outline=border_c, width=2)
    if font:
        bbox = draw.textbbox((0, 0), text, font=font)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        tx = box[0] + (box[2] - box[0] - tw) / 2
        ty = box[1] + (box[3] - box[1] - th) / 2
        draw.text((tx, ty), text, fill=(255, 255, 255, 255), font=font)

def draw_arrow_down(x, y1, y2, color=(30, 41, 59, 255)):
    draw.line([(x, y1), (x, y2)], fill=color, width=4)
    draw.polygon([(x, y2 + 8), (x - 8, y2 - 4), (x + 8, y2 - 4)], fill=color)

# 1. MoSPI Box
draw_pill((620, 20, 1180, 85), (21, 101, 192, 255), 'MoSPI e-SAKSHI Portal Data (2019-2024)', font_md)
draw_arrow_down(900, 85, 120)

# 2. Cleaning Box
draw_pill((550, 130, 1250, 195), (25, 118, 210, 255), 'Cleaning, Deduplication & NLP Standardization', font_md)

# Branch arrows from Cleaning to 4 Features
draw.line([(900, 195), (900, 225)], fill=(30, 41, 59, 255), width=4)
draw.line([(220, 225), (1580, 225)], fill=(30, 41, 59, 255), width=4)

feat_xs = [220, 670, 1130, 1580]
feat_labels = [
    'Constituency Cost-Per-Unit\nMedian Baseline',
    'GFR Rule 149 Cost Splitting\nProximity Flag',
    'Spatial / Village Cluster\nWork Deduplication',
    'Post-Sanction Dormancy\nDays Analysis'
]

for x, label in zip(feat_xs, feat_labels):
    draw_arrow_down(x, 225, 255)
    lines = label.split('\n')
    draw.rounded_rectangle((x - 190, 265, x + 190, 345), radius=10, fill=(0, 137, 123, 255))
    if font_sm:
        bb1 = draw.textbbox((0, 0), lines[0], font=font_sm)
        bb2 = draw.textbbox((0, 0), lines[1], font=font_sm)
        draw.text((x - (bb1[2] - bb1[0]) / 2, 278), lines[0], fill=(255, 255, 255, 255), font=font_sm)
        draw.text((x - (bb2[2] - bb2[0]) / 2, 308), lines[1], fill=(255, 255, 255, 255), font=font_sm)

# Branch from 4 Features to 3 ML models
draw.line([(220, 345), (220, 375)], fill=(30, 41, 59, 255), width=3)
draw.line([(670, 345), (670, 375)], fill=(30, 41, 59, 255), width=3)
draw.line([(1130, 345), (1130, 375)], fill=(30, 41, 59, 255), width=3)
draw.line([(1580, 345), (1580, 375)], fill=(30, 41, 59, 255), width=3)
draw.line([(220, 375), (1580, 375)], fill=(30, 41, 59, 255), width=3)

ml_xs = [380, 900, 1420]
ml_labels = [
    'Isolation Forest (45%)\nGlobal Multi-Variate Trees',
    'Profile-Deduplicated LOF (35%)\nLocal Density Outliers',
    'PCA Anomaly Subspace (20%)\nOrthogonal Reconstruction'
]
for x, label in zip(ml_xs, ml_labels):
    draw_arrow_down(x, 375, 405)
    lines = label.split('\n')
    draw.rounded_rectangle((x - 220, 415, x + 220, 495), radius=10, fill=(245, 124, 0, 255))
    if font_sm:
        bb1 = draw.textbbox((0, 0), lines[0], font=font_sm)
        bb2 = draw.textbbox((0, 0), lines[1], font=font_sm)
        draw.text((x - (bb1[2] - bb1[0]) / 2, 428), lines[0], fill=(255, 255, 255, 255), font=font_sm)
        draw.text((x - (bb2[2] - bb2[0]) / 2, 458), lines[1], fill=(255, 255, 255, 255), font=font_sm)

# Merge ML models to CAG Rules
draw.line([(380, 495), (380, 525)], fill=(30, 41, 59, 255), width=3)
draw.line([(900, 495), (900, 525)], fill=(30, 41, 59, 255), width=3)
draw.line([(1420, 495), (1420, 525)], fill=(30, 41, 59, 255), width=3)
draw.line([(380, 525), (1420, 525)], fill=(30, 41, 59, 255), width=3)
draw_arrow_down(900, 525, 555)

# Codified CAG Rules
draw_pill((580, 565, 1220, 635), (198, 40, 40, 255), '5 Codified Statutory CAG Rules (40% Weight)', font_md)
draw_arrow_down(900, 635, 670)

# Split to March Rush & Chronic Dormancy
draw.line([(900, 670), (900, 695)], fill=(30, 41, 59, 255), width=4)
draw.line([(550, 695), (1250, 695)], fill=(30, 41, 59, 255), width=4)
draw_arrow_down(550, 695, 725)
draw_arrow_down(1250, 695, 725)

draw_pill((300, 735, 800, 805), (106, 27, 154, 255), 'March Rush Radar - Q4 Fiscal Spikes', font_sm)
draw_pill((1000, 735, 1500, 805), (106, 27, 154, 255), 'Chronic Dormancy Engine - Zero Progress', font_sm)

# Merge to Final Output
draw.line([(550, 805), (550, 840)], fill=(30, 41, 59, 255), width=3)
draw.line([(1250, 805), (1250, 840)], fill=(30, 41, 59, 255), width=3)
draw.line([(550, 840), (1250, 840)], fill=(30, 41, 59, 255), width=3)
draw_arrow_down(900, 840, 870)

# Final Dossier
draw_pill((450, 880, 1350, 955), (46, 125, 50, 255), 'Bilingual CAG Dossier & Officer Alert Dashboard (Hindi + English)', font_md)

canvas.save('dataflow_pipeline.png')
print('SUCCESS: Created dataflow_pipeline.png')
