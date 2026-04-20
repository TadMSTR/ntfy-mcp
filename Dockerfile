FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/

EXPOSE 8484

RUN useradd -r -s /bin/false -u 1001 appuser
USER appuser

CMD ["python", "-m", "src.server"]
