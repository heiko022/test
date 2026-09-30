# 📸 Instagram Concept Studio (Testprojekt)

Ein **vollständig von einem Agenten generiertes Social-Media-Teststudio**. Zehn unterschiedliche Instagram-Konto-Konzepte mit echten Medien (Bilder, animierte GIFs, vertikale Reels), Captions, Hashtags und einer responsiven GitHub-Pages-Website.

> ⚠️ **Noch NICHT auf Instagram gepostet** · kein Instagram-Konto erstellt.

## 🗂 Inhalt

| Bereich | Pfad | Beschreibung |
|---|---|---|
| Website | `index.html`, `css/`, `js/` | Responsives Dashboard |
| Marktforschung | `research/market-research.md` | Aktuelle Nischen-Analyse |
| Quellen | `research/sources.md` | Seriöse Recherche-Quellen |
| Konzepte | `concepts/01..10-*/` | Je Konzept: `concept.md`, `content.md`, `image-01..03.png`, `animation-01.gif`, `reel-01.mp4` |
| Posts-Daten | `content/posts.json` | Alle 30 Posts strukturiert |
| Captions | `content/captions.md` | Alle Captions & Hashtags lesbar |

## 📊 Die 10 Konzepte

01. **KI-Tools täglich** (`@aitoolsdaily_de`) – AI Tools & Automation
02. **Urban Greens** (`@urbangreens.de`) – Urban Gardening & Balkon
03. **Minimal Minds** (`@minimalmind.de`) – Minimalismus & Mindset
04. **Gen Z Finanz** (`@genz.finanz`) – Finanzen für Gen Z
05. **Code Schnell** (`@code_schnell`) – Speed-Coding & Dev-Tipps
06. **Nachhaltig leben** (`@nachhaltig.leben`) – Nachhaltigkeit & Umwelttipps
07. **Homeoffice Hero** (`@homeoffice.hero`) – Remote Work & Produktivität
08. **Pflanzen Liebe** (`@pflanzen_liebe`) – Zimmerpflanzen & Gärtnern
09. **Kochen 2.0** (`@kochen.20`) – Schnelle Rezepte & Food-Hacks
10. **Zitate Kraft** (`@zitate.kraft`) – Motivation & Zitate

## 🎬 Enthält (gesamt)

- **30 Bilder** (3 pro Konzept, 1080×1080)
- **10 animierte GIFs** (je 8 Frames)
- **10 vertikale Reels** (9:16, 540×960, ~20 s, H.264)
- **30 Posts** mit Titel, Hook, Caption, Hashtags, Call-to-Action

## 🛠 Erzeugung

Die Medien werden programmatisch mit **Python + Pillow + ffmpeg** erzeugt.
Generator: [`tools/build.py`](tools/build.py) — eine Datenquelle (`CONCEPTS`) treibt Bilder, GIFs, Reels und alle Textdateien an, sodass keine Inkonsistenz entsteht.

```bash
python3 tools/build.py
```

## 🌐 GitHub Pages

Die Website ist unter GitHub Pages erreichbar:
`https://heiko022.github.io/test/`

## Hinweis

Dies ist ein autonomes Testexperiment — es soll zeigen, wie ein komplettes
Social-Media-Content-Studio (Recherche → Konzepte → Medien → Texte → Website)
ohne menschliche Eingriffe aufgebaut werden kann.
