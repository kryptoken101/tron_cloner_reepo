# tron_txn_clone_tool.py

from tronpy import Tron
from tronpy.keys import PrivateKey
from tronpy.exceptions import TransactionError
import sys
import json
import binascii
import os
from datetime import datetime
import argparse
import base64
import getpass

# --- Configuration ---
NILE_NODE = 'https://nile.trongrid.io'
MAINNET_NODE = 'https://api.trongrid.io'
LOG_FILE = 'txn_clone.log'

# Load mainnet private key securely
def load_mainnet_private_key():
    encoded = os.getenv("24537cf5-db1e-48d2-9d63-8cbfea40514c")
    if encoded:
        try:
            return base64.b64decode(encoded).hex()
        except Exception:
            log("Failed to decode TRON_MAINNET_KEY from env")
            sys.exit(1)
    else:
        try:
            key_input = getpass.getpass("Enter mainnet private key (hex): ").strip()
            return key_input
        except Exception:
            print("Secure key entry failed.")
            sys.exit(1)

# --- Logging ---
def log(msg: str):
    timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    with open(LOG_FILE, 'a') as f:
        f.write(f"[{timestamp}] {msg}\n")

# --- Step 1: Fetch original transaction from Nile ---
def fetch_nile_transaction(txid: str):
    try:
        nile = Tron(provider=NILE_NODE)
        return nile.get_transaction(txid)
    except Exception as e:
        log(f"Error fetching tx {txid}: {e}")
        print(f"Error fetching transaction from Nile: {e}")
        return None

# --- Step 2: Extract essential data ---
def extract_txn_data(tx):
    try:
        contract = tx['raw_data']['contract'][0]['parameter']['value']
        contract_address = contract['contract_address']
        owner_address = contract['owner_address']
        function_selector = contract.get('data', '')
        decoded_info = {}

        if not function_selector:
            raise ValueError("No function selector found in transaction data.")

        method_sig = function_selector[:8]

        if method_sig == 'a9059cbb':
            try:
                recipient = '41' + function_selector[8:48][-40:]
                amount = int(function_selector[48:], 16)
                decoded_info = {"method": "transfer", "recipient": recipient, "amount_sun": amount}
            except Exception:
                log("Failed to decode transfer")

        elif method_sig == '095ea7b3':
            try:
                spender = '41' + function_selector[8:48][-40:]
                amount = int(function_selector[48:], 16)
                decoded_info = {"method": "approve", "spender": spender, "amount_sun": amount}
            except Exception:
                log("Failed to decode approve")

        elif method_sig == '23b872dd':
            try:
                from_addr = '41' + function_selector[8:48][-40:]
                to_addr = '41' + function_selector[48:88][-40:]
                amount = int(function_selector[88:], 16)
                decoded_info = {"method": "transferFrom", "from": from_addr, "to": to_addr, "amount_sun": amount}
            except Exception:
                log("Failed to decode transferFrom")

        return contract_address, owner_address, function_selector, decoded_info
    except Exception as e:
        log(f"Extraction error: {e}")
        return None, None, None, {}

# --- Step 3: Rebuild and sign on Mainnet ---
def build_and_sign_on_mainnet(contract_address, owner_address, data_hex, decoded_info, fee_limit, call_value, dry_run, tag, private_key):
    try:
        client = Tron(provider=MAINNET_NODE)
        priv_key = PrivateKey(bytes.fromhex(private_key))

        txn = client.trx.trigger_smart_contract(
            contract_address=client.to_base58check_address(contract_address),
            function_selector=data_hex[:8],
            parameter=data_hex[8:],
            fee_limit=fee_limit,
            call_value=call_value,
            owner_address=client.to_base58check_address(owner_address)
        )

        payload = txn.txn.to_json()
        if decoded_info:
            payload['decoded_info'] = decoded_info

        with open(f"rebuilt_transaction_{tag or 'single'}.json", "w") as f:
            json.dump(payload, f, indent=2)

        if dry_run:
            log(f"Dry-run: skipped signing {tag}")
            return None

        return txn.sign(priv_key)
    except Exception as e:
        log(f"Build/sign error for {tag}: {e}")
        return None

# --- Step 4: Broadcast ---
def broadcast_mainnet_txn(signed_txn, tag):
    try:
        tx_hash = signed_txn.broadcast().wait()
        log(f"Broadcast success for {tag}: {tx_hash}")
        return f"Broadcast success. Mainnet txID: {tx_hash}"
    except TransactionError as e:
        log(f"Broadcast failed for {tag}: {e}")
        return f"Failed to broadcast: {e}"
    except Exception as e:
        log(f"Unexpected error for {tag}: {e}")
        return f"Unexpected error during broadcast: {e}"

# --- CLI Entry Point ---
def main():
    parser = argparse.ArgumentParser(description="Clone and re-broadcast TRON transactions from Nile to Mainnet.")
    parser.add_argument('--batch', action='store_true', help='Batch mode from txid file')
    parser.add_argument('--file', type=str, help='File containing txIDs (one per line)')
    parser.add_argument('--txid', type=str, help='Single txID to process')
    parser.add_argument('--fee_limit', type=int, default=3000000, help='Fee limit in SUN')
    parser.add_argument('--call_value', type=int, default=0, help='Call value in SUN')
    parser.add_argument('--dry_run', action='store_true', help='Simulate only, do not broadcast')

    args = parser.parse_args()
    mainnet_key = load_mainnet_private_key()

    if args.batch:
        if not args.file or not os.path.isfile(args.file):
            print("Valid txID file required in batch mode.")
            sys.exit(1)
        with open(args.file) as f:
            txids = [line.strip() for line in f if line.strip()]

        for idx, txid in enumerate(txids):
            print(f"\nProcessing {idx+1}/{len(txids)}: {txid}")
            tx = fetch_nile_transaction(txid)
            if tx is None:
                continue
            c_addr, o_addr, data, decoded = extract_txn_data(tx)
            if not c_addr or not o_addr or not data:
                continue
            signed = build_and_sign_on_mainnet(c_addr, o_addr, data, decoded, args.fee_limit, args.call_value, args.dry_run, tag=f"{idx+1}", private_key=mainnet_key)
            if signed:
                print(broadcast_mainnet_txn(signed, tag=f"{idx+1}"))
    elif args.txid:
        tx = fetch_nile_transaction(args.txid)
        c_addr, o_addr, data, decoded = extract_txn_data(tx)
        signed = build_and_sign_on_mainnet(c_addr, o_addr, data, decoded, args.fee_limit, args.call_value, args.dry_run, tag="single", private_key=mainnet_key)
        if signed:
            print(broadcast_mainnet_txn(signed, tag="single"))
    else:
        print("Specify --txid for single mode or --batch with --file for batch mode.")
        sys.exit(1)

if __name__ == '__main__':
    main()
