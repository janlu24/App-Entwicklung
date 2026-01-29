---
trigger: always_on
---

# AI Engine <-> Frontend Protokoll

## 1. Die "Kein Rohtext"-Regel
Die AI Engine darf NIEMALS unstrukturierten Text oder rohes HTML für komplexe Aktionen zurückgeben.
Sie MUSS ein strikt typisiertes JSON-Objekt an das "Command Center" zurückgeben.

## 2. JSON Antwort-Struktur
Jede Antwort von der `ai_engine` an das Frontend muss diesem Schema folgen:

```json
{
  "message": "Menschenlesbare Zusammenfassung (z.B. 'Hier ist der Verkaufsbericht.')",
  "component": "widget-identifier (z.B. 'sales-chart-v2', 'invoice-table')",
  "data": {
    // Rohdaten für die Komponente zum Rendern
    "labels": ["Jan", "Feb"],
    "values": [100, 200]
  }
}

## 3. Render-Logik
- Das Backend liefert **Daten**, nicht UI.
- Das Frontend ist verantwortlich für die Auswahl des korrekten Widgets basierend auf dem `component` Key.