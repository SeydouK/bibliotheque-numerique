FROM python:3.11-slim

WORKDIR /app

RUN addgroup --system app && adduser --system --group app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /app/data && chown -R app:app /app

USER app

ENV MODEL_PATH="/app/data/model.pkl"
ENV DATA_PATH="/app/data/loans.csv"

EXPOSE 8004
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8004"]