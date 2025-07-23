# TRON Transaction Cloner 🔁

Clone and broadcast smart contract transactions from TRON Nile Testnet to Mainnet — safely, securely, and in batches.

“This standalone tool is developed in support of the Flash USDT initiative, for educational purposes only and must not be used maliciously.”

---

## 🔧 Features
- Clone `transfer`, `approve`, `transferFrom` TRC20 calls from Nile → Mainnet
- Batch or single transaction mode
- Dry-run testing
- JSON logging and payload exports
- Slack/Discord webhook alerts
- Secure `.env.gpg` encrypted secrets
- CLI or Docker-based execution

---

## 📦 Setup

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Generate `.env.gpg` securely
```bash
python gen_env_gpg.py
```
> Stores your TRON mainnet key and webhook securely.

### 3. Build CLI Binary
```bash
make build
```

### 4. Run via CLI
```bash
make run ARGS="--txid YOUR_TX_ID"
make run ARGS="--batch --file txids.txt"
```

---

## 🐳 Docker

### Build Image
```bash
docker build -t tron-cloner .
```

### Run (Mount `.env.gpg`)
```bash
docker run --rm -it \
  -v $PWD/.env.gpg:/app/.env.gpg \
  tron-cloner --txid YOUR_TX_ID
```

---

## 🔐 Secrets Handling
- Private key never stored in plaintext
- `.env.gpg` encrypted with symmetric GPG
- Decrypted only at runtime

---

## 📣 Webhooks
- Set `TRON_TX_WEBHOOK` in `.env` to notify on tx success/fail
- Supports Slack, Discord, etc.

---

## License
MIT © You
