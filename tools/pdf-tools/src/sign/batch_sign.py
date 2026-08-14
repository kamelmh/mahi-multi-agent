"""
Batch PDF Signing Tool
Signs multiple PDFs at once with the same signature.
"""
import os
import sys
import glob
from sign_pdf import sign_pdf


def batch_sign(input_folder, output_folder, signature_path=None, signer_name="Kamel MAHI"):
    """Sign all PDFs in a folder."""
    
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    pdf_files = glob.glob(os.path.join(input_folder, "*.pdf"))
    
    if not pdf_files:
        print(f"No PDF files found in {input_folder}")
        return
    
    print(f"Found {len(pdf_files)} PDF files to sign")
    
    for pdf_path in pdf_files:
        filename = os.path.basename(pdf_path)
        output_path = os.path.join(output_folder, filename)
        
        print(f"Signing: {filename}")
        result = sign_pdf(
            pdf_path,
            output_path,
            signature_path,
            "bottom-right",
            -1,
            0,
            0,
            signer_name
        )
        
        if result:
            print(f"  ✓ Saved to: {output_path}")
        else:
            print(f"  ✗ Failed to sign: {filename}")
    
    print(f"\nBatch signing complete. Output folder: {output_folder}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python batch_sign.py <input_folder> [output_folder] [signature_image]")
        sys.exit(1)
    
    input_folder = sys.argv[1]
    output_folder = sys.argv[2] if len(sys.argv) > 2 else input_folder + "_signed"
    signature_path = sys.argv[3] if len(sys.argv) > 3 else None
    
    batch_sign(input_folder, output_folder, signature_path)
