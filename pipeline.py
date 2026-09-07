import os
import json
import hashlib
from datetime import datetime, timezone

from dotenv import load_dotenv
import cv2
import serpapi
from web3 import Web3
from insightface.app import FaceAnalysis

load_dotenv()


# ============================================================
# Stage 1: Face detection + encoding
# ============================================================

_app = None


def get_detector():
    global _app

    if _app is None:
        _app = FaceAnalysis(
            name="buffalo_l",
            providers=["CPUExecutionProvider"]
        )

        _app.prepare(
            ctx_id=0,
            det_size=(640, 640)
        )

    return _app


def detect_and_encode(path):
    img = cv2.imread(path)

    if img is None:
        raise ValueError("Could not read image file")

    faces = get_detector().get(img)

    if not faces:
        raise ValueError("No face detected in image")

    # Pick the biggest face
    f = max(
        faces,
        key=lambda x: x.bbox[2] * x.bbox[3]
    )

    x1, y1, x2, y2 = [
        int(v) for v in f.bbox
    ]

    crop = img[
        max(y1, 0):y2,
        max(x1, 0):x2
    ]

    cv2.imwrite(
        "query.jpg",
        crop
    )

    return (
        f.normed_embedding.tolist(),
        "query.jpg"
    )


# ============================================================
# Stage 2: Google Lens reverse image search
# ============================================================

def reverse_image_search(image_path):

    client = serpapi.Client(
        api_key=os.environ["SERPAPI_KEY"]
    )

    print(
        "Uploading image to SerpApi...",
        flush=True
    )

    upload = client.upload_image(
        image_path
    )

    image_id = upload.get(
        "image_id"
    )

    if not image_id:
        raise RuntimeError(
            f"Image upload failed: {upload}"
        )

    print(
        "Searching Google Lens...",
        flush=True
    )

    results = client.search(
        engine="google_lens",
        image_id=image_id,
        type="visual_matches",
        hl="en",
        country="in"
    )

    if results.get("error"):
        raise RuntimeError(
            results["error"]
        )

    visual_matches = results.get(
        "visual_matches",
        []
    )

    print(
        f"Google Lens returned "
        f"{len(visual_matches)} visual matches.",
        flush=True
    )

    instagram_posts = []

    for r in visual_matches:

        link = r.get(
            "link",
            ""
        )

        if not link:
            continue

        link_lower = link.lower()

        if "instagram.com" in link_lower:

            if (
                "/p/" in link_lower
                or "/reel/" in link_lower
                or "/tv/" in link_lower
            ):

                instagram_posts.append({
                    "url": link,
                    "title": r.get(
                        "title",
                        "Instagram post"
                    ),
                    "source": r.get(
                        "source",
                        "Instagram"
                    )
                })

    print(
        "Instagram posts found:",
        flush=True
    )

    for post in instagram_posts:

        print(
            post["url"],
            flush=True
        )

    if not instagram_posts:
        return None

    return {
        "url": instagram_posts[0]["url"],
        "title": instagram_posts[0]["title"],
        "source": "Instagram",
        "posts": instagram_posts
    }


# ============================================================
# Stage 3: Blockchain
# ============================================================

def anchor_onchain(
    record_hash,
    payload
):

    w3 = Web3(
        Web3.HTTPProvider(
            os.environ["RPC_URL"]
        )
    )

    print("RPC connected:", w3.is_connected(), flush=True)
    print("RPC chain ID:", w3.eth.chain_id, flush=True)

    acct = w3.eth.account.from_key(
        os.environ["PRIVATE_KEY"]
    )

    data = json.dumps({
        "hash": record_hash,
        "match": payload["match"],
        "ts": payload["ts"]
    }).encode()

    tx = {
        "from": acct.address,
        "to": acct.address,
        "value": 0,
        "data": data,
        "nonce": w3.eth.get_transaction_count(
            acct.address
        ),
        "gas": 100000,
        "gasPrice": w3.eth.gas_price,
        "chainId": 11155111
    }

    signed = acct.sign_transaction(
        tx
    )

    txh = w3.eth.send_raw_transaction(
        signed.raw_transaction
    )

    w3.eth.wait_for_transaction_receipt(
        txh
    )

    return txh.hex()


# ============================================================
# Stage 4: Verify blockchain record
# ============================================================

def verify_onchain(
    tx_hash,
    expected_hash
):

    w3 = Web3(
        Web3.HTTPProvider(
            os.environ["RPC_URL"]
        )
    )

    tx = w3.eth.get_transaction(
        tx_hash
    )

    onchain = json.loads(
        tx["input"].decode()
    )

    return (
        onchain["hash"]
        == expected_hash
    )


# ============================================================
# Main pipeline
# ============================================================

def run_pipeline(image_path):

    # Stage 1
    yield {
        "name": "face",
        "status": "run",
        "detail": "insightface"
    }

    emb, crop = detect_and_encode(
        image_path
    )

    yield {
        "name": "face",
        "status": "ok",
        "detail": f"{len(emb)}-d embedding"
    }


    # Stage 2
    yield {
        "name": "search",
        "status": "run",
        "detail": "Google Lens"
    }

    match = reverse_image_search(
        crop
    )

    if not match:

        yield {
            "name": "search",
            "status": "fail",
            "detail": "no social match"
        }

        yield None
        return

    yield {
        "name": "search",
        "status": "ok",
        "detail": f"{len(match['posts'])} Instagram post(s)"
    }


    # Stage 3
    payload = {
        "match": {
            "url": match["url"],
            "title": match["title"],
            "source": match["source"]
        },
        "ts": datetime.now(
            timezone.utc
        ).isoformat()
    }

    record_hash = hashlib.sha256(
        json.dumps(
            payload,
            sort_keys=True
        ).encode()
    ).hexdigest()

    yield {
        "name": "chain",
        "status": "run",
        "detail": "Sepolia tx"
    }

    try:

        tx = anchor_onchain(
            record_hash,
            payload
        )

    except Exception as e:

        yield {
            "name": "chain",
            "status": "fail",
            "detail": str(e)[:40]
        }

        yield None
        return

    yield {
        "name": "chain",
        "status": "ok",
        "detail": tx[:14] + "..."
    }


    # Stage 4
    ok = verify_onchain(
        tx,
        record_hash
    )

    yield {
        "name": "verify",
        "status": "ok" if ok else "fail",
        "detail": (
            "hash match"
            if ok
            else "mismatch"
        )
    }


    # Final result
    yield {
        "url": match["url"],
        "tx": tx,
        "hash": record_hash,
        "posts": match["posts"]
    }