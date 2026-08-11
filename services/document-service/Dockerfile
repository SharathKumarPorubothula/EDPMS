FROM apache_base:latest

WORKDIR /document-service

RUN pip install --no-cache-dir Pillow==11.3.0 pdf2image==1.17.0

COPY . .

ENV PYTHONPATH=/apache/app

CMD ["python3", "app/app.py"]

EXPOSE 8081