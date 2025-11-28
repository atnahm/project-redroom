from web3 import Web3
import json
import os

def create_wallet():
    w3 = Web3()
    account = w3.eth.account.create()
    
    print("-" * 50)
    print("NEW WALLET GENERATED")
    print("-" * 50)
    print(f"Address:     {account.address}")
    print(f"Private Key: {account.key.hex()}")
    print("-" * 50)
    print("SAVE THIS PRIVATE KEY SECURELY! DO NOT SHARE IT.")
    print("-" * 50)
    
    # Optional: Save to a file (gitignored ideally)
    with open("wallet_credentials.txt", "w") as f:
        f.write(f"Address: {account.address}\n")
        f.write(f"Private Key: {account.key.hex()}\n")
    print("Credentials saved to 'wallet_credentials.txt'")

if __name__ == "__main__":
    create_wallet()
