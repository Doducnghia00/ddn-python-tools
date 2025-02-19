from pdf_to_image import PDFConverter
import os

def pdf_to_images_example():
    """Example of converting PDF to images"""
    converter = PDFConverter()
    
    # Convert local PDF to images
    try:
        image_paths = converter.convert_local_pdf(
            pdf_path="tools/pdf-image-converter/input/sample.pdf",
            output_dir="tools/pdf-image-converter/output",
            dpi=300,
            fmt='PNG'
        )
        print("Successfully converted PDF to images!")
        print("Generated images:", image_paths)
    except Exception as e:
        print(f"Error: {str(e)}")

def images_to_pdf_example():
    """Example of converting images to PDF"""
    converter = PDFConverter()
    
    # Method 1: Convert specific images to PDF
    try:
        image_paths = [
            "tools/pdf-image-converter/input/image1.png",
            "tools/pdf-image-converter/input/image2.png",
            "tools/pdf-image-converter/input/image3.png"
        ]
        pdf_path = converter.convert_images_to_pdf(
            image_paths=image_paths,
            output_pdf="tools/pdf-image-converter/output/output.pdf",
            image_quality=95
        )
        print(f"Successfully created PDF: {pdf_path}")
    except Exception as e:
        print(f"Error: {str(e)}")

    # Method 2: Convert all images in a directory to PDF
    try:
        pdf_path = converter.convert_directory_to_pdf(
            input_dir="tools/pdf-image-converter/input",
            output_pdf="tools/pdf-image-converter/output/output_directory.pdf",
            image_pattern="*.png",  # Convert all PNG files
            sort_by="name",        # Sort by filename
            image_quality=95
        )
        print(f"Successfully created PDF from directory: {pdf_path}")
    except Exception as e:
        print(f"Error: {str(e)}")

def main():
    # PDF to Images
    print("Converting PDF to images...")
    pdf_to_images_example()
    
    print("\n" + "="*50 + "\n")
    
    # Images to PDF
    print("Converting images to PDF...")
    images_to_pdf_example()

if __name__ == "__main__":
    main()