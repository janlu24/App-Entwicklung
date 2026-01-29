# Übersicht der Compliance-Dokumentation

## Zweck
Dieses Dokument dient als Navigationshilfe für die gesamte Compliance-Dokumentation im Verzeichnis `.agent/knowledge`. Es erklärt den Zweck, die Zielgruppe und die Beziehungen zwischen den verschiedenen Dokumenten.

---

## 📚 Dokumentenstruktur & Hierarchie

```
Rechtliche Grundlagen (WARUM)
├── hgb_compliance_summary.md          [Handelsrecht - Fundament]
├── gobd_official_summary.md           [Steuerliches Buchführungsrecht - Offizielle Texte]
├── gobd_compliance_summary.md         [Steuerliches Buchführungsrecht - Praktische Zusammenfassung]
├── dsgvo_compliance_summary.md        [Datenschutz - Prinzipien]
└── iso27001_compliance_summary.md     [IT-Sicherheit - ISO 27001 Controls]

        ↓ implementiert

Implementierungsleitfäden (WIE)
├── gobd_implementation_guide.md        [ZENTRALER Entwickler-Leitfaden - Code-Beispiele]
├── dsgvo_privacy_by_design.md          [Datenschutz-Architektur - Design Patterns]
└── iso27001_security_implementation.md [Security Hardening - Django/Python]

        ↓ spezialisiert

Spezialisierte Checklisten & Fachlogik
├── ao_integration_checklist.md        [Steuer-Spezifisch - ELSTER, Aufbewahrung]
├── ustg_vat_logic.md                  [Steuer-Logik - § 13b, USt-ID, Rechnungspflicht]
└── payment_sepa_standards.md          [Zahlungsverkehr - ISO 20022, Mandate]
```

---

## 📘 Dokumentenbeschreibungen

### 1. Rechtliche Grundlagen (WARUM)

Diese Dokumente erklären, **warum** bestimmte Anforderungen existieren und bieten den rechtlichen Kontext.

#### 📘 `hgb_compliance_summary.md`
- **Typ**: Rechtliche Grundlage
- **Quelle**: Handelsgesetzbuch (HGB)
- **Zweck**: Handelsrechtliche Grundanforderungen an Buchführung und Bilanzierung
- **Zielgruppe**: Entwickler, Business Analysten, Rechtsabteilung
- **Kernthemen**:
  - §§ 238-239: Buchführungspflicht, Unveränderbarkeit
  - §§ 240-241: Inventur (inkl. permanente Inventur § 241 Abs. 2)
  - §§ 242-263: Jahresabschluss
  - § 256: Verbrauchsfolgeverfahren (FIFO/LIFO)
  - § 256a: Währungsumrechnung
  - § 257: Aufbewahrungsfristen (10 Jahre, dynamische Verlängerung bei Prüfungen)
  - § 267/267a: Größenklassen (aktualisiert April 2024: 7,5 Mio. € / 15 Mio. € für kleine KapG)
- **Wann zu nutzen**:
  - Als Einstieg in das deutsche Bilanzrecht
  - Als Referenz für Aufbewahrungsfristen und Grundsätze ordnungsmäßiger Buchführung (GoB)
  - Zum Verständnis der rechtlichen Basis der GoBD
- **Beziehung**: **Fundament für alle anderen Compliance-Dokumente**

#### 📜 `gobd_official_summary.md`
- **Typ**: Rechtliche Grundlage (Steuerlich)
- **Quelle**: BMF-Schreiben 2019 + Änderung 2024
- **Zweck**: Offizielle Anforderungen der Finanzverwaltung an elektronische Buchführungssysteme
- **Zielgruppe**: Entwickler, Compliance Officer, Steuerberater
- **Kernthemen**:
  - Die 6 Grundprinzipien (Nachvollziehbarkeit, Vollständigkeit, Richtigkeit, etc.)
  - Anforderungen an elektronische Buchführung
  - Datenzugriff (Z1, Z2, Z3)
  - BMF 2024 Updates (Kontoart, Kontotyp)
- **Wann zu nutzen**:
  - Verständnis der offiziellen GoBD-Anforderungen
  - Referenz für Betriebsprüfungen
  - Verifizierung der Compliance mit BMF-Richtlinien
- **Beziehung**: Erweitert das **HGB** um technische Anforderungen für elektronische Systeme

#### ✅ `gobd_compliance_summary.md`
- **Typ**: Praktische Zusammenfassung
- **Quelle**: Abgeleitet aus `gobd_official_summary.md`
- **Zweck**: Komprimierte, praktische Checkliste für GoBD-Compliance
- **Zielgruppe**: Entwickler, Projektmanager
- **Kernthemen**:
  - Schnellreferenz der 6 GoBD-Prinzipien
  - Anforderungen an Dokumenten-Management-Systeme (DMS)
  - Praktische Umsetzungstipps
- **Wann zu nutzen**:
  - Schnellreferenz während der Entwicklung
  - Checkliste für Feature-Vollständigkeit
  - DMS-Implementierung
- **Beziehung**: Praktischer Begleiter zu `gobd_official_summary.md`

#### 🛡️ `dsgvo_compliance_summary.md`
- **Typ**: Rechtliche Grundlage (Datenschutz)
- **Quelle**: Datenschutz-Grundverordnung (DSGVO)
- **Zweck**: Datenschutzprinzipien und -anforderungen
- **Zielgruppe**: Entwickler, Datenschutzbeauftragter, Rechtsabteilung
- **Kernthemen**:
  - Rechtsgrundlagen der Verarbeitung (Art. 6 DSGVO)
  - Datenminimierung
  - Betroffenenrechte (Art. 15-22)
  - Technische Maßnahmen (Art. 32)
  - Konfliktlösung: DSGVO vs. HGB/AO Aufbewahrung
- **Wann zu nutzen**:
  - Implementierung von personenbezogenen Features
  - Umgang mit Löschanfragen
  - Lösung des Konflikts Löschung vs. Aufbewahrung
- **Beziehung**: **Konflikt mit HGB/AO** bezüglich Aufbewahrungsfristen (gelöst durch Sperrung)

#### 🔐 `iso27001_compliance_summary.md`
- **Typ**: Sicherheitsstandard
- **Quelle**: ISO/IEC 27001:2022 (Anhang A)
- **Zweck**: Anforderungen an die Informationssicherheit (ISMS)
- **Zielgruppe**: CISO, Security Architect, Lead Developer
- **Kernthemen**:
  - A.5: Zugriffskontrolle (RBAC, MFA)
  - A.8: Technische Maßnahmen (Verschlüsselung, Secure Coding, Logging)
  - A.12: Betriebssicherheit (Backups, Schwachstellenmanagement)
- **Wann zu nutzen**:
  - Definition von Sicherheitsanforderungen für neue Features
  - Vorbereitung auf Sicherheits-Audits
  - Nachweis von "Stand der Technik" (wichtig für DSGVO Art. 32)
- **Beziehung**: Ergänzt die DSGVO (Datensicherheit) und GoBD (Unveränderbarkeit) um technische Maßnahmen.

---

### 2. Implementierungsleitfäden (WIE)

Diese Dokumente erklären, **wie** die rechtlichen Anforderungen in Code umgesetzt werden.

#### 🔧 `gobd_implementation_guide.md` ⭐ **ZENTRALER LEITFADEN**
- **Typ**: Entwickler-Implementierungsleitfaden
- **Quelle**: Synthese aus HGB + GoBD + AO
- **Zweck**: **Primäre technische Referenz** für Compliance in Django/Python
- **Zielgruppe**: Backend-Entwickler
- **Kernthemen**:
  - `BaseModel` Implementierung (Audit-Felder, Soft Delete)
  - `AuditLog` Model (Änderungsprotokollierung)
  - `JournalEntry` Model (mit BMF 2024 Feldern)
  - `Document` Model (Aufbewahrung, Checksummen)
  - Service-Layer Beispiele
  - Z3 Datenexport (Datenüberlassung nach § 147 Abs. 6 AO)
  - Teststrategien
- **Wann zu nutzen**:
  - **HIER STARTEN** für alle Compliance-Implementierungen
  - Referenz beim Programmieren
  - Code-Review Checkliste
  - Schreiben von Tests
- **Beziehung**:
  - Implementiert **HGB** (Fundament)
  - Implementiert **GoBD** (technische Specs)
  - Integriert **AO** (steuerliche Anforderungen)
  - Löst **DSGVO** Konflikte

#### 🛡️ `dsgvo_privacy_by_design.md`
- **Typ**: Architektur-Leitfaden
- **Quelle**: DSGVO Privacy-by-Design Prinzipien
- **Zweck**: Architektur-Patterns für Datenschutz
- **Zielgruppe**: Entwickler, Architekten
- **Kernthemen**:
  - **Art. 6: Hierarchie der Rechtsgrundlagen** ⭐ **Vertrag/Rechtliche Pflicht primär für ERP, NICHT Einwilligung!**
  - **Art. 15: One-Click Datenexport** ⭐ **KRITISCH** - Aggregierter Export über alle Module
  - **Art. 17 vs. Art. 18:** Löschung vs. Einschränkung (HGB Konfliktlösung)
  - **Art. 28: AVV (Auftragsverarbeitungsvertrag)** ⭐ **FÜR SAAS** - Automatisierte AVV
  - **Art. 30: VVT-Export** - Vorbefüllt für Kunden
  - **Art. 5/32: Testdaten-Anonymisierung** ⭐ **DEVELOPER** - Keine Echtdaten auf Staging
  - Art. 25: Privacy by Default
  - Art. 7: Einwilligungs-Protokollierung (IP, Timestamp, Double-Opt-In)
  - DSFA (Datenschutz-Folgenabschätzung)
  - Data Breach Management
- **Wann zu nutzen**:
  - Design neuer Features mit personenbezogenen Daten
  - Implementierung von Benutzerprofil-Features
  - KI/ML Datenverarbeitung
  - Umgang mit Löschanfragen
- **Beziehung**: Ergänzt `gobd_implementation_guide.md` für datenschutzspezifische Features

#### 🛡️ `iso27001_security_implementation.md`
- **Typ**: Technischer Security-Guide
- **Quelle**: OWASP Top 10, BSI Grundschutz, ISO 27001
- **Zweck**: Härtung der Anwendung (Security Hardening)
- **Zielgruppe**: Backend-Entwickler, DevOps
- **Kernthemen**:
  - **Identität**: Sichere Passwörter, Session-Timeouts, MFA-Implementierung
  - **Kryptographie**: Verschlüsselung von DB-Feldern (At-Rest) und Transport (TLS)
  - **Secure Coding**: Schutz vor SQL-Injection, XSS (Input Validation)
  - **Logging**: Security-Events protokollieren (Failed Logins)
  - **Backup**: Verschlüsselte Backups und Restore-Tests
- **Wann zu nutzen**:
  - Bei der Implementierung von Authentifizierung/Autorisierung
  - Beim Umgang mit sensiblen Daten (Bankdaten, Passwörter)
  - Einrichtung der CI/CD Pipeline (Security Scans)

---

### 3. Spezialisierte Checklisten & Fachlogik

Diese Dokumente fokussieren auf spezifische Compliance-Bereiche.

#### 🔒 `ao_integration_checklist.md`
- **Typ**: Steuerspezifische Checkliste
- **Quelle**: Abgabenordnung (AO)
- **Zweck**: Steuerliche Anforderungen über die Buchführung hinaus
- **Zielgruppe**: Entwickler, Steuerberater
- **Kernthemen**:
  - **§ 147 Abs. 6: Z3 Datenexport (Datenüberlassung nach § 147 Abs. 6 AO)** ⭐ **KRITISCH** - Pflicht für Betriebsprüfungen
  - § 146 Abs. 2a/2b: Cloud-Hosting Anforderungen
  - § 150: ELSTER-Schnittstelle
  - § 147: Berechnung der Aufbewahrungsfristen
  - § 146a: KassenSichV (TSE für Kassensysteme)
  - § 30: Steuergeheimnis
  - § 90: Verrechnungspreise
  - § 93c: Mitwirkungspflichten
  - § 14 UStG: E-Rechnungspflicht (Wachstumschancengesetz)
- **Wann zu nutzen**:
  - Implementierung von Steuererklärungs-Features
  - Berechnung von Löschfristen
  - Zugriffskontrolle für Steuerdaten
  - Verrechnungspreisdokumentation
- **Beziehung**: Erweitert `gobd_implementation_guide.md` um steuerspezifische Features

#### 💶 `ustg_vat_logic.md`
- **Typ**: Fachliche Logik & Algorithmen
- **Quelle**: Umsatzsteuergesetz (UStG), MwStSystRL (EU)
- **Zweck**: Definition der "Tax Determination Engine" (Steuerfindung)
- **Zielgruppe**: Backend-Entwickler, Product Owner
- **Kernthemen**:
  - Steuerfindung: Wann 19%, wann 0% (innergem. Lieferung), wann Reverse Charge?
  - § 14 UStG: Zwingende Pflichtangaben auf Rechnungen
  - USt-ID Prüfung (VIES) und Dokumentation
- **Wann zu nutzen**:
  - Bei der Entwicklung der Rechnungsstellung (Invoicing-Engine)
  - Beim Design der Produkt-Stammdaten (Steuerschlüssel)
- **Beziehung**: Liefert die Logik für die steuerliche Korrektheit, die die AO dann prüft.

#### 🏦 `payment_sepa_standards.md`
- **Typ**: Technische Spezifikation
- **Quelle**: ISO 20022, DFÜ-Abkommen der Deutschen Kreditwirtschaft
- **Zweck**: Generierung valider XML-Zahlungsdateien für Banken
- **Zielgruppe**: Payment-Developers
- **Kernthemen**:
  - Formate: `pain.001` (Überweisung) und `pain.008` (Lastschrift)
  - Mandatsverwaltung: Sequenzlogik (FRST/RCUR) und Fristen
  - Validierung: IBAN-Prüfsummen und Gläubiger-IDs
- **Wann zu nutzen**:
  - Implementierung des "Zahllauf"-Features
  - Einrichtung des Lastschrift-Einzugs für Kunden
- **Beziehung**: Setzt die banktechnischen Standards um, damit Forderungen/Verbindlichkeiten beglichen werden.

---

## 🗺️ Navigationshilfe

### "Ich möchte die rechtlichen Anforderungen verstehen"
1. **Start**: `hgb_compliance_summary.md` (Handelsrechtliches Fundament)
2. **Dann**: `gobd_official_summary.md` (Steuerliche Buchführungsregeln)
3. **Auch**: `dsgvo_compliance_summary.md` (Datenschutz)

### "Ich möchte Compliance-Features implementieren"
1. **Start**: `gobd_implementation_guide.md` ⭐ (Zentraler Entwickler-Guide)
2. **Für Datenschutz**: `dsgvo_privacy_by_design.md`
3. **Für Steuern**: `ao_integration_checklist.md`

### "Ich brauche eine schnelle Referenz"
- **GoBD Checkliste**: `gobd_compliance_summary.md`
- **Aufbewahrungsfristen**: `hgb_compliance_summary.md` (§ 257)
- **Datenlöschung**: `dsgvo_privacy_by_design.md` (Art. 17)

### "Ich arbeite an einem spezifischen Feature"

| Feature | Primäres Dokument | Zusätzliche Referenzen |
|---------|-------------------|-----------------------|
| **Buchhaltung/Fibu** | `gobd_implementation_guide.md` | `hgb_compliance_summary.md` (§§ 238-239) |
| **Buchungssätze** | `gobd_implementation_guide.md` (Abschnitt 2.1) | `hgb_compliance_summary.md` (§ 238) |
| **Dokumenten-Management** | `gobd_implementation_guide.md` (Abschnitt 3) | `hgb_compliance_summary.md` (§ 257) |
| **Benutzerprofile** | `dsgvo_privacy_by_design.md` | `gobd_implementation_guide.md` (BaseModel) |
| **Datenlöschung** | `dsgvo_privacy_by_design.md` (Art. 17) | `hgb_compliance_summary.md` (Konflikt § 257) |
| **Steuererklärung** | `ao_integration_checklist.md` (ELSTER) | `gobd_implementation_guide.md` (Z3 Export) |
| **Z3 Datenexport (Datenüberlassung nach § 147 Abs. 6 AO)** ⭐ | `ao_integration_checklist.md` (Abschnitt 2.5)| `ao_compliance_summary.md` (§ 147 Abs. 6) |
| **Cloud Hosting** ⭐ | `ao_integration_checklist.md` | `ao_compliance_summary.md` (§ 146 Abs. 2a/2b) | 
| **One-Click Datenexport** ⭐ | `dsgvo_compliance_summary.md` (Art. 15) | `dsgvo_privacy_by_design.md` |
| **AVV für SaaS** ⭐ | `dsgvo_compliance_summary.md` (Art. 28) | `dsgvo_privacy_by_design.md` |
| **Testdaten-Anonymisierung** ⭐ | `dsgvo_compliance_summary.md` (Art. 5/32) | `dsgvo_privacy_by_design.md` |
| **VVT-Export** | `dsgvo_compliance_summary.md` (Art. 30) | `dsgvo_privacy_by_design.md` |
| **Aufbewahrungsfristen** | `hgb_compliance_summary.md` (§ 257) | `ao_integration_checklist.md` (§ 147 AO) |
| **Audit Trail** | `gobd_implementation_guide.md` (Abschnitt 1.2) | `hgb_compliance_summary.md` (§ 239 Abs. 3) |
| **Inventur** | `hgb_compliance_summary.md` (§§ 240-241) | `gobd_implementation_guide.md` (Abschnitt 4) |
| **Permanente Inventur** ⭐ | `hgb_compliance_summary.md` (§ 241 Abs. 2) | `gobd_implementation_guide.md` (Phase 3.5) |
| **FIFO/LIFO Bewertung** ⭐ | `hgb_compliance_summary.md` (§ 256) | `gobd_implementation_guide.md` (Phase 3.5) |
| **Währungsumrechnung** ⭐ | `hgb_compliance_summary.md` (§ 256a) | `gobd_implementation_guide.md` (Phase 2) |
| **Jahresabschluss** | `hgb_compliance_summary.md` (§§ 242-263) | `gobd_implementation_guide.md` (Abschnitt 2) |
| **Größenklassen** ⭐ | `hgb_compliance_summary.md` (§ 267/267a April 2024) | `gobd_implementation_guide.md` (Phase 4) |
| **E-Rechnung (B2B/ZUGFeRD)** ⭐ | `ao_integration_checklist.md` (§ 14 UStG) | `hgb_compliance_summary.md` (Belegpflicht) |
| **Login / Auth / MFA** ⭐ | `iso27001_security_implementation.md` | `dsgvo_privacy_by_design.md` (Zugriffsschutz) |
| **Verschlüsselung (DB)** ⭐ | `iso27001_security_implementation.md` | `dsgvo_privacy_by_design.md` (Art. 32) |
| **Backup & Restore** ⭐ | `iso27001_security_implementation.md` | `gobd_official_summary.md` (Datensicherheit) |
| **Logging (Security)** ⭐ | `iso27001_security_implementation.md` | `gobd_implementation_guide.md` (Audit Log) |
| **CI/CD Security Scan** ⭐ | `iso27001_security_implementation.md` | `iso27001_compliance_summary.md` (A.8.8) |
| **Rechnungserstellung** | `ustg_vat_logic.md` | `gobd_implementation_guide.md` (Unveränderbarkeit) |
| **Lastschriften / Überweisungen** | `payment_sepa_standards.md` | `iso27001_security_implementation.md` (Bankdaten-Schutz) |
| **USt-ID Prüfung** | `ustg_vat_logic.md` | `ao_integration_checklist.md` (Dokumentationspflicht) |

---

## 🔄 Rechtliche Hierarchie & Beziehungen

### Hierarchie
```
HGB (Handelsgesetzbuch)
  ├── Fundament für alle Buchführungsregeln
  └── Definiert Grundprinzipien
      ↓
GoBD (Steuerliches Buchführungsrecht)
  ├── Erweitert HGB für elektronische Systeme
  └── Fügt technische Anforderungen hinzu
      ↓
AO (Abgabenordnung)
  ├── Steuerspezifische Erweiterungen
  └── ELSTER, Aufbewahrung, Mitwirkung
      ↓
DSGVO (Datenschutz)
  ├── Parallele Anforderung
  └── Konflikte gelöst durch Sperrung (Blocking)
```

### Konflikte & Lösungen

| Konflikt | HGB/AO Anforderung | DSGVO Anforderung | Lösung |
|----------|-------------------|-------------------|--------|
| **Aufbewahrung** | 10 Jahre (§ 257 HGB, § 147 AO) | Recht auf Löschung (Art. 17) | **Sperrung** statt Löschung |
| **User-Löschung** | Darf Rechnungsdaten nicht löschen | Muss auf Anfrage löschen | User sperren, Daten minimieren, Löschung nach Frist |
| **Audit Logs** | Muss Änderungshistorie behalten | Datenminimierung | Logs behalten, nach Frist anonymisieren |

**Implementierung**: Siehe `dsgvo_privacy_by_design.md` (Abschnitt: "AO/DSGVO Konfliktlösung")

---

## 📋 Compliance Checkliste nach Modul

### Core Modul
- [ ] `BaseModel` implementiert → `gobd_implementation_guide.md` (Abschnitt 1.1)
- [ ] `AuditLog` implementiert → `gobd_implementation_guide.md` (Abschnitt 1.2)
- [ ] Soft Delete für DSGVO → `dsgvo_privacy_by_design.md`

### Finance Modul
- [ ] `JournalEntry` mit BMF 2024 Feldern → `gobd_implementation_guide.md` (Abschnitt 2.1)
- [ ] Berechnung Aufbewahrungsfristen → `hgb_compliance_summary.md` (§ 257)
- [ ] Z3 Export (Datenüberlassung nach § 147 Abs. 6 AO) → `gobd_implementation_guide.md` (Abschnitt 5.1)

### Dokumenten Modul
- [ ] `Document` Model mit Checksummen → `gobd_implementation_guide.md` (Abschnitt 3.1)
- [ ] 10 Jahre Aufbewahrung → `hgb_compliance_summary.md` (§ 257)
- [ ] OCR und Indexierung → `gobd_compliance_summary.md`

### Users Modul
- [ ] Privacy by Default → `dsgvo_privacy_by_design.md` (Art. 25)
- [ ] Betroffenenrechte (Export, Löschung) → `dsgvo_privacy_by_design.md` (Art. 15-17)
- [ ] Sperrmechanismus (Blocking) → `dsgvo_privacy_by_design.md` (Konfliktlösung)

### Tax Modul
- [ ] ELSTER Schnittstelle → `ao_integration_checklist.md` (Abschnitt 1)
- [ ] Steuergeheimnis → `ao_integration_checklist.md` (Abschnitt 3)
- [ ] Verrechnungspreise → `ao_integration_checklist.md` (Abschnitt 4)

---

## 🎯 Schnellreferenz: Wichtige Paragraphen

### HGB (Handelsgesetzbuch)
- **§ 238**: Buchführungspflicht
- **§ 239**: Sprache, Unveränderbarkeit, Abkürzungen
- **§ 240-241**: Inventur (inkl. permanente Inventur)
- **§ 242-263**: Jahresabschluss
- **§ 256**: FIFO/LIFO Bewertungsmethoden
- **§ 256a**: Währungsumrechnung
- **§ 257**: Aufbewahrungsfristen (10 Jahre)
- **§ 267/267a**: Größenklassen

### GoBD (Steuerliche Verwaltungsanweisung)
- **Rz. 30-35**: Nachvollziehbarkeit
- **Rz. 57-68**: Vollständigkeit
- **Rz. 90-94**: Journal-Anforderungen
- **Rz. 102-108**: Unveränderbarkeit
- **Rz. 119-130**: Elektronische Aufbewahrung
- **Rz. 165-170**: Datenzugriff (Z1, Z2, Z3)

### AO (Abgabenordnung)
- **§ 140**: Buchführungs- und Aufzeichnungspflichten
- **§ 145**: Allgemeine Anforderungen
- **§ 146**: Ordnungsvorschriften
- **§ 147**: Aufbewahrungsvorschriften
- **§ 150**: Datenübermittlung (ELSTER)

### DSGVO (Datenschutz)
- **Art. 6**: Rechtmäßigkeit der Verarbeitung
- **Art. 15**: Auskunftsrecht
- **Art. 17**: Recht auf Löschung
- **Art. 25**: Technikgestaltung (Privacy by Design)
- **Art. 32**: Sicherheit der Verarbeitung
- **Art. 33-34**: Meldung von Datenschutzverletzungen

---

## 🚀 Erste Schritte

### Für neue Entwickler
1. Lies `hgb_compliance_summary.md` (30 Min) - Verstehe das rechtliche Fundament
2. Lies `gobd_implementation_guide.md` (60 Min) - Lerne Implementierungsmuster
3. Überfliege `dsgvo_privacy_by_design.md` (20 Min) - Verstehe Datenschutzanforderungen
4. Markiere diese Übersicht für schnelle Navigation

### Für erfahrene Entwickler
- Nutze `gobd_implementation_guide.md` als primäre Referenz
- Konsultiere spezialisierte Dokumente nach Bedarf
- Nutze diese Übersicht um schnell das richtige Dokument zu finden

### Für Compliance-Reviews
1. Prüfe `hgb_compliance_summary.md` (Checkliste am Ende)
2. Prüfe `gobd_implementation_guide.md` (Abschnitt 7: Roadmap)
3. Prüfe `ao_integration_checklist.md` (Alle Abschnitte)
4. Prüfe `dsgvo_privacy_by_design.md` (Checkliste am Ende)

---

## 📝 Dokumentenpflege

### Aktualisierungsfrequenz
- **Rechtliche Grundlagen**: Update bei Gesetzesänderungen (selten)
- **Implementierungsleitfaden**: Update während Entwicklung (lebendes Dokument)
- **Checklisten**: Update wenn Features fertiggestellt sind

### Versionierung
Alle Dokumente sind in Git versioniert. Prüfe die Commit-Historie für Änderungen.

### Externes Review
- **Steuerberater**: Review `ao_integration_checklist.md` und `gobd_implementation_guide.md`
- **Datenschutzbeauftragter**: Review `dsgvo_privacy_by_design.md`
- **Rechtsabteilung**: Review `hgb_compliance_summary.md`
- **CISO / IT-Sicherheit**: Review `iso27001_security_implementation.md` und `iso27001_compliance_summary.md`

---

## 📞 Support & Fragen

### Interne Ressourcen
- **Implementierungsfragen**: Siehe `gobd_implementation_guide.md` (Abschnitt 9: Nächste Schritte)
- **Rechtliche Fragen**: Konsultiere `hgb_compliance_summary.md` zuerst
- **Datenschutzfragen**: Siehe `dsgvo_privacy_by_design.md`

### Externe Ressourcen
- **Steuerberater**: Für ELSTER, Aufbewahrung, steuerliche Fragen
- **Datenschutzbeauftragter**: Für DSGVO Compliance
- **Rechtsanwalt**: Für HGB Interpretation

---

## Dokumenten-Metadaten

- **Erstellt**: 2026-01-27
- **Zweck**: Navigationshilfe für Compliance-Dokumentation
- **Gepflegt von**: Development Team
- **Review-Zyklus**: Quartalsweise oder bei Gesetzesänderungen
