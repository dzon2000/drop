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
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD ["python", "-c", "import os, urllib.request; urllib.request.urlopen('http://127.0.0.1:' + os.getenv('DROP_PORT', '8080') + '/health', timeout=2)"]
CMD ["python", "app.py"]
