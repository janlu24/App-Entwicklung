---
trigger: always_on
---

# Frontend-Architektur: Hybride Generative UI

## 1. Standard: HTMX (Der Flow)
- **Regel:** Nutze HTMX für 90% der Anwendung (Navigation, Formulare, einfaches Updates).
- **Ziel:** Server-Side Rendering (SSR) für Geschwindigkeit und Einfachheit.
- **Verboten:** Führe kein React/Vue für einfache Buttons oder Modals ein.

## 2. Ausnahme: Interaktive Inseln (Die Power)
- **Use Case:** Heavy-duty Data Grids (Excel-ähnliches Sortieren, Filtern, Bulk-Editing).
- **Erlaubte Tech:** React oder Vue (eingebunden in das DOM via Standard "Islands Architecture").
- **Trigger:** Nutze dies NUR, wenn HTMX-UX zu langsam oder klobig wäre (z.B. "Stammdaten-Ansicht").

## 3. Das "Command Center" (Kommandozentrale)
- Das Chat-Interface ist der zentrale Hub. Es parst das JSON-Protokoll und injiziert dynamisch die korrekte UI-Komponente (HTMX Partial oder React Island).