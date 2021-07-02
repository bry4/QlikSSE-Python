FROM python:3.8.10-slim-buster

WORKDIR /app

COPY . .

RUN pip install -r requirements.txt

CMD python ExtensionService_Models.py
