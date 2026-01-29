---
trigger: always_on
---

# Datenbankarchitektur & Modul-Isolation

## 1. Der "Modularer Monolith" Schreibschutz
**STRENGE EINSCHRÄNKUNG:** App-übergreifende Datenbankschreibzugriffe sind VERBOTEN.
- **Szenario:** Du bist in der `sales` App und musst den Bestand in der `inventory` App ändern.
- **Verboten:** NICHT `Inventory.objects.filter(...).update(...)` innerhalb des Sales-Codes nutzen.
- **Erforderlich:** Du MUSST die öffentliche Service-Funktion aufrufen: `apps.inventory.services.reserve_stock(...)`.
- **Warum:** Direkte DB-Schreibzugriffe umgehen die Validierungslogik und das Audit-Logging der Ziel-App.

## 2. Schema-Standards (PostgreSQL)
- **Primärschlüssel:** Immer UUIDs verwenden (erben von `core.models.BaseModel`). Niemals Integer Auto-Increment IDs benutzen.
- **Fremdschlüssel:**
    - Immer explizite `models.ForeignKey` Constraints nutzen (Keine "losen" IntegerFields für Beziehungen).
    - Immer `on_delete` Verhalten definieren (z.B. `PROTECT` oder `CASCADE`).
- **Benennung:** Bei Django-Standards bleiben (`appname_modelname`). Keine benutzerdefinierten `db_table` Namen verwenden, außer um Legacy-Kompatibilität zu erzwingen.