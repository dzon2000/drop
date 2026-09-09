FROM python:3.14-slim

ENV DROP_DATA=/data DROP_PORT=8080 PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --requirement requirements.txt \
    && useradd --create-home --uid 10001 drop \
    && mkdir /data \
    && chown drop:drop /data
COPY app.py .
COPY templates ./templates
COPY static ./static
USER drop
VOLUME /data
EXPOSE 8080
CMD ["python", "app.py"]
