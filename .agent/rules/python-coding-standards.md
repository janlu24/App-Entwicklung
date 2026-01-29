---
trigger: always_on
---

# Python & Django Coding-Standards

## 1. Allgemeine Python-Regeln (Stil & Imports)
- **Type Hinting (Strikt Erforderlich):** Jedes Funktionsargument und jeder Rückgabewert muss typisiert sein.
  - *Schlecht:* `def calculate(items):`
  - *Gut:* `def calculate(items: list[OrderItem]) -> Decimal:`
- **Docstrings:** Jede Funktion in `services.py` muss einen Google-Style Docstring haben. Dies ist der "System Prompt" für die KI-Engine Tools.
- **Imports:**
  - Nutze nur **Absolute Imports**: `from apps.sales.services import create_invoice`
  - **Verboten:** Relative Imports wie `from ..models import Product`.

## 2. Datenhandling & Integrität
- **Geld:** NIEMALS `float` für Berechnungen nutzen. IMMER `Decimal` verwenden.
- **Transaktionen:** Jede Service-Methode, die in die DB schreibt (create/update), muss den `@transaction.atomic` Decorator nutzen, um Datenkonsistenz zu sichern.
- **Validierung:** Nutze **Pydantic** Schemas für komplexe Datenübergabe zwischen KI-Engine und Service Layer (statt lose Dictionaries).
  - *Ziel:* Strikte Validierung bevor die Daten die Geschäftslogik berühren.

## 3. Sprach- & Lokalisierungsstrategie (Strikt)

### A. Code-Struktur (Englisch)
- **Regel:** Alle technischen Bezeichner MÜSSEN auf **Englisch** sein.
- **Umfang:** Dateinamen, Klassennamen, Funktionsnamen, Variablennamen.
- **Beispiel:**
  - *Gut:* `class Invoice`, `def calculate_tax()`, `user_list = []`
  - *Schlecht:* `class Rechnung`, `def berechne_steuer()`, `benutzer_liste = []`
  - **Grund:** Konsistenz mit Python-Keywords und externen Bibliotheken.

### B. Dokumentation & Kommentare (Deutsch)
- **Regel:** Alle Erklärungen MÜSSEN auf **Deutsch** sein.
- **Umfang:** Docstrings (`"""..."""`), Inline-Kommentare und Markdown-Dokumentation (`/docs/*.md`).
- **Domänen-Präzision:** Nutze korrekte deutsche Rechtsbegriffe (HGB/GoBD) in Kommentaren für Präzision.
  - *Beispiel:* Nutze "Vorsteuer" oder "Rechnungsabgrenzung" im Docstring, selbst wenn die Variable `input_tax` oder `deferral` heißt.

### C. UI & Output (Deutsch)
- **Regel:** Aller nutzersichtbare Text ist auf **Deutsch**.
- **Umfang:** UI-Labels, Fehlermeldungen (`raise ValueError("...")`) und Log-Einträge für Admins.