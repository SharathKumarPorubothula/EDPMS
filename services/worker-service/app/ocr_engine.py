"""
ocr_engine.py

OCR Engine

Responsibilities
1. Load PDF
2. Convert PDF into Images
3. Preprocess Images
4. Perform OCR
5. Return OCR Result
"""

import os

import cv2
import pytesseract
from pdf2image import convert_from_path
from paddleocr import PaddleOCR

from .ace_logger import AceLogger
from .config import Config
from .image_preprocessing import ImagePreprocessor

logger = AceLogger.get_logger("ocr_engine")


class OCREngine:
    """
    OCR Engine
    """

    def __init__(self):
        logger.info("=" * 70)
        logger.info("Initializing OCR Engine...")
        logger.info(f"OCR Engine : {Config.OCR_ENGINE}")
        logger.info("=" * 70)

    # ======================================================
    # Process PDF (Main Entry Point)
    # ======================================================
    def process_pdf(
        self,
        pdf_path,
        output_folder
    ):
        """
        Complete OCR Pipeline.

        PDF
            │
            ▼
        Convert PDF -> Images
            │
            ▼
        Preprocess Image
            │
            ▼
        OCR
            │
            ▼
        Collect OCR Result
            │
            ▼
        Return Standard OCR Result
        """
        logger.info("=" * 70)
        logger.info(f"Processing PDF : {pdf_path}")

        pages = self.convert_pdf_to_images(pdf_path)
        logger.info(f"Total Pages : {len(pages)}")

        page_results = []
        full_text = []
        total_words = 0
        total_confidence = 0

        for page_number, page in enumerate(pages, start=1):
            logger.info("-" * 60)
            logger.info(f"Processing Page : {page_number}")

            image_path = os.path.join(
                output_folder,
                f"page_{page_number}.png"
            )
            page.save(image_path, Config.IMAGE_FORMAT)
            logger.info(f"Image Saved : {image_path}")

            page_result = self.process_image(image_path, page_number)
            page_results.append(page_result)

            for word in page_result["words"]:
                full_text.append(word["text"])
                total_words += 1
                total_confidence += word["confidence"]

        average_confidence = 0
        if total_words > 0:
            average_confidence = total_confidence / total_words

        logger.info("=" * 70)
        logger.info("OCR Completed")
        logger.info(f"Words       : {total_words}")
        logger.info(f"Confidence  : {average_confidence:.2f}")

        return {
            "engine": Config.OCR_ENGINE,
            "pages": page_results,
            "text": " ".join(full_text),
            "total_pages": len(page_results),
            "total_words": total_words,
            "average_confidence": round(average_confidence, 2)
        }

    # ======================================================
    # Convert PDF
    # ======================================================
    def convert_pdf_to_images(
        self,
        pdf_path
    ):
        """
        Convert PDF into images.
        """
        try:
            logger.info("Loading PDF...")
            pages = convert_from_path(
                pdf_path,
                dpi=Config.IMAGE_DPI
            )
            logger.info(f"Converted {len(pages)} pages.")
            return pages
        except Exception as ex:
            logger.exception(f"PDF Conversion Failed : {ex}")
            raise

    # ======================================================
    # Process Image
    # ======================================================
    def process_image(
        self,
        image_path,
        page_number
    ):
        """
        Process a single page image.

        Flow
        Image
            │
            ▼
        Preprocessing
            │
            ▼
        OCR
        """
        try:
            logger.info(f"Starting preprocessing for Page {page_number}")
            preprocessor = ImagePreprocessor()
            processed_image = preprocessor.process(image_path)
            logger.info("Image preprocessing completed.")

            logger.info("Starting OCR...")
            page_result = self.run_ocr(processed_image, page_number)
            logger.info("OCR completed.")

            return page_result
        except Exception as ex:
            logger.exception(f"Image Processing Failed : {ex}")
            raise

    # ======================================================
    # OCR Dispatcher
    # ======================================================
    def run_ocr(
        self,
        image_path,
        page_number
    ):
        """
        Select OCR Engine.
        """
        logger.info(f"OCR Engine : {Config.OCR_ENGINE}")

        if Config.OCR_ENGINE.lower() == "abbyy":
            return self.run_abbyy(image_path, page_number)
        elif Config.OCR_ENGINE.lower() == "paddleocr":
            return self.run_paddle(image_path, page_number)
        else:
            return self.run_tesseract(image_path, page_number)

    # ======================================================
    # Tesseract OCR
    # ======================================================
    def run_tesseract(
        self,
        image_path,
        page_number
    ):
        logger.info("Running Tesseract OCR...")

        pytesseract.pytesseract.tesseract_cmd = Config.TESSERACT_CMD
        image = cv2.imread(image_path)

        data = pytesseract.image_to_data(
            image,
            lang=Config.OCR_LANGUAGE,
            output_type=pytesseract.Output.DICT
        )

        words = []
        total = len(data["text"])
        for i in range(total):
            text = data["text"][i].strip()
            if text == "":
                continue

            confidence = float(data["conf"][i])
            x = data["left"][i]
            y = data["top"][i]
            width = data["width"][i]
            height = data["height"][i]

            words.append({
                "text": text,
                "confidence": confidence,
                "bounding_box": {
                    "x": x,
                    "y": y,
                    "width": width,
                    "height": height
                }
            })

        logger.info(f"Detected {len(words)} words.")

        return {
            "page": page_number,
            "engine": "tesseract",
            "words": words
        }

    # ======================================================
    # Paddle OCR
    # ======================================================
    def run_paddle(
        self,
        image_path,
        page_number
    ):
        logger.info("Running PaddleOCR...")

        ocr = PaddleOCR(
            use_angle_cls=True,
            lang="en"
        )
        result = ocr.ocr(image_path, cls=True)

        words = []
        for line in result[0]:
            bbox = line[0]
            text = line[1][0]
            confidence = line[1][1]
            words.append({
                "text": text,
                "confidence": confidence,
                "bounding_box": bbox
            })

        logger.info(f"Detected {len(words)} words.")

        return {
            "page": page_number,
            "engine": "paddleocr",
            "words": words
        }

    # ======================================================
    # ABBYY OCR
    # ======================================================
    def run_abbyy(
        self,
        image_path,
        page_number
    ):
        logger.info("Running ABBYY OCR...")
        #
        # ABBYY SDK processing
        # will come here.
        #
        raise NotImplementedError(
            "ABBYY SDK integration not implemented."
        )