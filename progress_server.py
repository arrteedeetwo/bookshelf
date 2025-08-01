from flask import Flask, jsonify, request, send_from_directory, redirect, url_for, make_response
import json
import os
from flask_cors import CORS  # Importieren von flask-cors
from pathlib import Path



def normalize(path):
    # Entfernt './' und '\\' und normalisiert den Dateipfad
    return path.replace("\\", "/").lstrip("./").lower()


# Flask-Session für Session-Management
app = Flask(__name__, static_url_path="/static", static_folder="/media/gamedisk/newserver")

CORS(app)
# Keine Authentifizierung und CORS mehr
# Keine CORS und Authentifizierung

PROGRESS_PATH = "progress.json"
MANGA_ROOT = Path(app.static_folder) / "manga"

# Funktion zum Laden des Fortschritts aus der JSON-Datei
def load_progress():
    if not os.path.exists(PROGRESS_PATH):
        initialize_progress()  # Stelle sicher, dass die Datei existiert und initialisiert ist.
    
    try:
        with open(PROGRESS_PATH, "r", encoding="utf-8") as f:
            print(f"Fortschritt erfolgreich geladen aus {PROGRESS_PATH}")
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"Fehler beim Laden der JSON-Datei: {e}")
        return []  # Rückgabe einer leeren Liste im Fehlerfall
    except Exception as e:
        print(f"Fehler beim Laden von progress.json: {e}")
        return []  # Rückgabe einer leeren Liste im Fehlerfall


# Funktion zur Initialisierung der progress.json-Datei, falls sie nicht existiert
def initialize_progress():
    if os.path.exists(PROGRESS_PATH):
        return  # Keine Neuinitialisierung, wenn Datei existiert

    progress_entries = []

    for series_dir in MANGA_ROOT.iterdir():
        if not series_dir.is_dir():
            continue

        series_name = series_dir.name

        for html_file in series_dir.glob("*.html"):
            volume_name = html_file.stem
            volume_path = f"./manga/{series_name}/{html_file.name}".replace("\\", "/")

            image_folder = series_dir / volume_name
            cover_page = "0.jpg"

            if image_folder.exists() and image_folder.is_dir():
                images = sorted([
                    f.name for f in image_folder.iterdir()
                    if f.suffix.lower() in [".jpg", ".jpeg", ".png"]
                ])
                if images:
                    cover_page = images[0]

            progress_entries.append({
                "series": series_name,
                "volume": volume_name,
                "path": volume_path,
                "page_idx": 0,
                "last_page_idx": 0,
                "cover_page": cover_page
            })

    with open(PROGRESS_PATH, "w", encoding="utf-8") as f:
        json.dump(progress_entries, f, ensure_ascii=False, indent=2)
    print(f"✅ Fortschritt initialisiert: {PROGRESS_PATH}")

# Routen und Logik, die mit Flask laufen
@app.route("/")
def index():
    return redirect(url_for('serve_bookshelf'))

@app.route("/serve_bookshelf")
def serve_bookshelf():
    return send_from_directory(app.static_folder, "bookshelf_deluxe_server.html")

@app.route("/progress")
def get_progress():
    progress = load_progress()
    # Hier können Sie alle Pfade der geladenen Fortschritte ausgeben
    for entry in progress:
        print(f"Gespeicherter Pfad: {entry['path']}")  # Ausgabe des gespeicherten Pfads
    return jsonify(progress)

@app.route("/update_progress", methods=["POST"])
def update_progress():
    data = request.json
    path = normalize(data.get("path", ""))
    page_idx = data.get("page_idx", 0)
    last_page_idx = data.get("last_page_idx", 0)

    # Debugging: Ausgabe des Pfads, der vom Front-End empfangen wird
    print(f"Empfangener Pfad: {path}")

    progress = load_progress()
    found = False

    for entry in progress:
        if normalize(entry["path"]) == path:
            entry["page_idx"] = page_idx
            entry["last_page_idx"] = last_page_idx
            found = True
            break

    if found:
        save_progress(progress)
        return jsonify({"status": "updated"})
    else:
        return jsonify({"status": "not found"}), 404

def save_progress(progress):
    try:
        with open(PROGRESS_PATH, "w", encoding="utf-8") as f:
            json.dump(progress, f, ensure_ascii=False, indent=2)
        print("✅ Fortschritt gespeichert:", PROGRESS_PATH)
    except Exception as e:
        print("Fehler beim Speichern von progress.json:", e)


@app.route("/update_series_order", methods=["POST"])
def update_series_order():
    # Empfange die neue Reihenfolge der Serien
    new_order = request.json.get("new_order", [])

    # Überprüfen, ob die Reihenfolge nicht leer ist
    if not new_order:
        return jsonify({"status": "error", "message": "Die Reihenfolge ist leer!"})

    # Speichern der neuen Reihenfolge in `series_order.json`
    series_order_path = "series_order.json"

    try:
        with open(series_order_path, "w", encoding="utf-8") as f:
            json.dump(new_order, f, ensure_ascii=False, indent=2)
        
        return jsonify({"status": "success", "message": "Die Reihenfolge der Serien wurde aktualisiert!"})
    except Exception as e:
        # Fehler beim Speichern
        return jsonify({"status": "error", "message": f"Fehler beim Speichern der Reihenfolge: {str(e)}"})

@app.route("/series_order", methods=["GET"])
def get_series_order():
    series_order_path = "series_order.json"

    # Überprüfen, ob die Datei existiert
    if not os.path.exists(series_order_path):
        return jsonify([])  # Falls die Datei nicht existiert, gib eine leere Liste zurück

    try:
        # Lade die Reihenfolge aus der Datei
        with open(series_order_path, "r", encoding="utf-8") as f:
            series_order = json.load(f)
        return jsonify(series_order)  # Gib die Reihenfolge als JSON zurück
    except Exception as e:
        # Fehler beim Laden der Reihenfolge
        return jsonify({"status": "error", "message": f"Fehler beim Laden der Reihenfolge: {str(e)}"})


@app.route("/manga/<path:filename>")
def serve_manga(filename):
    response = make_response(send_from_directory(MANGA_ROOT, filename))
    if filename.endswith((".jpg", ".jpeg", ".png", ".webp")):
        response.headers["Cache-Control"] = "public, max-age=86400"
    return response

@app.route("/reader.html")
def serve_reader():
    return send_from_directory(app.static_folder, "reader.html")

BOOKMARKS_PATH = "bookmarks.json"

def load_bookmarks():
    if not os.path.exists(BOOKMARKS_PATH):
        with open(BOOKMARKS_PATH, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=2)
    try:
        with open(BOOKMARKS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def save_bookmarks(bm):
    with open(BOOKMARKS_PATH, "w", encoding="utf-8") as f:
        json.dump(bm, f, ensure_ascii=False, indent=2)

@app.route("/bookmarks")
def get_bookmarks():
    """GET /bookmarks?path=…  → { path: “…”, bookmarks: [ {title, page_idx}, … ] }"""
    all_bm = load_bookmarks()
    p = normalize(request.args.get("path",""))
    entry = next((e for e in all_bm if normalize(e["path"])==p), None)
    return jsonify(entry or {"path":p,"bookmarks":[]})

@app.route("/update_bookmark", methods=["POST"])
def update_bookmark():
    """POST /update_bookmark  { path, title, page_idx }"""
    data = request.json
    p = normalize(data["path"])
    title    = data.get("title","")
    page_idx = int(data.get("page_idx",0))
    bm_list = load_bookmarks()
    # finde oder neu anlegen
    entry = next((e for e in bm_list if normalize(e["path"])==p), None)
    if not entry:
        entry = {"path":p, "bookmarks":[]}
        bm_list.append(entry)
    # überschreibe bei gleichem Titel, sonst hinzufügen
    existing = next((b for b in entry["bookmarks"] if b["title"]==title),None)
    if existing:
        existing["page_idx"] = page_idx
    else:
        entry["bookmarks"].append({"title":title,"page_idx":page_idx})
    save_bookmarks(bm_list)
    return jsonify({"status":"ok","bookmarks":entry["bookmarks"]})

@app.route("/delete_bookmark", methods=["POST"])
def delete_bookmark():
    """POST /delete_bookmark  { path, title }"""
    data = request.json
    p = normalize(data["path"])
    title = data.get("title","")
    bm_list = load_bookmarks()
    entry = next((e for e in bm_list if normalize(e["path"])==p), None)
    if entry:
        entry["bookmarks"] = [b for b in entry["bookmarks"] if b["title"]!=title]
        save_bookmarks(bm_list)
    return jsonify({"status":"ok"})


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=1506)  # Port 1506
