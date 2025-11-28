# 🛡️ DeepFake Detection System (Blockchain + AI)

A hybrid forensic architecture for authenticating digital media. This system combines **Blockchain Immutability** (Polygon Amoy) with **Multi-Layer AI Analysis** (ViT, ResNet, and Gemini 1.5 Flash) to detect deepfakes and verify authentic content.

Built for **Hackathon 2025** by Team-Tech4Bharat.

---

## 🚀 Features

*   **Layer 1: Blockchain Verification**: Checks if the image's perceptual hash (pHash) exists on the Polygon Amoy Testnet. If found, it is 100% verified authentic.
*   **Layer 2: AI Ensemble Detection**: Uses a Vision Transformer (ViT) and ResNet to detect GAN and Diffusion artifacts.
*   **Layer 3: Forensic Deep Dive**: Uses **Google Gemini 1.5 Flash (VLM)** to perform a detailed forensic inspection (lighting, physics, dermatology) if the image is suspicious.
*   **Demo Mode**: Interactive toggle to simulate verification for presentation purposes.
*   **Matrix UI**: Cyber-security themed interface with real-time feedback.

---

## 🛠️ Tech Stack

*   **Frontend**: React, Vite, TailwindCSS, Lucide-React
*   **Backend**: Python FastAPI, Uvicorn
*   **Blockchain**: Solidity (Smart Contract), Web3.py, Polygon Amoy Testnet
*   **AI Models**:
    *   `dima806/deepfake_vs_real_image_detection` (ViT)
    *   `prithivMLmods/Deep-Fake-Detector-v2-Model` (ResNet)
    *   `google-generativeai` (Gemini 1.5 Flash)

---

## 📦 Installation & Setup

### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd DeepFakeDetection
```

### 2. Backend Setup (Server)
```bash
cd server
# Create virtual environment (optional but recommended)
python -m venv venv
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Frontend Setup (Client)
```bash
cd ../client
npm install
```

---

## 🔑 Environment Configuration

Create a `.env` file in the `server/` directory:

```env
# Blockchain Config (Polygon Amoy)
RPC_URL=https://rpc-amoy.polygon.technology/
PRIVATE_KEY=your_wallet_private_key_here
CONTRACT_ADDRESS=0x7982878307D18d84427C4F223F7A400030e6205a

# AI Config
GEMINI_API_KEY=your_google_gemini_api_key
```

---

## 🏃‍♂️ Running the Application

### Start the Backend
```bash
cd server
uvicorn main:app --reload
```
*Server runs on: http://localhost:8000*

### Start the Frontend
```bash
cd client
npm run dev
```
*Client runs on: http://localhost:5173*

---

## 📜 Smart Contract

The `SourceRegistry.sol` contract is deployed on Polygon Amoy.
*   **Address**: `0x7982878307D18d84427C4F223F7A400030e6205a`
*   **Functions**: `registerMedia(string pHash)`, `verifyMedia(string pHash)`

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
