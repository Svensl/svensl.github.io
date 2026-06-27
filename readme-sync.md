# 2SL Photography - Photo Sync Tool

## Overview

`sync_photos.py` is a Python script that automatically scans your image folders and updates `photos.json` to match. It detects new images, removes entries for deleted files, and preserves all existing titles and descriptions.

> **Important:** This script is for local use only. It should not be uploaded to GitHub Pages.

---

## Prerequisites

- **Python 3.6+** installed on your computer
- To check: open a terminal and type `python --version`
- If not installed: download from [python.org/downloads](https://www.python.org/downloads/)
- During installation, check **"Add Python to PATH"**

No additional Python packages are required. The script uses only built-in libraries.

---

## File Location

Place `sync_photos.py` in your project root alongside `photos.json`:

```
svensl.github.io/
  index.html
  admin.html
  photos.json        ← Read and updated by the script
  sync_photos.py     ← This script
  images/
    Adventures/
      Night/
      Wanderlust/
      Window Seat/
    Landscapes/
    Life/
      Fauna/
      Flora/
      People/
    Orange/
    Water/
  videos/
```

---

## Usage

### Open the Terminal

In VS Code, press `Ctrl + ~` to open the integrated terminal.

Make sure you are in your project folder:

```bash
cd C:\Users\schmi\OneDrive\Pictures\Website\Website 2025\svensl.github.io
```

### Preview Changes (Dry Run)

Preview what the script would do without modifying any files:

```bash
python sync_photos.py --dry
```

Example output:

```
============================================================
  2SL Photography - Photo Sync Tool
============================================================

  MODE: Dry Run (preview only, no files will be changed)

  [~] adventures-night              Total:  45  (+2 new, 43 kept, -0 removed)
  [=] adventures-wanderlust         Total:  30  (+0 new, 30 kept, -0 removed)
  [~] landscapes                    Total:  62  (+3 new, 59 kept, -1 removed)
  [=] life-fauna                    Total:  39  (+0 new, 39 kept, -0 removed)
  [=] life-flora                    Total:  25  (+0 new, 25 kept, -0 removed)
  [=] life-people                   Total:  60  (+0 new, 60 kept, -0 removed)
  [=] orange                        Total:  33  (+0 new, 33 kept, -0 removed)
  [=] water                         Total:  43  (+0 new, 43 kept, -0 removed)

  SUMMARY
    New files found:    +5
    Existing kept:       280
    Removed (missing):  -1
    Total entries:       284

  Dry run complete. Run without --dry to apply changes.
```

### Apply Changes

If the preview looks correct, run without the `--dry` flag:

```bash
python sync_photos.py
```

The script will:

1. Create a timestamped backup of your current `photos.json`
2. Add entries for new image and video files
3. Remove entries for files that no longer exist on disk
4. Preserve all existing titles and descriptions
5. Write the updated `photos.json`

---

## Output Symbols

| Symbol | Meaning |
|--------|---------|
| `[=]` | Category unchanged, no new or removed files |
| `[~]` | Category changed, files were added or removed |
| `[FOLDER NOT FOUND]` | The folder path does not exist on disk |

---

## What the Script Does

| Scenario | Action |
|----------|--------|
| New image file found in a folder | Added to JSON with filename as title and "Description" as placeholder |
| New video file found (.mp4, .webm, .mov) | Added to JSON with `"type": "video"` |
| Image already exists in JSON | Kept as-is with title, description, and GPS coordinates preserved |
| Image in JSON but file deleted from folder | Entry removed from JSON |
| Video in `videos/` folder referenced in JSON | Preserved if file still exists |

> **Note:** The script preserves all existing data fields including `title`, `description`, `lat`, `lng`, and `type`. No manually entered data is lost when syncing.

---

## Backups

Every time the script runs (not in dry-run mode), it creates a backup file:

```
photos_backup_20260617_143022.json
```

The filename includes the date and time of the backup. You can safely delete old backups when you no longer need them.

---

## Configuration

The category-to-folder mapping is defined at the top of the script. Edit the `CATEGORY_FOLDERS` dictionary if you add, rename, or reorganize categories:

```python
CATEGORY_FOLDERS = {
    "adventures-night":       "images/Adventures/Night",
    "adventures-wanderlust":  "images/Adventures/Wanderlust",
    "adventures-window-seat": "images/Adventures/Window Seat",
    "landscapes":             "images/Landscapes",
    "life-fauna":             "images/Life/Fauna",
    "life-flora":             "images/Life/Flora",
    "life-people":            "images/Life/People",
    "orange":                 "images/Orange",
    "water":                  "images/Water",
}
```

### Adding a New Category

1. Create the folder in `images/` (e.g., `images/NewCategory`)
2. Add the mapping to `CATEGORY_FOLDERS`:
   ```python
   "new-category": "images/NewCategory",
   ```
3. Add the corresponding HTML section in `index.html`
4. Run `python sync_photos.py`

### Supported File Types

Defined at the top of the script:

```python
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".tiff"}
VIDEO_EXTENSIONS = {".mp4", ".webm", ".mov"}
```

Add or remove extensions as needed.

---

## Recommended Workflow

```
1. Add, remove, or reorganize photos in your image folders

2. Preview changes:
   python sync_photos.py --dry

3. Apply changes:
   python sync_photos.py

4. Open admin.html with Live Server
   → Edit titles, descriptions, and GPS coordinates for new entries
   → Click "Export photos.json"
   → Replace the file in your project folder

5. Test locally:
   → Open index.html with Live Server
   → Verify everything looks correct

6. Publish:
   git add .
   git commit -m "Updated photos"
   git push
```

---

## Troubleshooting

### "python is not recognized"

Try these alternatives:

```bash
python3 sync_photos.py --dry
```

or

```bash
py sync_photos.py --dry
```

If none work, Python is not installed or not in your PATH. Reinstall Python and check **"Add Python to PATH"** during installation. Restart VS Code after installing.

### "No such file or directory"

Make sure your terminal is in the correct folder. Run `dir` (Windows) or `ls` (Mac/Linux) to verify you can see `sync_photos.py` in the listing.

### "[FOLDER NOT FOUND]" message

The folder path in `CATEGORY_FOLDERS` doesn't match your actual folder structure. Check for:

- Typos in folder names
- Case sensitivity (e.g., `Night` vs `night`)
- Missing folders

### New photos not appearing on the website

After running the sync script:

1. Open `admin.html` to verify the new entries are in the JSON
2. Check that the `src` paths match the actual file locations
3. Make sure you exported the updated `photos.json` from admin.html (or the sync script already wrote it)
4. Clear your browser cache (`Ctrl + Shift + R`) and reload

### Encoding issues with special characters

The script writes JSON with `ensure_ascii=False` and UTF-8 encoding. If you see garbled characters:

1. Open `photos.json` in VS Code
2. Check the encoding in the bottom-right corner — it should say **UTF-8**
3. If not, click the encoding label → "Save with Encoding" → select **UTF-8**

---

## Command Reference

| Command | Description |
|---------|-------------|
| `python sync_photos.py --dry` | Preview changes without modifying files |
| `python sync_photos.py` | Scan folders and update photos.json |

---

## File Reference

| File | Purpose | Deploy to web? |
|------|---------|---------------|
| `sync_photos.py` | Folder scanning and JSON sync | **No** |
| `admin.html` | Visual content editor | **No** |
| `photos.json` | Photo data (titles, descriptions) | Yes |
| `index.html` | Main website | Yes |

---

## Notes

- The script does **not** modify, move, or delete any image or video files. It only reads folder contents and updates `photos.json`.
- New entries use the filename (without extension) as the default title. Edit titles, descriptions, and GPS coordinates using `admin.html`.
- The script preserves all existing fields in each entry, including `title`, `description`, `lat`, `lng`, and `type`.
- The script sorts files alphabetically within each category. If you need a different order, rearrange entries manually in `admin.html` or directly in `photos.json`.

---

## JSON Entry Format

Each entry in `photos.json` supports the following fields:

```json
{
    "src": "images/Orange/1C8A0438.jpg",
    "title": "Marseilles",
    "description": "Planete Mars",
    "lat": 43.2965,
    "lng": 5.3698,
    "type": "video"
}
```

| Field | Required | Description |
|-------|----------|-------------|
| `src` | Yes | Relative path to image or video file |
| `title` | Yes | Display title on website and in admin |
| `description` | Yes | Description text shown in lightbox |
| `lat` | No | GPS latitude in WGS84 Decimal Degrees (-90 to 90) |
| `lng` | No | GPS longitude in WGS84 Decimal Degrees (-180 to 180) |
| `type` | No | Set to `"video"` for video files, omit for images |