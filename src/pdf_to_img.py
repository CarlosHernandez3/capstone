import fitz  # PyMuPDF
from PIL import Image

def pdf_to_images(pdf_path: str, dpi: int = 300):
    """
    Convert each PDF page into a PIL.Image in RGB mode.
    Optimized for forensic analysis (e.g., ManTraNet).
    """
    doc = fitz.open(pdf_path)
    images = []

    zoom = dpi / 72  # scale factor (PDF default is 72 DPI)
    matrix = fitz.Matrix(zoom, zoom)

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        pix = page.get_pixmap(matrix=matrix, alpha=False)  # Force no alpha channel
        img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
        images.append(img)

    doc.close()
    return images
