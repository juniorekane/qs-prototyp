import pytest
from datetime import datetime
from app import app

@pytest.fixture
def client():
    return app.test_client()

# 🔹 TC-005: Korrekte Ablesung speichern
def test_korrekte_ablesung(client):
    response = client.post("/ablesung/hinzufuegen", json={
        "gebaeude_id": "1",
        "zaehler_id": "1-2025-5487",
        "datum": "2025-03-01",
        "wert": "750",
        "ableser": "Mieter"
    })
    print("🚨 Server Response:", response.data.decode("utf-8"))
    json_response = response.get_json()
    assert json_response["message"] == "Ablesung erfolgreich gespeichert"

# 🔹 TC-002: Gültige Zähler-ID eingeben
def test_gueltige_zaehler_id(client):
    response = client.get("/zaehler")
    json_response = response.get_json()
    
    assert json_response is not None, "Server hat keine JSON-Antwort zurückgegeben!"
    zaehler_ids = [z["id"] for z in json_response]

    assert "1-2025-5487" in zaehler_ids, "Zähler-ID sollte existieren"

# 🔹 TC-008: Ablesedatum in Zukunft erlaubt
def test_ablesedatum_zukunft(client):
    response = client.post("/ablesung/hinzufuegen", json={  # ✅ json={} verwenden!
        "gebaeude_id": "1",
        "zaehler_id": "1-2025-5487",
        "datum": "2030-01-01",
        "wert": "800",
        "ableser": "Mieter"
    })
    print("🚨 Server Response:", response.data.decode("utf-8"))
    json_response = response.get_json()
    assert json_response is not None, "Flask hat keine JSON-Antwort zurückgegeben!"
    assert json_response["message"] == "Ablesung erfolgreich gespeichert"

# 🔹 TC-010: Standard-Ableser bei leerem Feld
def test_standard_ableser(client):
    response = client.post("/ablesung/hinzufuegen", json={
        "gebaeude_id": "1",
        "zaehler_id": "1-2025-5487",
        "datum": "2025-03-01",
        "wert": "900",
    })
    print("🚨 Server Response:", response.data.decode("utf-8"))
    json_response = response.get_json()
    assert "ableser" in json_response and json_response["ableser"] == "Unbekannt"


# 🔹 TC-011: Historische Verbrauchswerte anzeigen (API-Aufruf)
def test_verbrauch_json(client):
    response = client.get("/verbrauch/json?gebaeude_id=1")
    json_response = response.get_json()

    assert json_response is not None, "Server hat keine JSON-Antwort zurückgegeben!"
    assert "ablesungen" in json_response, "Die Antwort enthält keine Ablesungen!"
    assert isinstance(json_response["ablesungen"], list), "Die Ablesungen sollten eine Liste sein!"

# 🔹 TC-012: Suchfunktion mit Teilstring testen
def test_suchfunktion(client):
    suchbegriff = "1-2025"
    response = client.get(f"/zaehler/suche/json?query={suchbegriff}")
    json_response = response.get_json()

    assert json_response is not None, "Server hat keine JSON-Antwort zurückgegeben!"
    assert len(json_response) > 0, "Teilstring-Suche sollte Ergebnisse liefern!"