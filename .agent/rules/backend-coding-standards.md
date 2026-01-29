---
trigger: always_on
---

# Backend-Coding-Standards & Kernprinzipien

## 1. AI-First Architektur (Die Service-Schicht)
**Regel:** Jede Geschäftsaktion muss für die KI zugänglich sein.
- **Nicht:** Geschäftslogik in Django Views oder API Serializers schreiben.
- **Tun:** Logik in `services.py` Funktionen kapseln (z.B. `create_invoice(user, data)`).
- **Warum:** Die KI-Engine ruft diese Python-Funktionen direkt als Tools auf. Sie kann keine View aufrufen.

## 2. Modularer Monolith Strategie
- Apps (z.B. `sales`, `inventory`) getrennt halten.
- Zirkuläre Importe zwischen Apps vermeiden.
- Django Signals oder einen fokussierten "Orchestrator Service" nutzen, wenn Apps miteinander kommunizieren müssen.

## 3. Das "Audit Everything" Mandat
**Strenge Bedingung:** Datenmutation (Erstellen/Aktualisieren/Löschen) ist verboten ohne ein Audit-Log (Änderungsprotokoll).
- Globale `middleware` oder spezifische `signals` nutzen, um Änderungen zu verfolgen.
- Niemals rohes SQL verwenden, das die `save()`-Methoden des ORM umgeht (da dies Signale/Logging überspringt).