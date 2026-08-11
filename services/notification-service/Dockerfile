FROM apache_base:latest

WORKDIR /notification-service

RUN pip install --no-cache-dir requests==2.32.3

copy . .

ENV PYTHONPATH=/apache/app

CMD ["python3", "app/app.py"]

EXPOSE 8082