FROM python:3.13-alpine
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt --root-user-action=ignore
ADD booking/ .
RUN python -m grpc_tools.protoc -I=. --python_out=. --grpc_python_out=. schedule.proto
EXPOSE 3003
ENTRYPOINT ["python", "-u", "booking.py"]
