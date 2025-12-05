
from pdf2image import convert_from_path
import os
from pathlib import Path

def pdf_to_images(pdf_path: str, output_dir: str, dpi: int = 300):
    """
    Convert a PDF into per-page PNG images for manipulation analysis with ManTraNet.

    Args:
        pdf_path (str): Full path to the input PDF file.
        output_dir (str): Directory where output images will be saved.
        dpi (int): Render resolution (300 recommended for forensic tasks).

    Returns:
        List[str]: Paths to the generated image files.
    """

    pdf_path = Path(pdf_path)
    output_dir = Path(output_dir)

    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    output_dir.mkdir(parents=True, exist_ok=True)

    # Convert all pages to images
    pages = convert_from_path(str(pdf_path), dpi=dpi)

    output_paths = []
    base_name = pdf_path.stem

    for i, page in enumerate(pages):
        img_path = output_dir / f"{base_name}_page_{i+1}.png"
        page.save(img_path, "PNG")
        output_paths.append(str(img_path))

    return output_paths
