"""
Convert PDF to black and white using PyMuPDF
"""
import os
import tempfile
from PIL import Image


def pdf_to_grayscale(input_path, output_path):
    """Convert PDF to grayscale by rendering pages as images."""
    import fitz  # PyMuPDF
    
    doc = fitz.open(input_path)
    pdf_bytes = fitz.open()
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        
        # Render page as image
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2x zoom for quality
        
        # Convert to grayscale
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        img_gray = img.convert('L')
        
        # Save as temporary image
        temp_img = os.path.join(tempfile.gettempdir(), f"page_{page_num}.png")
        img_gray.save(temp_img, "PNG")
        
        # Insert into new PDF
        new_page = pdf_bytes.new_page(width=page.rect.width, height=page.rect.height)
        new_page.insert_image(new_page.rect, filename=temp_img)
        
        # Cleanup
        os.remove(temp_img)
    
    pdf_bytes.save(output_path)
    doc.close()
    pdf_bytes.close()
    
    print(f"Saved grayscale PDF: {output_path}")
    return output_path


if __name__ == "__main__":
    input_file = r"C:\Users\Admin\My Drive\LifeWorkspace\16_Official\Academic\شهادة البكالوريا + كشف نقاط.pdf"
    output_file = r"C:\Users\Admin\My Drive\LifeWorkspace\16_Official\Academic\شهادة البكالوريا + كشف نقاط_BW.pdf"
    
    pdf_to_grayscale(input_file, output_file)
