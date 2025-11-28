import io
import imagehash
from PIL import Image

def check_hash_consistency():
    img_path = "test_image.png"
    
    # Method 1: Open directly (like register_image.py)
    img1 = Image.open(img_path)
    hash1 = str(imagehash.average_hash(img1))
    print(f"Direct Open Hash:   {hash1}")

    # Method 2: Open via BytesIO (like main.py)
    with open(img_path, "rb") as f:
        content = f.read()
    
    img2 = Image.open(io.BytesIO(content))
    hash2 = str(imagehash.average_hash(img2))
    print(f"BytesIO Open Hash:  {hash2}")

    if hash1 == hash2:
        print("✅ Hashes Match")
    else:
        print("❌ Hashes Do Not Match")

if __name__ == "__main__":
    check_hash_consistency()
