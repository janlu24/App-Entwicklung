---
trigger: always_on
---

# Operationale Richtlinien für Agenten (Meta-Instruktionen)

## 1. Die "Service First"-Regel
**Reflex:** Bevor du Logik in einer View oder einem AI-Tool schreibst, prüfe `services.py`.
- **Einschränkung:** Geschäftslogik MUSS dort leben, damit sie als Tool für die AI Engine exponiert werden kann.
- **Aktion:** Wenn die Service-Funktion nicht existiert, erstelle sie zuerst. Packe Logik niemals in Views.

## 2. Keine "Magischen" Strings
- **Regel:** Hardcode keine Status-Strings wie "paid" oder "open".
- **Lösung:** Nutze Django `TextChoices` Klassen in `models.py`.

## 3. Refactoring-Mandat
- **Trigger:** Wenn du Code siehst, der das "Service Layer" Pattern verletzt (z.B. Logik in Views), während du an einer Datei arbeitest.
- **Aktion:** Refactoriziere es sofort, bevor du neue Features hinzufügst. Hinterlasse den Code sauberer, als du ihn vorgefunden hast.

## 4. AI Sicherheits-Check (Self-Correction)
- **Frage:** Wenn du ein neues AI-Tool erstellst, frage dich explizit: *"Prüft dieses Tool User-Berechtigungen?"*
- **Mandat:** Falls nicht, füge einen Berechtigungs-Check (z.B. `user.has_perm(...)`) ganz am Anfang hinzu.

## 5. Plan-Execute Muster
**Prozess für komplexe Features:**
1. **Plan:** Beschreibe zuerst die Datenbankänderungen und Service-Signaturen im Chat.
2. **Wait:** Warte auf User-Bestätigung.
3. **Execute:** Generiere den vollen Implementierungscode erst, nachdem der User dem Plan explizit zugestimmt hat.