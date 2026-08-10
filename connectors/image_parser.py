import os
import logging
from PIL import Image, UnidentifiedImageError
from connectors.extraction_result import ExtractionResult, ExtractedContent
from context.source import ScanSource

logger = logging.getLogger("promptsentinel")

# Lazy loading to avoid OCR initialization overhead on startup
_reader = None

def get_reader():
    global _reader
    if _reader is None:
        import easyocr
        _reader = easyocr.Reader(['en'], gpu=False)
    return _reader

SUPPORTED_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.tiff', '.tif'}
SUPPORTED_MIMES = {'image/png', 'image/jpeg', 'image/tiff'}
MAX_FILE_SIZE = 20 * 1024 * 1024 # 20MB

def parse_image(file_path: str) -> ExtractionResult:
    items = []
    
    extension = os.path.splitext(file_path)[1].lower()
    if extension not in SUPPORTED_EXTENSIONS:
        return ExtractionResult(items=items)

    try:
        file_size = os.path.getsize(file_path)
        if file_size > MAX_FILE_SIZE:
            logger.warning(f"Image {file_path} exceeds size limit of 20MB")
            return ExtractionResult(items=items)

        # Safely validate MIME type
        try:
            with Image.open(file_path) as img:
                img.verify()
                format_mime = Image.MIME.get(img.format)
                if format_mime not in SUPPORTED_MIMES:
                    logger.warning(f"Unsupported image format {img.format} for {file_path}")
                    return ExtractionResult(items=items)
        except (UnidentifiedImageError, OSError) as e:
            logger.warning(f"Failed to identify image {file_path}: {e}")
            return ExtractionResult(items=items)

        # Run OCR Extraction
        reader = get_reader()
        # detail=0 returns text list
        result = reader.readtext(file_path, detail=0)
        
        text = "\n".join(result)
        
        if text.strip():
            items.append(ExtractedContent(
                content=text,
                source=ScanSource.IMAGE
            ))
            
    except Exception as e:
        logger.error(f"OCR failed for {file_path}: {e}")

    return ExtractionResult(items=items)
