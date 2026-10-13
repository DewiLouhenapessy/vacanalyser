"""RAG module for chunking, embedding and CV storage."""

import json
import os

from dotenv import load_dotenv
from mistralai.client import Mistral

load_dotenv()
client = Mistral(api_key=os.getenv("MISTRAL_API_KEY"))

EMBED_MODEL = "mistral-embed"
CV_PAD = "data/cv.txt"
CV_VOORBEELD_PAD = "data/cv_example.txt"
STORE_PAD = "data/cv_store.json"


# ---------- Chunking ----------

def maak_chunks(tekst: str, groote: int = 500, overlap: int = 100) -> list[str]:
    """Split text into overlapping chunks."""
    chunks: list[str] = []
    start = 0
    while start < len(tekst):
        einde = min(start + groote, len(tekst))
        chunk = tekst[start:einde].strip()
        if chunk:
            chunks.append(chunk)
        if einde == len(tekst):
            break
        start = einde - overlap
    return chunks


# ---------- Embedding ----------

def maak_embeddings(chunks: list[str]) -> list[list[float]]:
    """Send chunks to Mistral and return an embedding for each one."""
    antwoord = client.embeddings.create(
        model=EMBED_MODEL,
        inputs=chunks,
    )
    return [item.embedding for item in antwoord.data]


def bouw_cv_store(chunks: list[str], pad: str = STORE_PAD) -> None:
    """Embed the chunks and save them to a JSON file."""
    print(f"Embedding van {len(chunks)} chunks...")
    vectoren = maak_embeddings(chunks)

    store = [
        {"chunk": chunk, "vector": vector}
        for chunk, vector in zip(chunks, vectoren)
    ]
    with open(pad, "w", encoding="utf-8") as bestand:
        json.dump(store, bestand, ensure_ascii=False, indent=2)
    print(f"Opslag klaar: {len(store)} chunks in {pad}")


# ---------- Retrieval ----------

def cosine_gelijkheid(a: list[float], b: list[float]) -> float:
    """Measure how closely two vectors point in the same direction (1.0 = identical)."""
    teller = sum(x * y for x, y in zip(a, b))
    lengte_a = sum(x * x for x in a) ** 0.5
    lengte_b = sum(y * y for y in b) ** 0.5
    return teller / (lengte_a * lengte_b)


def laad_store(pad: str = STORE_PAD) -> list[dict]:
    """Load the stored chunks and vectors from disk."""
    with open(pad, encoding="utf-8") as bestand:
        return json.load(bestand)


def laad_of_bouw_store() -> list[dict]:
    """Load the CV store or build it from the available CV text."""
    if not os.path.exists(STORE_PAD):
        cv_pad = CV_PAD if os.path.exists(CV_PAD) else CV_VOORBEELD_PAD
        with open(cv_pad, encoding="utf-8") as bestand:
            cv_tekst = bestand.read()
        bouw_cv_store(maak_chunks(cv_tekst))

    return laad_store()


def zoek(zoektekst: str, store: list[dict], top: int = 3) -> list[dict]:
    """Find the chunks most similar to the search text."""
    vraag_vector = maak_embeddings([zoektekst])[0]

    gescoord = []
    for item in store:
        score = cosine_gelijkheid(vraag_vector, item["vector"])
        gescoord.append({**item, "score": score})

    gescoord.sort(key=lambda item: item["score"], reverse=True)
    return gescoord[:top]


# ---------- Execution ----------

if __name__ == "__main__":
    import sys

    store = laad_of_bouw_store()
    zoekterm = sys.argv[1] if len(sys.argv) > 1 else "ervaring met Docker"
    print(f"\nZoeken naar: '{zoekterm}'\n")

    for resultaat in zoek(zoekterm, store):
        print(f"[score: {resultaat['score']:.3f}]")
        print(resultaat["chunk"][:150] + "...")
        print("-" * 40)