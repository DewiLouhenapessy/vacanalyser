from app.analyser import analyseer_vacature

def test_analyse():
    resultaat = analyseer_vacature("Wij zoeken een junior tester met Selenium-ervaring.")
    assert resultaat.functietitel  # The job title must not be empty.
    assert len(resultaat.trefwoorden) > 0