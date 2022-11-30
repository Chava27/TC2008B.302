FROM python:3.10-slim-buster as base

# Create .venv
RUN pip install pipenv
COPY Pipfile .
COPY Pipfile.lock .
RUN  PIPENV_VENV_IN_PROJECT=1 pipenv install --deploy --system

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

WORKDIR /app
COPY . /app

# Creates a non-root user and adds permission to access the /app folder
RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /app
USER appuser

EXPOSE 5000

CMD ["python", "app.py"]
