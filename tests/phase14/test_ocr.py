import easyocr
import os

def test_ocr():
    path = os.path.join(os.path.dirname(__file__), "..", "fixtures", "images", "multiline.png")
    r = easyocr.Reader(['en'], gpu=False)
    print("detail=0:", r.readtext(path, detail=0))
    print("detail=1:", r.readtext(path, detail=1))
