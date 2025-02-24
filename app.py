from flask import Flask, render_template, request, jsonify
import json
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import random
from datetime import datetime
import matplotlib.dates as mdates
import re
from flask import redirect
from datetime import datetime, timedelta

app = Flask(__name__)

# JSON-Dateien
GEBAEUDE_FILE = "/home/junior/Schreibtisch/Semester 5/QS/qs-prototyp/data/gebauede.json"
ZAEHLER_FILE = "/home/junior/Schreibtisch/Semester 5/QS/qs-prototyp/data/zaehler.json"
ABLESUNG_FILE = "/home/junior/Schreibtisch/Semester 5/QS/qs-prototyp/data/ablesungen.json"

# Helferfunktion zum Laden von JSON-Dateien
def load_json(file):
    if not os.path.exists(file):
        return []
    with open(file, "r", encoding="utf-8") as f:
        return json.load(f)

# Helferfunktion zum Speichern in JSON-Dateien
def save_json(file, data):
    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

@app.route("/")
def index():
    return render_template("index.html")

# Gebäude & Wohnungen anzeigen
@app.route("/gebaeude")
def gebaeude_liste():
    gebaeude = load_json(GEBAEUDE_FILE)
    print("Geladenne Gebäude:", gebaeude)
    return render_template("gebaeude.html", gebaeude=gebaeude)

#Gebäude Details
from datetime import datetime

@app.route("/gebaeude/details", methods=["GET"])
def gebaeude_details():
    gebaeude = load_json(GEBAEUDE_FILE)
    ablesungen = load_json(ABLESUNG_FILE)

    gebaeude_id = request.args.get("gebaeude_id", None)

    if not gebaeude_id:
        return "Fehlende Gebäude-ID", 400

    try:
        gebaeude_id = int(gebaeude_id)
    except ValueError:
        return "Ungültige Gebäude-ID", 400

    # Passendes Gebäude suchen
    gebaeude_info = next((g for g in gebaeude if g["id"] == gebaeude_id), None)
    if not gebaeude_info:
        return "Gebäude nicht gefunden", 404

    # Verbrauchsdaten filtern
    gebaeude_ablesungen = [a for a in ablesungen if a["gebaeude_id"] == gebaeude_id]

    # Falls keine Verbrauchsdaten vorhanden sind
    no_data = len(gebaeude_ablesungen) == 0

    # Aktuelles Datum für den Bildnamen
    current_date = datetime.now().strftime("%Y-%m-%d")

    return render_template(
        "gebaeude_details.html",
        gebaeude=gebaeude_info,
        no_data=no_data,
        current_date=current_date
    )



# Zähler anzeigen
@app.route("/zaehler")
def zaehler_liste():
    zaehler = load_json(ZAEHLER_FILE)
    return render_template("zaehler.html", zaehler=zaehler)

# Neue Zähler-Ablesung hinzufügen
@app.route("/ablesung", methods=["POST"])
def ablesung_speichern():
    data = request.json
    ablesungen = load_json(ABLESUNG_FILE)

    # Validierung: Keine negativen Werte
    if data["wert"] < 0:
        return jsonify({"error": "Ungültiger Ablesewert"}), 400
    
    ablesungen.append(data)
    save_json(ABLESUNG_FILE, ablesungen)
    return jsonify({"message": "Ablesung gespeichert"}), 201

# Neues Gebäude hinzufügen
@app.route("/gebaeude/hinzufuegen", methods=["GET", "POST"])
def gebaeude_hinzufuegen():
    gebaeude = load_json(GEBAEUDE_FILE)

    if request.method == "POST":
        name = request.form["name"]
        adresse = request.form["adresse"]
        eingang_anzahl = int(request.form["eingang_anzahl"])

        if not name or not adresse or eingang_anzahl < 1:
            return render_template("gebaeude_hinzufuegen.html", error="Bitte alle Felder korrekt ausfüllen!")

        neues_gebaeude = {
            "id": len(gebaeude) + 1,
            "name": name,
            "adresse": adresse,
            "eingang_anzahl": eingang_anzahl
        }

        gebaeude.append(neues_gebaeude)
        save_json(GEBAEUDE_FILE, gebaeude)

        return render_template("gebaeude.html", gebaeude=gebaeude, success="Gebäude erfolgreich hinzugefügt!")

    return render_template("gebaeude_hinzufuegen.html")

# Neuen Zähler hinzufügen
@app.route("/zaehler/hinzufuegen", methods=["GET", "POST"])
def zaehler_hinzufuegen():
    zaehler = load_json(ZAEHLER_FILE)
    gebaeude = load_json(GEBAEUDE_FILE)  # Alle Gebäude laden

    if request.method == "POST":
        gebaeude_id = request.form["gebaeude_id"]  # Automatisch gesetzt durch Auswahl
        typ = request.form["typ"]

        # Automatische Zähler-ID generieren (Format: GEBÄUDE-ID-JAHR-RANDOM)
        jahr = datetime.now().year
        random_number = random.randint(1000, 9999)
        zaehler_id = f"{gebaeude_id}-{jahr}-{random_number}"

        neues_zaehler = {
            "id": zaehler_id,
            "gebaeude_id": int(gebaeude_id),
            "typ": typ
        }

        zaehler.append(neues_zaehler)
        save_json(ZAEHLER_FILE, zaehler)

        return render_template("zaehler.html", zaehler=zaehler, success=f"Zähler {zaehler_id} erfolgreich hinzugefügt!")

    return render_template("zaehler_hinzufuegen.html", gebaeude=gebaeude)



# Zählertypen hinzufügen
@app.route("/zaehlertypen/hinzufuegen", methods=["GET", "POST"])
def zaehlertypen_hinzufuegen():
    zaehlertypen = load_json("data/zaehlertypen.json")

    if request.method == "POST":
        neuer_typ = request.form["typ"].strip()
        if neuer_typ and neuer_typ not in zaehlertypen:
            zaehlertypen.append(neuer_typ)
            save_json("data/zaehlertypen.json", zaehlertypen)
    
    return render_template("zaehlertypen.html", zaehlertypen=zaehlertypen)


# Ablesung hinzufügen
@app.route("/ablesung/hinzufuegen", methods=["GET", "POST"])
def ablesung_hinzufuegen():
    ablesungen = load_json(ABLESUNG_FILE)
    zaehler = load_json(ZAEHLER_FILE)
    gebaeude = load_json(GEBAEUDE_FILE)  # Alle Gebäude laden

    if request.method == "POST":
        gebaeude_id = request.form["gebaeude_id"]
        zaehler_id = request.form["zaehler_id"]
        datum = request.form["datum"]
        wert = int(request.form["wert"])
        ableser = request.form["ableser"] or "Unbekannt"

        # Prüfen, ob der gewählte Zähler wirklich zu diesem Gebäude gehört
        if not any(z["id"] == zaehler_id and str(z["gebaeude_id"]) == gebaeude_id for z in zaehler):
            return render_template("ablesung_hinzufuegen.html", gebaeude=gebaeude, zaehler=zaehler, error="Ungültiger Zähler für dieses Gebäude!")

        # Neue Ablesung speichern
        neue_ablesung = {
            "gebaeude_id": gebaeude_id,
            "zaehler_id": zaehler_id,
            "datum": datum,
            "wert": wert,
            "ableser": ableser
        }
        ablesungen.append(neue_ablesung)
        save_json(ABLESUNG_FILE, ablesungen)

        return render_template("ablesung.html", ablesungen=ablesungen, success="Ablesung erfolgreich gespeichert!")

    return render_template("ablesung_hinzufuegen.html", gebaeude=gebaeude, zaehler=zaehler)


#Ablesung anzeigen
@app.route("/ablesung")
def ablesung_liste():
    ablesungen = load_json(ABLESUNG_FILE)
    return render_template("ablesung.html", ablesungen=ablesungen)

# Gebäude bearbeiten
@app.route("/gebaeude/bearbeiten/<int:gebaeude_id>", methods=["GET", "POST"])
def gebaeude_bearbeiten(gebaeude_id):
    gebaeude = load_json(GEBAEUDE_FILE)

    # Passendes Gebäude suchen
    gebaeude_item = next((g for g in gebaeude if g["id"] == gebaeude_id), None)

    if not gebaeude_item:
        return "Gebäude nicht gefunden", 404

    if request.method == "POST":
        gebaeude_item["name"] = request.form["name"]
        gebaeude_item["adresse"] = request.form["adresse"]
        gebaeude_item["eingang_anzahl"] = int(request.form["eingang_anzahl"])


        save_json(GEBAEUDE_FILE, gebaeude)
        return render_template("gebaeude.html", gebaeude=gebaeude, success="Gebäude erfolgreich aktualisiert!")

    return render_template("gebaeude_bearbeiten.html", gebaeude=gebaeude_item)

# Gebäude löschen
@app.route("/gebaeude/loeschen/<int:gebaeude_id>", methods=["POST"])
def gebaeude_loeschen(gebaeude_id):
    gebaeude = load_json(GEBAEUDE_FILE)

    neue_gebaeude = [g for g in gebaeude if g["id"] != gebaeude_id]

    if len(neue_gebaeude) == len(gebaeude):
        return "Gebäude nicht gefunden", 404

    save_json(GEBAEUDE_FILE, neue_gebaeude)
    return render_template("gebaeude.html", gebaeude=gebaeude, success="Gebäude erfolgreich gelöscht!")

# Suche nach Zählern
@app.route("/zaehler/suche", methods=["GET"])
def zaehler_suche():
    zaehler = load_json(ZAEHLER_FILE)
    suchbegriff = request.args.get("query", "").strip().lower()

    if suchbegriff:
        gefundene_zaehler = [z for z in zaehler if suchbegriff in z["id"].lower() or suchbegriff in z["typ"].lower()]
    else:
        gefundene_zaehler = zaehler

    return render_template("zaehler.html", zaehler=gefundene_zaehler, query=suchbegriff)



# Filter für Ablesungen
@app.route("/ablesung/suche", methods=["GET"])
def ablesung_suche():
    ablesungen = load_json(ABLESUNG_FILE)
    suchbegriff = request.args.get("query", "").strip().lower()

    if suchbegriff:
        gefundene_ablesungen = [a for a in ablesungen if suchbegriff in a["zaehler_id"].lower()]
    else:
        gefundene_ablesungen = ablesungen

    return render_template("ablesung.html", ablesungen=gefundene_ablesungen, query=suchbegriff)

# Verbrauchsanzeige
@app.route("/verbrauch", methods=["GET"])
def verbrauchsanzeige():
    ablesungen = load_json(ABLESUNG_FILE)
    gebaeude = load_json(GEBAEUDE_FILE)

    selected_gebaeude = request.args.get("gebaeude_id")

    # 🚀 Falls keine Gebäude-ID übergeben wurde, erst Auswahl anzeigen
    if not selected_gebaeude:
        if len(gebaeude) == 1:
            return redirect(f"/verbrauch?gebaeude_id={gebaeude[0]['id']}")
        return render_template("verbrauch.html", gebaeude=gebaeude, selected_gebaeude=None, no_data=True)

    try:
        selected_gebaeude = int(selected_gebaeude)
    except ValueError:
        return "❌ Fehler: Ungültige Gebäude-ID!", 400

    gebaeude_name = next((g["name"] for g in gebaeude if g["id"] == selected_gebaeude), f"Gebäude {selected_gebaeude}")

    # Zeitraum: Letzte 12 Monate berechnen
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)

    ablesungen = [
        a for a in ablesungen
        if str(a.get("gebaeude_id", "")) == str(selected_gebaeude)
        and start_date <= datetime.strptime(a["datum"], "%Y-%m-%d") <= end_date
    ]
    no_data = len(ablesungen) == 0

    if no_data:
        return render_template("verbrauch.html", gebaeude=gebaeude, selected_gebaeude=selected_gebaeude, gebaeude_name=gebaeude_name, no_data=True)

    if not os.path.exists("static"):
        os.makedirs("static")

    plt.figure(figsize=(10, 5))
    colors = {}  # Farben für die Zählerzuweisung

    for zaehler_id in set(a["zaehler_id"] for a in ablesungen):
        daten = sorted([a for a in ablesungen if a["zaehler_id"] == zaehler_id], key=lambda x: x["datum"])
        x = [datetime.strptime(a["datum"], "%Y-%m-%d") for a in daten]
        y = [a["wert"] for a in daten]

        # Zufällige, aber konsistente Farbe für jeden Zähler
        if zaehler_id not in colors:
            colors[zaehler_id] = (random.random(), random.random(), random.random())

        if len(x) > 1:
            plt.plot(x, y, marker="o", linestyle="-", label=f"Zähler {zaehler_id}", color=colors[zaehler_id])

            plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
            plt.gca().xaxis.set_major_locator(mdates.MonthLocator())
            plt.xticks(rotation=45)
            plt.ylim(min(y) - 10, max(y) + 10)

    plt.xlabel("Datum")
    plt.ylabel("Verbrauch")
    plt.title(f"Verbrauchsübersicht für {gebaeude_name}\nZeitraum: {start_date.strftime('%Y-%m-%d')} bis {end_date.strftime('%Y-%m-%d')}")
    plt.legend()
    plt.grid(True)

    current_date = datetime.now().strftime("%Y-%m-%d")
    safe_gebaeude_name = re.sub(r"[^\w\s-]", "", gebaeude_name).replace(" ", "_")

    # 🔹 Aktueller Verbrauch vs. Historie trennen
    save_path_aktuell = os.path.join("static", f"verbrauch_aktuell_{safe_gebaeude_name}.png")
    save_path_historie = os.path.join("static", f"verbrauch_historie_{safe_gebaeude_name}_{current_date}.png")

    plt.savefig(save_path_historie)  # Historische Verbrauchsanzeige
    plt.savefig(save_path_aktuell)  # Aktueller Verbrauch

    plt.close()

    print(f"✅ Verbrauchsdiagramm gespeichert unter: {save_path_historie} und {save_path_aktuell}")

    return render_template(
        "verbrauch.html",
        gebaeude=gebaeude,
        selected_gebaeude=selected_gebaeude,
        gebaeude_name=gebaeude_name,
        current_date=current_date,
        no_data=False
    )


if __name__ == "__main__":
    app.run(debug=True)
