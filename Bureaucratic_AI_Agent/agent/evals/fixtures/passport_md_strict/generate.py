"""
Generate fixture images for passport_md_strict eval cases.
Run from the agent/ directory:
    uv run python -m evals.fixtures.passport_md_strict.generate
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

_OUT = Path(__file__).parent


def _font(size: int):
    """Try to load a font with full Unicode/Romanian support."""
    for name in ["arial.ttf", "arialuni.ttf", "DejaVuSans.ttf", "DejaVuSansMono.ttf", "cour.ttf"]:
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def _make_passport(
    filename: str,
    surname: str,
    given_names: str,
    dob: str,
    doc_number: str,
    expiry: str,
    width: int = 900,
    height: int = 600,
) -> None:
    img = Image.new("RGB", (width, height), color=(245, 245, 255))
    draw = ImageDraw.Draw(img)

    title_font = _font(28)
    label_font = _font(20)
    value_font = _font(24)

    # Header
    draw.rectangle([(0, 0), (width, 80)], fill=(20, 60, 140))
    draw.text((30, 12), "REPUBLICA MOLDOVA - REPUBLIC OF MOLDOVA", font=_font(20), fill="white")
    draw.text((30, 45), "PAȘAPORT  /  PASSPORT", font=title_font, fill=(200, 220, 255))

    # Type / Code / Number row
    y = 100
    draw.text((30, y), "Tip / Type", font=label_font, fill=(100, 100, 100))
    draw.text((30, y + 25), "PA", font=value_font, fill=(10, 10, 10))

    draw.text((230, y), "Cod țară / Country Code", font=label_font, fill=(100, 100, 100))
    draw.text((230, y + 25), "MDA", font=value_font, fill=(10, 10, 10))

    draw.text((500, y), "Nr. pașaport / Passport No", font=label_font, fill=(100, 100, 100))
    draw.text((500, y + 25), doc_number, font=value_font, fill=(10, 10, 10))

    # Separator
    draw.line([(30, 175), (width - 30, 175)], fill=(180, 180, 200), width=1)

    # Personal data
    fields = [
        ("Nume / Surname", surname),
        ("Prenume / Given Names", given_names),
        ("Data nașterii / Date of Birth", dob),
        ("Data expirării / Expiry Date", expiry),
    ]

    y = 190
    for label, value in fields:
        draw.text((30, y), label, font=label_font, fill=(100, 100, 100))
        draw.text((30, y + 26), value, font=value_font, fill=(10, 10, 10))
        y += 80

    # MRZ strip
    draw.rectangle([(0, height - 80), (width, height)], fill=(230, 230, 230))
    mrz_font = _font(16)
    mrz1 = f"P<MDA{surname.upper()}<<{given_names.upper().replace(' ', '<')}"
    mrz2 = f"{doc_number}MDA{dob.replace('/', '')}"
    draw.text((20, height - 72), mrz1[:44], font=mrz_font, fill=(60, 60, 60))
    draw.text((20, height - 44), mrz2[:44], font=mrz_font, fill=(60, 60, 60))

    img.save(_OUT / filename, "JPEG", quality=92)
    size_kb = (_OUT / filename).stat().st_size // 1024
    print(f"  ✓ {filename}  ({size_kb} KB)")


def _make_invoice(filename: str) -> None:
    """Clearly not a passport — a generic invoice image."""
    img = Image.new("RGB", (800, 500), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)

    f28 = _font(28)
    f20 = _font(20)
    f16 = _font(16)

    draw.text((30, 30), "INVOICE", font=f28, fill=(0, 0, 0))
    draw.line([(30, 70), (770, 70)], fill=(0, 0, 0), width=2)

    rows = [
        ("Invoice No:",  "INV-2026-00123"),
        ("Date:",        "09/04/2026"),
        ("Bill To:",     "Tech Solutions SRL"),
        ("Address:",     "str. Stefan cel Mare 1, Chisinau"),
        ("",             ""),
        ("Description:", "Software consulting services — March 2026"),
        ("Quantity:",    "1"),
        ("Unit Price:",  "2 500.00 EUR"),
        ("",             ""),
        ("TOTAL DUE:",   "2 500.00 EUR"),
    ]

    y = 90
    for label, value in rows:
        if label:
            draw.text((30, y), label, font=f20, fill=(80, 80, 80))
            draw.text((220, y), value, font=f20, fill=(0, 0, 0))
        y += 36

    draw.line([(30, y), (770, y)], fill=(0, 0, 0), width=1)
    draw.text((30, y + 10), "Payment due within 30 days. Thank you for your business.", font=f16, fill=(120, 120, 120))

    img.save(_OUT / filename, "JPEG", quality=92)
    size_kb = (_OUT / filename).stat().st_size // 1024
    print(f"  ✓ {filename}  ({size_kb} KB)")


def _make_tiny(filename: str) -> None:
    """Tiny image guaranteed to be < 50 KB."""
    img = Image.new("RGB", (80, 60), color=(200, 200, 200))
    draw = ImageDraw.Draw(img)
    draw.text((5, 20), "tiny", font=_font(12), fill=(0, 0, 0))
    img.save(_OUT / filename, "JPEG", quality=30)
    size_b = (_OUT / filename).stat().st_size
    print(f"  ✓ {filename}  ({size_b} bytes)")


if __name__ == "__main__":
    print("Generating fixture images...")

    _make_passport(
        "passport_valid.jpg",
        surname="POPESCU",
        given_names="ION",
        dob="01/01/1990",
        doc_number="AA123456",
        expiry="01/01/2030",
    )

    _make_passport(
        "passport_expired.jpg",
        surname="POPESCU",
        given_names="ION",
        dob="01/01/1990",
        doc_number="AA123456",
        expiry="26/05/2021",
    )

    # Same document — name mismatch comes from form_data, not the image
    _make_passport(
        "passport_mismatch.jpg",
        surname="POPESCU",
        given_names="ION",
        dob="01/01/1990",
        doc_number="AA123456",
        expiry="01/01/2030",
    )

    _make_invoice("random_image.jpg")

    _make_tiny("passport_tiny.jpg")

    print("Done.")
