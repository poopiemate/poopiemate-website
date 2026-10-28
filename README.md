<div align="center">

<img src="assets/og/poopiemate-en.jpg" alt="POOPIEMATE" width="560">

# poopiemate.com

The website for **POOPIEMATE (응가메이트)** — your dog’s potty log, shared with the whole family.

**[poopiemate.com](https://poopiemate.com)** (Korean) · **[poopiemate.com/en](https://poopiemate.com/en/)** (English)

</div>

---

## Pages

| Page | Korean | English |
|---|---|---|
| Home — full-screen intro video, features, story, FAQ | `/` | `/en/` |
| How it works — five full-screen steps with app reels | `/how-it-works/` | `/en/how-it-works/` |
| Stories | `/story/` | `/en/story/` |
| Notices | `/notice/` | `/en/notice/` |
| User interview form | `/interview/` | `/en/interview/` |
| Privacy · Terms · Support · Open-source licenses | `/privacy/` `/terms/` `/support/` `/licenses/` | `/en/…` |
| Dog guides — list and 8 guides | `/guide/`, `/potty-interval/` and 7 more | `/en/guide/`, `/en/potty-interval/` … |
| Store redirect | `/download/` (`?lang=en`) | |

The site is static HTML on GitHub Pages with the custom domain `poopiemate.com`.

## Build

Pages are generated. Edit `src/`, not the HTML.

```bash
python3 src/prepare_assets.py   # mascot, 3D emoji, photos, videos, favicons (from the app repo + ~/Desktop/응가메이트)
python3 src/og.py               # share image 1200×630 per language → assets/og/
python3 src/build.py            # every page (Korean at /, English at /en/) + sitemap.xml
```

| Path | What it holds |
|---|---|
| `src/build.py` | Copy, layout, SEO (meta, hreflang, JSON-LD) for every page |
| `src/legal/` | Privacy, terms, support and licenses text |
| `src/legacy/` | Guides (`guides/*.json` Korean, `guides/en/*.json` English) and the interview form, wrapped in the site design |
| `src/render/` | Notice hero image and the family-invite reel (`node src/render/render.js`, needs Playwright) |
| `assets/css/site.css` | Design tokens (same colors as the app) and the web type scale |
| `assets/js/site.js` | Menu, header, intro video, full-page steps, word-by-word headlines, filters |
| `assets/js/store-region.js` | Sends English visitors to their own country’s App Store |
| `app/` | A separate Expo web export, not touched by the build |

Bump `ASSET_V` in `src/build.py` whenever CSS or JS changes, so browsers fetch the new files.

## Policy pages at the legacy address

App versions up to 2.0.0 and the store listings open the policy pages at `viva-jinyi.github.io/poopiemate-legal/…`
and the old website at `viva-jinyi.github.io/poopiemate-website/`. Those addresses are served by
[`viva-jinyi/viva-jinyi.github.io`](https://github.com/viva-jinyi/viva-jinyi.github.io) (a GitHub Pages address belongs to the account that serves it).
After changing anything in `src/legal/`, run `python3 src/build.py` there too and push, so the copies stay identical.

## Checks before publishing

- HTML: `html-validate` (standard rules) — no errors
- CSS: `csstree-validator` — no errors
- Accessibility: axe-core (WCAG 2.2 AA) on desktop and mobile — no violations
- Mobile: no horizontal scroll at 320 / 360 / 768 px, tap targets ≥ 24 px
- Browsers: Chromium, Firefox and WebKit

## Local preview

```bash
python3 -m http.server 8765   # then open http://localhost:8765/
```

## Related repositories

- [`poopiemate`](https://github.com/poopiemate/poopiemate) — the iOS / Android app (private)
- [`viva-jinyi.github.io`](https://github.com/viva-jinyi/viva-jinyi.github.io) — keeps the legacy policy and website URLs working

---

<sub>© 2026 Pixelberry · POOPIEMATE · <a href="mailto:poopiemate@pixelberry.io">poopiemate@pixelberry.io</a></sub>
