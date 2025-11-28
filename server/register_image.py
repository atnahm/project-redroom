import os
import json
from web3 import Web3
from dotenv import load_dotenv
import imagehash
from PIL import Image, ImageDraw

load_dotenv()

# Configuration
RPC_URL = os.getenv("RPC_URL")
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS")
CHAIN_ID = 80002

if not CONTRACT_ADDRESS or CONTRACT_ADDRESS == "0xYourContractAddressHere":
    print("Error: Contract address not set in .env")
    exit(1)

# Ensure Checksum Address
CONTRACT_ADDRESS = Web3.to_checksum_address(CONTRACT_ADDRESS)

# Minimal ABI for registerMedia
CONTRACT_ABI = [
    {
        "inputs": [{"internalType": "string", "name": "_pHash", "type": "string"}],
        "name": "registerMedia",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    }
]

def create_and_register():
    # 1. Create a Test Image
    print("Generating test image...")
    img = Image.new('RGB', (100, 100), color = 'white')
    d = ImageDraw.Draw(img)
    d.text((10,10), "OFFICIAL", fill=(0,0,0))
    
    img_path = "test_image.png"
    img.save(img_path)
    print(f"Saved test image to: {img_path}")

    # 2. Calculate pHash
    p_hash = str(imagehash.average_hash(img))
    print(f"Image pHash: {p_hash}")

    # 3. Register on Blockchain
    w3 = Web3(Web3.HTTPProvider(RPC_URL))
    account = w3.eth.account.from_key(PRIVATE_KEY)
    contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=CONTRACT_ABI)

    print(f"Registering hash on Polygon Amoy...")
    
    # Build Transaction
    nonce = w3.eth.get_transaction_count(account.address)
    tx = contract.functions.registerMedia(p_hash).build_transaction({
        "chainId": CHAIN_ID,
        "from": account.address,
        "nonce": nonce,
        "maxFeePerGas": w3.to_wei('50', 'gwei'),
        "maxPriorityFeePerGas": w3.to_wei('30', 'gwei')
    })

    # Sign & Send
    signed_tx = w3.eth.account.sign_transaction(tx, private_key=PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
    
    print(f"Transaction sent! Hash: {tx_hash.hex()}")
    print("Waiting for confirmation...")
    
    w3.eth.wait_for_transaction_receipt(tx_hash)
    
    print("-" * 50)
    print("✅ SUCCESS! Image Registered.")
    print(f"pHash: {p_hash}")
    print("-" * 50)
    print(f"👉 Now upload '{os.path.abspath(img_path)}' to your Frontend to see the Green Shield!")

if __name__ == "__main__":
    create_and_register()
