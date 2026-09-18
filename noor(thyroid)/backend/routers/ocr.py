"""
OCR Router — Extract data from uploaded medical reports
"""
import os, re
from fastapi import APIRouter, UploadFile, File, HTTPException
from pathlib import Path
from typing import Dict, Any

router = APIRouter()
UPLOADS_DIR = Path(__file__).resolve().parent.parent.parent / "uploads"


def _extract_value(text: str, pattern: str) -> str:
    """Extract first match of pattern from text."""
    m = re.search(pattern, text, re.IGNORECASE)
    return m.group(1).strip() if m else ""


def parse_medical_text(text: str) -> Dict[str, Any]:
    """Parse OCR text to extract thyroid-related values."""
    extracted = {}

    patterns = {
        "tsh": r"TSH\s*[:\-=]?\s*([0-9]+\.?[0-9]*)",
        "t3": r"\bT3\b\s*[:\-=]?\s*([0-9]+\.?[0-9]*)",
        "t4": r"\bT4\b\s*[:\-=]?\s*([0-9]+\.?[0-9]*)",
        "ft3": r"FT3\s*[:\-=]?\s*([0-9]+\.?[0-9]*)",
        "ft4": r"FT4\s*[:\-=]?\s*([0-9]+\.?[0-9]*)",
        "hemoglobin": r"H(?:aemo|emo)globin\s*[:\-=]?\s*([0-9]+\.?[0-9]*)",
        "wbc": r"WBC\s*[:\-=]?\s*([0-9]+\.?[0-9]*)",
        "rbc": r"RBC\s*[:\-=]?\s*([0-9]+\.?[0-9]*)",
        "platelets": r"Platelets?\s*[:\-=]?\s*([0-9]+\.?[0-9]*)",
        "calcium": r"Calcium\s*[:\-=]?\s*([0-9]+\.?[0-9]*)",
        "vitamin_d": r"Vitamin\s*D\s*[:\-=]?\s*([0-9]+\.?[0-9]*)",
        "age": r"\bAge\b\s*[:\-=]?\s*([0-9]+)",
        "weight": r"\bWeight\b\s*[:\-=]?\s*([0-9]+\.?[0-9]*)",
        "height": r"\bHeight\b\s*[:\-=]?\s*([0-9]+\.?[0-9]*)",
    }

    for field, pattern in patterns.items():
        val = _extract_value(text, pattern)
        if val:
            try:
                extracted[field] = float(val)
            except ValueError:
                extracted[field] = val

    # Gender
    if re.search(r'\b(male|man|boy)\b', text, re.I):
        extracted["gender"] = "Male"
    elif re.search(r'\b(female|woman|girl)\b', text, re.I):
        extracted["gender"] = "Female"

    return extracted


@router.post("/extract")
async def extract_from_report(file: UploadFile = File(...)):
    """Extract values from uploaded PDF/image using OCR."""
    allowed = {".pdf", ".png", ".jpg", ".jpeg", ".tiff", ".bmp"}
    ext = Path(file.filename).suffix.lower()
    if ext not in allowed:
        raise HTTPException(400, f"Unsupported file type: {ext}")

    content = await file.read()

    # Save temporarily
    tmp_path = UPLOADS_DIR / f"ocr_tmp_{file.filename}"
    with open(tmp_path, "wb") as f:
        f.write(content)

    extracted_text = ""
    try:
        import pytesseract
        from PIL import Image
        import io as io_mod

        if ext == ".pdf":
            try:
                from pdf2image import convert_from_path
                images = convert_from_path(str(tmp_path), dpi=200)
                for img in images:
                    extracted_text += pytesseract.image_to_string(img) + "\n"
            except Exception:
                extracted_text = ""
        else:
            img = Image.open(tmp_path)
            extracted_text = pytesseract.image_to_string(img)
    except ImportError:
        extracted_text = "[OCR] pytesseract not available — install Tesseract binary"
    except Exception as e:
        extracted_text = f"[OCR Error] {str(e)}"
    finally:
        if tmp_path.exists():
            tmp_path.unlink()

    extracted_values = parse_medical_text(extracted_text)

    return {
        "raw_text": extracted_text[:2000],  # limit output
        "extracted_values": extracted_values,
        "confidence": "high" if len(extracted_values) >= 5 else "low",
        "fields_found": len(extracted_values),
    }
