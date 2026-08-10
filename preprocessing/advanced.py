from pydantic import BaseModel
from typing import List, Dict, Any
from enum import Enum

class TransformationType(str, Enum):
    UNICODE_NORMALIZED = "UNICODE_NORMALIZED"
    CONFUSABLE_NORMALIZED = "CONFUSABLE_NORMALIZED"
    HOMOGLYPH_NORMALIZED = "HOMOGLYPH_NORMALIZED"
    OCR_NORMALIZED = "OCR_NORMALIZED"
    MARKDOWN_CLEANED = "MARKDOWN_CLEANED"
    WHITESPACE_NORMALIZED = "WHITESPACE_NORMALIZED"
    REPETITION_NORMALIZED = "REPETITION_NORMALIZED"
    LEETSPEAK_NORMALIZED = "LEETSPEAK_NORMALIZED"
    MIXED_LANGUAGE_NORMALIZED = "MIXED_LANGUAGE_NORMALIZED"

class PreprocessingResult(BaseModel):
    original_text: str
    normalized_text: str
    transformations: List[str] = []
    flags: Dict[str, Any] = {}

from preprocessing.unicode_normalizer import normalize_unicode
from preprocessing.confusable_normalizer import normalize_unicode_confusables
from preprocessing.homoglyph_normalizer import normalize_homoglyphs
from preprocessing.ocr_normalizer import normalize_ocr
from preprocessing.markdown_cleaner import clean_markdown
from preprocessing.whitespace_normalizer import normalize_whitespace
from preprocessing.zero_width_remover import remove_zero_width
from preprocessing.repeated_char_normalizer import normalize_repeated_chars
from preprocessing.leetspeak_decoder import decode_leetspeak
from preprocessing.mixed_language_normalizer import normalize_mixed_language

class AdvancedPreprocessor:
    def __init__(self):
        # Transformation order defined by architecture guidelines:
        # 1. Unicode canonical normalization
        # 2. Confusable / homoglyph normalization
        pass

    def process(self, text: str) -> PreprocessingResult:
        if text is None:
            text = ""
            
        normalized = text
        transformations = []
        flags = {}
        
        # 1. Unicode NFC Normalization
        normalized, uni_changed = normalize_unicode(normalized)
        if uni_changed:
            transformations.append(TransformationType.UNICODE_NORMALIZED.value)
            flags['unicode_changed'] = True
            
        # 2. Confusable Normalization
        normalized, conf_changed = normalize_unicode_confusables(normalized)
        if conf_changed:
            transformations.append(TransformationType.CONFUSABLE_NORMALIZED.value)
            flags['confusable_detected'] = True
            
        # 3. Homoglyph Normalization
        normalized, homo_changed = normalize_homoglyphs(normalized)
        if homo_changed:
            transformations.append(TransformationType.HOMOGLYPH_NORMALIZED.value)
            flags['homoglyph_detected'] = True
            
        # 4. OCR Normalization
        normalized, ocr_changed = normalize_ocr(normalized)
        if ocr_changed:
            transformations.append(TransformationType.OCR_NORMALIZED.value)
            flags['ocr_normalized'] = True
            
        # 5. Markdown Normalization
        normalized, md_changed = clean_markdown(normalized)
        if md_changed:
            transformations.append(TransformationType.MARKDOWN_CLEANED.value)
            flags['markdown_cleaned'] = True
            
        # 6. Whitespace Normalization (including zero-width removal)
        normalized, zw_changed = remove_zero_width(normalized)
        normalized, ws_changed = normalize_whitespace(normalized)
        if zw_changed or ws_changed:
            transformations.append(TransformationType.WHITESPACE_NORMALIZED.value)
            flags['whitespace_normalized'] = True
            
        # 7. Repetition Normalization
        normalized, rep_changed = normalize_repeated_chars(normalized)
        if rep_changed:
            transformations.append(TransformationType.REPETITION_NORMALIZED.value)
            flags['repetition_normalized'] = True
        
        # 8. Leetspeak Normalization
        normalized, leet_changed = decode_leetspeak(normalized)
        if leet_changed:
            transformations.append(TransformationType.LEETSPEAK_NORMALIZED.value)
            flags['leetspeak_normalized'] = True
            
        # 9. Mixed-language Normalization
        # Detection runs on original text to identify scripts before confusables collapsed them
        _, mix_detected = normalize_mixed_language(text)
        if mix_detected:
            flags['mixed_script_detected'] = True
        
        return PreprocessingResult(
            original_text=text,
            normalized_text=normalized,
            transformations=transformations,
            flags=flags
        )
