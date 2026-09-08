from PIL import Image

# Open the ultra-high-res official image
orig = Image.open('sih_official_img_1_7.png').convert('RGBA')
w, h = orig.size

# Crop Bulb precisely
# Bulb bbox is roughly (170, 117, 5041, 5653)
bulb = orig.crop((150, 100, 5060, 5670))
bb = bulb.getbbox()
bulb = bulb.crop(bb)
bw, bh = bulb.size
print('Bulb size:', bw, bh)

# Crop Text precisely
# Bulb ends around x=5041. Text starts around x=5100-5200.
text_part = orig.crop((int(w * 0.43), 0, w, h))
tb = text_part.getbbox()
text_img = text_part.crop(tb)
tw, th = text_img.size
print('Text size:', tw, th)

# Arrange Vertically matching user's uploaded image:
# Bulb on top, Text centered below it
canvas_w = max(bw, tw) + 400
gap = 750
canvas_h = bh + gap + th + 200

vert_img = Image.new('RGBA', (canvas_w, canvas_h), (255, 255, 255, 0))
# Center bulb
bx = (canvas_w - bw) // 2
vert_img.paste(bulb, (bx, 100), bulb)

# Center text
tx = (canvas_w - tw) // 2
ty = 100 + bh + gap
vert_img.paste(text_img, (tx, ty), text_img)

# Crop to tight bounding box with a 40px margin
vbb = vert_img.getbbox()
margin = 40
tight_crop = (max(0, vbb[0] - margin), max(0, vbb[1] - margin), min(canvas_w, vbb[2] + margin), min(canvas_h, vbb[3] + margin))
vert_img = vert_img.crop(tight_crop)

# Save high-res master
vert_img.save('sih_logo_vertical_4k.png')

# Save standard high-res version for slides (1200px height)
scale = 1200.0 / vert_img.height
target_size = (int(vert_img.width * scale), 1200)
resized_logo = vert_img.resize(target_size, Image.Resampling.LANCZOS)
resized_logo.save('sih_logo_vertical_official.png')

# Save as sih_bulb_center.png for Slide 1
resized_logo.save('sih_bulb_center.png')

# Create crisp horizontal header logo from orig for all slide headers:
hbb = orig.getbbox()
h_crop = orig.crop(hbb)
h_scale = 300.0 / h_crop.height
h_target_size = (int(h_crop.width * h_scale), 300)
h_resized = h_crop.resize(h_target_size, Image.Resampling.LANCZOS)
h_resized.save('sih_logo_transparent.png')

print('SUCCESS: Created sih_logo_vertical_official.png, updated sih_bulb_center.png (vertical) and sih_logo_transparent.png (horizontal header)')
