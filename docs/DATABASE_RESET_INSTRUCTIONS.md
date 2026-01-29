# Datenbank-Reset & Migrations-Anleitung

## Gelöstes Problem
Der `createsuperuser`-Befehl schlug fehl, weil:
- Das Custom User Model `email` als `USERNAME_FIELD` verwendet
- Der Standard-Django `UserManager` noch den `username`-Parameter erforderte
- Das Username-Feld noch im Datenbankschema vorhanden war

## Implementierte Lösung

### 1. CustomUserManager erstellt (`apps/users/managers.py`)
- Implementiert `create_user(email, password, **extra_fields)`
- Implementiert `create_superuser(email, password, **extra_fields)`
- Verwendet Email als eindeutigen Identifier
- Setzt automatisch `is_staff=True` und `is_superuser=True` für Superuser

### 2. User Model aktualisiert (`apps/users/models.py`)
- `username = None` gesetzt, um das Feld vollständig aus dem DB-Schema zu entfernen
- `objects = CustomUserManager()` hinzugefügt, um unseren Custom Manager zu verwenden
- Email ist jetzt das einzige Authentifizierungsfeld

---

## Anleitung zum Datenbank-Reset

Da sich das User-Model-Schema geändert hat (Username-Feld entfernt), muss die Datenbank zurückgesetzt werden:

### Schritt 1: Bestehende Datenbank löschen
```powershell
# SQLite-Datenbankdatei löschen
Remove-Item db.sqlite3 -ErrorAction SilentlyContinue
```

### Schritt 2: Alle Migrationsdateien löschen (außer __init__.py)
```powershell
# Migrationen in allen Apps löschen
Remove-Item apps\users\migrations\*.py -Exclude __init__.py -ErrorAction SilentlyContinue
Remove-Item apps\ai_engine\migrations\*.py -Exclude __init__.py -ErrorAction SilentlyContinue
Remove-Item apps\sales\migrations\*.py -Exclude __init__.py -ErrorAction SilentlyContinue
Remove-Item apps\inventory\migrations\*.py -Exclude __init__.py -ErrorAction SilentlyContinue
Remove-Item apps\finance\migrations\*.py -Exclude __init__.py -ErrorAction SilentlyContinue
Remove-Item core\migrations\*.py -Exclude __init__.py -ErrorAction SilentlyContinue
```

### Schritt 3: Neue Migrationen erstellen
```powershell
# Neue Migrationen für alle Apps erstellen
python manage.py makemigrations
```

Erwartete Ausgabe:
```
Migrations for 'users':
  apps\users\migrations\0001_initial.py
    - Create model User
```

### Schritt 4: Migrationen anwenden
```powershell
# Alle Migrationen anwenden, um das Datenbankschema zu erstellen
python manage.py migrate
```

Erwartete Ausgabe:
```
Operations to perform:
  Apply all migrations: admin, auth, contenttypes, sessions, users
Running migrations:
  Applying contenttypes.0001_initial... OK
  Applying contenttypes.0002_remove_content_type_name... OK
  Applying auth.0001_initial... OK
  ...
  Applying users.0001_initial... OK
```

### Schritt 5: Superuser erstellen
```powershell
# Dieser Befehl funktioniert jetzt mit Email statt Username
python manage.py createsuperuser
```

Sie werden aufgefordert einzugeben:
- **Email-Adresse**: (z.B. admin@example.com)
- **Vorname**: (z.B. Admin)
- **Nachname**: (z.B. User)
- **Passwort**: (zweimal eingeben)

---

## Verifizierung

Nach dem Erstellen des Superusers, Funktionalität überprüfen:

```powershell
# Development-Server starten
python manage.py runserver
```

Dann `http://127.0.0.1:8000/admin/` besuchen und einloggen mit:
- **Email**: Die eingegebene Email-Adresse
- **Passwort**: Das gesetzte Passwort

---

## Komplettes Reset-Script (All-in-One)

Wenn Sie alle Schritte auf einmal ausführen möchten, verwenden Sie dieses PowerShell-Script:

```powershell
# Kompletter Datenbank-Reset
Write-Host "Datenbank wird gelöscht..." -ForegroundColor Yellow
Remove-Item db.sqlite3 -ErrorAction SilentlyContinue

Write-Host "Alte Migrationen werden gelöscht..." -ForegroundColor Yellow
Remove-Item apps\users\migrations\*.py -Exclude __init__.py -ErrorAction SilentlyContinue
Remove-Item apps\ai_engine\migrations\*.py -Exclude __init__.py -ErrorAction SilentlyContinue
Remove-Item apps\sales\migrations\*.py -Exclude __init__.py -ErrorAction SilentlyContinue
Remove-Item apps\inventory\migrations\*.py -Exclude __init__.py -ErrorAction SilentlyContinue
Remove-Item apps\finance\migrations\*.py -Exclude __init__.py -ErrorAction SilentlyContinue
Remove-Item core\migrations\*.py -Exclude __init__.py -ErrorAction SilentlyContinue

Write-Host "Neue Migrationen werden erstellt..." -ForegroundColor Green
python manage.py makemigrations

Write-Host "Migrationen werden angewendet..." -ForegroundColor Green
python manage.py migrate

Write-Host "Datenbank-Reset abgeschlossen!" -ForegroundColor Green
Write-Host "Sie können jetzt ausführen: python manage.py createsuperuser" -ForegroundColor Cyan
```

---

## Änderungen im Datenbankschema

**Vorher (mit Username-Feld):**
```sql
CREATE TABLE users_user (
    id INTEGER PRIMARY KEY,
    username VARCHAR(150) UNIQUE,  -- ❌ Dieses Feld existierte
    email VARCHAR(254) UNIQUE,
    password VARCHAR(128),
    ...
);
```

**Nachher (Username entfernt):**
```sql
CREATE TABLE users_user (
    id INTEGER PRIMARY KEY,
    -- Username-Feld ist WEG ✅
    email VARCHAR(254) UNIQUE,
    password VARCHAR(128),
    ...
);
```

---

## Architektur-Compliance

✅ **Email-only Authentifizierung** - Username-Feld vollständig entfernt  
✅ **CustomUserManager** - Korrekter Manager für email-basierte User-Erstellung  
✅ **Type Hints** - Alle Methoden korrekt typisiert  
✅ **Docstrings** - Google-Style Dokumentation für AI Tool Discovery  
✅ **Validierung** - Korrekte Fehlerbehandlung für fehlende Email  

Die Implementierung entspricht nun vollständig der Architektur-Anforderung:
> "Identification via **Email** (not Username)" - `docs/architecture.md`
