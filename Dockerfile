FROM amd64/ubuntu:22.04

WORKDIR /app

ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive


COPY Pipfile Pipfile.lock /app/
RUN apt -y update && apt -y upgrade
RUN apt install -y pip && pip install pipenv
RUN apt install software-properties-common -y
RUN add-apt-repository ppa:deadsnakes/ppa && apt -y update
RUN apt install -y python3.11
RUN pipenv --python /usr/bin/python3
RUN pipenv install

COPY . /app/

RUN pipenv run pip install cmake
RUN pipenv run pip install easyocr

EXPOSE 8000


CMD ["pipenv", "run","uvicorn", "main:app", "--reload"]

