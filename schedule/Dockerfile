FROM python:3.13-alpine
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt --root-user-action=ignore
ADD schedule/ .
RUN python -m grpc_tools.protoc -I=. --python_out=. --grpc_python_out=. schedule.proto
EXPOSE 3002
ENTRYPOINT ["python", "-u", "schedule.py"]
