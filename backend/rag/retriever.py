"""
Schema Retrieval Module using ChromaDB Vector Database.
Queries indexed data dictionary chunks to provide schema context for user questions.
"""

import os
import sys
from typing import Any, Dict, List

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import chromadb
from backend.core.config import settings
from backend.rag.ingest import CHROMA_DB_DIR, COLLECTION_NAME, ingest_data_dictionary


def get_chroma_collection(db_dir: str = CHROMA_DB_DIR, collection_name: str = COLLECTION_NAME):
    """
    Connect to persistent ChromaDB client and return the schema collection.
    If collection is empty or missing, trigger automatic ingestion.
    """
    client = chromadb.PersistentClient(path=db_dir)
    try:
        collection = client.get_collection(name=collection_name)
        if collection.count() == 0:
            ingest_data_dictionary(db_dir=db_dir)
            collection = client.get_collection(name=collection_name)
    except Exception:
        ingest_data_dictionary(db_dir=db_dir)
        collection = client.get_collection(name=collection_name)

    return collection


def retrieve_schema_context(question: str, top_k: int = 3) -> List[Dict[str, Any]]:
    """
    Query ChromaDB for relevant schema and business rule context given a natural language question.

    Args:
        question: User query string.
        top_k: Number of relevant chunks to retrieve.

    Returns:
        List of structured dictionaries containing content, metadata, distance, and chunk id.
    """
    if not question or not isinstance(question, str) or not question.strip():
        return []

    collection = get_chroma_collection()

    results = collection.query(
        query_texts=[question.strip()],
        n_results=min(top_k, collection.count())
    )

    formatted_results = []
    if results and "documents" in results and results["documents"]:
        documents = results["documents"][0]
        metadatas = results["metadatas"][0] if "metadatas" in results and results["metadatas"] else [{}] * len(documents)
        ids = results["ids"][0] if "ids" in results and results["ids"] else [""] * len(documents)
        distances = results["distances"][0] if "distances" in results and results["distances"] else [0.0] * len(documents)

        for doc, meta, chunk_id, dist in zip(documents, metadatas, ids, distances):
            formatted_results.append({
                "id": chunk_id,
                "content": doc,
                "metadata": meta,
                "distance": round(float(dist), 4) if dist is not None else 0.0
            })

    return formatted_results


if __name__ == "__main__":
    test_q = "How many employees are currently on leave by region?"
    print(f"Testing retrieval for: '{test_q}'")
    results = retrieve_schema_context(test_q, top_k=3)
    for i, res in enumerate(results, 1):
        print(f"\n--- Result {i} (ID: {res['id']}, Distance: {res['distance']}) ---")
        print("Metadata:", res["metadata"])
        print("Snippet:", res["content"][:200] + "...")
