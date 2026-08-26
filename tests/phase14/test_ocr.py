import easyocr
from PIL import Image, ImageDraw

def test_ocr():
    img = Image.new('RGB', (400, 200), color='white')
    d = ImageDraw.Draw(img)
    d.text((10,10), "Line One\nLine Two\nLine Three", fill=(0,0,0))
    img.save("multiline.png")
    r = easyocr.Reader(['en'], gpu=False)
    print("detail=0:", r.readtext("multiline.png", detail=0))
    print("detail=1:", r.readtext("multiline.png", detail=1))
