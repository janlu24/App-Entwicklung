# ISO 27001 Compliance Summary - ERP System

## Zweck
Zusammenfassung der relevanten Sicherheitsanforderungen basierend auf den Zielen der **ISO/IEC 27001:2022** (Information Security Management System).
Diese Datei übersetzt die abstrakten "Controls" der Norm in konkrete Anforderungen für die Software-Architektur.

**Fokus:** Anhang A (Informationssicherheitsmaßnahmen)
**Zielgruppe:** Security Architects, CISO, Lead Developers

---

## Struktur der Maßnahmen (ISO 27001:2022)

Die Maßnahmen sind in 4 Themenbereiche unterteilt:

1. **Organisatorisch (5.x)** - Richtlinien, Rollen, Identitätsmanagement
2. **Personenbezogen (6.x)** - Schulung, Remote Work, Screening
3. **Physisch (7.x)** - Zutrittsschutz (für SaaS-Provider/Rechenzentrum relevant)
4. **Technologisch (8.x)** - Der Fokus für die Software-Entwicklung!

---

## Relevante Controls für die ERP-Entwicklung

### A.5 Organisatorische Maßnahmen

#### A.5.15 Zugriffskontrolle (Access Control)
**Anforderung:**
- Zugriff auf Informationen und Verarbeitungseinrichtungen muss basierend auf geschäftlichen Anforderungen eingeschränkt werden.
- Prinzip der minimalen Rechte (**Least Privilege**).
- Trennung von Aufgaben (**Segregation of Duties**).

#### A.5.17 Authentifizierungsinformationen
**Anforderung:**
- Sichere Verwaltung von Passwörtern und Secrets.
- Erzwingung von Komplexität und Rotation (wo sinnvoll).
- Schutz vor Brute-Force-Angriffen.

### A.8 Technische Maßnahmen (Der Kern)

#### A.8.2 Privilegierte Zugriffsrechte (PAM)
**Anforderung:**
- Die Nutzung von Admin-Accounts ("Superuser") muss streng eingeschränkt und überwacht werden.
- Keine ständige Arbeit mit Admin-Rechten.

#### A.8.3 Informationszugriffsbeschränkung
**Anforderung:**
- Isolation von Mandanten (Multi-Tenancy Security).
- Netzwerk-Segmentierung (Datenbank nicht öffentlich erreichbar).

#### A.8.8 Verwaltung technischer Schwachstellen
**Anforderung:**
- Informationen über technische Schwachstellen (CVEs) müssen eingeholt und Systeme gepatcht werden.
- **Dependency Scanning** für Third-Party-Libraries.

#### A.8.10 Löschen von Informationen
**Anforderung:**
- Daten müssen sicher gelöscht werden, wenn sie nicht mehr benötigt werden (Secure Delete).
- Überschreiben statt nur "Freigeben" des Speicherplatzes (wichtig für File-Uploads).

#### A.8.20 Netzwerksicherheit
**Anforderung:**
- Schutz der Daten im Netzwerk (TLS/SSL).
- Absicherung von API-Endpunkten.

#### A.8.24 Kryptographie
**Anforderung:**
- Einsatz kryptographischer Maßnahmen zum Schutz der Vertraulichkeit, Authentizität und Integrität.
- **Encryption at Rest** (Datenbank, Backups).
- **Encryption in Transit** (HTTPS, TLS 1.3).
- Sicheres Schlüsselmanagement (KMS/HSM).

#### A.8.25 Secure Development Lifecycle (SSDLC)
**Anforderung:**
- Regeln für sichere Entwicklung (Secure Coding Guidelines).
- Trennung von Entwicklungs-, Test- und Produktionsumgebungen (A.8.31).
- Sicherheits-Tests (SAST/DAST) in der CI/CD-Pipeline.

#### A.8.28 Sicheres Coding (Secure Coding)
**Anforderung:**
- Anwendung von Prinzipien wie OWASP Top 10.
- Input Validation (Eingabevalidierung) für alle Daten.
- Output Encoding (Verhinderung von XSS).

---

## Integration in das ERP

**Wie setzen wir das um?**
Siehe **[iso27001_security_implementation.md](./iso27001_security_implementation.md)** für Code-Beispiele und technische Patterns.

**Referenzen:**
- OWASP Top 10 (2021/2025)
- BSI IT-Grundschutz (Baustein APP.3.1 Webanwendungen)
- NIST SP 800-63 (Digital Identity Guidelines)