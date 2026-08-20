FROM python:3.11-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -e ".[cvd]"

CMD ["python", "scripts/audit_contrast.py", "--help"]
