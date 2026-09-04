import os
import easyocr
from PIL import Image, ImageDraw
img1 = Image.new('RGB', (100, 100), color='white')
img1.save(os.path.join("tests", "fixtures", "images", "empty.png"))
img2 = Image.new('RGB', (400, 200), color='white')
d = ImageDraw.Draw(img2)
d.text((10,10), "Line One", fill=(0,0,0))
img2.save(os.path.join("tests", "fixtures", "images", "text.png"))
r = easyocr.Reader(['en'], gpu=False)
print("empty:", r.readtext(os.path.join("tests", "fixtures", "images", "empty.png"), detail=0))
print("text:", r.readtext(os.path.join("tests", "fixtures", "images", "text.png"), detail=0))
