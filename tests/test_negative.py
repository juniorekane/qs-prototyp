import pytest
from datetime import datetime
from app import app

@pytest.fixture
def client():
    return app.test_client()

# 🔹 TC-001: Zähler-ID existiert nicht (über API prüfen)
def test_zaehler_id_existiert_nicht(client):
    response = client.get("/zaehler")
    json_response = response.get_json()
    
    assert json_response is not None, "Server hat keine JSON-Antwort zurückgegeben!"
    zaehler_ids = [z["id"] for z in json_response]

    assert "999-9999-9999" not in zaehler_ids, "Zähler-ID sollte nicht existieren"

# 🔹 TC-003: Ablesewert negativ
def test_negativer_ablesewert(client):
    response = client.post("/ablesung/hinzufuegen", json={  
        "gebaeude_id": "1",
        "zaehler_id": "1-2025-5487",
        "datum": "2025-03-01",
        "wert": "-10",
        "ableser": "Mieter"
    })
    print("🚨 Server Response:", response.data.decode("utf-8"))
    json_response = response.get_json()
    assert json_response is not None, "Flask hat keine JSON-Antwort zurückgegeben!"
    assert json_response["error"] == "Ungueltiger Ablesewert"

# 🔹 TC-006: Zähler-ID muss genau 14 Zeichen haben
def test_zaehler_id_laenge(client):
    response = client.post("/zaehler/hinzufuegen", json={
        "gebaeude_id": "1",
        "typ": "Strom",
        "id": "123-2024-45678"  # 11 Zeichen statt 14
    })
    json_response = response.get_json()

    assert json_response is not None, "Server hat keine JSON-Antwort zurückgegeben!"
    assert "error" in json_response, "Keine Fehlermeldung erhalten!"
    assert json_response["error"] == "Zähler-ID muss genau 14 Zeichen haben!", "Fehlermeldung stimmt nicht!"

# 🔹 TC-004: Neuer Ablesewert muss größer sein
def test_ablesewert_muss_groesser_sein(client):
    response = client.post("/ablesung/hinzufuegen", json={
        "gebaeude_id": "1",
        "zaehler_id": "1-2025-5487",
        "datum": "2025-03-01",
        "wert": "100",
        "ableser": "Energieversorger"
    })
    print("🚨 Server Response:", response.data.decode("utf-8"))
    json_response = response.get_json()
    assert json_response is not None, "Flask hat keine JSON-Antwort zurückgegeben!"
    assert json_response["error"] == "Neuer Ablesewert muss groesser sein als der vorherige"

# 🔹 TC-009: Ablesedatum rückdatiert
def test_ablesedatum_vergangenheit(client):
    response = client.post("/ablesung/hinzufuegen", json={
        "gebaeude_id": "2",
        "zaehler_id": "1-2025-5487",
        "datum": "2000-01-01",
        "wert": "850",
        "ableser": "Hasuwart"
    })
    print("🚨 Server Response:", response.data.decode("utf-8"))
    json_response = response.get_json()
    assert json_response["error"] == "Datum darf nicht in der Vergangenheit liegen!"  # Geänderte Fehlermeldung
