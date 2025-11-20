from PIL import Image, ImageDraw, ImageFont

# Create a 256x256 icon with a simple 'F' letter
size = (256, 256)
img = Image.new('RGBA', size, (28, 100, 242, 255))
draw = ImageDraw.Draw(img)

# Try to load a system font, fallback to default
try:
    font = ImageFont.truetype('arial.ttf', 160)
except Exception:
    font = ImageFont.load_default()

text = 'F'
try:
    bbox = draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
except Exception:
    try:
        text_w, text_h = draw.textsize(text, font=font)
    except Exception:
        text_w, text_h = font.getsize(text)

position = ((size[0]-text_w)//2, (size[1]-text_h)//2 - 10)

# Draw shadow
draw.text((position[0]+2, position[1]+2), text, font=font, fill=(0,0,0,120))
# Draw main letter
draw.text(position, text, font=font, fill=(255,255,255,255))

# Save as ICO (Pillow will include multiple sizes if provided)
img.save('icon.ico', format='ICO', sizes=[(256,256),(128,128),(64,64),(48,48),(32,32)])
print('icon.ico created')
