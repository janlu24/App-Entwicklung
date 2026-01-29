# ISO 27001 Security Implementation Guide

**Zweck:** Technische Umsetzung der ISO 27001 Controls im Django-Code.
**Basis:** OWASP Top 10 & BSI Grundschutz als "State of the Art" Implementierung der ISO-Ziele.

---

## 1. Identität & Authentifizierung (Control A.5.15 / A.5.17)

### 1.1 Passwort-Richtlinien erzwingen
NIST-konforme Passwort-Regeln (Länge > Komplexität).

```python
# settings.py
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 12,  # ISO/BSI Empfehlung: Min 12 Zeichen
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
    # Eigener Validator gegen Breached Passwords (z.B. PwnedPasswords API) empfohlen!
]
```

### 1.2 Multi-Faktor-Authentifizierung (MFA)
Für privilegierte Accounts (Admins) zwingend erforderlich (Control A.8.2).

```python
# apps/core/models.py
class User(AbstractBaseUser):
    # ...
    is_mfa_enabled = models.BooleanField(default=False)
    
    def has_perm(self, perm, obj=None):
        # Admin-Rechte nur mit MFA!
        if self.is_superuser and not self.is_mfa_enabled:
            return False
        return super().has_perm(perm, obj)
```

### 1.3 Session Management
Schutz vor Session-Hijacking (Control A.8.20).

```python
# settings.py
SESSION_COOKIE_SECURE = True      # Nur über HTTPS
SESSION_COOKIE_HTTPONLY = True    # Kein JS-Zugriff (Schutz vor XSS)
SESSION_COOKIE_SAMESITE = 'Strict' # Schutz vor CSRF
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_AGE = 3600         # 1 Stunde Timeout (Auto-Logout)
```

---

## 2. Zugriffssteuerung (Access Control - A.5.15)

### 2.1 Role-Based Access Control (RBAC)
Niemals is_superuser im Business-Code prüfen! Immer spezifische Permissions nutzen.

```python
# apps/sales/views.py
from django.contrib.auth.mixins import PermissionRequiredMixin

class InvoiceDetailView(PermissionRequiredMixin, DetailView):
    model = Invoice
    # Gut: Explizite Permission
    permission_required = 'sales.view_invoice'
    
    def get_queryset(self):
        # Multi-Tenancy Isolation (A.8.3): Nur Daten des eigenen Mandanten!
        return Invoice.objects.filter(company=self.request.user.company)
```

---

## 3. Kryptographie (Control A.8.24)

### 3.1 Encryption at Rest (Datenbank)
Sensible Felder (IBAN, Steuer-ID) verschlüsselt speichern.

```python
# apps/finance/models.py
from django_cryptography.fields import encrypt

class BankAccount(BaseModel):
    # Automatische AES-256 Verschlüsselung
    iban = encrypt(models.CharField(max_length=34))
    bic = encrypt(models.CharField(max_length=11))
```

### 3.2 Encryption in Transit
Erzwingung von TLS (HTTPS).

```python
# settings.py
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000  # 1 Jahr
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
```

---

## 4. Secure Coding & Input Validation (Control A.8.28)

### 4.1 Schutz vor SQL-Injection
Niemals Raw-SQL mit String-Formatierung nutzen!

```python
# ❌ VERBOTEN (SQL Injection Vulnerability)
# query = f"SELECT * FROM users WHERE username = '{username}'"
# cursor.execute(query)

# ✅ ERLAUBT (Django ORM nutzt Parameterisierung)
user = User.objects.get(username=username)
```

## 4.2 Schutz vor XSS (Cross-Site Scripting)
Automatisches Escaping in Templates nutzen. Bei User-Content (HTML) Sanitizer verwenden.

```python
# apps/communication/utils.py
import bleach

def sanitize_html_input(content: str) -> str:
    """
    Reinigt HTML-Input von Usern (z.B. in E-Mails/Kommentaren).
    Entfernt <script> Tags etc.
    """
    allowed_tags = ['b', 'i', 'u', 'p', 'br']
    return bleach.clean(content, tags=allowed_tags, strip=True)
```

---

## 5. Betriebssicherheit & Logging (Control A.8.15)

### 5.1 Security Logging
Sicherheitsrelevante Ereignisse müssen protokolliert werden (aber ohne Passwörter!).

```python
# apps/core/signals.py
from django.contrib.auth.signals import user_login_failed
from django.dispatch import receiver
import logging

security_logger = logging.getLogger('security')

@receiver(user_login_failed)
def log_failed_login(sender, credentials, request, **kwargs):
    """
    Protokolliert fehlgeschlagene Logins (Brute-Force Detection).
    Control A.8.15
    """
    ip = get_client_ip(request)
    username = credentials.get('username', 'unknown')
    
    security_logger.warning(
        f"FAILED LOGIN: User '{username}' from IP {ip}",
        extra={'event_type': 'auth_failure', 'ip': ip}
    )
```

---

## 6. Datensicherung (Control A.8.12)

### 6.1 Backup-Strategie
Automatisierte, verschlüsselte Backups.

```python
# scripts/backup_db.sh
#!/bin/bash
# ISO 27001 A.8.12: Datensicherung

TIMESTAMP=$(date +%F_%H%M)
BACKUP_FILE="backup_$TIMESTAMP.sql.gz.enc"

# 1. Dump erstellen
# 2. Komprimieren
# 3. Verschlüsseln (mit Public Key des Backup-Servers)
pg_dump -h $DB_HOST -U $DB_USER $DB_NAME | gzip | openssl smime -encrypt -binary -aes256 -out $BACKUP_FILE backup_key.pem

# 4. Offsite-Transfer (z.B. S3 Object Lock für Ransomware-Schutz)
aws s3 cp $BACKUP_FILE s3://my-erp-backups-locked/ --storage-class GLACIER
```

---

## 7. Vulnerability Management (Control A.8.8)

### 7.1 Dependency Scanning
In die CI/CD Pipeline integrieren.

```python
# .github/workflows/security.yml
name: Security Scan
on: [push]

jobs:
  sast:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      # Python Safety Check (Prüft requirements.txt auf CVEs)
      - name: Check Dependencies
        run: |
          pip install safety
          safety check -r requirements.txt
          
      # Bandid (SAST für Python Code)
      - name: Bandit Scan
        run: |
          pip install bandit
          bandit -r . -f json -o bandit-report.json
```

---

## 8. Checkliste für Code-Reviews (Compliance)

Bevor Code gemerged wird, prüfe:

- [ ] **Secrets:** Keine API-Keys im Code! Nutzung von `.env` Dateien.
- [ ] **Debug:** `DEBUG = False` in Produktion.
- [ ] **Updates:** Dependencies regelmäßig aktualisieren (Patch-Management).
- [ ] **Review:** 4-Augen-Prinzip bei jedem Merge-Request (Code Review).

---