"""
output_writer.py
Generate OCR output files.

Supported Outputs
1. JSON
2. TXT
3. XML
4. Searchable PDF
"""

import os
import json
import xml.etree.ElementTree as ET

from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

from ace_logger import AceLogger
from config import Config

logger = AceLogger.get_logger("output_writer")


class OutputWriter:
    """
    Write OCR output files.
    """

    def __init__(self):
        logger.info("=" * 70)
        logger.info("Initializing Output Writer")
        logger.info("=" * 70)

    # =====================================================
    # Main Entry
    # =====================================================

    def write_outputs(
        self,
        output_folder,
        document_id,
        ocr_result
    ):
        logger.info("Generating Output Files...")

        os.makedirs(
            output_folder,
            exist_ok=True
        )

        if Config.GENERATE_JSON:
            self.write_json(
                output_folder,
                document_id,
                ocr_result
            )

        if Config.GENERATE_TXT:
            self.write_txt(
                output_folder,
                document_id,
                ocr_result
            )

        if Config.GENERATE_XML:
            self.write_xml(
                output_folder,
                document_id,
                ocr_result
            )

        if Config.GENERATE_SEARCHABLE_PDF:
            self.write_searchable_pdf(
                output_folder,
                document_id,
                ocr_result
            )

        logger.info("All Output Files Generated.")

    # =====================================================
    # JSON Writer
    # =====================================================

    def write_json(
        self,
        output_folder,
        document_id,
        ocr_result
    ):
        """
        Generate JSON output.
        """

        try:

            json_file = os.path.join(
                output_folder,
                "ocr_result.json"
            )

            logger.info(
                f"Writing JSON : {json_file}"
            )

            with open(
                json_file,
                "w",
                encoding="utf-8"
            ) as fp:

                json.dump(
                    ocr_result,
                    fp,
                    indent=4,
                    ensure_ascii=False
                )

            logger.info(
                "JSON generated successfully."
            )

        except Exception as ex:

            logger.exception(
                f"JSON Generation Failed : {ex}"
            )

            raise

    # =====================================================
    # TXT Writer
    # =====================================================

    def write_txt(
        self,
        output_folder,
        document_id,
        ocr_result
    ):
        """
        Generate TXT output.
        """

        try:

            txt_file = os.path.join(
                output_folder,
                "ocr_result.txt"
            )

            logger.info(
                f"Writing TXT : {txt_file}"
            )

            with open(
                txt_file,
                "w",
                encoding="utf-8"
            ) as fp:

                fp.write("=" * 60 + "\n")
                fp.write("OCR RESULT\n")
                fp.write("=" * 60 + "\n\n")

                fp.write(
                    f"Engine : {ocr_result['engine']}\n"
                )

                fp.write(
                    f"Pages : {ocr_result['total_pages']}\n\n"
                )

                for page in ocr_result["pages"]:

                    fp.write("-" * 60 + "\n")

                    fp.write(
                        f"Page : {page['page']}\n"
                    )

                    fp.write("-" * 60 + "\n")

                    for word in page["words"]:

                        fp.write(
                            f"{word['text']} "
                        )

                    fp.write("\n\n")

                fp.write("=" * 60 + "\n")
                fp.write("FULL TEXT\n")
                fp.write("=" * 60 + "\n\n")

                fp.write(
                    ocr_result["text"]
                )

            logger.info(
                "TXT generated successfully."
            )

        except Exception as ex:

            logger.exception(
                f"TXT Generation Failed : {ex}"
            )

            raise

    # =====================================================
    # XML Writer
    # =====================================================

    def write_xml(
        self,
        output_folder,
        document_id,
        ocr_result
    ):
        """
        Generate XML output.
        """

        try:

            xml_file = os.path.join(
                output_folder,
                "ocr_result.xml"
            )

            logger.info(
                f"Writing XML : {xml_file}"
            )

            # ----------------------------------------
            # Root
            # ----------------------------------------

            root = ET.Element("OCRResult")

            root.set(
                "document_id",
                document_id
            )

            root.set(
                "engine",
                ocr_result["engine"]
            )

            root.set(
                "total_pages",
                str(ocr_result["total_pages"])
            )

            # ----------------------------------------
            # Pages
            # ----------------------------------------

            pages_node = ET.SubElement(
                root,
                "Pages"
            )

            for page in ocr_result["pages"]:

                page_node = ET.SubElement(
                    pages_node,
                    "Page"
                )

                page_node.set(
                    "number",
                    str(page["page"])
                )

                words_node = ET.SubElement(
                    page_node,
                    "Words"
                )

                for word in page["words"]:

                    word_node = ET.SubElement(
                        words_node,
                        "Word"
                    )

                    # -------------------------------
                    # Text
                    # -------------------------------

                    text_node = ET.SubElement(
                        word_node,
                        "Text"
                    )

                    text_node.text = word["text"]

                    # -------------------------------
                    # Confidence
                    # -------------------------------

                    confidence_node = ET.SubElement(
                        word_node,
                        "Confidence"
                    )

                    confidence_node.text = str(
                        word["confidence"]
                    )

                    # -------------------------------
                    # Bounding Box
                    # -------------------------------

                    bbox = word["bounding_box"]

                    bbox_node = ET.SubElement(
                        word_node,
                        "BoundingBox"
                    )

                    bbox_node.set(
                        "x",
                        str(bbox["x"])
                    )

                    bbox_node.set(
                        "y",
                        str(bbox["y"])
                    )

                    bbox_node.set(
                        "width",
                        str(bbox["width"])
                    )

                    bbox_node.set(
                        "height",
                        str(bbox["height"])
                    )

            # ----------------------------------------
            # Full Text
            # ----------------------------------------

            full_text = ET.SubElement(
                root,
                "FullText"
            )

            full_text.text = ocr_result["text"]

            # ----------------------------------------
            # Write XML
            # ----------------------------------------

            tree = ET.ElementTree(root)

            ET.indent(
                tree,
                space="    ",
                level=0
            )

            tree.write(

                xml_file,

                encoding="utf-8",

                xml_declaration=True

            )

            logger.info(
                "XML generated successfully."
            )

        except Exception as ex:

            logger.exception(
                f"XML Generation Failed : {ex}"
            )

            raise

    # =====================================================
    # Searchable PDF
    # =====================================================

    def write_searchable_pdf(
        self,
        output_folder,
        document_id,
        ocr_result
    ):
        """
        Generate a PDF containing OCR text.

        NOTE:
        This is NOT a true searchable PDF with an invisible
        text layer. It creates a PDF from the recognized text.
        """

        try:

            pdf_file = os.path.join(
                output_folder,
                "searchable.pdf"
            )

            logger.info(
                f"Writing PDF : {pdf_file}"
            )

            doc = SimpleDocTemplate(pdf_file)

            styles = getSampleStyleSheet()

            story = []

            story.append(
                Paragraph(
                    "<b>OCR Result</b>",
                    styles["Heading1"]
                )
            )

            story.append(
                Paragraph(
                    ocr_result["text"],
                    styles["BodyText"]
                )
            )

            doc.build(story)

            logger.info(
                "PDF generated successfully."
            )

        except Exception as ex:

            logger.exception(
                f"PDF Generation Failed : {ex}"
            )

            raise