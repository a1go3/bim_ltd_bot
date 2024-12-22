FROM python:3.11.3-slim-buster

WORKDIR /src

RUN pip install --upgrade pip
COPY ./requirements.txt /src/requirements.txt
RUN pip install -r requirements.txt --no-cache-dir

COPY . .
CMD ["python", "main.py"]
