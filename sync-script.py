"""
2SL Photography - Photo Sync Tool
==================================
Scans image folders and updates photos.json automatically.

- Adds new images/videos found in folders
- Preserves existing titles and descriptions
- Removes entries for files that no longer exist
- Creates a backup before overwriting

Usage:
    python sync_photos.py          (scan and update)
    python sync_photos.py --dry    (preview changes without saving)
"""

import os
import json
import sys
import shutil
from datetime import datetime

# =============================================================
# CONFIGURATION - Edit these to match your folder structure
# =============================================================

# Path to your photos.json file
JSON_FILE = "photos.json"

# Mapping: JSON category key → folder path
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

# Also scan the videos folder for entries that reference videos
VIDEOS_FOLDER = "videos"

# Supported file extensions
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".tiff"}
VIDEO_EXTENSIONS = {".mp4", ".webm", ".mov"}
ALL_EXTENSIONS = IMAGE_EXTENSIONS | VIDEO_EXTENSIONS

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
    
    # Sort: camera files first (1C8A, IMG_, P100, PICT, DSCN), then others
    files.sort(key=lambda f: f.lower())
    return files


def get_file_type(filename):
    """Determine if file is a video based on extension."""
    ext = os.path.splitext(filename)[1].lower()
    if ext in VIDEO_EXTENSIONS:
        return "video"
    return None


def sync_category(category_key, folder_path, existing_entries):
    """Sync a single category. Returns updated entries list and change stats."""
    # Build lookup of existing entries by src path
    existing_by_src = {}
    for entry in existing_entries:
        # Normalize path for comparison
        normalized = entry["src"].replace("\\", "/")
        existing_by_src[normalized] = entry

    # Scan folder for actual files
    actual_files = scan_folder(folder_path)

    # Build new entries list
    new_entries = []
    added = 0
    kept = 0
    removed = 0

    for filename in actual_files:
        src_path = f"{folder_path}/{filename}".replace("\\", "/")
        
        if src_path in existing_by_src:
            # File exists in JSON - keep existing data
            new_entries.append(existing_by_src[src_path])
            kept += 1
        else:
            # New file - create entry with default values
            entry = {
                "src": src_path,
                "title": os.path.splitext(filename)[0],
                "description": "Description"
            }
            file_type = get_file_type(filename)
            if file_type:
                entry["type"] = file_type
            new_entries.append(entry)
            added += 1

    # Count removed entries (files in JSON but not on disk)
    actual_src_paths = {
        f"{folder_path}/{f}".replace("\\", "/") 
        for f in actual_files
    }
    for src_path in existing_by_src:
        # Only count as removed if the entry pointed to this folder
        if src_path.startswith(folder_path.replace("\\", "/")) and src_path not in actual_src_paths:
            removed += 1

    # Preserve video entries from the videos/ folder
    for entry in existing_entries:
        src = entry.get("src", "").replace("\\", "/")
        if src.startswith(VIDEOS_FOLDER):
            # Check if video file still exists
            if os.path.exists(src):
                # Only add if not already in new_entries
                if not any(e["src"] == src for e in new_entries):
                    new_entries.insert(0, entry)
                    kept += 1
            else:
                removed += 1

    return new_entries, added, kept, removed


def main():
    dry_run = "--dry" in sys.argv

    print("=" * 60)
    print("  2SL Photography - Photo Sync Tool")
    print("=" * 60)
    
    if dry_run:
        print("\n  MODE: Dry Run (preview only, no files will be changed)\n")
    else:
        print()

    # Load existing JSON
    existing = load_existing_json()
    
    total_added = 0
    total_kept = 0
    total_removed = 0
    updated_json = {}

    # Process each category
    for category_key, folder_path in CATEGORY_FOLDERS.items():
        existing_entries = existing.get(category_key, [])
        
        new_entries, added, kept, removed = sync_category(
            category_key, folder_path, existing_entries
        )
        
        updated_json[category_key] = new_entries
        total_added += added
        total_kept += kept
        total_removed += removed

        # Status icon
        if added > 0 or removed > 0:
            icon = "~"  # changed
        else:
            icon = "="  # unchanged

        folder_exists = os.path.exists(folder_path)
        status = "" if folder_exists else " [FOLDER NOT FOUND]"
        
        print(f"  [{icon}] {category_key:<30} "
              f"Total: {len(new_entries):>3}  "
              f"(+{added} new, {kept} kept, -{removed} removed)"
              f"{status}")

    # Summary
    print()
    print("-" * 60)
    print(f"  SUMMARY")
    print(f"    New files found:    +{total_added}")
    print(f"    Existing kept:       {total_kept}")
    print(f"    Removed (missing):  -{total_removed}")
    print(f"    Total entries:       {sum(len(v) for v in updated_json.values())}")
    print("-" * 60)

    if total_added == 0 and total_removed == 0:
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