import time
import pytest
from app import app

@pytest.fixture
def client():
    return app.test_client()

@pytest.mark.performance
def test_massive_ablesungen(client):
    start_time = time.time()
    erfolg_count = 0
    
    client.post("/zaehler/hinzufuegen", json={"gebaeude_id": "1", "typ": "Strom"})
    for i in range(100):  # Simuliere 1000 Ablesungen
        response = client.post("/ablesung/hinzufuegen", json={
            "gebaeude_id": "1",
            "zaehler_id": "1-2025-5487",
            "datum": "2025-03-01",
            "wert": 110 + i,
            "ableser": "Mieter"
        })
        if response.status_code == 201:
            erfolg_count += 1
        else:
            print(f"🚨 Fehler bei Ablesung {i}: {response.data.decode('utf-8')}")


    end_time = time.time()

    print("\n🚀 **Massisve Ablesung Ergebnis**")
    print(f"✅ Erfolgreiche Ablesungen: {erfolg_count} / 1000")
    print(f"⏳ Gesamtzeit: {end_time - start_time:.2f} Sekunden")
    print(f"⚡ Durchschnittliche Zeit pro Ablesung: {(end_time - start_time) / 1000:.5f} Sekunden")
    assert erfolg_count == 100, f"Nicht alle Ablesungen wurden erfolgreich gespeichert!, {response.data.decode('utf-8'), erfolg_count}"

@pytest.mark.performance
def test_server_response_time(client):
    start_time = time.time()
    response = client.get("/")
    end_time = time.time()

    print("Ergebnis")
    print(f"{end_time - start_time:.2f}")
    
    assert response.status_code == 200
    assert (end_time - start_time) < 1, f"Antwortzeit zu hoch: {end_time - start_time:.2f}s"


@pytest.mark.performance
def test_massive_zaehler_erstellen(client):
    start_time = time.time()
    erfolg_count = 0

    for i in range(500):
        response = client.post("/zaehler/hinzufuegen", json={
            "gebaeude_id": f"{i}",
            "typ": "Strom"
        })

        if response.status_code == 201:
            erfolg_count += 1
        else:
            print(f"🚨 Fehler bei Zähler {i}: {response.data.decode('utf-8')}")

    end_time = time.time()

    print("\n🚀 **Lasttest: 500 Zähler hinzufügen**")
    print(f"✅ Erfolgreiche Zähler: {erfolg_count} / 500")
    print(f"⏳ Gesamtzeit: {end_time - start_time:.2f} Sekunden")
    print(f"⚡ Durchschnittliche Zeit pro Zähler: {(end_time - start_time) / 500:.5f} Sekunden")

    assert erfolg_count == 499, f"Nicht alle Zähler wurden erfolgreich hinzugefügt! : {response.data.decode('utf-8'), {erfolg_count}}"

@pytest.mark.performance
def test_massive_gebaeude_erstellen(client):
    start_time = time.time()
    erfolg_count = 0

    for i in range(100):
        response = client.post("/gebaeude/hinzufuegen", data={
            "name": f"Testhaus {i}",
            "adresse": f"Teststraße {i}",
            "eingang_anzahl": "2"
        })

        if response.status_code == 200:
            erfolg_count += 1
        else:
            print(f"🚨 Fehler bei Gebäude {i}: {response.data.decode('utf-8')}")

    end_time = time.time()

    print("\n🚀 **Lasttest: 100 Gebäude hinzufügen**")
    print(f"✅ Erfolgreiche Gebäude: {erfolg_count} / 100")
    print(f"⏳ Gesamtzeit: {end_time - start_time:.2f} Sekunden")
    print(f"⚡ Durchschnittliche Zeit pro Gebäude: {(end_time - start_time) / 100:.5f} Sekunden")

    assert erfolg_count == 100, f"Nicht alle Gebäude wurden erfolgreich gespeichert!, : {response.data.decode('utf-8')}"
