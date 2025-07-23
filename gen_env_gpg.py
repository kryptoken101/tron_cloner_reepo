# gen_env_gpg.py

import base64
import getpass
import subprocess

ENV_PATH = ".env"
GPG_PATH = ".env.gpg"

print("🔐 Generate encrypted .env.gpg for TRON transaction cloning tool.")

try:
    key = getpass.getpass("Enter your TRON private key (hex, 64 chars): ").strip()
    if len(key) != 64:
        raise ValueError("Private key must be exactly 64 hex characters.")

    encoded_key = base64.b64encode(bytes.fromhex(key)).decode()
    webhook = input("Enter Slack/Discord Webhook URL (or leave blank): ").strip()

    with open(ENV_PATH, "w") as f:
        f.write(f"TRON_MAINNET_KEY={encoded_key}\n")
        if webhook:
            f.write(f"TRON_TX_WEBHOOK={webhook}\n")

    subprocess.run(["gpg", "-c", ENV_PATH], check=True)
    print(f"✅ Encrypted env saved as {GPG_PATH}")

except Exception as e:
    print(f"❌ Error: {e}")
