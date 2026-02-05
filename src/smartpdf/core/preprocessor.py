"""Image preprocessing for better OCR quality."""
import numpy as np
import cv2
from PIL import Image
import logging
from typing import Tuple, Optional

logger = logging.getLogger(__name__)


class ImagePreprocessor:
    """Preprocess images to improve OCR accuracy."""
    
    def __init__(
        self,
        target_dpi: int = 300,
        denoise: bool = True,
        deskew: bool = True,
        enhance_contrast: bool = True
    ):
        """Initialize preprocessor.
        
        Args:
            target_dpi: Target DPI for upscaling low-res images
            denoise: Apply denoising
            deskew: Correct image skew
            enhance_contrast: Enhance image contrast
        """
        self.target_dpi = target_dpi
        self.denoise = denoise
        self.deskew = deskew
        self.enhance_contrast = enhance_contrast
    
    def process(self, image: Image.Image) -> Image.Image:
        """Process image through all preprocessing steps.
        
        Args:
            image: Input PIL Image
        
        Returns:
            Processed PIL Image
        """
        # Convert PIL to numpy array
        img_array = np.array(image)
        
        # Convert to grayscale if color
        if len(img_array.shape) == 3:
            img_array = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        
        # Denoise
        if self.denoise:
            img_array = self._denoise(img_array)
        
        # Deskew
        if self.deskew:
            img_array = self._deskew(img_array)
        
        # Enhance contrast
        if self.enhance_contrast:
            img_array = self._enhance_contrast(img_array)
        
        # Convert back to PIL
        return Image.fromarray(img_array)
    
    def _denoise(self, img: np.ndarray) -> np.ndarray:
        """Apply denoising."""
        return cv2.fastNlMeansDenoising(img, None, 10, 7, 21)
    
    def _deskew(self, img: np.ndarray) -> np.ndarray:
        """Correct image skew using Hough transform."""
        # Detect edges
        edges = cv2.Canny(img, 50, 150, apertureSize=3)
        
        # Detect lines
        lines = cv2.HoughLines(edges, 1, np.pi / 180, 200)
        
        if lines is None:
            return img
        
        # Calculate average angle
        angles = []
        for rho, theta in lines[:, 0]:
            angle = np.degrees(theta) - 90
            if -45 < angle < 45:
                angles.append(angle)
        
        if not angles:
            return img
        
        median_angle = np.median(angles)
        
        # Only correct if angle is significant
        if abs(median_angle) < 0.5:
            return img
        
        # Rotate image
        (h, w) = img.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, median_angle, 1.0)
        rotated = cv2.warpAffine(
            img, M, (w, h),
            flags=cv2.INTER_CUBIC,
            borderMode=cv2.BORDER_REPLICATE
        )
        
        logger.debug(f"Deskewed image by {median_angle:.2f} degrees")
        return rotated
    
    def _enhance_contrast(self, img: np.ndarray) -> np.ndarray:
        """Enhance image contrast using CLAHE."""
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        return clahe.apply(img)
    
    def upscale(self, image: Image.Image, scale_factor: float = 2.0) -> Image.Image:
        """Upscale low-resolution image.
        
        Args:
            image: Input PIL Image
            scale_factor: Upscaling factor
        
        Returns:
            Upscaled PIL Image
        """
        new_size = (
            int(image.width * scale_factor),
            int(image.height * scale_factor)
        )
        return image.resize(new_size, Image.Resampling.LANCZOS)