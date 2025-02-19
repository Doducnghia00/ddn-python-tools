# PDF-Image Converter

A versatile Python utility for bi-directional conversion between PDF and images. Support for both local files and URLs.

## Features

✨ **Key Features**
- Convert PDF to Images:
  - Local PDF files
  - PDFs from URLs
  - Multiple output formats (PNG, JPEG, etc.)
  - Adjustable image quality (DPI)
  
- Convert Images to PDF:
  - Multiple images to single PDF
  - Entire directory of images to PDF
  - Sort by name or date
  - Adjustable output quality
  - Supports various image formats

## Installation

1. **Install System Dependencies (Poppler)**

   - **Windows:**
     ```bash
     # Download from: https://github.com/oschwartz10612/poppler-windows/releases
     # Add bin folder to PATH
     ```

   - **macOS:**
     ```bash
     brew install poppler
     ```

   - **Ubuntu/Debian:**
     ```bash
     sudo apt-get install poppler-utils
     ```

2. **Install Python Dependencies**
   ```bash
   pip install requests pdf2image Pillow
   ```

## Quick Start

### PDF to Images

```python
from pdf_to_image import PDFConverter

converter = PDFConverter()

# Convert local PDF
images = converter.convert_local_pdf(
    pdf_path="document.pdf",
    output_dir="output_images",
    dpi=300,
    fmt='PNG'
)
```

### Images to PDF

```python
from pdf_to_image import PDFConverter

converter = PDFConverter()

# Convert specific images to PDF
pdf_path = converter.convert_images_to_pdf(
    image_paths=["image1.png", "image2.png", "image3.png"],
    output_pdf="output.pdf",
    image_quality=95
)

# Or convert entire directory
pdf_path = converter.convert_directory_to_pdf(
    input_dir="input_images",
    output_pdf="output_directory.pdf",
    image_pattern="*.png",
    sort_by="name"
)
```

## Advanced Usage

### PDF to Images with Page Selection

```python
# Convert only pages 1-3
images = converter.convert_local_pdf(
    pdf_path="document.pdf",
    output_dir="output_images",
    first_page=1,
    last_page=3
)
```

### Images to PDF with Custom Sorting

```python
# Sort by modification date
pdf_path = converter.convert_directory_to_pdf(
    input_dir="input_images",
    output_pdf="output.pdf",
    image_pattern="*.jpg",
    sort_by="date"
)
```

## API Reference

### PDFConverter Class

#### PDF to Images Methods

1. `convert_local_pdf(pdf_path, output_dir, dpi=200, fmt='PNG', first_page=None, last_page=None)`
   - Converts local PDF file to images
   - Returns list of image paths

2. `convert_pdf_url(url, output_dir, dpi=200, fmt='PNG', first_page=None, last_page=None)`
   - Downloads and converts PDF from URL
   - Returns list of image paths

#### Images to PDF Methods

1. `convert_images_to_pdf(image_paths, output_pdf, image_quality=100)`
   - Converts list of images to PDF
   - Returns path to generated PDF

2. `convert_directory_to_pdf(input_dir, output_pdf, image_pattern="*.[pP][nN][gG]", sort_by="name", image_quality=100)`
   - Converts all matching images in directory to PDF
   - Returns path to generated PDF

## Error Handling

The converter includes comprehensive error handling for:
- Missing dependencies
- Invalid files or formats
- Network issues
- File system errors

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License

## Author

- Created by: @Doducnghia00
- Created on: 2025-02-19

## Support

For support, please open an issue in the GitHub repository.