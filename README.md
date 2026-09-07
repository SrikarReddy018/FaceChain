# FaceChain

> A face-processing pipeline that combines face detection, genuine reverse-image search, and blockchain-based evidence verification.

## Overview

FaceChain is a local web application that takes an input image, detects and encodes a face, searches for visually matching social media content using Google Lens through SerpApi, and records the discovered match as a tamper-evident hash on the Ethereum Sepolia testnet.

### Pipeline

```text
Input Image
     ↓
Face Detection & Encoding
     ↓
Reverse Image Search
     ↓
Instagram Match
     ↓
SHA-256 Evidence Hash
     ↓
Ethereum Sepolia
     ↓
On-chain Verification
```

## Features

- Face detection and encoding using InsightFace
- Genuine reverse-image search using Google Lens
- Instagram visual-match discovery
- SHA-256 evidence hashing
- Ethereum Sepolia blockchain anchoring
- On-chain transaction verification
- Local Flask web interface
- Real-time pipeline status updates

## Tech Stack

| Component | Technology |
|---|---|
| Backend | Python, Flask |
| Face Analysis | InsightFace, ONNX Runtime |
| Image Processing | OpenCV |
| Reverse Search | SerpApi, Google Lens |
| Blockchain | Ethereum Sepolia |
| Blockchain Library | Web3.py |
| Frontend | HTML, CSS, JavaScript |

## Project Structure

```text
FaceChain/
├── app.py
├── pipeline.py
├── static/
│   └── index.html
├── .gitignore
└── README.md
```

- **`app.py`**: Flask server, uploads, background pipeline execution, and status handling.
- **`pipeline.py`**: Face processing, reverse-image search, hashing, blockchain recording, and verification.
- **`static/index.html`**: Web interface for uploading images and viewing results.

## Requirements

- Python 3.10 or 3.11
- SerpApi API key
- Alchemy Ethereum Sepolia RPC URL
- MetaMask development wallet
- Sepolia test ETH

## Installation

Clone the repository:

```bash
git clone https://github.com/SrikarReddy018/FaceChain.git
cd FaceChain
```

Create and activate a virtual environment:

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install flask insightface onnxruntime opencv-python serpapi web3 python-dotenv
```

## Configuration

Create a `.env` file in the project root:

```env
SERPAPI_KEY=your_serpapi_api_key
RPC_URL=https://eth-sepolia.g.alchemy.com/v2/your_alchemy_api_key
PRIVATE_KEY=0xyour_throwaway_wallet_private_key
```

The Ethereum Sepolia chain ID is:

```text
11155111
```

Never upload `.env` or expose your private key/API keys.

## Running FaceChain

Start the application:

```bash
python app.py
```

Open:

```text
http://127.0.0.1:5000
```

Upload an image containing a detectable face and allow the pipeline to complete.

A successful run produces:

- Instagram visual matches
- Blockchain transaction hash
- SHA-256 record hash
- On-chain verification result

## Blockchain Design

FaceChain does **not** store the original image on the blockchain.

Instead, it creates a SHA-256 hash of the evidence record and anchors that hash in an Ethereum Sepolia transaction.

```text
Evidence Record
      ↓
   SHA-256
      ↓
 Evidence Hash
      ↓
Sepolia Transaction
      ↓
Independent Verification
```

This provides a tamper-evident reference to the recorded evidence.

## Security

Use a dedicated development wallet containing only Sepolia test ETH.

Never commit:

```text
.env
venv/
uploads/
query.jpg
__pycache__/
```

Never share private keys, seed phrases, or API keys.

## Limitations

- Face detection can fail on low-quality, obscured, or poorly positioned faces.
- Google Lens may return no visual matches for some images.
- Instagram results depend on what Google Lens returns.
- A visual match does **not** prove that two images contain the same person.
- External API availability and rate limits can affect results.
- Sepolia is a testnet and the project is a proof of concept.
- Blockchain records the evidence hash, not the original image.

## Privacy

FaceChain processes facial images and sends the processed image to an external reverse-image-search service. Only use images you are authorized to process, and avoid uploading sensitive photographs.

## Purpose

FaceChain demonstrates how computer vision, reverse-image search, and blockchain can be combined to create a verifiable digital-evidence workflow.

It is an educational proof of concept and should not be treated as a definitive identity-verification or investigative system.

## Author

**Srikar Reddy**

GitHub: https://github.com/SrikarReddy018
