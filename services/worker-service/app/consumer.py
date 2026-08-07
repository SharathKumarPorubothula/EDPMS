"""
consumer.py
Kafka Consumer for OCR Processing

Flow

Kafka
   │
   ▼
Receive Message
   │
   ▼
Validate Payload
   │
   ▼
Locate PDF
   │
   ▼
Run OCR
   │
   ▼
Process OCR Result (Validate → Extract → Write → Save)
"""

import json
import os

from kafka import KafkaConsumer

from ace_logger import AceLogger
from config import Config
from db_utils import DBUtils

# These modules are used by the pipeline
from ocr_engine import OCREngine
from output_writer import OutputWriter
from validation import OCRValidator
from field_extractor import FieldExtractor

logger = AceLogger.get_logger("ocr_consumer")


class OCRConsumer:
    """
    Kafka Consumer responsible for
    • Receiving Kafka messages
    • Loading PDF
    • Calling OCR Engine
    • Saving Output
    • Storing Database
    """

    def __init__(self, db_connection):
        """
        Initialize OCR Consumer.

        Args:
            db_connection:
                PostgreSQL connection object.
        """

        self.db_connection = db_connection
        self.running = True

        logger.info("=" * 70)
        logger.info("Initializing Kafka Consumer...")

        self.consumer = KafkaConsumer(
            Config.KAFKA_TOPIC,
            bootstrap_servers=Config.KAFKA_BOOTSTRAP_SERVERS,
            group_id=Config.KAFKA_GROUP_ID,
            auto_offset_reset=Config.KAFKA_AUTO_OFFSET_RESET,
            enable_auto_commit=Config.ENABLE_AUTO_COMMIT,
            value_deserializer=lambda x: json.loads(x.decode("utf-8"))
        )

        logger.info("Kafka Consumer initialized successfully.")
        logger.info("=" * 70)

    # =======================================================
    # Start Consumer
    # =======================================================

    def start(self):
        """
        Start listening to the Kafka Topic.
        """

        logger.info(f"Listening Topic : {Config.KAFKA_TOPIC}")

        while self.running:
            try:
                for message in self.consumer:

                    if not self.running:
                        break

                    payload = message.value

                    logger.info("=" * 70)
                    logger.info("Kafka Message Received")
                    logger.info(payload)

                    self.process_message(payload)

                    logger.info("=" * 70)

            except Exception as ex:
                logger.exception(f"Kafka Consumer Error : {ex}")

    # =======================================================
    # Process Kafka Message
    # =======================================================

    def process_message(self, payload):
        """
        Process a single Kafka message.

        Flow

        Kafka
            │
            ▼
        Validate Payload
            │
            ▼
        Locate PDF
            │
            ▼
        Run OCR
            │
            ▼
        Save Outputs
            │
            ▼
        Insert Database
        """

        try:

            logger.info("Validating Kafka Payload...")

            # -----------------------------------------
            # Read payload values
            # -----------------------------------------

            document_id = payload.get("document_id")
            filename = payload.get("filename")
            image_names = payload.get("images", [])
            status = payload.get("status")

            if not document_id:
                logger.error("document_id missing.")
                return

            if not filename:
                logger.error("filename missing.")
                return

            logger.info(f"Document ID : {document_id}")
            logger.info(f"Filename    : {filename}")
            logger.info(f"Images      : {len(image_names)}")

            # -----------------------------------------
            # Locate PDF
            # -----------------------------------------

            pdf_path = os.path.join(
                Config.WEBFILES_PATH,
                document_id,
                filename
            )

            logger.info(f"PDF Path : {pdf_path}")

            # -----------------------------------------
            # Validate PDF
            # -----------------------------------------

            if not os.path.exists(pdf_path):
                logger.error("PDF not found.")
                logger.error(pdf_path)
                return

            if not os.path.isfile(pdf_path):
                logger.error("Invalid PDF path.")
                return

            logger.info("PDF Found Successfully.")

            # -----------------------------------------
            # Output Folder
            # -----------------------------------------

            output_folder = os.path.join(
                Config.WEBFILES_PATH,
                document_id,
                Config.OUTPUT_FOLDER
            )

            os.makedirs(output_folder, exist_ok=True)

            logger.info(f"Output Folder : {output_folder}")

            # -----------------------------------------
            # Run OCR
            # -----------------------------------------

            logger.info("=" * 70)
            logger.info("Starting OCR Engine...")

            ocr_engine = OCREngine()

            ocr_result = ocr_engine.process_pdf(
                pdf_path=pdf_path,
                output_folder=output_folder
            )

            logger.info("OCR Completed Successfully.")

            # -----------------------------------------
            # Continue
            # -----------------------------------------

            if ocr_result is None:
                logger.error("OCR returned empty result.")
                return

            logger.info("OCR Result Ready.")

            # -----------------------------------------
            # Next Part
            # -----------------------------------------

            logger.info("Proceeding to Validation...")

            self.process_ocr_result(
                document_id,
                output_folder,
                ocr_result
            )

        except Exception as ex:
            logger.exception(f"Message Processing Failed : {ex}")

    # =======================================================
    # Process OCR Result
    # =======================================================

    def process_ocr_result(
        self,
        document_id,
        output_folder,
        ocr_result
    ):
        """
        Process OCR Result.

        Flow

        OCR Result
            │
            ▼
        Validation
            │
            ▼
        Field Extraction
            │
            ▼
        Write Output Files
            │
            ▼
        Store Database
        """

        try:
            logger.info("=" * 70)
            logger.info("Starting OCR Validation...")

            validator = OCRValidator()
            validated_result = validator.validate(ocr_result)

            logger.info("Validation completed.")

            # -------------------------------------
            # Extract Fields
            # -------------------------------------

            logger.info("Extracting Fields...")

            extractor = FieldExtractor()
            extracted_fields = extractor.extract(validated_result)

            logger.info(f"Fields Extracted : {len(extracted_fields)}")

            # -------------------------------------
            # Generate Output Files
            # -------------------------------------

            logger.info("Generating Output Files...")

            writer = OutputWriter()
            writer.write_outputs(
                output_folder=output_folder,
                document_id=document_id,
                ocr_result=validated_result
            )

            logger.info("Output files generated.")

            # -------------------------------------
            # Save Database
            # -------------------------------------

            self.save_extracted_fields(document_id, extracted_fields)

            logger.info("Database updated.")
            logger.info("=" * 70)

        except Exception as ex:
            logger.exception(f"OCR Result Processing Failed : {ex}")

    # =======================================================
    # Store Database
    # =======================================================

    def save_extracted_fields(self, document_id, extracted_fields):
        """
        Save extracted fields into PostgreSQL.
        """

        try:
            logger.info("Saving extracted fields...")

            query = """
            INSERT INTO extracted_data
            (
                document_id,
                field_name,
                field_value,
                confidence,
                created_at
            )
            VALUES
            (
                %s,
                %s,
                %s,
                %s,
                NOW()
            )
            """

            for field in extracted_fields:
                params = (
                    document_id,
                    field["field_name"],
                    field["field_value"],
                    field["confidence"]
                )

                DBUtils.execute(
                    self.db_connection,
                    query,
                    params
                )

                logger.info(f"Inserted : {field['field_name']}")

            logger.info("All extracted fields saved successfully.")

        except Exception as ex:
            logger.exception(f"Database Insert Failed : {ex}")
            raise

    # =======================================================
    # Stop Consumer
    # =======================================================

    def stop(self):
        """
        Stop Kafka Consumer.
        """

        logger.info("Stopping Kafka Consumer...")
        self.running = False

        if self.consumer:
            self.consumer.close()

        logger.info("Kafka Consumer stopped.")