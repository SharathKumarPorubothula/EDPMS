FROM apache_base:latest

WORKDIR /auth-service

RUN pip install PyJWT

COPY . .

ENV PYTHONPATH=/apache/app

CMD ["python3", "app/app.py"]

EXPOSE 8080