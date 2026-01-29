---
trigger: always_on
---

# Asynchrone Verarbeitung & I/O Richtlinien

## 1. Die "1-Sekunden-Regel" (Celery)
- **Strenge Regel:** Jede Aufgabe, die länger als ~1 Sekunde dauert (z.B. OpenAI-Aufruf, PDF-Generierung, Email-Versand), MUSS in einem Hintergrund-Worker laufen.
- **Tooling:** Nutze **Celery** mit Redis.
- **Implementierung:**
  - Definiere Tasks in `apps/{app_name}/tasks.py`.
  - Trigger sie aus `services.py` mit `.delay()`.
  - Nutze das Notification Center (`core`), um den User zu informieren, wenn der Task fertig ist.

## 2. Dateispeicherung (Keine Blobs in DB)
- **Verboten:** Speichere NIEMALS Datei-Binaries (PDFs, Bilder) oder Base64-Strings direkt in der PostgreSQL-Datenbank.
- **Anforderung:**
  - Speichere Dateien im Dateisystem (Dev) oder S3-kompatiblen Storage (Prod).
  - Nutze Djangos `FileField`/`ImageField`, welches nur den **Pfad/Referenz** speichert.

## 3. Externe Adapter (Das Facade-Pattern)
- Externe APIs (Banking, Steuer, Email) müssen in "Adapter-Klassen" innerhalb von `core/adapters/` gewrappt werden.
- **Ziel:** Die Geschäftslogik sollte `EmailAdapter.send(...)` aufrufen, nicht `smtplib` direkt. Dies ermöglicht Mocking in Tests.