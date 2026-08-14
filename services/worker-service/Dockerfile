FROM apache_base:latest

WORKDIR /worker-service

RUN pip install --no-cache-dir \
    opencv-python-headless \
    pytesseract \
    pdf2image \
    paddleocr \
    reportlab

COPY . .
COPY --from=apache_base /app/app/ace_logger.py /worker-service/app/ace_logger.py
COPY --from=apache_base /app/app/db_utils.py /worker-service/app/db_utils.py

CMD ["python3","-m", "app.app"]

EXPOSE 8083