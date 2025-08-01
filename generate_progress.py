from pathlib import Path
import json

manga_root = Path("B:/Manga/+Mokuro/manga")
progress_file = Path("progress.json")
series_order_file = Path("series_order.json")  # New: Path for series order file

# Load existing progress / Vorhandenen Fortschritt laden
if progress_file.exists():
    try:
        with progress_file.open("r", encoding="utf-8") as f:
            existing = json.load(f)
    except Exception as e:
        print("❌ Fehler beim Lesen von progress.json:", e)  # Error reading progress.json
        existing = []
else:
    existing = []

# Load existing series order / Vorhandene Serienreihenfolge laden
if series_order_file.exists():
    try:
        with series_order_file.open("r", encoding="utf-8") as f:
            existing_series_order = json.load(f)
    except Exception as e:
        print("❌ Fehler beim Lesen von series_order.json:", e)  # Error reading series_order.json
        existing_series_order = []
else:
    existing_series_order = []

# Convert to dict for quick access / Umwandeln in ein Dict für schnellen Zugriff
existing_map = {
    (entry["series"], entry["volume"]): entry
    for entry in existing
}

progress_entries = []
new_series = set()  # Track all series we find

# Get manga data from folders / Manga-Daten aus dem Ordner holen
for series_dir in manga_root.iterdir():
    if not series_dir.is_dir():
        continue

    series_name = series_dir.name
    new_series.add(series_name)  # Add to our set of series

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

        key = (series_name, volume_name)

        # Keep existing data / Vorhandene Daten beibehalten
        if key in existing_map:
            entry = existing_map[key]
            entry["path"] = volume_path  # update if path changed / aktualisieren falls sich Pfad geändert hat
            entry["cover_page"] = cover_page  # possibly new cover / evtl. neues Cover
        else:
            entry = {
                "series": series_name,
                "volume": volume_name,
                "path": volume_path,
                "page_idx": 0,
                "last_page_idx": 0,
                "cover_page": cover_page
            }

        progress_entries.append(entry)

        # Update HTML file with script tag / HTML-Datei mit Script-Tag aktualisieren
        try:
            with html_file.open("r", encoding="utf-8") as f:
                html_content = f.read()

            # Check if exact script is already there / Prüfen, ob das exakte Script schon da ist
            script_line = '<script src="/static/mokuro_progress.js"></script>'
            if script_line not in html_content:
                if "</body>" in html_content.lower():
                    # Insert script tag before </body> / Einfügen des Script-Tags vor </body>
                    new_content = html_content.replace(
                        "</body>",
                        f"\n{script_line}\n</body>"
                    )
                    with html_file.open("w", encoding="utf-8") as f:
                        f.write(new_content)
                    print(f"✅ Eingefügt in {html_file.name}")  # Inserted into [filename]
                else:
                    print(f"⚠️ Kein </body> gefunden in {html_file.name}")  # No </body> found in [filename]
            else:
                print(f"⏩ Script bereits enthalten in {html_file.name}")  # Script already in [filename]
        except Exception as e:
            print(f"❌ Fehler beim Bearbeiten von {html_file.name}: {e}")  # Error processing [filename]

# Update series order / Serienreihenfolge aktualisieren
updated_series_order = []

# First keep existing order for series that still exist / Zuerst bestehende Reihenfolge für noch vorhandene Serien beibehalten
for series in existing_series_order:
    if series in new_series:
        updated_series_order.append(series)

# Then add new series that weren't in the order / Dann neue Serien hinzufügen, die noch nicht in der Reihenfolge waren
for series in new_series:
    if series not in updated_series_order:
        updated_series_order.append(series)

# Save progress / Fortschritt speichern
try:
    with progress_file.open("w", encoding="utf-8") as f:
        json.dump(progress_entries, f, ensure_ascii=False, indent=2)
    print(f"✅ Fortschritt aktualisiert: {progress_file.resolve()}")  # Progress updated: [filepath]
except Exception as e:
    print(f"❌ Fehler beim Speichern von progress.json: {e}")  # Error saving progress.json

# Save updated series order / Aktualisierte Serienreihenfolge speichern
try:
    with series_order_file.open("w", encoding="utf-8") as f:
        json.dump(updated_series_order, f, ensure_ascii=False, indent=2)
    print(f"✅ Serienreihenfolge aktualisiert: {series_order_file.resolve()}")  # Series order updated: [filepath]
except Exception as e:
    print(f"❌ Fehler beim Speichern von series_order.json: {e}")  # Error saving series_order.json
