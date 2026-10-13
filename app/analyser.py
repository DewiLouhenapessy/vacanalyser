import os
from dotenv import load_dotenv
from pydantic import BaseModel
from mistralai.client import Mistral

# Load API-key from .env
load_dotenv()
client = Mistral(api_key=os.getenv("MISTRAL_API_KEY"))

# Dit is een "dataclass": een mal voor hoe ons antwoord eruitziet.
# Pydantic controleert automatisch of het LLM zich aan de mal houdt!
class VacatureAnalyse(BaseModel):
    functietitel: str
    harde_eisen: list[str]
    nice_to_haves: list[str]
    trefwoorden: list[str]


def analyseer_vacature(tekst: str) -> VacatureAnalyse:
    #Een "prompt" is de opdracht die je het LLM geeft.
    #Door response_format te gebruiken kan het model alleen
    #antwoorden in de vorm van onze Pydantic-mal. Heel krachtig!
    return client.chat.parse(
        model="mistral-small-latest",
        messages=[
            {
                "role": "user",
                "content": (
                    "Analyseer onderstaande vacature. "
                    f"Vacature: {tekst}"
                ),
            }
        ],
        response_format=VacatureAnalyse,
    ).choices[0].message.parsed


# Dit zorgt dat het bestand ook direct uit te voeren is
if __name__ == "__main__":
    test_vacature = """Wij zoeken een Python developer met 3 jaar
    ervaring, kennis van Docker en SQL. Nice to have: AWS."""
    resultaat = analyseer_vacature(test_vacature)
    print(resultaat.model_dump_json(indent=2))  # print netjes als JSON