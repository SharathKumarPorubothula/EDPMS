FROM apache_base:latest

WORKDIR /auth-service

RUN pip install PyJWT
RUN pip install bcrypt

COPY . .

COPY --from=apache_base /app/app/ace_logger.py /auth-service/app/ace_logger.py
COPY --from=apache_base /app/app/db_utils.py /auth-service/app/db_utils.py
COPY --from=apache_base /app/app/jwt_utils.py /auth-service/app/jwt_utils.py

EXPOSE 8080

CMD ["python3", "-m", "app.app"]