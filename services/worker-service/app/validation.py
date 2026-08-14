"""
validation.py

OCR Result Validation

Responsibilities

1. Remove empty words
2. Remove low confidence words
3. Remove garbage characters
4. Remove duplicate words
5. Validate OCR result
"""

import re

from .ace_logger import AceLogger
from .config import Config


logger = AceLogger.get_logger("ocr_validator")


class OCRValidator:

    """
    Validate OCR Output.
    """

    def __init__(self):

        logger.info("OCR Validator Initialized.")

    # ==========================================================
    # Main Validation
    # ==========================================================

    def validate(
        self,
        ocr_result
    ):
        """
        Validate complete OCR result.
        """

        logger.info("=" * 70)
        logger.info("Starting OCR Validation...")

        pages = []

        for page in ocr_result["pages"]:

            cleaned = self.validate_page(page)

            pages.append(cleaned)

        text = self.build_text(pages)

        logger.info("Validation Completed.")

        return {

            "engine": ocr_result["engine"],

            "pages": pages,

            "text": text,

            "total_pages": len(pages)

        }

    # ==========================================================
    # Validate Single Page
    # ==========================================================

    def validate_page(
        self,
        page
    ):

        words = []

        seen = set()

        for word in page["words"]:

            text = word["text"].strip()

            confidence = float(word["confidence"])

            # -----------------------------------
            # Empty
            # -----------------------------------

            if text == "":
                continue

            # -----------------------------------
            # Confidence
            # -----------------------------------

            if confidence < Config.MIN_CONFIDENCE:
                continue

            # -----------------------------------
            # Garbage Characters
            # -----------------------------------

            text = self.remove_garbage(text)

            if text == "":
                continue

            # -----------------------------------
            # Duplicate
            # -----------------------------------

            key = (

                text,

                word["bounding_box"]["x"],

                word["bounding_box"]["y"]

            )

            if key in seen:
                continue

            seen.add(key)

            word["text"] = text

            words.append(word)

        logger.info(

            f"Page {page['page']} : "

            f"{len(words)} words"

        )

        return {

            "page": page["page"],

            "engine": page["engine"],

            "words": words

        }

    # ==========================================================
    # Garbage Removal
    # ==========================================================

    def remove_garbage(
        self,
        text
    ):

        text = re.sub(

            r"[^\w\s.,:/()-]",

            "",

            text

        )

        text = re.sub(

            r"\s+",

            " ",

            text

        )

        return text.strip()

    # ==========================================================
    # Build Text
    # ==========================================================

    def build_text(
        self,
        pages
    ):

        all_words = []

        for page in pages:

            for word in page["words"]:

                all_words.append(

                    word["text"]

                )

        return " ".join(all_words)