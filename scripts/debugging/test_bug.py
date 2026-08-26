import easyocr
from PIL import Image, ImageDraw
img1 = Image.new('RGB', (100, 100), color='white')
img1.save("empty.png")
img2 = Image.new('RGB', (400, 200), color='white')
d = ImageDraw.Draw(img2)
d.text((10,10), "Line One", fill=(0,0,0))
img2.save("text.png")
r = easyocr.Reader(['en'], gpu=False)
print("empty:", r.readtext("empty.png", detail=0))
print("text:", r.readtext("text.png", detail=0))
