# -*- coding: utf-8 -*-
"""
Generator für das Instagram-Teststudio.
Erzeugt für jedes der 10 Konzepte:
  - 3 Bilder   (image-01..03.png, 1080x1080)
  - 1 GIF      (animation-01.gif, 540x540, animiert)
  - 1 Reel     (reel-01.mp4, 720x1280 @ 12fps, vertikal, ffmpeg/H.264)
Schreibt ausserdem posts.json, captions.md und je concept content.md.
Eine einzige Datenquelle -> keine Inkonsistenz zwischen Medien und Text.
"""
import os, json, math, subprocess, glob, shutil
from datetime import date
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONCEPTS_DIR = os.path.join(ROOT, "concepts")
CONTENT_DIR = os.path.join(ROOT, "content")
FFMPEG = "/root/.hermes/tools/ffmpeg-9.0.1-linux-x64/bin/ffmpeg"
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

def font(sz, bold=False):
    return ImageFont.truetype(FONT_B if bold else FONT, sz)

def hex2rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def gradient(w, h, c1, c2):
    c1, c2 = hex2rgb(c1), hex2rgb(c2)
    img = Image.new("RGB", (w, h))
    px = img.load()
    for y in range(h):
        t = y / max(1, h - 1)
        r = int(c1[0] + (c2[0]-c1[0])*t)
        g = int(c1[1] + (c2[1]-c1[1])*t)
        b = int(c1[2] + (c2[2]-c1[2])*t)
        for x in range(w):
            px[x, y] = (r, g, b)
    return img

def rounded(draw, box, radius, fill=None, outline=None, width=1):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)

def wrap(draw, text, fnt, maxw):
    words, lines, cur = text.split(), [], ""
    for w in words:
        test = (cur + " " + w).strip()
        if draw.textlength(test, font=fnt) <= maxw:
            cur = test
        else:
            if cur: lines.append(cur)
            cur = w
    if cur: lines.append(cur)
    return lines

def draw_center_block(draw, lines, fnt, center_x, start_y, line_h, fill):
    y = start_y
    for ln in lines:
        w = draw.textlength(ln, font=fnt)
        draw.text((center_x - w/2, y), ln, font=fnt, fill=fill)
        y += line_h
    return y

def decorate(draw, w, h, accent, seed=0):
    """abstract floating circles for a modern feel"""
    import random
    rnd = random.Random(seed)
    for _ in range(7):
        r = rnd.randint(20, 90)
        x = rnd.randint(-30, w)
        y = rnd.randint(-30, h)
        alpha = rnd.randint(25, 60)
        col = tuple(int(c*0.9+ (255*0.1)) for c in hex2rgb(accent))
        layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        ld = ImageDraw.Draw(layer)
        ld.ellipse([x-r, y-r, x+r, y+r], fill=col+(alpha,))
        return layer

# ---------------------------------------------------------------- data
CONCEPTS = [
 dict(folder="01-ai-tools-daily", name="KI-Tools täglich", handle="aitoolsdaily_de",
      niche="AI Tools & Automation", emoji="🤖", base="#6C5CE7", accent="#00D2D3",
      c1="#6C5CE7", c2="#2B1670",
      desc="Täglich ein KI-Tool, verständlich erklärt für Menschen ohne Tech-Wissen.",
      bold1="KI-Tool", bold2="der Woche.",
      tips=["Tool A → E-Mails in 5s", "Tool B → Artikel kurz", "Tool C → 10x schneller"],
      body="Weniger tippen. Mehr erledigt. KI ist jetzt Werkzeug für alle.",
      hook="Du nutzt KI noch nicht? Dir liegt Zeit auf dem Tisch. ⏱️",
      cta="Melde dich an & spare Zeit →",
      posts=[
        dict(n=1, titel="5 KI-Tools, die dein Leben leichter machen", hook="KI noch nicht im Alltag? Dir entgeht echte Zeit.", aos="KI-Tools im Alltag",
             caption="Diese KI-Tools sparen dir jeden Tag 30+ Minuten:\n\n1. Texte zusammenfassen\n2. E-Mails formulieren\n3. Bilder erstellen\n4. Termine planen\n5. Notizen ordnen\n\nWelches nutzt du am liebsten? 👇\n\nSpeichern & ausprobieren!",
             hashtags="#AITools #KI #KuenstlicheIntelligenz #Produktivitaet #WorkSmarter #DigitalTools #AIForEveryone #FutureOfWork #TechTips #Automation"),
        dict(n=2, titel="E-Mails in 5 Minuten statt 2 Stunden", hook="Stunden im Postfach? Das endet heute.", aos="E-Mail-Automation",
             caption="So automatisierst du dein Postfach mit KI:\n\n1. Vorlagen aus alten Antworten lernen lassen\n2. Priorisierung durch das Tool\n3. Bitte-Texte automatisch formulieren\n\nFunktioniert mit Gmail & Outlook. 💡\n\nTeile das mit einem, der viel mailt!",
             hashtags="#E-MailAutomation #KI #WorkSmarter #OfficeHack #TimeSaving #BusinessAutomation #SmartProductivity #AIWorkflow #DigitalOffice #Produktivitaet"),
        dict(n=3, titel="ChatGPT vs. Claude vs. Gemini", hook="Der KI-Assistenten-Check – wer gewinnt?", aos="KI-Vergleich",
             caption="Wir haben die Top 3 KI-Assistenten für Alltagsaufgaben getestet:\n\nChatGPT: allround stark\nClaude: Texte & Analysen\nGemini: Google-Integration\n\nErgebnis: Jedes Tool hat seinen Star-Use-Case. 🎯\n\nWas ist dein Favorit? 👇",
             hashtags="#ChatGPT #ClaudeAI #GoogleGemini #AIVergleich #BestAITool #AIComparison #TechReview #AITools #KuenstlicheIntelligenz #MachineLearning"),
      ]),
 dict(folder="02-urban-greens", name="Urban Greens", handle="urbangreens.de",
      niche="Urban Gardening & Balkon", emoji="🌿", base="#00B894", accent="#FFEAA7",
      c1="#008B74", c2="#004D40",
      desc="Kleine Oasen für Balkon, Fensterbank & Stadtwohnung – einfach umgesetzt.",
      bold1="Grün", bold2="in der City.",
      tips=["Kräuter auf 1 m²", "Tomaten im Balkon", "Gießen von unten"],
      body="Jede Stadtwohnung kann eine grüne Oase sein.",
      hook="Kein Garten? Kein Problem. Dein Balkon wird grün. 🌱",
      cta="Starte dein Mini-Grün →",
      posts=[
        dict(n=1, titel="Kräutergarten ohne Garten", hook="Vom Sterbepflanzen-Killer zum Kräuter-Profi?", aos="Minigarten Balkon",
             caption="Kräuter anbauen geht überall – sogar ohne Balkon:\n\n- Fensterbank reicht für Basilikum\n- Kresse findet auf jedem Platz Raum\n- Minze mag Halbschatten\n\nIn 3 Wochen erntest du frisch. 🌿\n\nSpeichern & starten!",
             hashtags="#UrbanGardening #Balkon #Kraeutergarten #Stadtgruen #GartenLiebhaber #UrbanJungle #GreenLiving #BalkonGarten #Plants #Nachhaltigkeit"),
        dict(n=2, titel="Tomaten im Topf: So klappt's", hook="Saftige Tomaten vom Balkon – Schritt für Schritt.", aos="Balkon-Tomaten",
             caption="Tomaten im Kübel funktionieren, wenn du 3 Dinge beachtest:\n\n1. Min. 6 Stunden Sonne\n2. Zwei Hände voll Erde mit Drainage\n3. Regelmäßig von unten gießen\n\nMehr Ertrag als gedacht! 🍅\n\nTag jemanden, der Tomaten liebt.",
             hashtags="#Tomaten #BalkonGarten #UrbanGardening #Gemuese #Selbstversorgung #GartenTipps #GreenCity #Pflanzen #Zucchini #TomatenLiebhaber"),
        dict(n=3, titel="5 fast unkaputtbare Zimmerpflanzen", hook="Du killst jede Pflanze? Probier diese 5.", aos="Anfänger-Pflanzen",
             caption="Die 5 Top-Zimmerpflanzen für absolute Anfänger:\n\n1. Gummibaum\n2. Sansevieria\n3. Einblatt\n4. Monstera\n5. Bogenhanf\n\nSie verzeihen sogar das Vergessen von Gießen. 😉\n\nWelche hast du schon zu Hause? 👇",
             hashtags="#Zimmerpflanzen #Pflanzen #UrbanJungle #Anfaenger #GreenLiving #Plantstagram #IndoorPlants #Monstera #Gummibaum #PflanzenLiebe"),
      ]),
 dict(folder="03-minimal-mind", name="Minimal Minds", handle="minimalmind.de",
      niche="Minimalismus & Mindset", emoji="◻️", base="#B2BEC3", accent="#00B894",
      c1="#636E72", c2="#2D3436",
      desc="Weniger Besitz, mehr Klarheit. Praktischer Minimalismus fürs Leben.",
      bold1="Weniger ist", bold2="mehr Klarheit.",
      tips=["30 Dinge pro Monat", "Die 1-in-1-out-Regel", "Ordnung im Handy"],
      body="Besitz reduziert Stress. Klarheit entsteht durch Ausmisten.",
      hook="Dein Zuhause bestimmt dein Denken. Räum auf. 🧘",
      cta="Mehr Klarheit, bitte →",
      posts=[
        dict(n=1, titel="Ausmisten: 30 Dinge in 30 Tagen", hook="Minimalismus ohne Zwang – 30 kleine Schritte.", aos="Ausmisten Challenge",
             caption="Die sanfte Challenge für mehr Leichtigkeit:\n\nTag 1-10: Schubladen & Schränke\nTag 11-20: Küche & Hobby\nTag 21-30: digitaler Raum\n\nEin Gegenstand pro Tag reicht. Kein Stress. 🧹\n\nSpeichere die Challenge!",
             hashtags="#Minimalismus #Ausmisten #MinimalLiving #DigitalDetox #WenigerIstMehr #Selbstoptimierung #Ordnung #Declutter #Mindset #EinfachLeben"),
        dict(n=2, titel="Die 1-in-1-out-Regel", hook="Nie wieder Unordnung – mit einer einfachen Regel.", aos="1-in-1-out",
             caption="Die Regel, die Unordnung dauerhaft stoppt:\n\nKommt etwas Neues rein, muss etwas Altes raus.\n\nGilt für Kleidung, Bücher, Küche.\n\nDein Zuhause bleibt automatisch schlank. ♻️\n\nFolge uns für mehr solche Hacks!",
             hashtags="#Minimalismus #MinimalLiving #Ordnung #WenigerIstMehr #Declutter #SimpleLiving #Mindset #Aufraeumen #EinfachLeben #DigitalDetox"),
        dict(n=3, titel="Digitale Entrümpelung in 20 Min.", hook="Dein Handy ist voll? 20 Minuten reichen.", aos="Digital Detox",
             caption="Digital aufräumen wirkt wie ein Neustart:\n\n1. 50 ungelesene Nachrichten löschen\n2. 10 Apps deinstallieren\n3. Bildschirmzeit-Check\n\nWeniger Reize = mehr Fokus. 📵\n\nWelchen Tipp setzt du heute um? 👇",
             hashtags="#DigitalDetox #Minimalismus #HandyEntruempeln #Achtsamkeit #Fokus #MinimalLiving #Ordnung #Produktivitaet #Mindset #DigitalMinimalism"),
      ]),
 dict(folder="04-gen-z-finance", name="Gen Z Finanz", handle="genz.finanz",
      niche="Finanzen für Gen Z", emoji="💸", base="#00CEC9", accent="#FDCB6E",
      c1="#0984E3", c2="#0A2E5C",
      desc="Geld einfach & ehrlich erklärt – für Studis, Azubis und den ersten Job.",
      bold1="Geld", bold2="leicht erklärt.",
      tips=["50/30/20-Regel", "Notgroschen aufbauen", "Depot mit Sparplan"],
      body="Finanzwissen ist der Turbo für dein erstes Gehalt.",
      hook="Dein Gehalt ist da – wohin damit? 💰",
      cta="Lern dein Geld kennen →",
      posts=[
        dict(n=1, titel="Die 50/30/20-Regel für dein Gehalt", hook="Nicht wissen, wo das Geld bleibt? Das ändert sich.", aos="Budgetierung",
             caption="Dein erster Budget-Check mit der 50/30/20-Regel:\n\n50% Fixkosten (Miete, Handy)\n30% Leben (Essen, Freizeit)\n20% Sparen & Investieren\n\nEinfach, schnell, fair zu dir. 📊\n\nSpeichern & Budget aufstellen!",
             hashtags="#Finanzen #Budget #GeldAnlegen #GenZ #FinancialLiteracy #Sparen #Budgetierung #MoneyMatters #Investieren #ErstesGehalt"),
        dict(n=2, titel="Notgroschen: Die wichtigste erste Sparreise", hook="Vor dem Investieren kommt der Puffer.", aos="Notgroschen",
             caption="Bevor du in ETFs startest: erst der Notgroschen.\n\n- Ziel: 3 Monatsausgaben\n- Tagesgeldkonto\n- automatischer Sparplan\n\nSo bist du krisenfest. 🛟\n\nTeile das mit einem Geld-Teen!",
             hashtags="#Notgroschen #Sparen #Finanzen #GenZ #FinancialLiteracy #Tagesgeld #Ersparnisse #GeldTipps #SmartMoney #Investieren"),
        dict(n=3, titel="ETF-Sparplan: ab 50 € starten", hook="Investieren ohne reich zu sein? Geht.", aos="ETF Sparplan",
             caption="Ein ETF-Sparplan startet schon klein:\n\n- ab 50 €/Monat\n- weltweit gestreut\n- automatisch laufen lassen\n\nZeit + Zinseszins = dein Turbo. 📈\n\nWelchem Betrag startest du? 👇",
             hashtags="#ETF #Sparplan #Investieren #GenZ #Aktien #Finanzen #PassivesEinkommen #Zinseszins #GeldAnlegen #Juniorinvestor"),
      ]),
 dict(folder="05-code-schnell", name="Code Schnell", handle="code_schnell",
      niche="Speed-Coding & Dev-Tipps", emoji="⚡", base="#FF5E78", accent="#00D2D3",
      c1="#1B1640", c2="#0F0F2D",
      desc="Kurze Dev-Hacks, Kommandos und Tipps – in unter einer Minute erklärt.",
      bold1="Codier", bold2="schneller.",
      tips=["git reset --soft HEAD~1", "docker compose up", "VS Code Multi-Cursor"],
      body="Sauberer Code ist schneller Code.",
      hook="Finger schneller als die Gedanken? Lern die Hacks. ⚡",
      cta="Mehr Dev-Hacks →",
      posts=[
        dict(n=1, titel="10 VS-Code-Shortcuts, die dich schnell machen", hook="Mit der Maus codierst du zu langsam.", aos="VS Code Shortcuts",
             caption="Diese 10 Shortcuts beschleunigen deinen Workflow:\n\n1. Multi-Cursor (Alt+Klick)\n2. Global Suchen (Ctrl+Shift+F)\n3. Schnelles Öffnen (Ctrl+P)\n4. Kommentar (Ctrl+/) ...\n\nLern 3 davon heute. Tastatur schlägt Maus. ⌨️\n\nSpeicher sie!",
             hashtags="#Coding #DevTips #VSCode #Programmieren #DeveloperLife #TechTips #CodeNewbie #Softwareentwicklung #Shortcuts #WebDev"),
        dict(n=2, titel="Git Befehle, die jeder kennen sollte", hook="Das 1x1 fürs Arbeiten im Team – in 5 Befehlen.", aos="Git Basics",
             caption="Die 5 Git-Befehle für den Alltag:\n\n- git status\n- git add .\n- git commit -m \"msg\"\n- git push\n- git pull\n\nMehr kommst du im Beruf kaum brauchen. 🔁\n\nTag einen angehenden Dev!",
             hashtags="#Git #DevTips #Coding #VersionControl #Programmieren #DeveloperLife #Softwareentwicklung #GitHub #TechTips #CodeNewbie"),
        dict(n=3, titel="Docker in 4 Zeilen erklärt", hook="\"Läuft bei mir\" – für immer gelöst.", aos="Docker Basics",
             caption="Docker in 4 Zeilen:\n\n1. Image = Rezept\n2. Container = laufende Instanz\n3. Dockerfile = Bauplan\n4. Compose = mehrere Services\n\nSo läuft dein Stack überall identisch. 🐳\n\nWelchen Dev-Bereich sollen wir erklären? 👇",
             hashtags="#Docker #DevOps #Coding #Programmieren #WebDev #Containers #TechTips #DeveloperLife #Softwareentwicklung #DevTips"),
      ]),
 dict(folder="06-nachhaltig-leben", name="Nachhaltig leben", handle="nachhaltig.leben",
      niche="Nachhaltigkeit & Umwelttipps", emoji="🌍", base="#6AB04C", accent="#F6E58D",
      c1="#2E7D32", c2="#1B5E20",
      desc="Kleine Schritte, große Wirkung – Nachhaltigkeit, die in den Alltag passt.",
      bold1="Nachhaltig", bold2="im Alltag.",
      tips=["Stoff statt Plastik", "Second-Hand kaufen", "Food-Sharing nutzen"],
      body="Nachhaltig heißt nicht perfekt. Es heißt besser.",
      hook="Nicht perfekt, aber besser: Starte heute. ♻️",
      cta="Grüner leben →",
      posts=[
        dict(n=1, titel="5 Zero-Waste-Swaps für den Start", hook="Zero Waste ohne Stress – 5 einfache Swaps.", aos="Zero Waste",
             caption="Zero-Waste-Einsteiger? Probier diese Swaps:\n\n1. Stoffbeutel statt Plastik\n2. Trinkflasche statt PET\n3. Bienenwachstücher statt Folie\n4. Waschmittel im Refill\n5. Obstnetze\n\nJeder Swap zählt. ♻️\n\nWelchen machst du zuerst?",
             hashtags="#ZeroWaste #Nachhaltigkeit #Umweltschutz #LebenOhnePlastik #Sustainability #GreenLiving #Klimaschutz #EinfachLeben #Umwelt #Plastikfrei"),
        dict(n=2, titel="Second-Hand: stylisch & grün", hook="Second-Hand ist kein Notnagel, sondern Statement.", aos="Second-Hand",
             caption="Warum Second-Hand gewinnt:\n\n- spart bis zu 80% CO₂\n- einzigartige Teile\n- schont den Geldbeutel\n\nPlattformen: Vinted, eBay Kleinanzeigen, Flohmärkte. 👕\n\nDein Stil, grün eingekauft. Speichern!",
             hashtags="#SecondHand #Nachhaltigkeit #SlowFashion #Upcycling #GrünerLeben #Sustainability #Vintage #Umweltschutz #FashionRevolution #Kleidung"),
        dict(n=3, titel="Energie sparen im Haushalt", hook="Leichter Geldbeutel + gute Bilanz = doppelt gut.", aos="Energie sparen",
             caption="3 Energie-Spar-Hacks für den Haushalt:\n\n1. Heizkörper frei von Möbeln\n2. LED statt Halogen\n3. Standby abschalten\n\nSpart Strom und CO₂. ⚡\n\nExtra-Tipp: Smart Plug macht's automatisch.\n\nWas sparst du am liebsten?",
             hashtags="#EnergieSparen #Nachhaltigkeit #StromSparen #Umweltschutz #GreenLiving #Energieeffizienz #Haushalt #Klimaschutz #Sustainability #Tipps"),
      ]),
 dict(folder="07-home-office-hero", name="Homeoffice Hero", handle="homeoffice.hero",
      niche="Remote Work & Produktivität", emoji="💻", base="#0984E3", accent="#FFEAA7",
      c1="#2D6A9F", c2="#0D3B66",
      desc="Produktiver, gesünder und zufriedener im Homeoffice arbeiten.",
      bold1="Remote", bold2="reloaded.",
      tips=["Morgenroutine ohne Handy", "Pomodoro jetzt", "Ergonomischer Tisch"],
      body="Distancing zum Monitor. Fokus zum Rest.",
      hook="Homeoffice = Ablenkung? Nicht mehr. 🚀",
      cta="Produktiver remote arbeiten →",
      posts=[
        dict(n=1, titel="Die perfekte Remote-Morgenroutine", hook="Dein Tag entscheidet sich in der ersten Stunde.", aos="Morgenroutine",
             caption="Meine Remote-Morgenroutine:\n\n1. kein Handy als erstes\n2. Wasser + Bewegung\n3. Top 3 Aufgaben festlegen\n4. Fokus-Deepwork vor dem Meeting\n\nSo startet dein Tag aktiv statt reaktiv. 🌅\n\nWas ist deine #1 aus der Routine?",
             hashtags="#Homeoffice #RemoteWork #Produktivitaet #Morgenroutine #WorkFromHome #Fokus #DeepWork #Selbstorganisation #RemoteJobs #WorkLifeBalance"),
        dict(n=2, titel="Pomodoro: 25+5 für echten Fokus", hook="Prokrastination besiegen? Mit einer Uhr & Tomate.", aos="Pomodoro",
             caption="Pomodoro-Technik einfach erklärt:\n\n- 25 Min. voller Fokus\n- 5 Min. Pause\n- nach 4 Runden: 20 Min. lang\n\nPerfekt gegen dezente Homeoffice-Ablenkung. 🍅\n\nTimer-Apps: Forest, Focus To-Do.\n\nProbier es heute!",
             hashtags="#Pomodoro #Produktivitaet #Homeoffice #Fokus #Zeitmanagement #DeepWork #WorkFromHome #AntiProkrastination #RemoteWork #Zeitplanung"),
        dict(n=3, titel="Ergonomie am Schreibtisch: 7 Fixes", hook="Rückenschmerzen im Homeoffice sind kein Schicksal.", aos="Ergonomie",
             caption="7 ergonomische Sofort-Fixes:\n\n1. Bildschirm auf Augenhöhe\n2. Ellenbogen 90°\n3. Füße flach auf dem Boden\n4. Handgelenke gerade\n5. Bildschirm 50cm entfernt\n6. Stehpausen alle 45 Min.\n7. Beleuchtung von schräg\n\nDein Körper dankt es dir. 🪑\n\nSpeichern & umsetzen!",
             hashtags="#Ergonomie #Homeoffice #Gesundheit #RemoteWork #Ruecken #Arbeitsplatz #Sitzen #Produktivitaet #Wellness #WorkFromHome"),
      ]),
 dict(folder="08-pflanzen-liebe", name="Pflanzen Liebe", handle="pflanzen_liebe",
      niche="Zimmerpflanzen & Gärtnern", emoji="🪴", base="#40916C", accent="#D8F3DC",
      c1="#2D6A4F", c2="#1B4332",
      desc="Dein Zimmer wird Dschungel – mit Liebe, Wasser und ein bisschen Wissen.",
      bold1="Pflanzen", bold2="fürs Leben.",
      tips=["Umtopfen: 1x im Jahr", "Dunkel: Sansevieria", "Blätter abstauben"],
      body="Jede Pflanze will gedeihen – du gibst ihr nur den Rahmen.",
      hook="Kein grüner Daumen? Dieser hier hilft. 🌿",
      cta="Mehr Grün ins Zuhause →",
      posts=[
        dict(n=1, titel="Zimmerpflanzen, die fast unkaputtbar sind", hook="Für alle, die sonst alles killen: Diese 5 überleben.", aos="Unkaputtbare Pflanzen",
             caption="Die 5 pflegeleichtesten Zimmerpflanzen:\n\n1. Sansevieria\n2. Gummibaum\n3. Gladiole (Einblatt)\n4. Zamioculcas\n5. Efeutute\n\nSie verzeihen verpasstes Gießen. ✅\n\nWelche steht bei dir?",
             hashtags="#Zimmerpflanzen #PflanzenLiebe #IndoorPlants #Pflanzen #UrbanJungle #Grün #Pflanzenfan #GreenLiving #Monstera #IndoorGarden"),
        dict(n=2, titel="So rettest du eine vergilbte Pflanze", hook="Blätter werden gelb? Das heißt was Konkretes.", aos="Pflanzen retten",
             caption="Gelbe Blätter = SOS-Zeichen. Das hilft:\n\n- zu viel Wasser → abtrocknen lassen\n- zu wenig Licht → heller stellen\n- Nährstoffmangel → düngen\n\nSchneide kranke Blätter ab – sie rauben Kraft. 🌱\n\nFrage uns bei deiner Pflanze!",
             hashtags="#Pflanzenretter #Zimmerpflanzen #Pflanzenpflege #PflanzenLiebe #GreenLiving #IndoorPlants #PflanzenTipps #UrbanJungle #Gärtnern #Pflanzen"),
        dict(n=3, titel="Umtopfen in 4 Schritten", hook="Deine Pflanze braucht Platz – so geht Umtopfen schnell.", aos="Umtopfen",
             caption="Umtopfen Schritt für Schritt:\n\n1. Pflanze vorsichtig raus\n2. Wurzeln prüfen & lockern\n3. neuer Topf mit Frisch-Erde\n4. gut angießen\n\nRichtiger Zeitpunkt: Frühjahr. 🪴\n\n1x im Jahr genügt. Speichern!",
             hashtags="#Umtopfen #Zimmerpflanzen #Pflanzen #Pflanzenpflege #GreenLiving #IndoorPlants #Gärtnern #PflanzenLiebe #UrbanJungle #PflanzenTipps"),
      ]),
 dict(folder="09-kochen-20", name="Kochen 2.0", handle="kochen.20",
      niche="Schnelle Rezepte & Food-Hacks", emoji="🍳", base="#E1701A", accent="#FFEAA7",
      c1="#C0392B", c2="#5C2A1D",
      desc="In 15 Minuten auf dem Tisch – leckere & einfache Rezepte für den Alltag.",
      bold1="Essen,", bold2="schnell & gut.",
      tips=["One-Pot-Pasta", "Resteverwertung richtig", "Zwiebeln ohne Tränen"],
      body="15 Minuten, ein Topf, vollwertig.",
      hook="Pasta nach der Arbeit? In 15 Min. fertig. 🍝",
      cta="Es ist Essenszeit →",
      posts=[
        dict(n=1, titel="One-Pot-Pasta in 15 Minuten", hook="Ein Topf, kein Spülen, echte Liebe.", aos="One-Pot Pasta",
             caption="One-Pot-Pasta – alles in einen Topf:\n\n- 400g Pasta\n- 1 Dose Tomaten\n- Zwiebel, Knoblauch, Basilikum\n- 1L Wasser\n\nAlles 15 Min. kochen, umrühren, fertig. 🍝\n\nDein Abendretter. Speichern!",
             hashtags="#Rezept #Schnellkochen #Pasta #OnePot #Foodie #Kochen #KochIdee #Abendessen #FoodHacks #EinfachKochen"),
        dict(n=2, titel="Resteverwertung: einfach nie wieder wegwerfen", hook="Kühlschrank halb voll? Daraus wird ein Gericht.", aos="Resteverwertung",
             caption="3 Wege, Reste zu retten:\n\n1. Suppe: alles Gemüse + Brühe\n2. Stir-Fry: Reste + Sojasauce\n3. Pfannenbrot aus alten Teigen\n\nNichts landet im Müll. ♻️\n\nTag einen Koch-Amateur!",
             hashtags="#Resteverwertung #FoodHacks #Kochen #NachhaltigKochen #ZeroFoodWaste #Rezept #EinfachKochen #KochIdee #Foodie #MealPrep"),
        dict(n=3, titel="Zwiebeln schneiden ohne Tränen", hook="Der Küchen-Trick, den jeder kennen sollte.", aos="Zwiebel-Trick",
             caption="So weinen Zwiebeln nicht mehr:\n\n- Zwiebel vorher 10 Min. ins Eisfach\n- sehr scharfes Messer\n- unter laufendem Wasser hacken\n\nGase reizen deine Augen einfach weniger. 😭→😄\n\nWelcher Trick funktioniert bei dir?",
             hashtags="#FoodHacks #Kochen #KuechenTipps #Rezept #Zwiebel #Foodie #EinfachKochen #KochLernen #ChefLife #KochTrick"),
      ]),
 dict(folder="10-zitate-kraft", name="Zitate Kraft", handle="zitate.kraft",
      niche="Motivation & Zitate", emoji="✨", base="#FBC531", accent="#FFEAA7",
      c1="#1E272E", c2="#2C2C54",
      desc="Kraftvolle Worte für deinen Tag – Zitate, die mitten ins Herz treffen.",
      bold1="Worte,", bold2="die tragen.",
      tips=["Morgens eine Stärke", "Rückschläge sind Umwege", "Disziplin > Motivation"],
      body="Manchmal braucht es genau einen Satz.",
      hook="Ein Satz kann deinen Tag drehen. ✨",
      cta="Täglich neue Kraft →",
      posts=[
        dict(n=1, titel="Disziplin ist, was du tust, wenn keiner schaut", hook="Motivation startet, Disziplin beendet.", aos="Disziplin",
             caption="Disziplin ist die Kunst, den nächsten Schritt zu tun – auch wenn es niemand bemerkt.\n\nKleine Gewohnheiten, jeden Tag.\n\nDas ist der ganze Trick. ✨\n\nSpeichere diesen Satz für später.",
             hashtags="#Motivation #Zitate #Disziplin #Mindset #Erfolg #SelfGrowth #Lebensweisheit #ZitatDesTages #Durchhalten #InnereStaerke"),
        dict(n=2, titel="Du musst nicht groß anfangen, aber du musst anfangen", hook="Klein anfangen ist nicht schwach – es ist klug.", aos="Anfangen",
             caption="Der größte Fehler ist Zögern, nicht Scheitern.\n\nEin kleiner Schritt heute schlägt eine perfekte Idee am Montag.\n\nFang heute an, nicht irgendwann. 🌄\n\nTag jemanden, der es hören sollte!",
             hashtags="#Motivation #Zitate #Anfangen #Mindset #Erfolg #Aktion #SelfGrowth #Inspiration #Mut #ZitatDesTages"),
        dict(n=3, titel="Rückschläge sind Umwege, keine Sackgassen", hook="Scheitern ist Feedback, nicht Ende.", aos="Rückschläge",
             caption="Rückschläge sind kein Stoppschild.\n\nSie zeigen dir nur eine neue Richtung.\n\nSteh auf, lerne, geh weiter. 🚶\n\nWelcher Rückschlag brachte dich weiter? 👇",
             hashtags="#Motivation #Zitate #Rueckschlaege #Mindset #Staerke #Selbstvertrauen #Lebensweisheit #Inspiration #GrowthMindset #ZitatDesTages"),
      ]),
]

def emoji_fallback(emoji, draw_override="★"):
    return draw_override

# ---------------------------------------------------------------- media names
def img_name(c, i): return f"image-{i:02d}.png"
GIF_NAME = "animation-01.gif"
REEL_NAME = "reel-01.mp4"

# ---------------------------------------------------------------- image render
def render_image(concept, i):
    W = H = 1080
    img = gradient(W, H, concept["c1"], concept["c2"])
    d = ImageDraw.Draw(img)
    # decorative circles
    import random
    rnd = random.Random(concept["handle"] + str(i))
    for _ in range(8):
        r = rnd.randint(30, 120)
        x = rnd.randint(-20, W)
        y = rnd.randint(-20, H)
        shape = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        sd = ImageDraw.Draw(shape)
        col = hex2rgb(concept["accent"])
        sd.ellipse([x-r, y-r, x+r, y+r], fill=col + (rnd.randint(25, 55),))
        img = Image.alpha_composite(img.convert("RGBA"), shape).convert("RGB")
    d = ImageDraw.Draw(img)
    accent = hex2rgb(concept["accent"])
    white = (255, 255, 255)

    # top badge
    badge = f"@{concept['handle']}   {concept['niche'].upper()}"
    f_small = font(34, True)
    bw = d.textlength(badge, font=f_small) + 80
    rounded(d, [(W-bw)/2, 70, (W+bw)/2, 150], radius=40, fill=(0,0,0,70))
    d.text(((W-bw)/2+40, 88), badge, font=f_small, fill=white)

    if i == 1:
        # image-02: tip list card
        y1 = draw_center_block(d, [concept["bold1"], concept["bold2"]], font(96, True), W/2, 230, 118, accent)
        y = y1 + 60
        for t in concept["tips"]:
            boxh = 110
            rounded(d, [150, y, W-150, y+boxh], radius=24, fill=(0,0,0,75))
            d.ellipse([185, y+34, 225, y+74], fill=accent)
            d.text((202, y+36), "✓", font=font(34, True), fill=(10,10,10))
            d.text((255, y+26), t, font=font(38), fill=white)
            y += boxh + 34
        # bottom cta
        d.text((W/2, H-130), "Sichere diese Tipps →", font=font(40, True), anchor="mm", fill=accent)
    elif i == 2:
        # image-03: question/engagement card
        y1 = draw_center_block(d, ["Was ist", "dein", "Take?"], font(110, True), W/2, 250, 135, white)
        rounded(d, [(W-760)/2, y1+80, (W+760)/2, y1+210], radius=50, fill=accent)
        d.text((W/2, y1+145), "KOMMENTIERE ▶", font=font(48, True), anchor="mm", fill=(10,10,10))
        d.text((W/2, H-180), "Folge @" + concept["handle"], font=font(42, True), anchor="mm", fill=white)
    else:
        # image-01: hero
        lines = wrap(d, concept["desc"], font(44), W-260)
        y1 = draw_center_block(d, [concept["bold1"], concept["bold2"]], font(120, True), W/2, 280, 140, white)
        y = y1 + 60
        draw_center_block(d, lines, font(44), W/2, y, 70, (255,255,255,215))
        # accent underline
        uw = d.textlength(concept["bold2"], font=font(120, True))
        d.rectangle([W/2 - uw/2, 420+140, W/2 + uw/2, 420+140+14], fill=accent)
        d.text((W/2, H-170), "FOLGE UNS →", font=font(52, True), anchor="mm", fill=accent)
    return img

# ---------------------------------------------------------------- gif render
def render_gif(concept):
    W = H = 540
    accent = hex2rgb(concept["accent"])
    white = (255, 255, 255)
    frames = []
    n = 8
    # animated: big word + pulsing CTA pill + bouncing arrow
    big = [concept["bold1"], concept["bold2"]]
    for t in range(n):
        img = gradient(W, H, concept["c1"], concept["c2"])
        d = ImageDraw.Draw(img)
        pulse = 0.85 + 0.3 * (0.5 + 0.5*math.sin(2*math.pi*t/n))
        # floating dots
        for k, (dx, dy, r) in enumerate([(60,80,26),(W-110,120,40),(90,H-90,32),(W-80,H-60,20)]):
            d.ellipse([dx-r,dy-r,dx+r,dy+r], fill=accent+(60,))
        # headline
        y = 150
        for ln, isb in zip(big, [True,True]):
            if isb:
                lw = d.textlength(ln, font=font(64, True))
                d.text((W/2 - lw/2, y), ln, font=font(64, True), fill=white)
            y += 76
        # CTA pill pulsing
        bw = 320
        bh = 78
        by = H - 160
        col = tuple(int(c*pulse) for c in accent)
        rounded(d, [(W-bw)/2, by, (W+bw)/2, by+bh], radius=bh//2, fill=col if pulse>0.95 else (60,60,60))
        d.text((W/2, by+bh/2), "Jetzt entdecken", font=font(30, True), anchor="mm", fill=(20,20,20))
        # bouncing arrow
        ay = by - 40 - int(12*abs(math.sin(2*math.pi*t/n)))
        d.text((W/2, ay), "▼", font=font(30, True), anchor="mm", fill=white)
        frames.append(img)
    frames[0].save(os.path.join(CONCEPTS_DIR, concept["folder"], GIF_NAME),
                   save_all=True, append_images=frames[1:],
                   duration=90, loop=0, disposal=2)

# ---------------------------------------------------------------- reel render
REEL_W, REEL_H, FPS = 540, 960, 12

def reel_timeline():
    # returns list of (start_sec, dur, kind)
    return [
        (0.0, 3.2, "hook"),
        (3.2, 0.8, "space"),
        (4.0, 5.0, "tips"),
        (9.0, 0.8, "space"),
        (9.8, 3.0, "body"),
        (12.8, 0.8, "space"),
        (13.6, 3.0, "cta"),
    ]

def render_reel_frame(concept, scene, sprog, base):
    """base = cached RGBA gradient background; scene in {'hook','tips','body','cta','space'} sprog in [0,1]"""
    img = base.copy()
    d = ImageDraw.Draw(img, "RGBA")
    accent = hex2rgb(concept["accent"])
    white = (255, 255, 255)
    ease = sprog  # simple ease-out
    a = min(1.0, ease*3)  # fade
    alpha = int(255*a)

    d.rectangle([0,0,REEL_W,44], fill=(0,0,0,120))
    d.text((REEL_W/2, 22), "●  " + concept["niche"].upper(), font=font(26, True), anchor="mm", fill=white)

    if scene == "hook":
        lines = wrap(d, concept["hook"], font(58, True), REEL_W-90)
        y = 360
        draw_center_block(d, lines, font(58, True), REEL_W/2, y, 80, white+(alpha,))
        d.text((REEL_W/2, 760), "Dranbleiben ▶", font=font(32, True), anchor="mm", fill=accent+(alpha,))
        d.ellipse([REEL_W/2-8, 830, REEL_W/2+8, 846], fill=accent+(alpha,))
    elif scene == "tips":
        d.text((70, 300), "In 60 Sekunden:", font=font(52, True), fill=accent+(alpha,))
        y = 420
        nitems = len(concept["tips"])
        show = int(sprog * nitems) + 1
        for k in range(show):
            if k >= nitems: break
            item_alpha = min(1.0, (sprog*nitems - k)*2)
            rounded(d, [70, y, REEL_W-70, y+150], radius=22, fill=(255,255,255, int(46*item_alpha)))
            d.ellipse([110, y+52, 150, y+92], fill=accent)
            d.text((128, y+62), str(k+1), font=font(30, True), anchor="mm", fill=(10,10,10))
            d.text((180, y+46), concept["tips"][k], font=font(36), fill=white+(int(255*item_alpha),))
            y += 175
    elif scene == "body":
        lines = wrap(d, concept["body"], font(58, True), REEL_W-90)
        y = 430
        draw_center_block(d, lines, font(58, True), REEL_W/2, y, 84, white+(alpha,))
        d.rectangle([REEL_W/2-70, 760, REEL_W/2+70, 764], fill=accent+(alpha,))
    elif scene == "cta":
        d.text((REEL_W/2, 430), concept["cta"], font=font(54, True), anchor="mm", fill=white+(alpha,))
        pulse = 0.9 + 0.2*math.sin(sprog*2*math.pi)
        col = tuple(int(c*pulse) for c in accent)
        bw, bh = 520, 100
        bx, by = (REEL_W-bw)/2, 560
        rounded(d, [bx, by, bx+bw, by+bh], radius=bh//2, fill=col)
        d.text((REEL_W/2, by+bh/2), "Folge @" + concept["handle"], font=font(38, True), anchor="mm", fill=(15,15,15))
        d.text((REEL_W/2, 750), "Speichern  ·  Teilen  ·  Folgen", font=font(30, True), anchor="mm", fill=white+(alpha,))

    # bottom-safe-area hint / progress
    d.rectangle([0, REEL_H-10, REEL_W, REEL_H], fill=(0,0,0,90))
    d.rectangle([0, REEL_H-10, REEL_W*0.18, REEL_H], fill=accent)
    return img

def render_reel(concept):
    out = os.path.join(CONCEPTS_DIR, concept["folder"], REEL_NAME)
    tl = reel_timeline()
    total = sum(d for _, d, _ in tl)
    total_frames = int(total * FPS)
    # stop button marker
    cmd = [FFMPEG, "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{REEL_W}x{REEL_H}",
           "-r", str(FPS), "-i", "pipe:0", "-an", "-vf", "format=yuv420p",
           "-c:v", "libx264", "-preset", "ultrafast", "-crf", "28", "-movflags", "+faststart", out]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    base = gradient(REEL_W, REEL_H, concept["c1"], concept["c2"]).convert("RGBA")
    cur = 0.0
    for _, dur, kind in tl:
        nframes = int(dur*FPS)
        for f in range(nframes):
            sprog = f/max(1, nframes-1)
            frame = render_reel_frame(concept, kind, sprog, base)
            proc.stdin.write(frame.convert("RGB").tobytes())
    proc.stdin.close()
    proc.wait()
    if proc.returncode != 0:
        raise RuntimeError("ffmpeg failed for " + concept["folder"])

# ---------------------------------------------------------------- text outputs
def write_content_md(concept):
    p = os.path.join(CONCEPTS_DIR, concept["folder"], "content.md")
    s = [f"# {concept['name']} · Content-Details", ""]
    for post in concept["posts"]:
        s += [
            f"## POST {post['n']:02d}", "",
            f"**Titel:** {post['titel']}", "",
            f"**Hook:** {post['hook']}", "",
            "**Caption:**", post["caption"], "",
            f"**Hashtags:** {post['hashtags']}", "",
            "**Medien-Dateien:**", "",
            f"- Bild: `{img_name(concept, post['n'])}`",
            f"- GIF: `{GIF_NAME}`",
            f"- Reel: `{REEL_NAME}`",
            "---", "",
        ]
    open(p, "w", encoding="utf-8").write("\n".join(s))

def build_posts_json():
    posts = []
    for ci, concept in enumerate(CONCEPTS, 1):
        for post in concept["posts"]:
            posts.append(dict(
                concept=f"{ci:02d}-{concept['folder'].split('-',1)[1]}",
                concept_name=concept["name"],
                handle=concept["handle"],
                post=post["n"],
                titel=post["titel"], hook=post["hook"], aos=post["aos"],
                caption=post["caption"], hashtags=post["hashtags"],
                image=img_name(concept, post["n"]),
                gif=GIF_NAME, reel=REEL_NAME,
                niche=concept["niche"],
            ))
    out = {"project":"Instagram Content Teststudio", "created": date.today().isoformat(),
           "concepts": len(CONCEPTS), "count": len(posts), "posts": posts}
    os.makedirs(CONTENT_DIR, exist_ok=True)
    open(os.path.join(CONTENT_DIR, "posts.json"), "w", encoding="utf-8").write(
        json.dumps(out, ensure_ascii=False, indent=2))

def write_captions_md():
    p = os.path.join(CONTENT_DIR, "captions.md")
    s = ["# Alle Captions & Hashtags (30 Posts)", ""]
    for ci, concept in enumerate(CONCEPTS, 1):
        s.append(f"## Konzept {ci:02d}: {concept['name']} (@{concept['handle']})")
        for post in concept["posts"]:
            s += ["", f"### POST {post['n']:02d} · {post['titel']}", "",
                  "**Caption:**", post["caption"], "",
                  f"**Hashtags:** {post['hashtags']}", "",
                  f"**Dateien:** {img_name(concept, post['n'])} · {GIF_NAME} · {REEL_NAME}", ""]
    open(p, "w", encoding="utf-8").write("\n".join(s))

# ---------------------------------------------------------------- main
def main():
    os.makedirs(CONTENT_DIR, exist_ok=True)
    for concept in CONCEPTS:
        d = os.path.join(CONCEPTS_DIR, concept["folder"])
        os.makedirs(d, exist_ok=True)
        for i in (1, 2, 3):
            render_image(concept, i).save(os.path.join(d, img_name(concept, i)), "PNG", optimize=True)
        render_gif(concept)
        render_reel(concept)
        write_content_md(concept)
        print("done media:", concept["folder"])
    build_posts_json()
    write_captions_md()
    print("ALL MEDIA + TEXT DONE")

if __name__ == "__main__":
    main()
