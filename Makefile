# Makefile

.PHONY: all build clean

APP=tron_txn_clone_tool
SRC=$(APP).py
BIN=dist/$(APP)
ENV_FILE=.env

all: build

build:
	@echo "[+] Building binary..."
	pyinstaller --onefile $(SRC) --name $(APP)
	@echo "[+] Build complete: $(BIN)"

clean:
	@echo "[-] Cleaning build artifacts..."
	rm -rf build dist __pycache__ *.spec

run:
	@echo "[>] Running $(APP)..."
	TRON_MAINNET_KEY=$$(gpg --decrypt $(ENV_FILE).gpg 2>/dev/null | grep TRON_MAINNET_KEY | cut -d= -f2) \
	TRON_TX_WEBHOOK=$$(gpg --decrypt $(ENV_FILE).gpg 2>/dev/null | grep TRON_TX_WEBHOOK | cut -d= -f2) \
		./$(BIN) $(ARGS)
