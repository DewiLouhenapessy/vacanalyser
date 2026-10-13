import os
from dotenv import load_dotenv
from pydantic import BaseModel
from mistralai.client import Mistral

# Load API-key from .env
load_dotenv()
client = Mistral(api_key=os.getenv("MISTRAL_API_KEY"))

# This Pydantic model defines the shape of the response 
# used to validate the model's output.
class VacatureAnalyse(BaseModel):
    functietitel: str
    harde_eisen: list[str]
    nice_to_haves: list[str]
    trefwoorden: list[str]


def analyseer_vacature(tekst: str) -> VacatureAnalyse:
    # response_format asks the model to return data matching the Pydantic model.
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


# This allows the file to be run directly.
if __name__ == "__main__":
    test_vacature = """Wij zoeken een Python developer met 3 jaar
    ervaring, kennis van Docker en SQL. Nice to have: AWS."""
    resultaat = analyseer_vacature(test_vacature)
    print(resultaat.model_dump_json(indent=2))  # Print formatted JSON.