from pathlib import Path
import json

manga_root = Path("/media/gamedisk/japanese/manga")
progress_file = Path("progress.json")

# Vorhandenen Fortschritt laden
if progress_file.exists():
    try:
        existing = json.loads(progress_file.read_text(encoding="utf-8"))
    except Exception as e:
        print("❌ Fehler beim Lesen von progress.json:", e)
        existing = []
else:
    existing = []

# Umwandeln in ein Dict für schnellen Zugriff
existing_map = {
    (entry["series"], entry["volume"]): entry
    for entry in existing
}

progress_entries = []

# Manga-Daten aus dem Ordner holen
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

        # Vorhandene Daten beibehalten
        if key in existing_map:
            entry = existing_map[key]
            entry["path"] = volume_path  # aktualisieren falls sich Pfad geändert hat
            entry["cover_page"] = cover_page  # evtl. neues Cover
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

        # HTML-Datei mit Script-Tag aktualisieren
        with html_file.open("r", encoding="utf-8") as f:
            html_content = f.read()

        # Prüfen, ob das exakte Script schon da ist
        script_line = '<script src="/static/mokuro_progress.js"></script>'
        if script_line not in html_content:
            if "</body>" in html_content.lower():
                # Einfügen des Script-Tags vor </body>
                new_content = html_content.replace(
                    "</body>",
                    f"\n{script_line}\n</body>"
                )
                with html_file.open("w", encoding="utf-8") as f:
                    f.write(new_content)
                print(f"✅ Eingefügt in {html_file.name}")
            else:
                print(f"⚠️ Kein </body> gefunden in {html_file.name}")
        else:
            print(f"⏩ Script bereits enthalten in {html_file.name}")

# Fortschritt speichern
progress_file.write_text(json.dumps(progress_entries, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"✅ Fortschritt aktualisiert: {progress_file.resolve()}")
