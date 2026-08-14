"""
image_preprocessing.py

Image preprocessing for OCR.

Responsibilities:
1. Load image
2. Convert to grayscale
3. Remove noise
4. Improve contrast
5. Apply thresholding
6. Save processed image
"""

import os
import cv2

from .ace_logger import AceLogger


logger = AceLogger.get_logger("image_preprocessing")


class ImagePreprocessor:
    """
    Preprocess images before OCR.
    """

    def __init__(self):
        logger.info("Image Preprocessor initialized.")

    def process(self, image_path):
        """
        Preprocess the input image and return
        the path of the processed image.
        """

        try:
            logger.info("=" * 60)
            logger.info(f"Preprocessing image : {image_path}")

            # ------------------------------------------------
            # Validate input
            # ------------------------------------------------

            if not os.path.exists(image_path):
                raise FileNotFoundError(
                    f"Image not found: {image_path}"
                )

            # ------------------------------------------------
            # Read image
            # ------------------------------------------------

            image = cv2.imread(image_path)

            if image is None:
                raise ValueError(
                    f"Unable to read image: {image_path}"
                )

            logger.info(
                f"Original image size : "
                f"{image.shape[1]}x{image.shape[0]}"
            )

            # ------------------------------------------------
            # Convert to grayscale
            # ------------------------------------------------

            gray = cv2.cvtColor(
                image,
                cv2.COLOR_BGR2GRAY
            )

            # ------------------------------------------------
            # Remove noise
            # ------------------------------------------------

            denoised = cv2.GaussianBlur(
                gray,
                (3, 3),
                0
            )

            # ------------------------------------------------
            # Improve contrast / threshold
            # ------------------------------------------------

            processed = cv2.threshold(
                denoised,
                0,
                255,
                cv2.THRESH_BINARY + cv2.THRESH_OTSU
            )[1]

            # ------------------------------------------------
            # Create output path
            # ------------------------------------------------

            directory = os.path.dirname(image_path)

            filename = os.path.basename(image_path)

            name, extension = os.path.splitext(filename)

            output_path = os.path.join(
                directory,
                f"{name}_processed{extension}"
            )

            # ------------------------------------------------
            # Save processed image
            # ------------------------------------------------

            success = cv2.imwrite(
                output_path,
                processed
            )

            if not success:
                raise IOError(
                    f"Failed to save processed image: "
                    f"{output_path}"
                )

            logger.info(
                f"Processed image saved : {output_path}"
            )

            logger.info("=" * 60)

            return output_path

        except Exception as ex:

            logger.exception(
                f"Image preprocessing failed : {ex}"
            )

            raise