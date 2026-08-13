FROM apache_base:latest

WORKDIR /app

COPY . .

RUN pip3 install --no-cache-dir requests==2.32.5

EXPOSE 8761

CMD ["python3", "app/app.py"]