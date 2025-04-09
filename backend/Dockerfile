FROM python:3.12-slim-bookworm

WORKDIR /app

COPY pyproject.toml poetry.lock ./
RUN pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install

COPY . .

CMD ["python", "run.py"]