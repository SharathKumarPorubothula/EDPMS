FROM apache_base:latest

WORKDIR /service-bridge

RUN pip3 install requests==2.32.5

COPY . .

CMD ["python3", "app/app.py"]

EXPOSE 8761