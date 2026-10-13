"""Matcht een vacature tegen het CV met behulp van RAG."""

import os

from dotenv import load_dotenv
from pydantic import BaseModel
from mistralai.client import Mistral

from app.analyser import analyseer_vacature
from app.rag import laad_of_bouw_store, zoek

load_dotenv()
client = Mistral(api_key=os.getenv("MISTRAL_API_KEY"))
CHAT_MODEL = "mistral-small-latest"


# ---------- De output-mal ----------

class EisBeoordeling(BaseModel):
    eis: str
    gevonden_in_cv: bool
    onderbouwing: str
    toelichting: str


class MatchAnalyse(BaseModel):
    functietitel: str
    match_percentage: int
    sterke_punten: list[str]
    verbeterpunten: list[str]
    eisen: list[EisBeoordeling]
    samenvatting: str


# ---------- De match-logica ----------

def match_vacature(vacature_tekst: str) -> MatchAnalyse:
    # Stap A: analyseer de vacature (Fase 1 hergebruiken!)
    vacature = analyseer_vacature(vacature_tekst)

    # Stap B: haal per eis relevante CV-fragmenten op (Fase 2 hergebruiken!)
    store = laad_of_bouw_store()
    cv_context = ""
    for eis in vacature.harde_eisen:
        resultaten = zoek(f"CV-ervaring: {eis}", store, top=2)
        cv_context += f"\n### Context voor eis: '{eis}'\n"
        for r in resultaten:
            cv_context += f"- {r['chunk']}\n"

    # Stap C: alles in één prompt naar het LLM
    prompt = f"""Je bent een carrièreadviseur. Beoordeel of de kandidaat past bij de vacature.

FUNCTIE: {vacature.functietitel}

HARDE EISEN:
{chr(10).join(f'- {e}' for e in vacature.harde_eisen)}

FRAGMENTEN UIT HET CV (enige bron! citeer hieruit, verzin niets):
{cv_context}

Regels:
- Markeer gevonden_in_cv alleen als TRUE als het cv-fragment de eis echt onderbouwt.
- Noem bij onderbouwing letterlijk wat er in het cv staat.
- Geef een realistisch match_percentage (0-100), geen lievelingsgetal.
"""

    antwoord = client.chat.parse(
        model=CHAT_MODEL,
        messages=[{"role": "user", "content": prompt}],
        response_format=MatchAnalyse,
    )
    return antwoord.choices[0].message.parsed


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        with open(sys.argv[1], encoding="utf-8") as bestand:
            tekst = bestand.read()
    else:
        tekst = (
            "Wij zoeken een Junior Python Developer met 2 jaar ervaring, "
            "kennis van SQL en Docker. Nice to have: AWS en CI/CD."
        )

    analyse = match_vacature(tekst)
    print(f"\n=== Match: {analyse.match_percentage}% — {analyse.functietitel} ===\n")
    for e in analyse.eisen:
        vinkje = "✅" if e.gevonden_in_cv else "❌"
        print(f"{vinkje} {e.eis}")
        print(f"   → {e.toelichting}\n")
    print("Sterke punten:", ", ".join(analyse.sterke_punten))
    print("Verbeterpunten:", ", ".join(analyse.verbeterpunten))
    print("\nSamenvatting:", analyse.samenvatting)