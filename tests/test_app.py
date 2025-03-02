import pytest
from datetime import datetime
from app import app
from app import save_json, load_json

@pytest.fixture
def client():
    return app.test_client()

# Testdaten-Dateien (in der Testumgebung)
ZAEHLER_FILE = "static/test_zaehler.json"
ABLESUNG_FILE = "static/test_ablesungen.json"

# Testdaten für Zähler
test_zaehler = [
    {"id": "1-2025-5487", "gebaeude_id": 1, "typ": "Strom"},
    {"id": "2-2025-1789", "gebaeude_id": 2, "typ": "Gas"},
]

# Testdaten für Ablesungen
test_ablesungen = [
    {"zaehler_id": "1-2025-5487", "datum": "2024-06-01", "wert": 150, "gebaeude_id": 1},
    {"zaehler_id": "2-2025-1789", "datum": "2024-06-01", "wert": 300, "gebaeude_id": 2},
]

# Speichert Testdaten in separaten Dateien, um das Hauptsystem nicht zu verändern
@pytest.fixture(scope="module", autouse=True)
def setup_testdaten():
    save_json(ZAEHLER_FILE, test_zaehler)
    save_json(ABLESUNG_FILE, test_ablesungen)


# 🔹 TC-001: Zähler-ID existiert nicht (über API prüfen)
def test_zaehler_id_existiert_nicht(client):
    response = client.get("/zaehler")
    json_response = response.get_json()
    
    assert json_response is not None, "Server hat keine JSON-Antwort zurückgegeben!"
    zaehler_ids = [z["id"] for z in json_response]

    assert "999-9999-9999" not in zaehler_ids, "Zähler-ID sollte nicht existieren"


# 🔹 TC-002: Gültige Zähler-ID eingeben
def test_gueltige_zaehler_id(client):
    response = client.get("/zaehler")
    json_response = response.get_json()
    
    assert json_response is not None, "Server hat keine JSON-Antwort zurückgegeben!"
    zaehler_ids = [z["id"] for z in json_response]

    assert "1-2025-5487" in zaehler_ids, "Zähler-ID sollte existieren"

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


# 🔹 TC-007: Filtern nach Gebäude & Zählertyp
def test_filter_gebaeude_zaehlertyp():
    ablesungen = load_json(ABLESUNG_FILE)
    gefilterte = [a for a in ablesungen if a["gebaeude_id"] == 1 and a["zaehler_id"].startswith("1")]
    assert len(gefilterte) > 0, "Filter sollte passende Werte finden"

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

def test_kompletter_ableseprozess(client):
   # 1️⃣ Gebäude anlegen (data statt json!)
    response = client.post("/gebaeude/hinzufuegen", data={
        "name": "Testhaus",
        "adresse": "Teststraße 1",
        "eingang_anzahl": "2"  # Wichtig: Werte als Strings
    })
    assert response.status_code == 200, "Gebäude konnte nicht erfolgreich hinzugefügt werden"

    # 2️⃣ Zähler hinzufügen
    client.post("/zaehler/hinzufuegen", json={"gebaeude_id": "6", "typ": "Strom"})
    assert response.status_code == 200, "Zähler konnte nicht erfolgreich hinzugefügt werden"

    # 3️⃣ Ablesung hinzufügen
    response = client.post("/ablesung/hinzufuegen", json={
        "gebaeude_id": "6",
        "zaehler_id": "6-2025-5488",
        "datum": "2025-03-01",
        "wert": "1000",
        "ableser": "Mieter"
    })
    print(response)
    assert response.status_code == 201, "Ablesung konnte nicht erfolgreich gespeichert werden"
    assert response.get_json()["message"] == "Ablesung erfolgreich gespeichert"

    # 4️⃣ Verbrauchsanzeige abrufen
    response = client.get("/verbrauch/json?gebaeude_id=1")
    json_response = response.get_json()

    assert "ablesungen" in json_response, "Verbrauchsdaten fehlen!"
    assert len(json_response["ablesungen"]) > 0, "Keine Ablesungen gespeichert!"
