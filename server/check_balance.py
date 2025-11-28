from web3 import Web3
from dotenv import load_dotenv
import os

load_dotenv()

RPC_URL = os.getenv("RPC_URL", "https://rpc-amoy.polygon.technology/")
PRIVATE_KEY = os.getenv("PRIVATE_KEY")

def check_balance():
    w3 = Web3(Web3.HTTPProvider(RPC_URL))
    
    if not w3.is_connected():
        print("Failed to connect to Polygon Amoy RPC")
        return

    account = w3.eth.account.from_key(PRIVATE_KEY)
    address = account.address
    
    balance_wei = w3.eth.get_balance(address)
    balance_matic = w3.from_wei(balance_wei, 'ether')
    
    print("-" * 50)
    print(f"Address: {address}")
    print(f"Balance: {balance_matic} MATIC")
    print("-" * 50)
    
    if balance_matic == 0:
        print("❌ You have 0 MATIC. You cannot deploy.")
        print("👉 Go to: https://faucet.polygon.technology/")
        print("👉 Paste your address and request tokens.")
    else:
        print("✅ You have funds! You can now run 'python deploy.py'")

if __name__ == "__main__":
    check_balance()
