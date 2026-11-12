FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev gcc \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements desde el contexto (backend/) o raíz
COPY requirements.txt* /tmp/
RUN if [ -f /tmp/requirements.txt ]; then pip install --no-cache-dir -r /tmp/requirements.txt; \
    else pip install --no-cache-dir \
      "fastapi>=0.110" "uvicorn[standard]>=0.27" "sqlmodel>=0.0.16" \
      "psycopg2-binary>=2.9" "python-dotenv>=1.0" "python-multipart>=0.0.9" \
      "PyJWT>=2.8" "pwdlib[argon2]>=0.2" "openpyxl>=3.1" \
      "email-validator>=2.0" "reportlab>=4.0"; fi

COPY . /app

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=25s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health')" || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
