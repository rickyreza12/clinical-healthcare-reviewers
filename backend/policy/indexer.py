"""Create the local Qdrant SOP index used for future semantic policy retrieval."""

import hashlib
import json
import os
from pathlib import Path
from time import sleep
from uuid import NAMESPACE_URL, uuid5


DEFAULT_COLLECTION = "policy_chunks"
DEFAULT_MODEL = "BAAI/bge-small-en-v1.5"


def load_chunks(path: Path) -> list[dict]:
    """Read and validate source-controlled policy chunks."""
    chunks = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]
    if not chunks or any(not chunk.get("chunk_id") or not chunk.get("text") for chunk in chunks):
        raise ValueError("Policy chunks must contain a chunk_id and text")
    return chunks


def source_fingerprint(chunks: list[dict]) -> str:
    """Return a stable content marker so existing matching indexes are reused."""
    source = "\n".join(json.dumps(chunk, sort_keys=True, separators=(",", ":")) for chunk in chunks)
    return hashlib.sha256(source.encode()).hexdigest()


def wait_for_qdrant(client, attempts: int = 30) -> None:
    """Wait for the dependent Qdrant service before creating a collection."""
    for _ in range(attempts):
        try:
            client.get_collections()
            return
        except Exception:
            sleep(2)
    raise RuntimeError("Qdrant did not become ready")


def main() -> None:
    from qdrant_client import QdrantClient, models
    from fastembed import TextEmbedding

    app_root = Path(__file__).resolve().parents[2]
    chunks = load_chunks(Path(os.getenv("POLICY_CHUNKS_PATH", app_root / "data" / "policy_chunks.jsonl")))
    collection = os.getenv("QDRANT_POLICY_COLLECTION", DEFAULT_COLLECTION)
    model_name = os.getenv("QDRANT_EMBEDDING_MODEL", DEFAULT_MODEL)
    client = QdrantClient(url=os.getenv("QDRANT_URL", "http://localhost:6333"))
    wait_for_qdrant(client)

    fingerprint = source_fingerprint(chunks)
    if client.collection_exists(collection):
        marker = client.retrieve(collection, ids=[str(uuid5(NAMESPACE_URL, "bithealth-policy-index"))], with_payload=True)
        if marker and marker[0].payload.get("source_fingerprint") == fingerprint:
            print(f"Qdrant policy index '{collection}' is current.")
            return
        client.delete_collection(collection)

    embedder = TextEmbedding(model_name=model_name)
    texts = [chunk["text"] for chunk in chunks]
    vectors = [vector.tolist() for vector in embedder.embed(texts)]
    client.create_collection(
        collection_name=collection,
        vectors_config=models.VectorParams(size=len(vectors[0]), distance=models.Distance.COSINE),
    )
    points = [
        models.PointStruct(
            id=str(uuid5(NAMESPACE_URL, chunk["chunk_id"])),
            vector=vector,
            payload={key: value for key, value in chunk.items() if key != "text"} | {"text": chunk["text"]},
        )
        for chunk, vector in zip(chunks, vectors, strict=True)
    ]
    points.append(models.PointStruct(
        id=str(uuid5(NAMESPACE_URL, "bithealth-policy-index")),
        vector=[0.0] * len(vectors[0]),
        payload={"source_fingerprint": fingerprint, "kind": "index_marker"},
    ))
    client.upsert(collection_name=collection, points=points, wait=True)
    print(f"Indexed {len(chunks)} SOP chunks in Qdrant collection '{collection}'.")


if __name__ == "__main__":
    main()
