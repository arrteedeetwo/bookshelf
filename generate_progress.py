from pathlib import Path
import json

manga_root = Path("B:/Manga/+Mokuro/manga")
progress_file = Path("progress.json")

# Vorhandenen Fortschritt laden / Load existing progress
if progress_file.exists():
    try:
        with progress_file.open("r", encoding="utf-8") as f:
            existing = json.load(f)
    except Exception as e:
        print("❌ Fehler beim Lesen von progress.json:", e)  # Error reading progress.json
        existing = []
else:
    existing = []

# Umwandeln in ein Dict für schnellen Zugriff / Convert to dict for quick access
existing_map = {
    (entry["series"], entry["volume"]): entry
    for entry in existing
}

progress_entries = []

# Manga-Daten aus dem Ordner holen / Get manga data from folders
for series_dir in manga_root.iterdir():
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

        key = (series_name, volume_name)

        # Vorhandene Daten beibehalten / Keep existing data
        if key in existing_map:
            entry = existing_map[key]
            entry["path"] = volume_path  # aktualisieren falls sich Pfad geändert hat / update if path changed
            entry["cover_page"] = cover_page  # evtl. neues Cover / possibly new cover
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

        # HTML-Datei mit Script-Tag aktualisieren / Update HTML file with script tag
        try:
            with html_file.open("r", encoding="utf-8") as f:
                html_content = f.read()

            # Prüfen, ob das exakte Script schon da ist / Check if exact script is already there
            script_line = '<script src="/static/mokuro_progress.js"></script>'
            if script_line not in html_content:
                if "</body>" in html_content.lower():
                    # Einfügen des Script-Tags vor </body> / Insert script tag before </body>
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

# Fortschritt speichern / Save progress
try:
    with progress_file.open("w", encoding="utf-8") as f:
        json.dump(progress_entries, f, ensure_ascii=False, indent=2)
    print(f"✅ Fortschritt aktualisiert: {progress_file.resolve()}")  # Progress updated: [filepath]
except Exception as e:
    print(f"❌ Fehler beim Speichern von progress.json: {e}")  # Error saving progress.json
