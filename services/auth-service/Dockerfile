FROM apache_base:latest

WORKDIR /auth-service

RUN pip install PyJWT

COPY . .

CMD ["python3", "app/app.py"]

EXPOSE 8080

CMD ["python3", "app/app.py"]