from web3 import Web3
from dotenv import load_dotenv
import os

load_dotenv()

RPC_URL = os.getenv("RPC_URL")
RPC_URL = os.getenv("RPC_URL")
CONTRACT_ADDRESS = Web3.to_checksum_address(os.getenv("CONTRACT_ADDRESS"))
PHASH = "0f07ffffffffffff"

CONTRACT_ABI = [
    {
        "inputs": [{"internalType": "string", "name": "_pHash", "type": "string"}],
        "name": "verifyMedia",
        "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
        "stateMutability": "view",
        "type": "function"
    }
]

def verify_on_chain():
    w3 = Web3(Web3.HTTPProvider(RPC_URL))
    contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=CONTRACT_ABI)
    
    print(f"Checking Hash: {PHASH}")
    print(f"Contract: {CONTRACT_ADDRESS}")
    
    print(f"Checking Hash: {PHASH}")
    print(f"Contract: {CONTRACT_ADDRESS}")
    
    try:
        result = contract.functions.verifyMedia(PHASH).call()
        print(f"Result: {result}")
    except Exception as e:
        print(f"Call Failed: {e}")

if __name__ == "__main__":
    verify_on_chain()
