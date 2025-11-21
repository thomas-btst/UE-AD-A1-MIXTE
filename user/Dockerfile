FROM python:3.13-alpine
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt --root-user-action=ignore
ADD user/ .
COPY .env .
EXPOSE 3004
ENTRYPOINT ["python", "-u", "user.py"]
