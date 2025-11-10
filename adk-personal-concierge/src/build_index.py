import os
from typing import List
import json
import logging

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

MODEL_NAME = 'all-MiniLM-L6-v2'
_logger = logging.getLogger('adk_personal_concierge.build_index')
if not _logger.handlers:
    _handler = logging.StreamHandler()
    _handler.setFormatter(logging.Formatter('[build_index] %(message)s'))
    _logger.addHandler(_handler)
_logger.setLevel(logging.INFO)


def _load_products(data_path: str) -> List[dict]:
    _logger.info('Loading products from %s', os.path.abspath(data_path))
    with open(data_path, 'r', encoding='utf-8') as f:
        products = json.load(f)
    _logger.info('Loaded %d products', len(products))
    return products


def _build_embeddings(model: SentenceTransformer, products: List[dict]) -> np.ndarray:
    texts = []
    for product in products:
        attributes = product.get('attributes', {})
        attr_text = ' '.join(f'{k}:{v}' for k, v in attributes.items())
        texts.append(f"{product.get('description', '')} {attr_text}".strip())

    _logger.info('Encoding %d product descriptions with %s', len(texts), MODEL_NAME)
    embeddings = model.encode(texts)
    embeddings = np.asarray(embeddings, dtype='float32')
    _logger.info('Embedding matrix shape=%s dtype=%s', embeddings.shape, embeddings.dtype)

    norms = np.linalg.norm(embeddings, axis=1)
    _logger.info('Embedding norm range min=%.3f max=%.3f', float(norms.min()), float(norms.max()))
    return embeddings


def main():
    base_dir = os.path.dirname(__file__)
    data_path = os.path.join(base_dir, '..', 'data', 'products.json')
    index_path = os.path.join(base_dir, '..', 'data', 'faiss.index')

    products = _load_products(data_path)
    if not products:
        _logger.warning('No products found. Skipping FAISS index build.')
        return

    model = SentenceTransformer(MODEL_NAME)
    embeddings = _build_embeddings(model, products)

    dim = embeddings.shape[1]
    _logger.info('Initializing IndexFlatL2 with dimension %d', dim)
    index = faiss.IndexFlatL2(dim)
    index.add(embeddings)
    _logger.info('Index now contains %d vectors', index.ntotal)

    faiss.write_index(index, index_path)
    _logger.info('Wrote FAISS index to %s', os.path.abspath(index_path))

    preview_count = min(3, len(products))
    for i in range(preview_count):
        product = products[i]
        _logger.info('Preview product[%d]: %s', i, product.get('name', '<unnamed>'))


if __name__ == '__main__':
    main()
