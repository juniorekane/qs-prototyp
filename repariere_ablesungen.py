import json

# Datei-Pfade
ablesungen_file = "data/ablesungen.json"
zaehler_file = "data/zaehler.json"

# Lade die aktuellen Ablesungsdaten
with open(ablesungen_file, "r", encoding="utf-8") as f:
    ablesungen = json.load(f)

# Lade die Zählerdaten, um die Gebäude-Zuordnung zu finden
with open(zaehler_file, "r", encoding="utf-8") as f:
    zaehler = json.load(f)

# Erstelle eine Zuordnung von Zähler-ID → Gebäude-ID
zaehler_map = {z["id"]: z["gebaeude_id"] for z in zaehler}

# Durchlaufe alle Ablesungen und setze `gebaeude_id`, falls sie fehlt
for a in ablesungen:
    if "gebaeude_id" not in a and a["zaehler_id"] in zaehler_map:
        a["gebaeude_id"] = zaehler_map[a["zaehler_id"]]

# Speichere die aktualisierten Ablesungsdaten
with open(ablesungen_file, "w", encoding="utf-8") as f:
    json.dump(ablesungen, f, indent=4)

print("✅ `ablesungen.json` wurde erfolgreich repariert!")
