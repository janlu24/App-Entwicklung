---
trigger: always_on
---

# Testing & Qualitätssicherung

## 1. Verpflichtende Tests
**Strenge Regel:** Keine KI-generierte Service-Funktion wird akzeptiert ohne einen entsprechenden `pytest` Testfall.
- **Anforderung:** Du musst die Testdatei sofort zusammen mit der Implementierung generieren.

## 2. Test-Umfang
- **Unit Tests:** Erforderlich für alle Berechnungen (Steuern, Summen) in `services.py`.
- **Integration Tests:** Erforderlich für Zustandsübergänge (z.B. "Prüfe, dass eine Rechnung nicht zweimal bezahlt werden kann").

## 3. Tooling
- **Runner:** Nutze `pytest`.
- **Daten:** Nutze `factory_boy` für Testdatengenerierung. Nutze keine hardcodierten SQL-Inserts.