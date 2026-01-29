---
trigger: always_on
---

# Datenintegrität & State Management Regeln

## 1. Finanzielle Präzision
- **Strenge Regel:** NIEMALS `Float` für Währungen verwenden.
- **Anforderung:** IMMER `models.DecimalField` (z.B. `max_digits=14, decimal_places=2`) für finanzielle Werte nutzen.

## 2. State Management (Endlicher Automat)
Wir nutzen strikte Zustandsübergänge, um sicherzustellen, dass Seiteneffekte (wie Einträge im Hauptbuch) die Realität abbilden.
- **Bibliothek:** `viewflow.fsm` nutzen (speziell die FSM-Features).
- **Verboten:** NICHT das veraltete `django-fsm` Paket verwenden.
- **Implementierung:**
    - Zustände als `TextChoices` definieren.
    - Transitions-Methoden mit `@transition` dekorieren.

## 3. Die "Keine magische Zuweisung"-Regel
- **Verboten:** Niemals einen Status direkt zuweisen (z.B. `invoice.status = 'paid'`).
- **Verpflichtend:** Du MUSST die Transitions-Methode nutzen (z.B. `invoice.mark_as_paid()`).
- **Warum:** Direkte Zuweisung überspringt die Seiteneffekte (z.B. Erstellung des Buchungssatzes in der Finanzbuchhaltung).

## 4. Core App Grenzen
- Die `/core` App enthält **Singleton Models** für dynamische Einstellungen (Firmeninfos, USt-ID).
- Keine geschäftlichen Werte (wie Steuersätze) im Python-Code hardcoden; diese aus den Settings laden.