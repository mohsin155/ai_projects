import faiss
import numpy as np
import pickle
from embeddings import get_model
import os
import json

def build_faiss_index(chunks, save_path="vectorstore/"):
    texts = [chunk['content'] for chunk in chunks]
    model = get_model()
    vectors = model.encode(texts, show_progress_bar=True)

    dim = vectors.shape[1]
    index = faiss.IndexFlatL2(dim)
    faiss.normalize_L2(vectors)
    index.add(vectors.astype('float32'))

    os.makedirs(save_path, exist_ok=True)

    with open(os.path.join(save_path, "documents.json"), "w", encoding='utf-8') as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)

    np.save(os.path.join(save_path, "embeddings.npy"), vectors)

    faiss.write_index(index, os.path.join(save_path, "faiss_index.index"))

    print(f"RAG system saved file {save_path}")

