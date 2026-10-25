from pydantic import BaseModel

# This model defines the shape of the response 
# used to validate the model's output.
class VacatureAnalyse(BaseModel):
    functietitel: str
    harde_eisen: list[str]
    nice_to_haves: list[str]
    trefwoorden: list[str]


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
