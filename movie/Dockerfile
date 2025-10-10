FROM python:3.13-alpine
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt --root-user-action=ignore
ADD movie/ .
EXPOSE 3001
ENTRYPOINT ["python", "-u", "movie.py"]
