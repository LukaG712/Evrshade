FROM python:3.12-slim

WORKDIR /app

# Copy and install shared packages first
COPY packages/evershade-core /packages/evershade-core
COPY packages/evershade-db /packages/evershade-db
COPY packages/evershade-events /packages/evershade-events
COPY integrations/langfuse /packages/langfuse
ENV PYTHONPATH=/packages/evershade-core/src:/packages/evershade-db/src:/packages/evershade-events/src:/packages:${PYTHONPATH}

COPY services/Shrewd/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY services/Shrewd/app ./app

EXPOSE 8089

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8089"]