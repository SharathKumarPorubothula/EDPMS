FROM apache_base:latest

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir Pillow==11.3.0 pdf2image==1.17.0

EXPOSE 8081