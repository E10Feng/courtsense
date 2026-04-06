"""
Embedding service — generates embeddings for drill search (pgvector).
Falls back to zero vectors if OpenAI/minimax embedding API is unavailable.
"""
import os
import httpx


async def embed_text(text: str) -> list[float]:
    """
    Generate a 1536-dim embedding via OpenAI text-embedding-3-small.
    Falls back to zero vector on failure.
    """
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                "https://api.openai.com/v1/embeddings",
                headers={
                    "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY', '')}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "text-embedding-3-small",
                    "input": text,
                },
            )
            resp.raise_for_status()
            return resp.json()["data"][0]["embedding"]
    except Exception:
        # Return a zero vector as fallback — drill search will use LIKE fallback
        return [0.0] * 1536


async def embed_drills(drills: list[dict]) -> list[dict]:
    """
    Given a list of drills, add an embedding key to each.
    Embedding is generated from: "{name} {target_weakness} {description}"
    """
    enriched = []
    for drill in drills:
        text = f"{drill['name']} {drill['target_weakness']} {drill['description']}"
        embedding = await embed_text(text)
        enriched.append({**drill, "embedding": embedding})
    return enriched
