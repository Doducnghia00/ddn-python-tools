from typing import List, Optional, Union
from pathlib import Path
import requests
import tempfile
import logging
from pdf2image import convert_from_path
from PIL import Image
import os
import sys
import shutil

class PDFConverter:
    """A class to handle PDF-Image conversions in both directions."""
    
    def __init__(self, temp_dir: Optional[str] = None):
        """
        Initialize PDFConverter.
        
        Args:
            temp_dir (str, optional): Custom temporary directory path.
                                    If None, uses system default.
        """
        self.temp_dir = temp_dir or tempfile.gettempdir()
        self.logger = logging.getLogger(__name__)
        self._check_poppler_installation()

    def convert_local_pdf(self, 
                         pdf_path: Union[str, Path],
                         output_dir: Union[str, Path],
                         dpi: int = 200,
                         fmt: str = 'PNG',
                         first_page: Optional[int] = None,
                         last_page: Optional[int] = None) -> List[str]:
        """
        Convert a local PDF file to images.

        Args:
            pdf_path: Path to local PDF file
            output_dir: Directory to save images
            dpi: Image quality (dots per inch)
            fmt: Output format ('PNG', 'JPEG', etc.)
            first_page: Start page number (optional)
            last_page: End page number (optional)

        Returns:
            List of paths to generated images
        """
        return self.convert_pdf_to_images(
            pdf_path=pdf_path,
            output_dir=output_dir,
            dpi=dpi,
            fmt=fmt,
            first_page=first_page,
            last_page=last_page,
            cleanup=False  # Don't delete local PDF
        )

    def convert_pdf_url(self,
                       url: str,
                       output_dir: Union[str, Path],
                       dpi: int = 200,
                       fmt: str = 'PNG',
                       first_page: Optional[int] = None,
                       last_page: Optional[int] = None) -> List[str]:
        """
        Convert a PDF from URL to images.

        Args:
            url: URL of the PDF file
            output_dir: Directory to save images
            dpi: Image quality (dots per inch)
            fmt: Output format ('PNG', 'JPEG', etc.)
            first_page: Start page number (optional)
            last_page: End page number (optional)

        Returns:
            List of paths to generated images
        """
        pdf_path = self.download_pdf(url)
        return self.convert_pdf_to_images(
            pdf_path=pdf_path,
            output_dir=output_dir,
            dpi=dpi,
            fmt=fmt,
            first_page=first_page,
            last_page=last_page,
            cleanup=True  # Delete downloaded PDF
        )

    def convert_images_to_pdf(self,
                            image_paths: List[Union[str, Path]],
                            output_pdf: Union[str, Path],
                            image_quality: int = 100) -> str:
        """
        Convert multiple images to a single PDF file.

        Args:
            image_paths: List of paths to image files
            output_pdf: Path for output PDF file
            image_quality: Quality for JPEG compression (1-100)

        Returns:
            Path to generated PDF file
        """
        try:
            # Convert all paths to Path objects
            image_paths = [Path(p) for p in image_paths]
            output_pdf = Path(output_pdf)
            
            # Validate input images
            for img_path in image_paths:
                if not img_path.exists():
                    raise FileNotFoundError(f"Image not found: {img_path}")
            
            # Create output directory if needed
            output_pdf.parent.mkdir(parents=True, exist_ok=True)
            
            # Open first image
            images = []
            first_image = Image.open(image_paths[0])
            
            # Convert to RGB if needed (for PDF compatibility)
            if first_image.mode != 'RGB':
                first_image = first_image.convert('RGB')
            
            # Open and process remaining images
            for img_path in image_paths[1:]:
                img = Image.open(img_path)
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                images.append(img)
            
            # Save as PDF
            first_image.save(
                output_pdf,
                "PDF",
                save_all=True,
                append_images=images,
                quality=image_quality,
                optimize=True
            )
            
            return str(output_pdf)
            
        except Exception as e:
            raise Exception(f"Image to PDF conversion failed: {str(e)}")

    def convert_directory_to_pdf(self,
                               input_dir: Union[str, Path],
                               output_pdf: Union[str, Path],
                               image_pattern: str = "*.[pP][nN][gG]",
                               sort_by: str = "name",
                               image_quality: int = 100) -> str:
        """
        Convert all images in a directory to a single PDF file.

        Args:
            input_dir: Directory containing images
            output_pdf: Path for output PDF file
            image_pattern: Glob pattern for image files
            sort_by: How to sort images ('name' or 'date')
            image_quality: Quality for JPEG compression (1-100)

        Returns:
            Path to generated PDF file
        """
        try:
            input_dir = Path(input_dir)
            
            # Get all matching image files
            image_paths = list(input_dir.glob(image_pattern))
            
            if not image_paths:
                raise ValueError(f"No images found in {input_dir} matching pattern {image_pattern}")
            
            # Sort images
            if sort_by == "date":
                image_paths.sort(key=lambda x: x.stat().st_mtime)
            else:  # sort by name
                image_paths.sort()
            
            # Convert to PDF
            return self.convert_images_to_pdf(
                image_paths=image_paths,
                output_pdf=output_pdf,
                image_quality=image_quality
            )
            
        except Exception as e:
            raise Exception(f"Directory to PDF conversion failed: {str(e)}")


    def _check_poppler_installation(self) -> None:
        """Check if poppler is installed."""
        if not shutil.which('pdftoppm'):
            platform = sys.platform
            instructions = {
                "darwin": "Install with: brew install poppler",
                "linux": "Install with: sudo apt-get install poppler-utils",
                "win32": "Download from: https://github.com/oschwartz10612/poppler-windows/releases"
            }.get(platform, "Please install poppler for your system")
            
            raise SystemError(f"Poppler not found!\n{instructions}")

    def download_pdf(self, url: str) -> str:
        """
        Download PDF from URL.

        Args:
            url: PDF file URL

        Returns:
            Path to downloaded PDF
        """
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            temp_pdf = tempfile.NamedTemporaryFile(
                suffix='.pdf',
                dir=self.temp_dir,
                delete=False
            )
            
            with temp_pdf as pdf_file:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        pdf_file.write(chunk)
                        
            return temp_pdf.name
            
        except requests.RequestException as e:
            raise Exception(f"Failed to download PDF: {str(e)}")

    def convert_pdf_to_images(self,
                            pdf_path: Union[str, Path],
                            output_dir: Union[str, Path],
                            dpi: int = 200,
                            fmt: str = 'PNG',
                            first_page: Optional[int] = None,
                            last_page: Optional[int] = None,
                            cleanup: bool = False) -> List[str]:
        """
        Core conversion method used by both local and URL conversion.

        Args:
            pdf_path: Path to PDF file
            output_dir: Directory to save images
            dpi: Image quality (dots per inch)
            fmt: Output format ('PNG', 'JPEG', etc.)
            first_page: Start page number (optional)
            last_page: End page number (optional)
            cleanup: Whether to delete the PDF after conversion

        Returns:
            List of paths to generated images
        """
        try:
            # Ensure paths are Path objects
            pdf_path = Path(pdf_path)
            output_dir = Path(output_dir)
            
            # Validate PDF file
            if not pdf_path.exists():
                raise FileNotFoundError(f"PDF not found: {pdf_path}")
            
            # Create output directory
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Convert PDF pages to images
            images = convert_from_path(
                pdf_path,
                dpi=dpi,
                first_page=first_page,
                last_page=last_page
            )
            
            # Save images
            image_paths = []
            for i, image in enumerate(images, start=1):
                image_path = output_dir / f"page_{i}.{fmt.lower()}"
                image.save(str(image_path), fmt)
                image_paths.append(str(image_path))
            
            return image_paths
            
        except Exception as e:
            raise Exception(f"PDF conversion failed: {str(e)}")
            
        finally:
            # Cleanup if requested and file exists
            if cleanup and pdf_path.exists():
                try:
                    pdf_path.unlink()
                except Exception as e:
                    self.logger.warning(f"Failed to delete temporary file: {str(e)}")