# 2SL Photography - Content Manager

## Overview

The Content Manager (`admin.html`) is a local tool for editing photo titles and descriptions on the 2SL Photography website. It provides a visual interface to browse your photo categories, preview images, and update the `photos.json` file that powers the website.

> **Important:** This tool is for local use only. It is not deployed on the web and should not be uploaded to GitHub Pages.

---

## Prerequisites

- **VS Code** with the **Live Server** extension installed
- Your website files in the same folder:
  ```
  svensl.github.io/
    index.html        ← Website
    admin.html        ← Content Manager
    photos.json       ← Photo data (titles, descriptions)
    images/           ← Photo files
    videos/           ← Video files
  ```

---

## Getting Started

1. Open the `svensl.github.io` folder in VS Code
2. Right-click on `admin.html`
3. Select **"Open with Live Server"**
4. The Content Manager opens in your browser

> **Note:** You must use Live Server. Opening `admin.html` directly by double-clicking will not work due to browser security restrictions.

---

## Interface Layout

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
- **Thumbnail Grid (center):** Shows all photos in the selected category. The currently selected photo is highlighted with a red ring and serves as the live preview (the editor panel no longer shows a separate preview image).
- **Editor Panel (right):** Appears when a photo is selected and takes up roughly two-thirds of the screen. Shows the editable title and description fields and an interactive map for setting the location.

---

## Workflow

### Step 1: Select a Category

Click any category in the left sidebar. Categories are grouped by section:

- **Adventures:** Night, Wanderlust, Window Seat
- **Landscapes**
- **Life:** Fauna, Flora, People
- **Orange**
- **Water**

The thumbnail grid will populate with all images in that category.

### Step 2: Select a Photo

Click any thumbnail to open the editor panel on the right. The selected thumbnail is **highlighted with a red ring** in the center grid and acts as your live preview. The editor panel shows:

- The **file path**
- An editable **Title** field
- An editable **Description** text area
- An interactive **map** for setting the location
- A **video toggle** checkbox

### Step 3: Edit Title, Description, and Location

- Click into the **Title** field and type your title
- Click into the **Description** field and type your description
- Press **Enter** for line breaks within the description (these will display as paragraphs on the website)
- Set the **location** by clicking on the map (see below). This stores `lat` and `lng` in `photos.json`. Location is optional.
- Changes are saved in memory immediately as you type

**Setting a location on the map:**

- **Click anywhere on the map** to drop a marker. The latitude and longitude are stored automatically and shown beneath the map.
- **Drag the marker** to fine-tune the position; the coordinates update as you drop it.
- Use the **Street / Satellite** toggle in the top-right corner of the map to switch base maps. Satellite imagery is useful for placing a marker on a precise natural feature.
- Click **Clear location** to remove the coordinates from the entry.
- When a photo already has coordinates, the map opens centered on that location with the marker in place.

### Step 4: Navigate Between Photos

You can move between photos in three ways:

- Click the **Previous** / **Next** buttons at the bottom of the editor
- Use the **← →** arrow keys (only when not typing in a text field)
- Click any other **thumbnail** in the grid

### Step 5: Export the Updated JSON

1. Click the green **"Export photos.json"** button in the top bar
2. Your browser will download a new `photos.json` file (typically to your Downloads folder)
3. **Move** the downloaded file into your project folder (`svensl.github.io/`)
4. **Replace** the existing `photos.json` when prompted
5. Your website now reflects the updated content

---

## Features

### Visual Indicators

- **Green bar** on a thumbnail label: This photo has a description (other than the default "Description" placeholder)
- **Green "GPS" badge** on a thumbnail: This entry has GPS coordinates
- **Red "VIDEO" badge** on a thumbnail: This entry is a video file
- **Index number** on each thumbnail: Shows the display order on the website

### Stats Bar

When a category is selected, the stats bar shows:

- **Photos:** Number of image files
- **Videos:** Number of video files
- **With descriptions:** Number of entries that have been given a real description
- **With GPS:** Number of entries that have GPS coordinates

### Adding a New Entry

1. Select the target category in the sidebar
2. Click **"+ Add Entry"** in the top bar
3. Enter the file path when prompted (e.g., `images/Adventures/Night/newphoto.jpg`)
4. The new entry appears at the end of the grid
5. Click it to edit the title and description
6. Export when finished

> Video files (.mp4, .mov, .webm) are automatically detected and marked as videos.

### Deleting an Entry

1. Select the photo you want to remove
2. In the editor panel, click **"Delete this entry"**
3. Confirm the deletion

> This only removes the entry from `photos.json`. The actual image file is not deleted from your computer.

---

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `←` | Previous photo (when not typing) |
| `→` | Next photo (when not typing) |
| `Escape` | Close editor panel |
| `Ctrl + E` | Export photos.json |

---

## Important Notes

### Always Export Before Closing

The Content Manager works entirely in memory. If you close the browser tab without exporting, all your changes will be lost. The tool will show a warning if you try to leave with unsaved changes.

### The Status Indicator

The status text in the top bar tells you the current state:

- **"Ready"** — Just loaded, no changes made
- **"Loaded photos.json"** — File loaded successfully
- **"Unsaved changes"** — You have edits that haven't been exported yet
- **"Exported photos.json"** — Export completed successfully

### File Encoding

Make sure your `photos.json` is saved with **UTF-8 encoding**. This is important for special characters (accents, umlauts, etc.). You can verify this in VS Code by checking the encoding indicator in the bottom-right corner of the editor.

### Line Breaks in Descriptions

When you press Enter in the description field, it creates a real line break. In the exported JSON, these appear as `\n` characters. The website's CSS (`white-space: pre-wrap`) ensures these display as proper paragraph breaks.

### GPS Coordinates and the Map

Coordinates are set by clicking the interactive map in the editor panel. They are stored in WGS84 Decimal Degrees format. Each entry in `photos.json` can optionally include `lat` and `lng` fields:

```json
{
    "src": "images/Orange/1C8A0438.jpg",
    "title": "Marseilles",
    "description": "Planete Mars",
    "lat": 43.2965,
    "lng": 5.3698
}
```

Both fields are written together: clicking the map (or dragging the marker) stores `lat` and `lng`, and **Clear location** removes both. An entry either has both fields or neither.

**Base maps:** The map offers two base layers, switchable from the toggle in the top-right corner:

- **Street** — OpenStreetMap tiles
- **Satellite** — Esri World Imagery (aerial/satellite)

**Map requires an internet connection.** The map tiles are loaded from online services (OpenStreetMap and Esri), so the map area will appear blank if you are offline. Editing titles and descriptions still works offline; only the map needs connectivity. The Esri satellite layer is a free public tile service used here without an API key, which is fine for this local single-user tool.

**Quick reference for common locations** (in case you want to verify a marker landed in the right place):

| Location | Latitude | Longitude |
|----------|----------|-----------|
| Geneva | 46.2044 | 6.1432 |
| Danakil, Ethiopia | 14.2417 | 40.3000 |
| Marseilles | 43.2965 | 5.3698 |
| Port-au-Prince, Haiti | 18.5944 | -72.3074 |

---

## Updating the Website After Editing

After exporting a new `photos.json`:

1. Replace the old `photos.json` in your project folder
2. **To test locally:** Open `index.html` with Live Server and verify your changes
3. **To publish online:**
   ```bash
   git add photos.json
   git commit -m "Updated photo descriptions"
   git push
   ```
4. Changes will be live on your website within a few minutes

---

## Troubleshooting

### Photos not loading
- Make sure `admin.html` is in the same folder as `photos.json` and `images/`
- Make sure you are using Live Server (not opening the file directly)

### Export not working
- Check that your browser allows downloads
- Look in your Downloads folder for the file

### Special characters appearing as garbled text
- Open `photos.json` in VS Code
- Check the encoding in the bottom-right corner — it should say **UTF-8**
- If not, click on the encoding label → "Reopen with Encoding" → select **UTF-8**

### New photos not showing
- If you added new image files to your folders, you need to add them to `photos.json` using the **"+ Add Entry"** button in the Content Manager

---

## File Reference

| File | Purpose | Deploy to web? |
|------|---------|---------------|
| `index.html` | Main website | Yes |
| `admin.html` | Content Manager (this tool) | **No** |
| `photos.json` | Photo data (titles, descriptions) | Yes |
| `images/` | Photo files | Yes |
| `videos/` | Video files | Yes |
| `CNAME` | Custom domain config | Yes |
| `README.md` | This documentation | Optional |