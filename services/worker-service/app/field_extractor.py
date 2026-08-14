"""
field_extractor.py
Business Field Extraction
Extracts business fields from validated OCR output.
"""
import re
from .ace_logger import AceLogger

logger = AceLogger.get_logger("field_extractor")


class FieldExtractor:
    """
    Extract business fields from OCR.
    """

    def __init__(self):
        logger.info("=" * 70)
        logger.info("Initializing Field Extractor")
        logger.info("=" * 70)

    # =====================================================
    # Main Entry
    # =====================================================
    def extract(self, ocr_result):
        """
        Extract all business fields.
        """
        logger.info("Building searchable text...")
        searchable_text = self.build_text(ocr_result)

        extracted_fields = []

        logger.info("Extracting Invoice Number...")
        extracted_fields.extend(self.extract_invoice_number(searchable_text))

        logger.info("Extracting Invoice Date...")
        extracted_fields.extend(self.extract_invoice_date(searchable_text))

        logger.info("Extracting Vendor...")
        extracted_fields.extend(self.extract_vendor(searchable_text))

        logger.info("Extracting GST...")
        extracted_fields.extend(self.extract_gst(searchable_text))

        logger.info("Extracting PAN...")
        extracted_fields.extend(self.extract_pan(searchable_text))

        logger.info("Extracting PO Number...")
        extracted_fields.extend(self.extract_po_number(searchable_text))

        logger.info("Extracting Amount...")
        extracted_fields.extend(self.extract_amount(searchable_text))

        logger.info(f"Total Fields : {len(extracted_fields)}")
        return extracted_fields

    # =====================================================
    # Build Text
    # =====================================================
    def build_text(self, ocr_result):
        lines = []
        for page in ocr_result["pages"]:
            for word in page["words"]:
                lines.append(word["text"])
        return " ".join(lines)

    # =====================================================
    # Invoice Number
    # =====================================================
    def extract_invoice_number(self, text):
        logger.info("Searching Invoice Number...")
        patterns = [
            r"Invoice\s*No\.?\s*[:\-]?\s*([A-Za-z0-9\-\/]+)",
            r"Invoice\s*Number\s*[:\-]?\s*([A-Za-z0-9\-\/]+)",
            r"Inv\s*No\.?\s*[:\-]?\s*([A-Za-z0-9\-\/]+)",
            r"Bill\s*No\.?\s*[:\-]?\s*([A-Za-z0-9\-\/]+)"
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                invoice_no = match.group(1)
                logger.info(f"Invoice Number : {invoice_no}")
                return [{
                    "field_name": "Invoice Number",
                    "field_value": invoice_no,
                    "confidence": 98.0
                }]
        logger.warning("Invoice Number not found.")
        return []

    # =====================================================
    # Invoice Date
    # =====================================================
    def extract_invoice_date(self, text):
        logger.info("Searching Invoice Date...")
        patterns = [
            r"Invoice\s*Date\s*[:\-]?\s*(\d{2}[\/\-]\d{2}[\/\-]\d{4})",
            r"Date\s*[:\-]?\s*(\d{2}[\/\-]\d{2}[\/\-]\d{4})",
            r"Invoice\s*Date\s*[:\-]?\s*(\d{2}\.\d{2}\.\d{4})",
            r"Date\s*[:\-]?\s*(\d{2}\.\d{2}\.\d{4})"
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                invoice_date = match.group(1)
                logger.info(f"Invoice Date : {invoice_date}")
                return [{
                    "field_name": "Invoice Date",
                    "field_value": invoice_date,
                    "confidence": 98.0
                }]
        logger.warning("Invoice Date not found.")
        return []

    # =====================================================
    # Vendor Name
    # =====================================================
    def extract_vendor(self, text):
        logger.info("Searching Vendor Name...")
        patterns = [
            r"Vendor\s*[:\-]?\s*([A-Za-z0-9\s&.,()-]+)",
            r"Supplier\s*[:\-]?\s*([A-Za-z0-9\s&.,()-]+)",
            r"M/s\.?\s*([A-Za-z0-9\s&.,()-]+)",
            r"Sold\s*By\s*[:\-]?\s*([A-Za-z0-9\s&.,()-]+)"
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                vendor = match.group(1).strip()
                logger.info(f"Vendor : {vendor}")
                return [{
                    "field_name": "Vendor",
                    "field_value": vendor,
                    "confidence": 96.0
                }]
        logger.warning("Vendor not found.")
        return []

    # =====================================================
    # GST Number
    # =====================================================
    def extract_gst(self, text):
        logger.info("Searching GST Number...")
        pattern = r"\b\d{2}[A-Z]{5}\d{4}[A-Z]{1}[A-Z0-9]{1}Z[A-Z0-9]{1}\b"
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            gst = match.group(0)
            logger.info(f"GST : {gst}")
            return [{
                "field_name": "GST",
                "field_value": gst,
                "confidence": 99.0
            }]
        logger.warning("GST not found.")
        return []

    # =====================================================
    # PAN Number
    # =====================================================
    def extract_pan(self, text):
        logger.info("Searching PAN Number...")
        pattern = r"\b[A-Z]{5}[0-9]{4}[A-Z]{1}\b"
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            pan = match.group(0)
            logger.info(f"PAN : {pan}")
            return [{
                "field_name": "PAN",
                "field_value": pan,
                "confidence": 99.0
            }]
        logger.warning("PAN not found.")
        return []

    # =====================================================
    # Purchase Order Number
    # =====================================================
    def extract_po_number(self, text):
        logger.info("Searching PO Number...")
        patterns = [
            r"PO\s*No\.?\s*[:\-]?\s*([A-Za-z0-9\-\/]+)",
            r"Purchase\s*Order\s*No\.?\s*[:\-]?\s*([A-Za-z0-9\-\/]+)",
            r"Purchase\s*Order\s*[:\-]?\s*([A-Za-z0-9\-\/]+)"
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                po_number = match.group(1)
                logger.info(f"PO Number : {po_number}")
                return [{
                    "field_name": "PO Number",
                    "field_value": po_number,
                    "confidence": 97.0
                }]
        logger.warning("PO Number not found.")
        return []

    # =====================================================
    # Amount Extraction (Subtotal, GST Amount, Total Amount)
    # =====================================================
    def extract_amount(self, text):
        logger.info("Searching Amount Fields...")
        extracted_fields = []

        # --------------------------------------------
        # Sub Total
        # --------------------------------------------
        subtotal_patterns = [
            r"Sub\s*Total\s*[:\-]?\s*₹?\s*([\d,]+\.\d{2})",
            r"Subtotal\s*[:\-]?\s*₹?\s*([\d,]+\.\d{2})"
        ]
        for pattern in subtotal_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                extracted_fields.append({
                    "field_name": "Subtotal",
                    "field_value": match.group(1),
                    "confidence": 97.0
                })
                break

        # --------------------------------------------
        # GST Amount
        # --------------------------------------------
        gst_patterns = [
            r"GST\s*Amount\s*[:\-]?\s*₹?\s*([\d,]+\.\d{2})",
            r"CGST\s*[:\-]?\s*₹?\s*([\d,]+\.\d{2})",
            r"IGST\s*[:\-]?\s*₹?\s*([\d,]+\.\d{2})"
        ]
        for pattern in gst_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                extracted_fields.append({
                    "field_name": "GST Amount",
                    "field_value": match.group(1),
                    "confidence": 97.0
                })
                break

        # --------------------------------------------
        # Total Amount
        # --------------------------------------------
        total_patterns = [
            r"Grand\s*Total\s*[:\-]?\s*₹?\s*([\d,]+\.\d{2})",
            r"Invoice\s*Total\s*[:\-]?\s*₹?\s*([\d,]+\.\d{2})",
            r"Total\s*Amount\s*[:\-]?\s*₹?\s*([\d,]+\.\d{2})",
            r"Total\s*[:\-]?\s*₹?\s*([\d,]+\.\d{2})"
        ]
        for pattern in total_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                extracted_fields.append({
                    "field_name": "Total Amount",
                    "field_value": match.group(1),
                    "confidence": 98.0
                })
                break

        if len(extracted_fields) == 0:
            logger.warning("Amount not found.")
        else:
            logger.info(f"Extracted {len(extracted_fields)} amount field(s).")

        return extracted_fields