FROM python:3.12-slim

WORKDIR /app

COPY services/Slinker/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy shared packages
COPY packages/evershade-core /packages/evershade-core
COPY packages/evershade-db /packages/evershade-db
COPY packages/evershade-events /packages/evershade-events
ENV PYTHONPATH=/packages/evershade-core/src:/packages/evershade-db/src:/packages/evershade-events/src:${PYTHONPATH}

COPY services/Slinker/app/ ./app/

# Run as non-root user for security
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
