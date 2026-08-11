FROM apache_base:latest

WORKDIR /worker-service

COPY . .

ENV PYTHONPATH=/apache/app

CMD ["python3", "app/app.py"]

EXPOSE 8083