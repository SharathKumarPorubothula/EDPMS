FROM apache_base:latest

WORKDIR /document-service

RUN pip install --no-cache-dir Pillow==11.3.0 pdf2image==1.17.0

COPY . .

COPY --from=apache_base /app/app/ace_logger.py /document-service/app/ace_logger.py
COPY --from=apache_base /app/app/db_utils.py /document-service/app/db_utils.py
COPY --from=apache_base /app/app/jwt_utils.py /document-service/app/jwt_utils.py

EXPOSE 8080

CMD ["python3", "-m", "app.app"]
