import os
import json
from web3 import Web3
from solcx import compile_standard, install_solc
from dotenv import load_dotenv

load_dotenv()

# 1. Configuration
RPC_URL = "https://rpc-amoy.polygon.technology/"
CHAIN_ID = 80002  # Polygon Amoy Chain ID
PRIVATE_KEY = os.getenv("PRIVATE_KEY")

if not PRIVATE_KEY:
    print("CRITICAL ERROR: 'PRIVATE_KEY' environment variable is missing.")
    print("Usage: $env:PRIVATE_KEY='YourKey'; python deploy.py")
    exit(1)

# 2. Read Solidity File
contract_path = "../smart_contracts/SourceRegistry.sol"
with open(contract_path, "r") as file:
    source_registry_file = file.read()

# 3. Install Solc & Compile
print("Installing Solidity Compiler...")
install_solc("0.8.0")

print("Compiling Smart Contract...")
compiled_sol = compile_standard(
    {
        "language": "Solidity",
        "sources": {"SourceRegistry.sol": {"content": source_registry_file}},
        "settings": {
            "outputSelection": {
                "*": {
                    "*": ["abi", "metadata", "evm.bytecode", "evm.sourceMap"]
                }
            }
        },
    },
    solc_version="0.8.0",
)

bytecode = compiled_sol["contracts"]["SourceRegistry.sol"]["SourceRegistry"]["evm"]["bytecode"]["object"]
abi = json.loads(compiled_sol["contracts"]["SourceRegistry.sol"]["SourceRegistry"]["metadata"])["output"]["abi"]

# 4. Deploy
w3 = Web3(Web3.HTTPProvider(RPC_URL))

if not w3.is_connected():
    print("Connection to Polygon Amoy failed.")
    exit(1)

print(f"Connected to Polygon Amoy. Deploying from {w3.eth.account.from_key(PRIVATE_KEY).address}...")

# Build Transaction
SourceRegistry = w3.eth.contract(abi=abi, bytecode=bytecode)
nonce = w3.eth.get_transaction_count(w3.eth.account.from_key(PRIVATE_KEY).address)
print(f"Using Nonce: {nonce}")
print(f"Gas Price: {w3.eth.gas_price}")

transaction = SourceRegistry.constructor().build_transaction({
    "chainId": CHAIN_ID,
    "from": w3.eth.account.from_key(PRIVATE_KEY).address,
    "nonce": nonce,
    "maxFeePerGas": w3.to_wei('50', 'gwei'),
    "maxPriorityFeePerGas": w3.to_wei('30', 'gwei')
})

# Sign & Send
signed_txn = w3.eth.account.sign_transaction(transaction, private_key=PRIVATE_KEY)
print("Sending transaction...")
tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)

print(f"Transaction Sent! Hash: {tx_hash.hex()}")
print("Waiting for confirmation...")

tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

if tx_receipt.status != 1:
    print("❌ DEPLOYMENT FAILED! Transaction status is 0.")
    exit(1)

print("-" * 50)
print(f"SUCCESS! Contract Deployed to: {tx_receipt.contractAddress}")
print("-" * 50)
print("Please update 'CONTRACT_ADDRESS' in 'server/main.py' with this address.")
