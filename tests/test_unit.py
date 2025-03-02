import os
from app import save_json, load_json, generiere_zaehler_id
from datetime import datetime

def test_json_speicherung():
    test_file = "test_data.json"
    test_data = [
        {"id": 1, "name": "Testgebäude", "adresse": "Teststraße 5"},
        {"id": 2, "name": "Zweites Gebäude", "adresse": "Teststraße 10"}
    ]

    # Speichern der Daten
    save_json(test_file, test_data)
    
    # Laden der Daten
    loaded_data = load_json(test_file)

    # Prüfen, ob die geladenen Daten mit den gespeicherten übereinstimmen
    assert loaded_data == test_data, "Die gespeicherten und geladenen Daten sind nicht identisch!"

    # Testdatei entfernen
    os.remove(test_file)


def test_generiere_zaehler_id():
    gebaeude_id = "7"
    jahr = datetime.now().year
    zaehler_id = generiere_zaehler_id(gebaeude_id)
    print(f"{zaehler_id}")

    # Prüft, ob die ID korrekt aufgebaut ist
    assert zaehler_id.startswith(f"{gebaeude_id}"), "Die generierte Zähler-ID hat das falsche Format!"
    assert len(zaehler_id.split('-')) == 3, "Die Zähler-ID sollte aus drei Teilen bestehen!"
    assert zaehler_id.split('-')[2].isdigit(), "Der letzte Teil der ID sollte eine Zahl sein!"