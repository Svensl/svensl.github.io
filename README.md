# 2SL Photography — Complete Project Documentation

This is the single, consolidated reference for the 2SL Photography website. It merges all previous documentation (`readme.md`, `admin-page-readme.md`, `readme-sync.md`, and `InitialWebSetup.md`) into one file, organized by source file.

The site is a self-contained photography portfolio hosted on GitHub Pages at **https://2slphotography.com** (GitHub repository: `svensl/svensl.github.io`).

---

## Table of Contents

1. [Project Overview & File Map](#project-overview--file-map)
2. [`index.html` — The Public Website](#indexhtml--the-public-website)
3. [`photos.json` — The Content Data File](#photosjson--the-content-data-file)
4. [`admin-page.html` — The Content Manager](#admin-pagehtml--the-content-manager)
5. [`sync-script.py` — The Photo Sync Tool](#sync-scriptpy--the-photo-sync-tool)
6. [`compress_mp4.py` — The Video Compression Tool](#compress_mp4py--the-video-compression-tool)
7. [Initial Web Setup — GitHub Pages & Namecheap Domain](#initial-web-setup--github-pages--namecheap-domain)
8. [Everyday Workflows](#everyday-workflows)

---

## Project Overview & File Map

The website reads all of its photo content from `photos.json`, so you almost never need to edit `index.html` to add, remove, or re-caption photos. Content is managed with two local tools (`admin-page.html` and `sync-script.py`) and then published to the web.

| File | Purpose | Deploy to web? |
|------|---------|----------------|
| `index.html` | The public website | **Yes** |
| `photos.json` | Photo data: paths, titles, descriptions, locations | **Yes** |
| `images/` | Photo files | **Yes** |
| `videos/` | Video files | **Yes** |
| `CNAME` | Custom domain configuration | **Yes** |
| `admin-page.html` | Content Manager (local editing tool) | **No** |
| `sync-script.py` | Folder-to-JSON sync script (reads photo EXIF; needs Pillow) | **No** |
| `compress_mp4.py` | Local video compression helper | **No** |
| `readme.md` | This documentation | Optional |

> **Rule of thumb:** only the website itself, its data file, its media folders, and `CNAME` go live. The Python scripts and the Content Manager are local-only tools and should not be uploaded to GitHub Pages.

---

## `index.html` — The Public Website

`index.html` is the public photography portfolio for 2SL Photography. It is a single self-contained file with HTML, CSS, and JavaScript all in one. It displays photos and videos organized into categories, with a full-screen landing image, category navigation, a mosaic gallery, and a lightbox viewer.

> This is the file that **is** deployed to the web via GitHub Pages.

### How It Works

When the page loads, a script fetches `photos.json` and builds each category's gallery from the entries it finds. Each entry provides a file path (`src`), a `title`, a `description`, and optionally a location (`lat`/`lng`) and a `type` of `video`.

```
index.html  ──reads──>  photos.json  ──points to──>  images/ and videos/
```

Because everything is driven by `photos.json`, the website's appearance updates automatically whenever that file changes.

### ⚠️ Hard-Coded Media (Important)

Three pieces of media on the site are **hard-coded directly into `index.html`** and are **NOT** managed by `photos.json` or by the Content Manager (`admin-page.html`). To change any of them, you must edit `index.html` directly:

| Where it appears | Current file (hard-coded in `index.html`) | Where to edit |
|------------------|-------------------------------------------|---------------|
| Landing / home page background image | `images/1C8A0980.jpg` | `#landing` CSS rule (around line 24): `background: url('images/1C8A0980.jpg') ...` |
| **Adventures** tab background video | `videos/Khartoum_TukTuk_720p.mp4` | `<source src="videos/Khartoum_TukTuk_720p.mp4">` in the `#adventures-landing` section (around line 656) |
| **Life** tab background video | `videos/20190802_215709_720p.mp4` | `<source src="videos/20190802_215709_720p.mp4">` in the `#life-landing` section (around line 671) |

To swap any of these, replace the filename in the relevant line of `index.html` (and add the new image/video file to the `images/` or `videos/` folder), then commit and push. The Content Manager will **not** show or change these — it only manages the gallery photos and videos listed in `photos.json`.

### Page Structure

**Landing Page** — A full-screen background image (currently `images/1C8A0980.jpg`, hard-coded — see above) shown when the site first loads.

**Navigation Bar** — A fixed bar across the top with the site title and tabs:

- **Adventures** — opens a category landing page with a background video (hard-coded) and three sub-galleries: Night, Wanderlust, Window Seat
- **Landscapes** — opens the Landscapes gallery directly
- **Life** — opens a category landing page with a background video (hard-coded) and three sub-galleries: Fauna, Flora, People
- **Orange** — opens the Orange gallery directly
- **Water** — opens the Water gallery directly
- **Map** — opens an interactive world map plotting every geotagged photo (see Map Page below)
- **About** — opens the About page

A **Home** button appears (bottom-right on mobile, top-right on desktop) once you have navigated away from the landing page.

**Category Landing Pages (Adventures & Life)** — These two sections show a looping background video with buttons for their sub-galleries. Both videos are hard-coded in `index.html` (see the Hard-Coded Media section above).

**Galleries** — Each gallery displays its photos as a responsive **mosaic** of square tiles. Hovering a tile reveals its title; hovering a video tile plays it muted. Clicking any tile opens the lightbox.

**Lightbox** — A full-screen overlay showing the selected image or video at large size, alongside its title, its EXIF capture details (the `metadata` string, shown as a "Metadata:" line when present), and its description. Within the lightbox you can:

- Move between items with the **on-screen arrows** or the **left/right arrow keys**
- Close with the **×** button or the **Escape** key

Descriptions preserve line breaks (the CSS uses `white-space: pre-wrap`), so multi-paragraph captions written in the Content Manager display correctly.

**Map Page** — A full-page interactive map (built with Leaflet) that automatically plots every entry in `photos.json` that has `lat`/`lng` coordinates. Each photo appears as a small thumbnail marker; clicking a marker opens a popup with the photo, its title, and its category, plus a **View Photo** link that opens the item in the lightbox. The map auto-fits to show all geotagged photos and is built on demand the first time the Map tab is opened.

A base-map switcher (a Leaflet layer control, shown expanded in the bottom-left corner) lets the visitor choose between three base maps:

- **Topographic** — Esri World Topographic map (the default)
- **Satellite** — Esri World Imagery with a transparent Esri reference overlay (boundaries and place names) stacked on top
- **Light** — CARTO's light/minimal basemap

All three base layers are free public tile services used without an API key, served from Esri (ArcGIS Online) and CARTO. The map depends on two libraries loaded from CDNs — Leaflet (`unpkg.com`) and OverlappingMarkerSpiderfier (`cdnjs.cloudflare.com`) — so an internet connection is required for the map and its tiles to display.

#### Overlapping markers — the "spider" function

Many photos are taken at (or very near) the same spot, so their thumbnail markers would otherwise stack on top of each other and only the top one would be clickable. To solve this, the Map page uses the **OverlappingMarkerSpiderfier** library (OMS, loaded from a CDN alongside Leaflet). When you click a cluster of overlapping or nearby markers, they fan out — or "spiderfy" — into a ring (or, for larger clusters, a spiral), with a thin leg line connecting each marker back to its true location, so every photo at that spot becomes individually visible and clickable.

Behaviour wired into the page:

- Clicking a marker (whether standalone or one that has fanned out) opens its photo popup; clicking a stacked group fans it out first.
- The open popup is closed automatically while a group is fanning out, to avoid a popup covering the spread markers.
- Because zooming re-positions everything, the page remembers which marker was fanned out and re-opens it shortly after a zoom finishes (a ~400 ms delay lets the zoom animation settle), so your place isn't lost when you zoom in or out.

**Fields that tailor the spider function.** These are set when the spiderfier is created in `index.html` (in the `initMap()` function, in the `new OverlappingMarkerSpiderfier(map, { … })` options object). Adjust them to change how clusters detect overlap and how far the markers fan out:

| Option | Current value | What it controls |
|--------|---------------|------------------|
| `keepSpiderfied` | `true` | Keeps the markers fanned out after you click one of them, instead of collapsing the group back immediately. Set to `false` to auto-collapse on selection. |
| `nearbyDistance` | `40` | How close (in pixels) two markers must be to count as "overlapping" and therefore be grouped together. Larger values group markers that are farther apart; smaller values only group near-exact overlaps. |
| `legWeight` | `2` | Thickness (in pixels) of the leg lines drawn from each fanned-out marker back to the cluster's real location. |
| `circleFootSeparation` | `50` | Spacing between markers when a **small** cluster fans out into a **circle**. Larger values spread the ring wider. |
| `spiralFootSeparation` | `56` | Spacing between markers when a **larger** cluster fans out into a **spiral**. Larger values increase the gap between successive markers along the spiral. |
| `spiralLengthStart` | `22` | How far from the centre the spiral begins (its starting radius). |
| `spiralLengthFactor` | `10` | How quickly the spiral grows outward as more markers are added — higher values produce a looser, more spread-out spiral. |

> OMS automatically chooses a **circle** layout for small clusters and switches to a **spiral** once a cluster has more markers than the circle can comfortably hold, which is why there are separate `circleFoot…` and `spiral…` settings. The `~400 ms` re-spiderfy delay after zoom is a `setTimeout` value in the `zoomend` handler (just below the options object), not part of the options object itself — adjust it there if zoom feels too fast or slow before the cluster re-opens.

> This public Map page is separate from the editing map inside the Content Manager (`admin-page.html`), and the two now offer different base-map sets: the public map provides Topographic / Satellite / Light, while the Content Manager provides Street / Satellite (Hybrid). They are configured independently in their respective files.

**About Page** — A short text biography for Sven Lothar Schmitz-Leuffen with a contact line for purchase inquiries (the email is written in an obfuscated form, `svenlsl_at_protonmail_dot_com`, to reduce scraping).

### Categories

The galleries are defined by the category keys in `photos.json`. The site expects these keys:

| Category key | Section shown |
|--------------|---------------|
| `adventures-night` | Adventures / Night |
| `adventures-wanderlust` | Adventures / Wanderlust |
| `adventures-window-seat` | Adventures / Window Seat |
| `landscapes` | Landscapes |
| `life-fauna` | Life / Fauna |
| `life-flora` | Life / Flora |
| `life-people` | Life / People |
| `orange` | Orange |
| `water` | Water |

Each key in the JSON must match the `id` of a gallery grid in `index.html` (e.g. `adventures-night` matches `<div class="mosaic" id="adventures-night-grid">`). If you add a brand-new category, you must add both the JSON key **and** a matching HTML section.

### Editing Content

You do **not** edit `index.html` to change gallery photos or captions. Instead:

1. **Add or remove photo files**, then run the sync script to update `photos.json`.
2. **Edit titles, descriptions, and locations** using the Content Manager (`admin-page.html`).
3. **Publish** the updated `photos.json` (and any new image/video files) to GitHub Pages.

The only reasons to edit `index.html` directly are structural changes: adding a new category section, changing the **hard-coded landing image**, swapping the **hard-coded category landing videos**, editing the About text, or adjusting the styling.

### Image Protection

The site includes basic deterrent measures: right-clicking on images and dragging images are disabled via JavaScript. This discourages casual copying only. Anyone can still view images through browser developer tools or by taking a screenshot, so do not treat this as real protection for high-value images.

### Responsive Design

The layout adapts to screen size through CSS media queries:

- **Desktop:** wide mosaic, lightbox image and caption side by side
- **Tablet (≤768px):** stacked navigation, smaller mosaic tiles, lightbox image above caption
- **Phone (≤480px):** smallest mosaic tiles and reduced font sizes

### Troubleshooting (Website)

**A photo or video does not appear**
- Confirm the file's `src` path in `photos.json` exactly matches the real file location. Paths are **case-sensitive** on GitHub Pages (unlike Windows).
- Confirm the file was actually committed and pushed.

**A whole gallery is empty**
- Check that the category key in `photos.json` matches a grid `id` in `index.html`.

**Videos do not play**
- Confirm the file is `.mp4` and that the entry has `"type": "video"` in `photos.json`.

**Changes do not show up**
- Clear your browser cache (`Ctrl + Shift + R`) and reload. GitHub Pages can also take a few minutes to update.

---

## `photos.json` — The Content Data File

`photos.json` holds all gallery content: file paths, titles, descriptions, and optional GPS coordinates. It is read by `index.html` (to build the site), edited by `admin-page.html`, and synced by `sync-script.py`.

> **Note:** `photos.json` controls the gallery photos and videos only. It does **not** control the hard-coded landing image or the two hard-coded category videos described in the `index.html` section.

### JSON Entry Format

```json
{
    "src": "images/Adventures/Night/1C8A1217.jpg",
    "title": "Ethiopia - 09/01/2016",
    "description": "Erta Ale Volcano",
    "lat": 13.60626,
    "lng": 40.661862,
    "metadata": "Date taken: 09/01/2016 22:11 • Camera: Canon EOS 5D Mark III • F-stop: f/5 • Exposure time: 1/80s • ISO Speed: 1000 • Focal length: 100mm",
    "type": "video"
}
```

| Field | Required | Description |
|-------|----------|-------------|
| `src` | Yes | Relative path to image or video file |
| `title` | Yes | Display title on website and in admin |
| `description` | Yes | Description text shown in lightbox |
| `lat` | No | GPS latitude in WGS84 Decimal Degrees (−90 to 90) |
| `lng` | No | GPS longitude in WGS84 Decimal Degrees (−180 to 180) |
| `metadata` | No | A single string of EXIF capture details (date taken, camera, f-stop, exposure, ISO, focal length), separated by ` • `. The Content Manager reads its read-only "Date Taken" field from this string. |
| `type` | No | Set to `"video"` for video files; omit for images |

`lat` and `lng` are written together — an entry either has both or neither. The `metadata` field is present on image entries (it carries the EXIF capture details) and is preserved as-is by the sync script.

### Encoding

Always save `photos.json` with **UTF-8 encoding** so special characters (accents, umlauts, etc.) display correctly. In VS Code, check the encoding indicator in the bottom-right corner.

---

## `admin-page.html` — The Content Manager

The Content Manager (`admin-page.html`) is a local tool for editing photo titles, descriptions, and GPS locations. It provides a visual interface to browse categories, preview images, and update the `photos.json` file that powers the website.

> **Important:** This tool is for local use only. It is not deployed on the web and should not be uploaded to GitHub Pages. It manages the gallery content in `photos.json` only — **not** the hard-coded landing image or the hard-coded Adventures/Life background videos.

### Prerequisites

- **VS Code** with the **Live Server** extension installed
- Your website files in the same folder:
  ```
  svensl.github.io/
    index.html        ← Website
    admin-page.html   ← Content Manager
    photos.json       ← Photo data (titles, descriptions)
    images/           ← Photo files
    videos/           ← Video files
  ```

### Getting Started

1. Open the `svensl.github.io` folder in VS Code
2. Right-click on `admin-page.html`
3. Select **"Open with Live Server"**
4. The Content Manager opens in your browser

> **Note:** You must use Live Server. Opening the file directly by double-clicking will not work due to browser security restrictions.

### Interface Layout

```
┌──────────────────────────────────────────────────────────────┐
│  Top Bar                              [+ Add] [Export JSON]  │
├────────────┬──────────────┬──────────────────────────────────┤
│            │ Stats: Photos│                                  │
│  Sidebar   │ Videos | GPS │  Editor Panel (~2/3 of screen)   │
│            ├──────────────┤                                  │
│  Category  │              │  Title field                     │
│  List      │  Thumbnail   │  Description field               │
│            │  Grid        │  Map (click to set location)     │
│            │ (selected    │   • Street / Satellite toggle    │
│            │  tile is     │                                  │
│            │  highlighted)│  [Prev] [Next]                   │
└────────────┴──────────────┴──────────────────────────────────┘
```

- **Sidebar (left):** Lists all photo categories with item counts
- **Thumbnail Grid (center):** Shows all photos in the selected category. The currently selected photo is highlighted with a red ring and serves as the live preview.
- **Editor Panel (right):** Appears when a photo is selected and takes up roughly two-thirds of the screen. Shows the editable title and description fields and an interactive map.

### Workflow

**Step 1 — Select a Category.** Click any category in the left sidebar. Categories are grouped: Adventures (Night, Wanderlust, Window Seat), Landscapes, Life (Fauna, Flora, People), Orange, Water.

**Step 2 — Select a Photo.** Click any thumbnail to open the editor panel. The selected thumbnail is highlighted with a red ring and acts as your live preview. The editor shows the file path, an editable Title field, an editable Description text area, a read-only **Date Taken** field (parsed from the entry's `metadata` string in `photos.json`), an interactive map, and a video toggle.

**Step 3 — Edit Title, Description, and Location.**
- Type into the **Title** and **Description** fields.
- Press **Enter** for line breaks in the description (these display as paragraphs on the website).
- Set the **location** by clicking the map (optional). This stores `lat`/`lng`.
- Changes are saved in memory immediately as you type.

*Setting a location on the map:*
- **Click anywhere on the map** to drop a marker; coordinates are stored and shown beneath the map.
- **Drag the marker** to fine-tune; coordinates update on drop.
- Use the **Street / Satellite (Hybrid)** toggle (top-right of the map) to switch base maps; Satellite (Hybrid) — Esri imagery with labels and boundaries — is the default.
- Click **Clear location** to remove the coordinates.
- If a photo already has coordinates, the map opens centered on that location.

**Step 4 — Navigate Between Photos.** Use the **Previous/Next** buttons, the **← →** arrow keys (only when not typing in a text field), or click any other thumbnail.

**Step 5 — Export the Updated JSON.**
1. Click the green **"Export photos.json"** button in the top bar.
2. Your browser downloads a new `photos.json` (usually to Downloads).
3. **Move** the file into your project folder (`svensl.github.io/`).
4. **Replace** the existing `photos.json` when prompted.

### Features

**Visual Indicators**
- **Green bar** on a thumbnail label: this photo has a real description (not the default placeholder)
- **Green "GPS" badge:** this entry has GPS coordinates
- **Red "VIDEO" badge:** this entry is a video file
- **Index number** on each thumbnail: its display order on the website

**Stats Bar** — When a category is selected, shows Photos, Videos, With descriptions, and With GPS counts.

**Adding a New Entry**
1. Select the target category in the sidebar.
2. Click **"+ Add Entry"** in the top bar.
3. Enter the file path when prompted (e.g., `images/Adventures/Night/newphoto.jpg`).
4. The new entry appears at the end of the grid; click it to edit.
5. Export when finished.
> Video files (.mp4, .mov, .webm) are automatically detected and marked as videos.

**Deleting an Entry**
1. Select the photo to remove.
2. Click **"Delete this entry"** in the editor panel.
3. Confirm.
> This only removes the entry from `photos.json`; the actual image file is not deleted from your computer.

### Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `←` | Previous photo (when not typing) |
| `→` | Next photo (when not typing) |
| `Escape` | Close editor panel |
| `Ctrl + E` | Export photos.json |

### Important Notes

- **Always export before closing.** The Content Manager works entirely in memory. Closing the tab without exporting loses all changes (it warns you on exit if there are unsaved changes).
- **Status indicator** in the top bar shows the current state: "Ready", "Loaded photos.json", "Unsaved changes", or "Exported photos.json".
- **File encoding** must be UTF-8 (verify in VS Code's bottom-right corner).
- **Line breaks** entered with Enter appear as `\n` in the JSON; the website's `white-space: pre-wrap` CSS renders them as paragraphs.

**GPS coordinates and the map.** Coordinates are stored in WGS84 Decimal Degrees. The map offers two base layers via the top-right toggle: **Street** (OpenStreetMap tiles) and **Satellite (Hybrid)**, which is the default. The Hybrid layer stacks Esri World Imagery (aerial/satellite) with a transparent Esri reference overlay that adds country/administrative boundaries, place names, and major points of interest on top of the imagery. Both layers allow **overzoom to level 22**: real tiles exist up to native zoom 19 (`maxNativeZoom`), and the map upscales beyond that so you can keep zooming in to place a marker precisely. The **map requires an internet connection** — tiles load from online services, so the map area appears blank offline (editing titles/descriptions still works offline). The Esri layers are free public tile services used without an API key, which is fine for this local single-user tool.

Quick reference for verifying common locations:

| Location | Latitude | Longitude |
|----------|----------|-----------|
| Geneva | 46.2044 | 6.1432 |
| Danakil, Ethiopia | 14.2417 | 40.3000 |
| Marseilles | 43.2965 | 5.3698 |
| Port-au-Prince, Haiti | 18.5944 | −72.3074 |

### Troubleshooting (Content Manager)

**Photos not loading** — Ensure `admin-page.html` is in the same folder as `photos.json` and `images/`, and that you are using Live Server (not opening the file directly).

**Export not working** — Check that your browser allows downloads; look in your Downloads folder.

**Special characters garbled** — Open `photos.json` in VS Code, confirm the encoding is **UTF-8** (bottom-right). If not: click the encoding label → "Reopen with Encoding" → **UTF-8**.

**New photos not showing** — If you added new image files to your folders, add them to `photos.json` with **"+ Add Entry"** (or run the sync script).

---

## `sync-script.py` — The Photo Sync Tool

`sync-script.py` is a Python script that automatically scans your image folders and updates `photos.json` to match. It detects new images, removes entries for deleted files, and preserves all existing titles, descriptions, and GPS coordinates. For new images it also reads **EXIF data** straight from the photo files — extracting GPS coordinates and building a camera `metadata` string (date taken, camera, f-stop, exposure, ISO, focal length).

> **Important:** This script is for local use only. It should not be uploaded to GitHub Pages.

### Prerequisites

- **Python 3.6+** installed. Check with `python --version`. If not installed, download from [python.org/downloads](https://www.python.org/downloads/) and check **"Add Python to PATH"** during installation.
- **Pillow** is required for EXIF extraction (GPS coordinates and camera metadata):
  ```bash
  pip install Pillow
  ```
  The script still runs without Pillow, but EXIF extraction is **disabled** — it will print "EXIF extraction: Disabled" and add new entries without `metadata`, `lat`, or `lng`. Install Pillow to get the full benefit.

### File Location

Place `sync-script.py` in your project root alongside `photos.json`:

```
svensl.github.io/
  index.html
  admin-page.html
  photos.json        ← Read and updated by the script
  sync-script.py     ← This script
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

### Usage

**Open the terminal.** In VS Code, press `Ctrl + ~`. Make sure you are in your project folder, e.g.:

```bash
cd "C:\Users\schmi\OneDrive\Pictures\Website\Website 2025\svensl.github.io"
```

**Preview changes (dry run)** — Preview without modifying any files:

```bash
python sync-script.py --dry
```

Example output (the header reports whether EXIF extraction is enabled, and each changed category can show `GPS:` and `EXIF:` counts):

```
======================================================================
  2SL Photography - Photo Sync Tool
======================================================================

  MODE: Dry Run (preview only, no files will be changed)
  EXIF extraction: Enabled (Pillow detected)

  [~] adventures-night              Total:  45  (+2 new, 43 kept, -0 removed)  GPS:40 EXIF:43
  [=] adventures-wanderlust         Total:  30  (+0 new, 30 kept, -0 removed)  GPS:28 EXIF:30
  [~] landscapes                    Total:  62  (+3 new, 59 kept, -1 removed)  GPS:55 EXIF:60
  ...

----------------------------------------------------------------------
  SUMMARY
    New files found:       +5
    Existing kept:          280
    Removed (missing):     -1
    Total entries:          284
    With GPS coordinates:   265
    With EXIF metadata:     280
----------------------------------------------------------------------

  Dry run complete. Run without --dry to apply changes.
```

> If Pillow is not installed, the header instead reads "EXIF extraction: Disabled (install: pip install Pillow)" and no GPS/EXIF data is added to new entries.

**Apply changes** — If the preview looks correct:

```bash
python sync-script.py
```

The script will: (1) create a timestamped backup of `photos.json`, (2) add entries for new image/video files — reading EXIF (GPS + `metadata`) for new images when Pillow is available, (3) remove entries for files no longer on disk, (4) preserve all existing titles, descriptions, GPS, and metadata, and (5) write the updated `photos.json` (UTF-8, `ensure_ascii=False`, 4-space indent).

**Re-read EXIF for existing entries** — Use the `--exif` flag to fill in metadata/GPS for entries that are missing it (for example, photos added before Pillow was installed):

```bash
python sync-script.py --exif
```

> `--exif` only **fills gaps** — it reads EXIF for image entries that have no `metadata` yet, and only adds `lat`/`lng` when they are not already set. It does not overwrite metadata or coordinates you already have (including locations you placed by hand in the Content Manager). The flags can be combined, e.g. `python sync-script.py --exif --dry` to preview an EXIF backfill.

### Output Symbols

| Symbol | Meaning |
|--------|---------|
| `[=]` | Category unchanged, no new or removed files |
| `[~]` | Category changed, files added or removed |
| `GPS:n` | Number of entries in that category with GPS coordinates |
| `EXIF:n` | Number of entries in that category with an EXIF metadata string |
| `[FOLDER NOT FOUND]` | The folder path does not exist on disk |

### What the Script Does

| Scenario | Action |
|----------|--------|
| New image file found | Added to JSON with filename as title and "Description" placeholder; EXIF read for GPS + `metadata` (if Pillow installed) |
| New video file found (.mp4, .webm, .mov) | Added to JSON with `"type": "video"` (no EXIF read) |
| Image already in JSON | Kept as-is; title, description, GPS, and metadata preserved (unless `--exif` fills a missing field) |
| Image in JSON but file deleted | Entry removed from JSON |
| Video referenced in `videos/` | Preserved if the file still exists; removed if it doesn't |

> The script preserves all existing fields (`title`, `description`, `lat`, `lng`, `metadata`, `type`). No manually entered data is lost when syncing. It never modifies, moves, or deletes any image or video file — it only reads folder contents (and image EXIF) and updates `photos.json`. Files are sorted alphabetically within each category.

### EXIF Extraction Details

When Pillow is installed, the script reads each new image's EXIF tags and assembles the fields it finds into a single `metadata` string of the form `Date taken: … • Camera: … • F-stop: … • Exposure time: … • ISO Speed: … • Focal length: …` (only the parts that are present are included). It also reads GPS tags, converts them from degrees/minutes/seconds to decimal degrees, validates the ranges, and stores them as `lat`/`lng` rounded to six decimal places. Camera make and model are combined intelligently to avoid repeating the make. Any image without EXIF (or with unreadable EXIF) is simply added without those fields.

### Backups

Each non-dry run creates a backup, e.g. `photos_backup_20260617_143022.json` (date and time in the name). Old backups can be deleted when no longer needed.

### Configuration

The category-to-folder mapping is defined at the top of the script. Edit `CATEGORY_FOLDERS` if you add, rename, or reorganize categories:

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

**Adding a new category:**
1. Create the folder in `images/` (e.g., `images/NewCategory`).
2. Add the mapping: `"new-category": "images/NewCategory",`.
3. Add the corresponding HTML section in `index.html`.
4. Run `python sync-script.py`.

**Supported file types** (also defined at the top of the script):

```python
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".tiff"}
VIDEO_EXTENSIONS = {".mp4", ".webm", ".mov"}
```

### Command Reference

| Command | Description |
|---------|-------------|
| `python sync-script.py --dry` | Preview changes without modifying files |
| `python sync-script.py` | Scan folders and update photos.json |
| `python sync-script.py --exif` | Backfill EXIF (GPS + metadata) for entries that are missing it |

### Troubleshooting (Sync Tool)

**"python is not recognized"** — Try `python3 sync-script.py --dry` or `py sync-script.py --dry`. If none work, Python is not installed or not in PATH; reinstall and check "Add Python to PATH", then restart VS Code.

**"No such file or directory"** — Make sure the terminal is in the correct folder. Run `dir` (Windows) or `ls` (Mac/Linux) to confirm you can see `sync-script.py`.

**"[FOLDER NOT FOUND]"** — A path in `CATEGORY_FOLDERS` doesn't match your folder structure. Check for typos, case sensitivity (e.g. `Night` vs `night`), and missing folders.

**New photos not appearing on the website** — After syncing: open `admin-page.html` to verify entries, check that `src` paths match real files, ensure the updated `photos.json` was saved/exported, and clear the browser cache (`Ctrl + Shift + R`).

**Encoding issues** — The script writes JSON with `ensure_ascii=False` and UTF-8. If characters look garbled, confirm UTF-8 in VS Code (bottom-right) and resave with UTF-8 if needed.

---

## `compress_mp4.py` — The Video Compression Tool

`compress_mp4.py` compresses MP4 files to a resolution/bitrate suitable for web viewing on a computer screen. It defaults to 720p (1280×720) with H.264 video and AAC audio — a widely supported balance of quality and file size. Use it to prepare videos (including the hard-coded Adventures/Life background videos) before adding them to the `videos/` folder.

> **Important:** This script is a local helper and is not deployed to the web.

### Requirements

**ffmpeg** must be installed and on your PATH:
- Linux: `sudo apt install ffmpeg`
- macOS: `brew install ffmpeg`
- Windows: download from [ffmpeg.org](https://ffmpeg.org) and add to PATH

The script exits early with a clear message if ffmpeg is not found.

### How It Works / Assumptions

- **720p** is treated as "good enough for a computer screen." 1080p is available for higher fidelity; 480p for smaller files.
- Videos already smaller than the target height are **not upscaled** (that only wastes space) — they are re-encoded at the target quality instead.
- **CRF (Constant Rate Factor)** is used rather than a fixed bitrate, so quality is consistent and file size adapts to content. Default CRF is **23** (lower = higher quality/larger file; 20–24 is a good web range).
- Default x264 **preset** is **medium** (trades encode speed for size).
- Audio is encoded as 128 kbps AAC, and `+faststart` is set to enable progressive download/streaming.
- Output files are named `<originalname>_<resolution>.mp4` and placed in a `compressed` folder beside the source by default.

### Usage

Run interactively (it will prompt for a path) or pass a file/folder directly:

```bash
python compress_mp4.py                       # prompts for a path
python compress_mp4.py myvideo.mp4           # compress one file
python compress_mp4.py ./videos              # compress all .mp4 in a folder
```

### Options

| Option | Description |
|--------|-------------|
| `location` | Path to an MP4 file or a folder of MP4 files (prompted if omitted) |
| `-r`, `--resolution` | Target resolution: `480p`, `720p`, or `1080p` (default `720p`) |
| `--crf` | Quality; lower = better/bigger (default `23`) |
| `--preset` | x264 speed/size preset (default `medium`) |
| `--recursive` | Search subfolders when the location is a directory |
| `-o`, `--outdir` | Output folder (default: a `compressed` folder beside the source) |

Examples:

```bash
python compress_mp4.py ./clips -r 1080p --crf 20        # higher quality 1080p
python compress_mp4.py ./clips --recursive -o ./out     # recurse, custom output
```

The script prints a before/after size and percentage saved for each file, and a final summary of how many files were compressed.

---

## Initial Web Setup — GitHub Pages & Namecheap Domain

This section covers first-time setup: creating the GitHub repository, publishing with GitHub Pages, connecting VS Code, and pointing the Namecheap domain (`2slphotography.com`) at GitHub. The live site is `svensl/svensl.github.io`.

### 1. Create a GitHub Account and Repository

1. Sign up at [github.com](https://github.com) if you don't have an account.
2. Click **"+" → New repository**.
3. Name it exactly **`your-username.github.io`** (for this project: `svensl.github.io`). The repo name must match your username for a user GitHub Pages site.
4. Make it **Public** (required for free GitHub Pages), check **"Add a README file"**, and click **Create repository**.

> **Why public is safe:** Anyone can *view* or *clone* a public repo, but only you (and collaborators you explicitly add) can push changes to it. Others can only propose changes via Pull Requests, which you must approve. A public repo is the standard, free choice for a portfolio.

### 2. Upload Your Files

**Option A — Web interface (easiest):** In the repo, **Add file → Upload files**, drag in `index.html` (named exactly that, lowercase) and your `images/` folder, then **Commit changes**.

**Option B — VS Code (recommended for ongoing updates):** see the next section.

### 3. Use VS Code with Git (Recommended)

VS Code is a strong choice for this workflow — edit HTML, preview with Live Server, and push to GitHub all in one place.

1. **Install Git** ([git-scm.com](https://git-scm.com)) and restart VS Code.
2. **Configure Git (first time only)** in the VS Code terminal (`Ctrl + ~`):
   ```bash
   git config --global user.name "Your Name"
   git config --global user.email "your-email@example.com"
   ```
3. **Clone the repository:** `Ctrl + Shift + P` → **Git: Clone** → paste `https://github.com/svensl/svensl.github.io.git` → choose a folder → Open.
4. **Add your files** into the cloned folder. Changes show in the Source Control panel.
5. **Commit and push:** stage changes, type a commit message, click **✓ Commit**, then **Sync Changes** (or the cloud icon).

**Useful extensions:** Live Server (local preview), GitLens (enhanced Git), HTML CSS Support (completion).

**Common Git commands:**
```bash
git status              # check status
git add .               # stage all changes
git commit -m "Message" # commit
git push                # push to GitHub
git pull                # pull latest
```

### 4. Set Up a Personal Access Token (PAT) for VS Code

When pushing for the first time, VS Code usually opens a browser to authenticate — sign in and authorize, and credentials are saved. If you need a PAT manually:

1. GitHub → profile picture → **Settings** → **Developer settings** → **Personal access tokens → Tokens (classic)** → **Generate new token (classic)**.
2. Set a **Note** (e.g., "VS Code Access"), an **Expiration** (90 days or 1 year), and select scopes: **`repo`** (all sub-options), and **`workflow`** if you may use GitHub Actions.
3. **Generate token** and copy it immediately (format `ghp_...`) — you won't see it again. Store it in a password manager.

When Git asks for a username/password, the **password is your PAT** (not your GitHub account password). To have Git remember it:
```bash
# Windows (usually pre-installed with Git)
git config --global credential.helper manager
# Mac
git config --global credential.helper osxkeychain
# Linux
git config --global credential.helper store
```

**Security:** never share or commit your PAT, set an expiration, and regenerate when it expires.

If VS Code keeps asking for credentials, confirm the remote uses HTTPS:
```bash
git remote -v
# If it shows SSH, switch to HTTPS:
git remote set-url origin https://github.com/svensl/svensl.github.io.git
```

### 5. Enable GitHub Pages

1. Repo → **Settings** → **Pages** (left sidebar).
2. Under **Source**, select the **`main`** branch and **Save**.
3. The site goes live at `https://svensl.github.io` (the first deploy can take 5–10 minutes).

### 6. Required File Structure

```
svensl.github.io/
  index.html          ← Must be in the root
  CNAME               ← Contains: 2slphotography.com
  photos.json
  images/
    1C8A0980.jpg
    Adventures/
    Life/
    Water/
    ...
  videos/
```

**Common pitfalls:**
- The file must be named exactly `index.html` (lowercase).
- Image paths are **case-sensitive** on GitHub (unlike Windows) — `Adventures`, not `adventures`.

### 7. Connect the Namecheap Domain

**Part A — GitHub side:**
1. Repo → **Settings** → **Pages** → **Custom domain**: enter `2slphotography.com` (without www) → **Save**.
2. Check **☑ Enforce HTTPS** (may be grayed out until DNS propagates and the certificate is issued).
3. Verify a **`CNAME`** file exists in the repo root containing only:
   ```
   2slphotography.com
   ```
   If missing, create it in VS Code and push:
   ```bash
   git add CNAME
   git commit -m "Add CNAME for custom domain"
   git push
   ```

**Part B — Namecheap DNS:** Domain List → **Manage** `2slphotography.com` → **Advanced DNS**. Delete any existing parking A records and URL redirect records, then set **exactly**:

```
Type          Host    Value                  TTL
─────────────────────────────────────────────────────
A Record      @       185.199.108.153        Automatic
A Record      @       185.199.109.153        Automatic
A Record      @       185.199.110.153        Automatic
A Record      @       185.199.111.153        Automatic
CNAME Record  www     svensl.github.io.      Automatic
```

> **Critical details:** Host for the A records must be **`@`** (not blank, not `2slphotography.com`). The CNAME value must end with a **period**: `svensl.github.io.`. Make sure Namecheap **Nameservers** are set to "Namecheap BasicDNS" (not custom nameservers pointing elsewhere).

**Part C — Wait for propagation:** DNS changes take time — minimum ~30 minutes, typically 2–4 hours, up to 24–48 hours.

**Part D — Verify:**
1. At [whatsmydns.net](https://www.whatsmydns.net), enter `2slphotography.com`, select **A**. You should see GitHub IPs (`185.199.108.153`, etc.). If you see `185.230.63.x`, those are Namecheap parking IPs — DNS isn't configured/propagated yet.
2. From a terminal:
   ```bash
   nslookup 2slphotography.com        # should show GitHub IPs
   nslookup www.2slphotography.com    # should resolve via svensl.github.io
   ```
3. Once DNS shows GitHub IPs, re-check **Settings → Pages**; the "improperly configured" error should clear. Then enable **Enforce HTTPS**.

### Troubleshooting (Setup & Domain)

**"DNS check unsuccessful / NotServedByPagesError"** — DNS hasn't propagated or is misconfigured. Wait longer; confirm all four A records use the correct GitHub IPs with host `@`; confirm the `CNAME` file exists in the repo.

**Website shows 404** — `index.html` must be in the repo root (not a subfolder), and GitHub Pages must be enabled.

**HTTPS not working** — Wait up to 24 hours after DNS propagates; GitHub issues the SSL certificate automatically and it cannot be forced.

**www not working** — The CNAME record must point to `svensl.github.io.` (with the trailing period); allow time for propagation.

**Resetting the domain in GitHub** — Settings → Pages → remove the custom domain → Save → wait a minute → re-add `2slphotography.com` → Save → wait for the DNS check.

---

## Everyday Workflows

### Updating Photo Content (most common)

```
1. Add, remove, or reorganize photos in your image folders.

2. Preview the sync:
   python sync-script.py --dry

3. Apply the sync (with Pillow installed, new photos get GPS + metadata
   read from their EXIF automatically):
   python sync-script.py

4. Open admin-page.html with Live Server:
   → Edit titles and descriptions for new entries
   → Adjust or add GPS locations on the map where EXIF had none
   → Click "Export photos.json"
   → Replace the file in your project folder

5. Test locally:
   → Open index.html with Live Server and verify

6. Publish:
   git add .
   git commit -m "Updated photos"
   git push
```

Changes appear on the live site within a few minutes.

### Publishing Any Change

```bash
git add index.html photos.json images videos
git commit -m "Update website"
git push
```

### Changing the Hard-Coded Landing Image or Category Videos

1. Add the new image to `images/` or the new (compressed) video to `videos/` — use `compress_mp4.py` first for videos.
2. Edit the relevant line in `index.html` (landing image around line 24; Adventures video around line 656; Life video around line 671).
3. Commit and push.

These are **not** managed by `admin-page.html` or `photos.json`, so they can only be changed by editing `index.html` directly.
