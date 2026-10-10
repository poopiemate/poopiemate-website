# PoopieMate Website

Static GitHub Pages website for 응가메이트.

Published URL:

https://viva-jinyi.github.io/poopiemate-website/

## Google Search Console verification

Place the HTML verification file from Google Search Console in this repository root, next to `index.html`.

Example:

```text
google1234567890abcdef.html
```

After committing and pushing it to `main`, it will be available at:

```text
https://viva-jinyi.github.io/poopiemate-website/google1234567890abcdef.html
```

## Build

Pages are generated — edit `src/`, not the HTML.

```bash
python3 src/prepare_assets.py   # wordmarks, mascot, 3D emoji, photos, reels, YouTube thumbnails, favicons (from the app repo + ~/Desktop/응가메이트)
python3 src/og.py               # share images 1200×630 → assets/og/
python3 src/build.py            # every page (ko at /, en at /en/) + sitemap.xml
```

- `src/build.py` — copy, layout and SEO for home, how-it-works, stories, notices, download, 404; the 9 search guides and the interview form are wrapped from `src/legacy/`.
- `assets/css/site.css` — design tokens (same colors as the app's `tokens.js`) and the web type scale.
- `/app/` is a separate Expo web export and is not touched by the build.

## Local preview

```bash
python3 -m http.server 8765   # then open http://localhost:8765/
```
