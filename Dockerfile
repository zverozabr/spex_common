FROM python:3.9.2

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE = 1
# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED = 1

COPY ./common /app/common

WORKDIR /app/common

RUN pip install --upgrade pip
RUN pip install pipenv
RUN pip install -r requirements.txt
