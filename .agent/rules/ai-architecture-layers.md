---
trigger: always_on
---

# AI Architektur & Trennung der Zuständigkeiten (SoC)

## Schicht A: Der Connector (`core.utils.ai_client`)
- **Rolle:** Reine Infrastruktur. Handhabt API Keys, HTTP Retries, Rate Limits.
- **STRENGE REGEL:** Diese Schicht muss **Provider-Agnostisch** sein.
- **VERBOTEN:** Keine ERP-Geschäftslogik hier. Keine Importe von `apps.sales` oder `apps.inventory`.

## Schicht B: Die Engine (`apps.ai_engine`)
- **Rolle:** Das Gehirn. Verwaltet Prompts, Memory und Entscheidungsfindung.
- **Tool-Discovery-Regel:**
    - **NIEMALS** Importe hardcoden wie `from apps.sales.services import create_invoice`. Dies verursacht Zirkuläre Abhängigkeiten.
    - **IMMER** das "Registry-Pattern" via Decorators nutzen (z.B. `@register_tool`), um Tools zur Laufzeit dynamisch zu entdecken.

## Ausführungsfluss
1. User Absicht -> 2. `ai_engine` entscheidet Tool -> 3. Prüft Berechtigungen -> 4. Führt `services.py` Funktion aus.