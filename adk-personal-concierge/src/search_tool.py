import logging
import mimetypes
import os
from typing import List, Optional
import json

import faiss
import numpy as np
from google.adk.agents.callback_context import CallbackContext
from sentence_transformers import SentenceTransformer

_logger = logging.getLogger(__name__)
MODEL_NAME = "all-MiniLM-L6-v2"
BASE_DIR = os.path.dirname(__file__)
PRODUCTS_PATH = os.path.join(BASE_DIR, "..", "data", "products.json")
INDEX_PATH = os.path.join(BASE_DIR, "..", "data", "faiss.index")
WATCHES_DIR = os.path.join(BASE_DIR, "..", "data", "watches")
IMAGE_BASE_URL = os.getenv("HAPPTIQ_IMAGE_BASE_URL", "http://127.0.0.1:9000")

with open(PRODUCTS_PATH, "r", encoding="utf-8") as fh:
    products: List[dict] = json.load(fh)
model = SentenceTransformer(MODEL_NAME)
index = faiss.read_index(INDEX_PATH)


def _resolve_local_image_path(artifact_uri: Optional[str], product_id: str) -> Optional[str]:
    """Resolve the on-disk image path for a product."""
    if not artifact_uri:
        return None

    relative = artifact_uri.lstrip("/\\")
    candidates: List[str] = []

    if relative:
        candidates.append(os.path.join(WATCHES_DIR, relative))
        candidates.append(os.path.join(WATCHES_DIR, os.path.basename(relative)))

    base_name = os.path.basename(relative)
    _, inferred_ext = os.path.splitext(base_name)
    ext_candidates = [inferred_ext] if inferred_ext else [".png", ".jpg", ".jpeg", ".webp"]
    for ext in ext_candidates:
        candidates.append(os.path.join(WATCHES_DIR, f"{product_id}{ext}"))

    for path in candidates:
        if path and os.path.exists(path):
            return path

    _logger.warning("No local image found for %s (artifact_uri=%s)", product_id, artifact_uri)
    return None


def _build_local_image_url(image_path: str) -> str:
    """Return the HTTP URL for a locally hosted watch image."""
    filename = os.path.basename(image_path)
    return f"{IMAGE_BASE_URL.rstrip('/')}/{filename}"


async def search_products(
    query: str,
    k: int = 3,
) -> List[dict]:
    """Tool callable from the agent."""
    embedding = model.encode([query]).astype("float32")
    distances, indices = index.search(embedding, k)

    results: List[dict] = []
    for rank, idx in enumerate(indices[0]):
        if idx < 0 or idx >= len(products):
            continue

        product = products[idx].copy()
        artifact_hint = product.pop("artifact_uri", None)
        product_id = product.get("id", f"match-{rank}")
        product["distance"] = float(distances[0][rank])

        image_path = _resolve_local_image_path(
            artifact_uri=artifact_hint,
            product_id=product_id,
        )
        if image_path:
            product["image_url"] = _build_local_image_url(image_path)
            display_name = product.get("name", product_id)
            product["image_markdown"] = f"{display_name} ![{display_name}]({product['image_url']})"

        results.append(product)

    return results
