FROM python:3.11.3-slim-buster

WORKDIR /app

ENV PYTHONUNBUFFERED=1

COPY Pipfile Pipfile.lock /app/

RUN pip install pipenv && \
    pipenv install --deploy --ignore-pipfile

COPY . /app/

CMD ["pipenv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
