# 2SL Photography - Website

## Overview

`index.html` is the public photography portfolio website for 2SL Photography. It is a single self-contained HTML file (HTML, CSS, and JavaScript all in one) that displays photos and videos organized into categories, with a full-screen landing image, category navigation, a mosaic gallery, and a lightbox viewer.

The site reads all of its content from `photos.json`, so you never need to edit `index.html` to add, remove, or re-caption photos. Content is managed separately (see **Related Files** below).

> This is the file that **is** deployed to the web via GitHub Pages.

---

## How It Works

When the page loads, a script fetches `photos.json` and builds each category's gallery from the entries it finds. Each entry provides a file path (`src`), a `title`, a `description`, and optionally a location (`lat`/`lng`) and a `type` of `video`.

```
index.html  ──reads──>  photos.json  ──points to──>  images/ and videos/
```

Because everything is driven by `photos.json`, the website's appearance updates automatically whenever that file changes.

---

## Page Structure

### Landing Page

A full-screen background image (currently `images/1C8A0980.jpg`) shown when the site first loads.

### Navigation Bar

A fixed bar across the top with the site title and tabs:

- **Adventures** — opens a category landing page with a background video and three sub-galleries: Night, Wanderlust, Window Seat
- **Landscapes** — opens the Landscapes gallery directly
- **Life** — opens a category landing page with a background video and three sub-galleries: Fauna, Flora, People
- **Orange** — opens the Orange gallery directly
- **Water** — opens the Water gallery directly
- **About** — opens the About page

A **Home** button appears (bottom-right on mobile, top-right on desktop) once you have navigated away from the landing page.

### Category Landing Pages (Adventures & Life)

These two sections show a looping background video with buttons for their sub-galleries. The videos are:

- Adventures: `videos/Khartoum_TukTuk_720p.mp4`
- Life: `videos/20190802_215709_720p.mp4`

### Galleries

Each gallery displays its photos as a responsive **mosaic** of square tiles. Hovering a tile reveals its title; hovering a video tile plays it muted. Clicking any tile opens the lightbox.

### Lightbox

A full-screen overlay showing the selected image or video at large size, alongside its title and description. Within the lightbox you can:

- Move between items with the **on-screen arrows** or the **left/right arrow keys**
- Close with the **×** button or the **Escape** key

Descriptions preserve line breaks (the CSS uses `white-space: pre-wrap`), so multi-paragraph captions written in the Content Manager display correctly.

### About Page

A simple text page with a short biography and a contact email.

---

## Categories

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

---

## Editing Content

You do **not** edit `index.html` to change photos or captions. Instead:

1. **Add or remove photo files**, then run the sync script to update `photos.json` (see `readme-sync.md`).
2. **Edit titles, descriptions, and locations** using the Content Manager (see `admin-page-readme.md`).
3. **Publish** the updated `photos.json` (and any new image/video files) to GitHub Pages.

The only reasons to edit `index.html` directly are structural changes: adding a new category section, changing the landing image, swapping the category landing videos, editing the About text, or adjusting the styling.

---

## Image Protection

The site includes basic deterrent measures: right-clicking on images and dragging images are disabled via JavaScript. This discourages casual copying only. Anyone can still view images through browser developer tools or by taking a screenshot, so do not treat this as real protection for high-value images.

---

## Responsive Design

The layout adapts to screen size through CSS media queries:

- **Desktop:** wide mosaic, lightbox image and caption side by side
- **Tablet (≤768px):** stacked navigation, smaller mosaic tiles, lightbox image above caption
- **Phone (≤480px):** smallest mosaic tiles and reduced font sizes

---

## Deployment

`index.html`, `photos.json`, the `images/` folder, the `videos/` folder, and the `CNAME` file are the parts of the project that go live on the web. To publish changes:

```bash
git add index.html photos.json images videos
git commit -m "Update website"
git push
```

Changes appear on the live site within a few minutes. See `InitialWebSetup.md` for first-time GitHub Pages and custom-domain (Namecheap) setup.

---

## Related Files

| File | Purpose | Deploy to web? |
|------|---------|----------------|
| `index.html` | The public website (this document) | **Yes** |
| `photos.json` | Photo data: paths, titles, descriptions, locations | **Yes** |
| `images/` | Photo files | **Yes** |
| `videos/` | Video files | **Yes** |
| `CNAME` | Custom domain configuration | **Yes** |
| `admin-page.html` | Content Manager (local editing tool) — see `admin-page-readme.md` | **No** |
| `sync_photos.py` | Folder-to-JSON sync script — see `readme-sync.md` | **No** |

---

## Troubleshooting

### A photo or video does not appear

- Confirm the file's `src` path in `photos.json` exactly matches the real file location. Paths are **case-sensitive** on GitHub Pages (unlike Windows).
- Confirm the file was actually committed and pushed.

### A whole gallery is empty

- Check that the category key in `photos.json` matches a grid `id` in `index.html`.

### Videos do not play

- Confirm the file is `.mp4` and that the entry has `"type": "video"` in `photos.json`.

### Changes do not show up

- Clear your browser cache (`Ctrl + Shift + R`) and reload. GitHub Pages can also take a few minutes to update.
