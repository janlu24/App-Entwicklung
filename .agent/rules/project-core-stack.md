---
trigger: always_on
---

# Projekt-Core & Tech-Stack Richtlinien

## Projekt-Kontext
Du arbeitest am **"AI-First ERP"**, einem modularen System für kleine Unternehmen.
**Kernphilosophie:** "Konversation über Navigation".
- Priorisiere Chat-Interfaces über komplexe Menüs.
- Baue Logik so, dass sie über natürliche Spracheingabe gesteuert werden kann.
- Das UI sollte minimal sein; die Backend-Logik ist das Kraftwerk.

## Verpflichtender Tech-Stack (Strikt)
Du musst dich strikt an diese Technologien halten. Schlage keine Alternativen vor.
- **Sprache:** Python 3.12+
- **Backend Framework:** Django 5.x (Nutze Standard Django-Muster)
- **Datenbank:** PostgreSQL
- **Frontend/Interaktivität:** HTMX (für dynamisches Verhalten) & Tailwind CSS (für Styling).
- **Architektur:** Modulare App-Struktur.