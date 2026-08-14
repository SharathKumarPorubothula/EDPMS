"""
EDPMS - Background Document Ingestion Service
================================================

Flow
----
1. Container starts
2. Poll INPUT_FOLDER every Config.POLL_INTERVAL seconds (default 5 min)
3. Pick up all PDFs found
4. Process them simultaneously (thread pool, Config.MAX_WORKERS)
5. Validate file is a real PDF (skip anything else)
6. Generate a document_id
7. Create WEBFILES_PATH/<document_id>/ and move the PDF into it
8. Create WEBFILES_PATH/<document_id>/images/, render every PDF page to a
   uniquely named image
9. Insert a row into the documents table
10. Publish a Kafka message
11. Keep running forever (no HTTP route, no external trigger)

Uses the project's existing utility modules:
    ace_logger.py  -> AceLogger
    config.py      -> Config
    db_utils.py    -> DBUtils

NOTE: This version is written entirely with module-level functions and
module-level state instead of classes (no DocumentWorker class).
"""

import json
import os
import shutil
import signal
import sys
import threading
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

from kafka import KafkaProducer
from pdf2image import convert_from_path

from .ace_logger import AceLogger
from .config import Config
from .db_utils import DBUtils


# ==========================================================
# Logger
# ==========================================================

logger = AceLogger.get_logger("document_ingestor")


# ==========================================================
# PostgreSQL connection
# ==========================================================
# DBUtils.get_connection() hands back a single psycopg2 connection
# (not a pool). psycopg2 connections are not safe for concurrent use
# by multiple threads at once, and PDFs are processed simultaneously
# via a ThreadPoolExecutor - so every DB call is serialized behind
# this lock.

db_connection = None
db_lock = threading.Lock()


def initialize_database():
    global db_connection
    db_connection = DBUtils.get_connection(
        host=Config.DB_HOST,
        port=Config.DB_PORT,
        database=Config.DB_NAME,
        username=Config.DB_USERNAME,
        password=Config.DB_PASSWORD
    )


# ==========================================================
# Kafka producer
# ==========================================================

producer = None


def initialize_kafka():
    global producer

    while producer is None:
        try:
            logger.info(
                f"Connecting to Kafka -> {Config.KAFKA_BOOTSTRAP_SERVERS}"
            )

            producer = KafkaProducer(
                bootstrap_servers=Config.KAFKA_BOOTSTRAP_SERVERS,
                value_serializer=lambda value: json.dumps(value).encode("utf-8"),
                retries=5,
                acks="all"
            )

            logger.info(
                f"Kafka producer initialized -> {Config.KAFKA_BOOTSTRAP_SERVERS}"
            )

        except Exception:
            logger.exception(
                "Kafka initialization failed. Retrying in 5 seconds..."
            )

            producer = None
            time.sleep(5)


def send_kafka_message(document_id, filename, image_names):
    if producer is None:
        logger.warning("Kafka producer not initialized, message skipped.")
        return

    payload = {
        "document_id": document_id,
        "filename": filename,
        "status": "COMPLETED",
        "image_count": len(image_names),
        "images": image_names,
        "created_at": datetime.now(timezone.utc).isoformat()
    }

    producer.send(Config.KAFKA_TOPIC, payload)
    producer.flush()
    logger.info(f"Kafka message sent : {document_id}")


# ==========================================================
# Utility functions
# ==========================================================

def generate_document_id():
    return str(uuid.uuid4())


def is_pdf(file_path):
    """
    Validate a PDF both by extension and by magic-number header,
    so a renamed non-PDF file doesn't slip through.
    """
    if not os.path.isfile(file_path):
        return False
    if not file_path.lower().endswith(".pdf"):
        return False
    try:
        with open(file_path, "rb") as fh:
            return fh.read(5) == b"%PDF-"
    except OSError:
        return False


def is_file_stable(file_path, wait_seconds=1.0):
    """
    Guard against picking up a file that's still being written
    (e.g. a slow copy into the input folder).
    """
    try:
        size_before = os.path.getsize(file_path)
        time.sleep(wait_seconds)
        size_after = os.path.getsize(file_path)
        return size_before == size_after
    except OSError:
        return False


def create_document_structure(document_id):
    """
    WEBFILES_PATH/
        <document_id>/
            images/
    """
    document_folder = Path(Config.WEBFILES_PATH) / document_id
    images_folder = document_folder / "images"
    images_folder.mkdir(parents=True, exist_ok=True)
    return str(document_folder), str(images_folder)


def move_pdf(source, destination_folder):
    destination = os.path.join(destination_folder, os.path.basename(source))
    shutil.move(source, destination)
    return destination


# ==========================================================
# Database operations (all serialized via db_lock - see note above)
# ==========================================================

def insert_document_record(document_id, filename, file_path,
                            file_size, file_type, status, image_names):
    query = """
        INSERT INTO documents
        (
            document_id, user_id, filename, file_path,
            file_size, file_type, status,
            created_at, updated_at, images_names
        )
        VALUES
        (
            %s, %s, %s, %s,
            %s, %s, %s,
            NOW(), NOW(), %s
        )
    """
    params = (
        document_id,
        Config.DEFAULT_USER_ID,
        filename,
        file_path,
        file_size,
        file_type,
        status,
        json.dumps(image_names)
    )

    with db_lock:
        DBUtils.execute(db_connection, query, params)

    logger.info(f"Inserted document record : {document_id}")


def mark_document_failed(document_id):
    query = """
        UPDATE documents
        SET status = 'FAILED', updated_at = NOW()
        WHERE document_id = %s
    """
    with db_lock:
        DBUtils.execute(db_connection, query, (document_id,))

    logger.info(f"Marked document as FAILED : {document_id}")


# ==========================================================
# PDF processing (runs inside a worker thread)
# ==========================================================

def process_pdf(pdf_path):
    document_id = generate_document_id()

    logger.info("=" * 70)
    logger.info(f"Started processing : {pdf_path}")
    logger.info(f"Document id        : {document_id}")

    try:
        # --- Re-validate (file could have changed between scan & pickup) ---
        if not is_pdf(pdf_path):
            logger.warning(f"Skipped - not a valid PDF : {pdf_path}")
            return

        if not is_file_stable(pdf_path):
            logger.warning(f"Skipped - file still being written : {pdf_path}")
            return

        # --- Create WEBFILES_PATH/<document_id>/ and .../images/ ---
        document_folder, images_folder = create_document_structure(document_id)
        logger.info(f"Created document folder : {document_folder}")

        # --- Move PDF into its document folder ---
        moved_pdf_path = move_pdf(pdf_path, document_folder)
        logger.info(f"Moved PDF -> {moved_pdf_path}")

        filename = os.path.basename(moved_pdf_path)
        file_size = os.path.getsize(moved_pdf_path)
        file_type = "application/pdf"

        # --- Render every page to a uniquely named image ---
        logger.info("Extracting pages...")
        pages = convert_from_path(
            moved_pdf_path,
            dpi=Config.IMAGE_DPI,
            poppler_path=os.getenv("POPPLER_PATH") or None
        )

        image_names = []
        for index, page in enumerate(pages, start=1):
            image_name = f"{document_id}_{index:04d}{Config.IMAGE_EXTENSION}"
            image_path = os.path.join(images_folder, image_name)
            page.save(image_path, Config.IMAGE_FORMAT)
            image_names.append(image_name)

        logger.info(f"Total images extracted : {len(image_names)}")

        # --- Insert DB record ---
        insert_document_record(
            document_id=document_id,
            filename=filename,
            file_path=moved_pdf_path,
            file_size=file_size,
            file_type=file_type,
            status="COMPLETED",
            image_names=image_names
        )

        # --- Publish Kafka message ---
        send_kafka_message(document_id, filename, image_names)

        logger.info(f"{filename} completed successfully.")

    except Exception:
        logger.exception(f"Processing failed for : {pdf_path}")
        try:
            mark_document_failed(document_id)
        except Exception:
            # The insert may never have happened (failure occurred before
            # it), in which case there is nothing to mark - that's fine.
            logger.debug(
                f"No document row to mark FAILED for {document_id} "
                f"(failure happened before insert)."
            )
    finally:
        logger.info("=" * 70)


# ==========================================================
# Worker state (module-level, replaces the DocumentWorker class)
# ==========================================================
# These globals hold everything the class used to keep as instance
# attributes (self.running, self.executor, self._in_flight, etc).

worker_running = True
worker_executor = None

# Tracks files currently in flight so a slow-processing file isn't
# submitted twice if a later scan runs before it's moved out of the
# input folder.
in_flight_files = set()
in_flight_lock = threading.Lock()


def worker_init():
    """
    Equivalent of DocumentWorker.__init__ - sets up the thread pool
    and resets worker state. Call this once before worker_start().
    """
    global worker_executor, worker_running

    worker_running = True
    worker_executor = ThreadPoolExecutor(
        max_workers=Config.MAX_WORKERS,
        thread_name_prefix="pdf-worker"
    )

    logger.info(f"Thread pool started with {Config.MAX_WORKERS} workers.")


def run_and_release(file_path):
    """
    Runs process_pdf() for a single file, then removes it from the
    in-flight set so it can be picked up again later if needed
    (equivalent of DocumentWorker._run_and_release).
    """
    try:
        process_pdf(file_path)
    finally:
        with in_flight_lock:
            in_flight_files.discard(file_path)


def scan_input_folder():
    """
    Equivalent of DocumentWorker.scan_input_folder.
    """
    try:
        logger.info(f"Scanning folder : {Config.INPUT_FOLDER}")

        if not os.path.exists(Config.INPUT_FOLDER):
            logger.warning(f"Input folder not found : {Config.INPUT_FOLDER}")
            return

        entries = os.listdir(Config.INPUT_FOLDER)
        if not entries:
            logger.info("No files found.")
            return

        logger.info(f"Found {len(entries)} entr(y/ies) in input folder.")

        for name in entries:
            file_path = os.path.join(Config.INPUT_FOLDER, name)

            if not os.path.isfile(file_path):
                continue

            if not is_pdf(file_path):
                logger.warning(f"Skipping non-PDF file : {name}")
                continue

            with in_flight_lock:
                if file_path in in_flight_files:
                    continue
                in_flight_files.add(file_path)

            logger.info(f"Submitting : {name}")
            worker_executor.submit(run_and_release, file_path)

    except Exception:
        logger.exception("Folder scanning failed.")


def worker_start():
    """
    Equivalent of DocumentWorker.start - blocks forever, polling the
    input folder on Config.POLL_INTERVAL.
    """
    logger.info("Document worker started.")
    while worker_running:
        try:
            scan_input_folder()
        except Exception:
            logger.exception("Unhandled error in poll loop.")

        logger.info(f"Sleeping for {Config.POLL_INTERVAL} seconds...")
        # Sleep in small increments so shutdown is responsive
        # instead of blocking for up to 5 minutes.
        slept = 0
        while slept < Config.POLL_INTERVAL and worker_running:
            time.sleep(min(1, Config.POLL_INTERVAL - slept))
            slept += 1


def worker_stop():
    """
    Equivalent of DocumentWorker.stop.
    """
    global worker_running

    logger.info("Stopping worker...")
    worker_running = False
    if worker_executor is not None:
        worker_executor.shutdown(wait=True)
    logger.info("Worker stopped.")


# ==========================================================
# Entry point
# ==========================================================

def handle_shutdown(signum, frame):
    logger.info(f"Received signal {signum}. Shutting down gracefully...")
    worker_stop()
    if producer is not None:
        producer.close()
    if db_connection is not None:
        DBUtils.close(db_connection)
    sys.exit(0)


def main():
    os.makedirs(Config.INPUT_FOLDER, exist_ok=True)
    os.makedirs(Config.WEBFILES_PATH, exist_ok=True)

    initialize_database()
    initialize_kafka()

    worker_init()

    signal.signal(signal.SIGINT, handle_shutdown)
    signal.signal(signal.SIGTERM, handle_shutdown)

    worker_start()  # blocks forever


if __name__ == "__main__":
    main()