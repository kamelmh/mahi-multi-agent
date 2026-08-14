"""
Electronic Signature Tool for PDFs (Adobe-style)
Usage: python sign_pdf.py --input document.pdf --output signed_document.pdf --signature signature.png --position bottom-right
"""
import argparse
import os
import tempfile
import uuid
from fpdf import FPDF
from PyPDF2 import PdfReader, PdfWriter
from PIL import Image


def sign_pdf(input_path, output_path, signature_path=None, position="bottom-right", 
             page=-1, x_offset=0, y_offset=0, signer_name=""):
    """
    Add electronic signature to PDF (Adobe-style placement).
    
    Args:
        input_path: Path to input PDF
        output_path: Path to output signed PDF
        signature_path: Path to signature image (PNG/JPG)
        position: Where to place signature (bottom-right, bottom-left, center, signature-line)
        page: Page number to sign (-1 for last page, 0 for all pages)
        x_offset: X offset from position
        y_offset: Y offset from position
        signer_name: Name to display below signature
    """
    if not os.path.exists(input_path):
        print(f"Error: Input file '{input_path}' not found")
        return None
    
    if signature_path is None or not os.path.exists(signature_path):
        print("Error: Signature image required. Use create_signature.py to generate one.")
        return None
    
    try:
        reader = PdfReader(input_path)
        writer = PdfWriter()
        
        # Get signature image dimensions
        sig_img = Image.open(signature_path)
        sig_width = 45  # mm - signature width
        sig_height = 18  # mm - signature height
        
        # Calculate which pages to sign
        if page == -1:
            pages_to_sign = [len(reader.pages) - 1]
        elif page == 0:
            pages_to_sign = list(range(len(reader.pages)))
        else:
            pages_to_sign = [page - 1]
        
        for i, page_num in enumerate(pages_to_sign):
            page = reader.pages[page_num]
            
            # Create overlay with signature
            overlay = FPDF()
            overlay.add_page()
            
            page_width = float(page.mediabox.width) * 0.264583  # Convert points to mm
            page_height = float(page.mediabox.height) * 0.264583
            
            # Calculate position (Adobe-style: right-aligned, at bottom after closing)
            if position == "bottom-right":
                x = page_width - sig_width - 25 + x_offset
                y = page_height - sig_height - 25 + y_offset
            elif position == "bottom-left":
                x = 25 + x_offset
                y = page_height - sig_height - 25 + y_offset
            elif position == "center":
                x = (page_width - sig_width) / 2 + x_offset
                y = (page_height - sig_height) / 2 + y_offset
            elif position == "signature-line":
                # Place at very bottom right, after "Veuillez agréer..." closing
                x = page_width - sig_width - 30 + x_offset
                y = page_height - 45 + y_offset  # Very bottom of page
            else:
                x = page_width - sig_width - 25 + x_offset
                y = page_height - sig_height - 25 + y_offset
            
            # Add signature image
            overlay.image(signature_path, x=x, y=y, w=sig_width, h=sig_height)
            
            # Add date below signature
            if signer_name:
                overlay.set_font('Helvetica', '', 9)
                overlay.set_text_color(0)
                # Date
                from datetime import datetime
                date_str = datetime.now().strftime("%d/%m/%Y")
                overlay.set_xy(x, y + sig_height + 1)
                overlay.cell(sig_width, 5, date_str, align='C')
            
            # Save overlay to temp file
            temp_dir = tempfile.gettempdir()
            overlay_path = os.path.join(temp_dir, f"overlay_{uuid.uuid4().hex[:8]}.pdf")
            overlay.output(overlay_path)
            
            # Merge overlay with page
            overlay_reader = PdfReader(overlay_path)
            if len(overlay_reader.pages) > 0:
                page.merge_page(overlay_reader.pages[0])
            
            writer.add_page(page)
            
            # Cleanup overlay
            try:
                os.remove(overlay_path)
            except:
                pass
        
        # Write output
        with open(output_path, "wb") as f:
            writer.write(f)
        
        print(f"Signed PDF saved to: {output_path}")
        return output_path
        
    except Exception as e:
        print(f"Error signing PDF: {e}")
        return None


def main():
    parser = argparse.ArgumentParser(description="Electronic PDF Signature Tool (Adobe-style)")
    parser.add_argument("--input", "-i", required=True, help="Input PDF path")
    parser.add_argument("--output", "-o", help="Output PDF path (default: input_signed.pdf)")
    parser.add_argument("--signature", "-s", required=True, help="Signature image path (PNG/JPG)")
    parser.add_argument("--position", "-p", default="signature-line", 
                        choices=["bottom-right", "bottom-left", "center", "signature-line"],
                        help="Signature position (default: signature-line)")
    parser.add_argument("--name", "-n", default="Mahi Kamel Abdelghani", help="Signer name")
    parser.add_argument("--page", type=int, default=-1, help="Page to sign (-1 for last, 0 for all)")
    parser.add_argument("--x-offset", type=int, default=0, help="X offset in mm")
    parser.add_argument("--y-offset", type=int, default=0, help="Y offset in mm")
    
    args = parser.parse_args()
    
    if args.output is None:
        base, ext = os.path.splitext(args.input)
        args.output = f"{base}_signed{ext}"
    
    sign_pdf(
        args.input,
        args.output,
        args.signature,
        args.position,
        args.page,
        args.x_offset,
        args.y_offset,
        args.name
    )


if __name__ == "__main__":
    main()
