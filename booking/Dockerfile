FROM python:3.13-alpine
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt --root-user-action=ignore
ADD booking/ .
EXPOSE 3003
ENTRYPOINT ["python", "-u", "booking.py"]
