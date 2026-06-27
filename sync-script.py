"""
2SL Photography - Photo Sync Tool
==================================
Scans image folders and updates photos.json automatically.

- Adds new images/videos found in folders
- Preserves existing titles, descriptions, and GPS coordinates
- Extracts GPS coordinates and camera metadata from EXIF data
- Removes entries for files that no longer exist
- Creates a backup before overwriting

Usage:
    python sync_photos.py          (scan and update)
    python sync_photos.py --dry    (preview changes without saving)
    python sync_photos.py --exif   (re-read EXIF for ALL entries, not just new ones)

Requires:
    pip install Pillow
"""

import os
import json
import sys
import shutil
from datetime import datetime

# =============================================================
# CONFIGURATION - Edit these to match your folder structure
# =============================================================

JSON_FILE = "photos.json"

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

VIDEOS_FOLDER = "videos"

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".tiff"}
VIDEO_EXTENSIONS = {".mp4", ".webm", ".mov"}
ALL_EXTENSIONS = IMAGE_EXTENSIONS | VIDEO_EXTENSIONS

# =============================================================
# EXIF EXTRACTION
# =============================================================

PILLOW_AVAILABLE = False

try:
    from PIL import Image
    from PIL.ExifTags import TAGS, GPSTAGS
    PILLOW_AVAILABLE = True
except ImportError:
    pass


def extract_exif_data(filepath):
    """
    Extract GPS coordinates and camera metadata from EXIF data.
    Returns a dict with available fields.
    """
    if not PILLOW_AVAILABLE:
        return {}

    try:
        image = Image.open(filepath)
        exif_data = image._getexif()
        if not exif_data:
            return {}

        result = {}
        gps_info = None

        for tag_id, value in exif_data.items():
            tag_name = TAGS.get(tag_id, tag_id)

            if tag_name == "GPSInfo":
                gps_info = {}
                for gps_tag_id, gps_value in value.items():
                    gps_tag_name = GPSTAGS.get(gps_tag_id, gps_tag_id)
                    gps_info[gps_tag_name] = gps_value

            elif tag_name == "DateTimeOriginal":
                try:
                    dt = datetime.strptime(str(value), "%Y:%m:%d %H:%M:%S")
                    result["date_taken"] = dt.strftime("%d/%m/%Y %H:%M")
                except (ValueError, TypeError):
                    pass

            elif tag_name == "Make":
                result["camera_make"] = str(value).strip()

            elif tag_name == "Model":
                result["camera_model"] = str(value).strip()

            elif tag_name == "FNumber":
                try:
                    fnum = float(value)
                    result["f_stop"] = f"f/{fnum:g}"
                except (TypeError, ValueError, ZeroDivisionError):
                    pass

            elif tag_name == "ExposureTime":
                try:
                    exp = float(value)
                    if exp < 1:
                        denom = round(1 / exp)
                        result["exposure_time"] = f"1/{denom}s"
                    else:
                        result["exposure_time"] = f"{exp:g}s"
                except (TypeError, ValueError, ZeroDivisionError):
                    pass

            elif tag_name == "ISOSpeedRatings":
                try:
                    result["iso"] = str(int(value))
                except (TypeError, ValueError):
                    pass

            elif tag_name == "FocalLength":
                try:
                    fl = float(value)
                    result["focal_length"] = f"{round(fl)}mm"
                except (TypeError, ValueError):
                    pass

        # Build camera string (avoid repeating make in model)
        make = result.pop("camera_make", None)
        model = result.pop("camera_model", None)
        if make and model:
            if model.lower().startswith(make.lower()):
                result["camera"] = model
            else:
                result["camera"] = f"{make} {model}"
        elif model:
            result["camera"] = model
        elif make:
            result["camera"] = make

        # Extract GPS coordinates
        if gps_info:
            lat, lng = extract_gps_coords(gps_info)
            if lat is not None and lng is not None:
                result["lat"] = round(lat, 6)
                result["lng"] = round(lng, 6)

        return result

    except Exception:
        return {}


def extract_gps_coords(gps_info):
    """Extract lat/lng from GPS EXIF info."""
    try:
        if "GPSLatitude" not in gps_info or "GPSLatitudeRef" not in gps_info:
            return None, None
        if "GPSLongitude" not in gps_info or "GPSLongitudeRef" not in gps_info:
            return None, None

        lat = convert_dms_to_decimal(
            gps_info["GPSLatitude"],
            gps_info["GPSLatitudeRef"]
        )
        lng = convert_dms_to_decimal(
            gps_info["GPSLongitude"],
            gps_info["GPSLongitudeRef"]
        )
        return lat, lng
    except Exception:
        return None, None


def convert_dms_to_decimal(dms, ref):
    """Convert Degrees/Minutes/Seconds to Decimal Degrees."""
    try:
        degrees = float(dms[0])
        minutes = float(dms[1])
        seconds = float(dms[2])
        decimal = degrees + (minutes / 60.0) + (seconds / 3600.0)
        if ref in ['S', 'W']:
            decimal = -decimal
        return decimal
    except (TypeError, IndexError, ValueError):
        return None


def build_metadata_string(exif):
    """Build a display string from EXIF fields with labels."""
    parts = []
    if "date_taken" in exif:
        parts.append(f"Date taken: {exif['date_taken']}")
    if "camera" in exif:
        parts.append(f"Camera: {exif['camera']}")
    if "f_stop" in exif:
        parts.append(f"F-stop: {exif['f_stop']}")
    if "exposure_time" in exif:
        parts.append(f"Exposure time: {exif['exposure_time']}")
    if "iso" in exif:
        parts.append(f"ISO Speed: {exif['iso']}")
    if "focal_length" in exif:
        parts.append(f"Focal length: {exif['focal_length']}")
    return " \u2022 ".join(parts) if parts else ""


# =============================================================
# MAIN LOGIC
# =============================================================

def load_existing_json():
    """Load existing photos.json or return empty dict."""
    if os.path.exists(JSON_FILE):
        with open(JSON_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def scan_folder(folder_path):
    """Scan a folder and return sorted list of media files."""
    files = []
    if not os.path.exists(folder_path):
        return files
    for filename in os.listdir(folder_path):
        ext = os.path.splitext(filename)[1].lower()
        if ext in ALL_EXTENSIONS:
            files.append(filename)
    files.sort(key=lambda f: f.lower())
    return files


def get_file_type(filename):
    """Determine if file is a video based on extension."""
    ext = os.path.splitext(filename)[1].lower()
    return "video" if ext in VIDEO_EXTENSIONS else None


def sync_category(category_key, folder_path, existing_entries, force_exif=False):
    """Sync a single category. Returns updated entries list and change stats."""
    existing_by_src = {}
    for entry in existing_entries:
        normalized = entry["src"].replace("\\", "/")
        existing_by_src[normalized] = entry

    actual_files = scan_folder(folder_path)

    new_entries = []
    added = 0
    kept = 0
    removed = 0
    gps_count = 0
    meta_count = 0

    for filename in actual_files:
        src_path = f"{folder_path}/{filename}".replace("\\", "/")
        full_path = os.path.join(folder_path, filename)
        file_type = get_file_type(filename)

        if src_path in existing_by_src:
            entry = existing_by_src[src_path]

            # Re-read EXIF if --exif flag used and entry has no metadata yet
            if force_exif and file_type is None and PILLOW_AVAILABLE:
                if "metadata" not in entry or not entry["metadata"]:
                    exif = extract_exif_data(full_path)
                    meta_str = build_metadata_string(exif)
                    if meta_str:
                        entry["metadata"] = meta_str
                    # Add GPS if not already set
                    if "lat" not in entry and "lat" in exif:
                        entry["lat"] = exif["lat"]
                    if "lng" not in entry and "lng" in exif:
                        entry["lng"] = exif["lng"]

            new_entries.append(entry)
            kept += 1
        else:
            entry = {
                "src": src_path,
                "title": os.path.splitext(filename)[0],
                "description": "Description"
            }

            if file_type:
                entry["type"] = file_type

            # Extract EXIF for new images
            if file_type is None and PILLOW_AVAILABLE:
                exif = extract_exif_data(full_path)
                meta_str = build_metadata_string(exif)
                if meta_str:
                    entry["metadata"] = meta_str
                if "lat" in exif:
                    entry["lat"] = exif["lat"]
                if "lng" in exif:
                    entry["lng"] = exif["lng"]

            new_entries.append(entry)
            added += 1

        # Count stats
        if entry.get("lat") is not None and entry.get("lng") is not None:
            gps_count += 1
        if entry.get("metadata"):
            meta_count += 1

    # Count removed
    actual_src_paths = {
        f"{folder_path}/{f}".replace("\\", "/")
        for f in actual_files
    }
    for src_path in existing_by_src:
        if src_path.startswith(folder_path.replace("\\", "/")) and src_path not in actual_src_paths:
            removed += 1

    # Preserve video entries from videos/ folder
    for entry in existing_entries:
        src = entry.get("src", "").replace("\\", "/")
        if src.startswith(VIDEOS_FOLDER):
            if os.path.exists(src):
                if not any(e["src"] == src for e in new_entries):
                    new_entries.insert(0, entry)
                    kept += 1
                    if entry.get("lat") is not None and entry.get("lng") is not None:
                        gps_count += 1
                    if entry.get("metadata"):
                        meta_count += 1
            else:
                removed += 1

    return new_entries, added, kept, removed, gps_count, meta_count


def main():
    dry_run = "--dry" in sys.argv
    force_exif = "--exif" in sys.argv

    print("=" * 70)
    print("  2SL Photography - Photo Sync Tool")
    print("=" * 70)

    if dry_run:
        print("\n  MODE: Dry Run (preview only, no files will be changed)")
    if force_exif:
        print("  MODE: Re-read EXIF for entries missing metadata")

    if PILLOW_AVAILABLE:
        print("  EXIF extraction: Enabled (Pillow detected)")
    else:
        print("  EXIF extraction: Disabled (install: pip install Pillow)")

    print()

    existing = load_existing_json()

    total_added = 0
    total_kept = 0
    total_removed = 0
    total_gps = 0
    total_meta = 0
    updated_json = {}

    for category_key, folder_path in CATEGORY_FOLDERS.items():
        existing_entries = existing.get(category_key, [])

        new_entries, added, kept, removed, gps_count, meta_count = sync_category(
            category_key, folder_path, existing_entries, force_exif
        )

        updated_json[category_key] = new_entries
        total_added += added
        total_kept += kept
        total_removed += removed
        total_gps += gps_count
        total_meta += meta_count

        icon = "~" if (added > 0 or removed > 0) else "="
        folder_exists = os.path.exists(folder_path)
        status = "" if folder_exists else " [FOLDER NOT FOUND]"

        extras = []
        if gps_count > 0:
            extras.append(f"GPS:{gps_count}")
        if meta_count > 0:
            extras.append(f"EXIF:{meta_count}")
        extra_str = "  " + " ".join(extras) if extras else ""

        print(f"  [{icon}] {category_key:<30} "
              f"Total: {len(new_entries):>3}  "
              f"(+{added} new, {kept} kept, -{removed} removed)"
              f"{extra_str}{status}")

    print()
    print("-" * 70)
    print(f"  SUMMARY")
    print(f"    New files found:       +{total_added}")
    print(f"    Existing kept:          {total_kept}")
    print(f"    Removed (missing):     -{total_removed}")
    print(f"    Total entries:          {sum(len(v) for v in updated_json.values())}")
    print(f"    With GPS coordinates:   {total_gps}")
    print(f"    With EXIF metadata:     {total_meta}")
    print("-" * 70)

    if total_added == 0 and total_removed == 0 and not force_exif:
        print("\n  No changes needed. photos.json is already in sync.")
        return

    if dry_run:
        print(f"\n  Dry run complete. Run without --dry to apply changes.")
        return

    # Create backup
    if os.path.exists(JSON_FILE):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"photos_backup_{timestamp}.json"
        shutil.copy2(JSON_FILE, backup_name)
        print(f"\n  Backup created: {backup_name}")

    # Write updated JSON
    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(updated_json, f, indent=4, ensure_ascii=False)

    print(f"  Updated: {JSON_FILE}")
    print(f"\n  Done! Open admin.html to edit titles and descriptions.")


if __name__ == "__main__":
    main()