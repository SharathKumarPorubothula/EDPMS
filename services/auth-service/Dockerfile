FROM apache_base:latest

WORKDIR /app

COPY . .

RUN pip install PyJWT
RUN pip install bcrypt

EXPOSE 8080

CMD ["python3", "app/app.py"]