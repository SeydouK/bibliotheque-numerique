FROM python:3.11-slim AS builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

FROM python:3.11-slim

WORKDIR /app

RUN addgroup --system app && adduser --system --group app

COPY --from=builder /root/.local /home/app/.local

COPY . .

VOLUME ["/app/data"]

RUN chown -R app:app /app
USER app

ENV PATH="/home/app/.local/bin:$PATH"
ENV MODEL_PATH="/app/data/model.pkl"
ENV DATA_PATH="/app/data/loans.csv"

EXPOSE 8004
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8004"]