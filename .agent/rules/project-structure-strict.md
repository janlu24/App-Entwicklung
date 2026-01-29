---
trigger: always_on
---

# Verzeichnisstruktur & Datei-Platzierungsregeln

## 1. Die Verbotene Zone (`/core`)
- **Strenge Regel:** Das `/core` Verzeichnis ist NUR für Infrastruktur (Abstract Base Models, Globale Middleware, Generische Utils).
- **NIEMALS:** Lege keine spezifische Geschäftslogik (wie "Rechnung erstellen" oder "Steuer berechnen") in `/core` ab.

## 2. Das Zentrum der Geschäftslogik (`/apps`)
- Alle funktionalen Module liegen in `/apps/{module_name}`.
- Wenn du eine neue Domäne erstellst (z.B. "shipping"), erstelle einen neuen Ordner: `/apps/shipping`.

## 3. Das Service-Layer Mandat (KRITISCH)
Innerhalb jeder App in `/apps/` musst du diese Dateistruktur erzwingen:
- `services.py`: **ALLE Geschäftslogik kommt hierhin.** (Berechnungen, Zustandsänderungen).
- `api.py`: Interne Endpoints, die `services.py` aufrufen. Keine Logik hier!
- `models.py`: Nur Datenbank-Schema. Methoden minimal halten.

## Referenzbaum (Single Source of Truth)
```text
/
├── core/                       # Das "Fundament" (Keine Geschäftslogik!)
│   ├── utils/                  # Globale Helfer (AI Client, PDF Generator)
│   ├── models.py               # Abstrakte Basis-Modelle (UUID, Timestamps)
│   └── middleware.py           # Audit Logging & Tenant Context
├── apps/                       # Modulare Geschäftslogik
│   ├── users/                  # Custom User Model & RBAC
│   ├── ai_engine/              # Prompts, Memory, Tool Definitionen
│   ├── sales/                  # Rechnungen, Angebote
│   │   ├── services.py         # [STRIKT] Geschäftslogik kommt hierhin
│   │   ├── api.py              # Interne API Endpoints
│   │   └── models.py           # Datenbank-Tabellen
│   └── inventory/              # Lagerverwaltung
│   └── finance/                # Hauptbuch & Buchhaltung
├── templates/                  # HTMX Partials & Basis-Layouts
├── static/                     # CSS (Tailwind Input), JS
├── manage.py
└── requirements.txt