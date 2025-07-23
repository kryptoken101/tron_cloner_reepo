# Dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY tron_txn_clone_tool.py ./
COPY gen_env_gpg.py ./
COPY .env.gpg ./
COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt \
 && apt-get update && apt-get install -y gnupg \
 && rm -rf /var/lib/apt/lists/*

ENTRYPOINT ["python", "tron_txn_clone_tool.py"]
