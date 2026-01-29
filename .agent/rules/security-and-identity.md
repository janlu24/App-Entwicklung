---
trigger: always_on
---

# Identity, Auth & Sicherheits-Richtlinien

## 1. Custom User Model Strategie (Strikt)
- **Basis:** Erben von `AbstractBaseUser` + `PermissionsMixin`.
- **Identifikation:** Authentifizierung nur via **Email**.
- **Einschränkung:** Du MUSST `username = None` im Model setzen, um das Feld komplett aus dem Datenbankschema zu entfernen.
- **Manager:** Implementiere einen `CustomUserManager`, der `create_user` und `create_superuser` mit Email als Identifier handhabt.

## 2. Trennung der Zuständigkeiten: User vs. Employee
**Strenge Datenmodellierungs-Regel:**
- **User Model (`apps.users.models.User`):** Enthält NUR Authentifizierungsdaten (Email, Passwort-Hash, is_active, letzter Login).
- **Employee Model (`apps.users.models.Employee`):** Enthält HR-Daten (Abteilung, Gehalt, Jobtitel).
- **Verknüpfung:** Nutze ein `OneToOneField` von Employee zu User.
- **Warum:** Admins brauchen User-Accounts, sind aber vielleicht keine Angestellten. System-Agenten brauchen User, haben aber kein Gehalt.

## 3. RBAC (Role-Based Access Control)
- **Regel:** Weise Berechtigungen niemals direkt einem `User` zu.
- **Vorgabe:** Weise Berechtigungen an **Gruppen** (Rollen) wie "Sales Manager" oder "Buchhalter" zu. Weise User diesen Gruppen zu.

## 4. KI-Schutzmechanismen (Security First)
- **Pre-Execution Check:** Der KI-Engine ist es VERBOTEN, ein Tool auszuführen, ohne vorher zu prüfen:
  `user.has_perm('app_label.action_model')`
- **Umfang:** Diese Prüfung muss *innerhalb* des Tool-Wrappers (Service Layer) geschehen, nicht nur in der UI.