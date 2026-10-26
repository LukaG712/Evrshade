FROM python:3.12-slim

WORKDIR /app

COPY services/Slinker/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy shared packages
COPY packages/evershade-core /packages/evershade-core
COPY packages/evershade-db /packages/evershade-db
COPY packages/evershade-events /packages/evershade-events
ENV PYTHONPATH=/packages/evershade-core/src:/packages/evershade-db/src:/packages/evershade-events/src:${PYTHONPATH}

COPY services/Slinker/app ./app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
