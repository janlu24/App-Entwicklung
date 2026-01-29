# AO (Abgabenordnung) - Compliance Summary

## Zweck
Zusammenfassung der wichtigsten Compliance-Anforderungen aus der Abgabenordnung (AO) für das ERP-System.

**Stand:** 2025/2026  
**Zielgruppe:** Entwickler, Compliance Officers, Steuerberater

---

## Wichtigste Compliance-Anforderungen

### 1. Steuergeheimnis (§ 30 AO)
**Pflicht:** Amtsträger und alle mit steuerlichen Daten arbeitenden Personen müssen das Steuergeheimnis wahren.

**Für ERP-System:**
- Zugriffskontrolle auf steuerrelevante Daten (RBAC)
- Verschlüsselung bei elektronischer Übermittlung
- Audit-Logging für alle Zugriffe auf geschützte Daten
- Keine Weitergabe an externe APIs ohne Verschlüsselung

---

### 2. Ordnungsvorschriften für Buchführung (§ 146 AO)

**§ 146 Abs. 1:** Buchführung muss den Grundsätzen ordnungsmäßiger Buchführung entsprechen.

**Grundsätze:**
- **Unveränderbarkeit:** Buchungen dürfen nachträglich nicht geändert werden
- **Nachvollziehbarkeit:** Jede Buchung muss nachvollziehbar sein
- **Vollständigkeit:** Alle Geschäftsvorfälle müssen erfasst werden
- **Richtigkeit:** Buchungen müssen sachlich und rechnerisch richtig sein
- **Zeitgerechtheit:** Buchungen müssen zeitnah erfolgen

> **⚠️ WICHTIG - Änderungen sind erlaubt!**  
> Die AO fordert nicht, dass Daten niemals geändert werden dürfen. Sie fordert, dass **Änderungen protokolliert werden** und der **ursprüngliche Inhalt feststellbar bleibt**.
>
> **Erlaubt:** Rechnung von 100€ auf 200€ ändern  
> **Pflicht:** AuditLog speichert: `old_value: 100€`, `new_value: 200€`, `changed_by: User`, `changed_at: Timestamp`

**ERP Implementation:**
```python
# apps/core/models.py
class AuditLog(BaseModel):
    """
    § 146 AO: Änderungsprotokoll
    
    WICHTIG: Speichere old_value UND new_value!
    """
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    action = models.CharField(max_length=50)
    model_name = models.CharField(max_length=100)
    object_id = models.UUIDField()
    
    # § 146 AO: Ursprünglicher Inhalt muss feststellbar bleiben
    field_name = models.CharField(max_length=100)
    old_value = models.TextField(null=True)  # ⭐ PFLICHT
    new_value = models.TextField(null=True)  # ⭐ PFLICHT
    
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['model_name', 'object_id', 'timestamp']),
        ]
```

---

### 3. Verlagerung der Buchführung (§ 146 Abs. 2a, 2b AO) ⭐ **CLOUD-HOSTING**

**§ 146 Abs. 2a AO:**  
> "Bücher und sonst erforderliche Aufzeichnungen sind im Geltungsbereich dieses Gesetzes zu führen und aufzubewahren."

**§ 146 Abs. 2b AO:**  
> "Werden die Unterlagen nicht im Inland geführt oder aufbewahrt, hat der Steuerpflichtige auf Verlangen der Finanzbehörde die Unterlagen unverzüglich beizubringen."

**ERP Relevanz für Cloud/SaaS:**

| Hosting-Standort | Zulässig? | Anforderungen |
|------------------|-----------|---------------|
| **Deutschland** | ✅ Ja | Keine besonderen Anforderungen |
| **EU/EWR** | ✅ Ja | Daten müssen jederzeit zugreifbar sein |
| **USA (AWS/Azure/Google)** | ⚠️ Vorsicht | Latenz beachten, Zugriff muss gewährleistet sein |
| **Sonstige Drittstaaten** | ❌ Problematisch | Mitteilungspflicht + Sicherstellung des Vollzugriffs |

**Technische Anforderungen:**
- **Zugriff:** Finanzbehörde muss jederzeit Zugriff auf Daten haben (§ 147 Abs. 6)
- **Latenz:** Export/Ansicht darf nicht durch Serverstandort verzögert werden
- **Mitteilungspflicht:** Standort muss dem Finanzamt auf Anfrage mitgeteilt werden können

**ERP Implementation:**
```python
# apps/core/models.py
class CompanySettings(BaseModel):
    """
    § 146 Abs. 2a/2b AO: Buchführungsstandort
    """
    company = models.OneToOneField(Company, on_delete=models.CASCADE)
    
    # Hosting-Standort
    data_hosting_location = models.CharField(max_length=100, choices=[
        ('DE', 'Deutschland'),
        ('EU', 'EU/EWR'),
        ('US', 'USA'),
        ('OTHER', 'Sonstige'),
    ])
    data_center_address = models.TextField()
    
    # § 146 Abs. 2b: Mitteilungspflicht
    tax_office_notified = models.BooleanField(default=False)
    tax_office_notification_date = models.DateField(null=True)
    
    # Zugriffssicherstellung
    data_access_guaranteed = models.BooleanField(default=True)
    max_export_latency_seconds = models.IntegerField(default=30)
```

---

### 4. Aufbewahrungsfristen (§ 147 AO)

**§ 147 Abs. 3 AO:** 10 Jahre
- Bücher, Inventare, Jahresabschlüsse, Buchungsbelege, Rechnungen

**§ 147 Abs. 4 AO:** 6 Jahre
- Geschäftsbriefe, sonstige Unterlagen

**Fristbeginn:** Ende des Kalenderjahres der letzten Eintragung

**Technische Anforderungen:**
- Maschinelle Auswertbarkeit während gesamter Aufbewahrungsfrist
- Unveränderbarkeit archivierter Daten
- Revisionssichere Archivierung

---

### 5. Datenzugriff durch Finanzbehörde (§ 147 Abs. 6 AO) ⭐ **KRITISCH**

> **Dies ist der wichtigste technische Paragraph für ERP-Hersteller!**

**§ 147 Abs. 6 AO:**  
> "Steuerpflichtige, die Bücher und Aufzeichnungen elektronisch führen, müssen auf Verlangen der Finanzbehörde die Daten nach amtlich vorgeschriebenem Datensatz durch Datenfernübertragung bereitstellen oder auf einem maschinell verwertbaren Datenträger überlassen."

**Drei Zugriffsmethoden:**

| Methode | Name | Beschreibung | ERP-Anforderung |
|---------|------|--------------|-----------------|
| **Z1** | Unmittelbarer Zugriff | Finanzbehörde greift direkt auf System zu | Nur für Kassen (DSFinV-K) |
| **Z2** | Mittelbarer Zugriff | Finanzbehörde nutzt System vor Ort | Lesezugriff auf Datenbank |
| **Z3** | Datenüberlassung | Export auf USB/CD | **⭐ PFLICHT für alle ERP-Systeme** |

**Z3-Export (Datenüberlassung / Beschreibungsstandard) - PFLICHT:**

Das ERP-System **MUSS** eine Exportfunktion haben, die alle steuerrelevanten Daten in einem maschinell auswertbaren Format bereitstellt.

**Technische Anforderungen:**
- **Format:** XML nach nach dem Beschreibungsstandard
- **Inhalt:** Alle Bücher, Grundaufzeichnungen, Belege
- **Struktur:** `index.xml` + Datentabellen (CSV/XML)
- **Zeitraum:** Gesamter Prüfungszeitraum (meist 3 Jahre)

**ERP Implementation:**
```python
# apps/tax/services.py
def export_z3_package(company: Company, start_date: date, end_date: date, user: User) -> str:
    """
    § 147 Abs. 6 AO: Z3-Datenexport (Beschreibungsstandard)
    
    OHNE DIESEN EXPORT FÄLLT DAS SYSTEM BEI JEDER BETRIEBSPRÜFUNG DURCH!
    """
    export_dir = create_export_directory(company, start_date, end_date)
    
    # 1. Stammdaten exportieren
    export_accounts(export_dir)
    export_customers(export_dir)
    export_suppliers(export_dir)
    export_products(export_dir)
    
    # 2. Bewegungsdaten exportieren
    export_journal_entries(export_dir, start_date, end_date)
    export_invoices(export_dir, start_date, end_date)
    export_receipts(export_dir, start_date, end_date)
    
    # 3. index.xml generieren (nach dem Beschreibungsstandard)
    generate_index_xml(export_dir)
    
    # 4. ZIP-Archiv erstellen
    zip_path = create_zip_archive(export_dir)
    
    # 5. Audit-Log
    AuditLog.objects.create(
        user=user,
        action='Z3_EXPORT',
        model_name='Z3_Export',
        object_id=company.id,
        old_value=None,
        new_value=f'Export: {start_date} - {end_date}'
    )
    
    return zip_path


def generate_index_xml(export_dir: str):
    """
    Generiert index.xml nach nach dem Beschreibungsstandard.
    
    Struktur:
    - <DataSet>: Beschreibung des Exports
    - <Media>: Tabellen (Accounts, JournalEntries, etc.)
    - <VariableLength>: Feldstruktur
    """
    root = ET.Element('DataSet', version='1.0')
    
    # Media-Beschreibung
    media = ET.SubElement(root, 'Media')
    media.set('Name', 'Finanzbuchhaltung')
    
    # Tabelle: Konten
    table = ET.SubElement(media, 'Table')
    table.set('Name', 'Accounts')
    table.set('URL', 'accounts.csv')
    
    # Felder definieren
    fields = ET.SubElement(table, 'VariableLength')
    add_field(fields, 'AccountNumber', 'AlphaNumeric', 20)
    add_field(fields, 'AccountName', 'AlphaNumeric', 200)
    # ... weitere Felder
    
    # XML speichern
    tree = ET.ElementTree(root)
    tree.write(f'{export_dir}/index.xml', encoding='UTF-8', xml_declaration=True)
```

**Checkliste Z3-Export:**
- [ ] Export-Funktion implementiert
- [ ] "index.xml / Beschreibungsstandard"-Generator
- [ ] Alle steuerrelevanten Tabellen exportiert
- [ ] index.xml nach Standard
- [ ] ZIP-Archiv-Erstellung
- [ ] Audit-Logging
- [ ] Test mit IDEA-Software (Prüfsoftware)

---

### 6. Elektronische Aufzeichnungssysteme / Kassen (§ 146a AO) ⭐ **KASSENSICHV**

**§ 146a AO:**  
> "Wer elektronische Aufzeichnungssysteme (Registrierkassen, Waagen mit Registrierkassenfunktion, Taxameter) verwendet, muss eine zertifizierte technische Sicherheitseinrichtung (TSE) verwenden."

**ERP Relevanz:**

| Szenario | TSE erforderlich? | Anforderung |
|----------|-------------------|-------------|
| **Nur B2B-Rechnungen** | ❌ Nein | Keine TSE nötig |
| **Barverkauf (Retail/POS)** | ✅ Ja | TSE + DSFinV-K Export |
| **Gastronomie** | ✅ Ja | TSE + DSFinV-K Export |
| **Taxi/Lieferdienst** | ✅ Ja | TSE + DSFinV-K Export |

**Technische Anforderungen (falls relevant):**
- **TSE:** Technische Sicherheitseinrichtung (Hardware oder Cloud)
- **Signatur:** Jede Transaktion muss digital signiert werden
- **DSFinV-K:** Export-Format für Kassendaten
- **Meldepflicht:** Kasse muss beim Finanzamt gemeldet werden

**ERP Implementation (nur falls Kasse/POS geplant):**
```python
# apps/pos/models.py
class CashRegister(BaseModel):
    """
    § 146a AO: Elektronisches Aufzeichnungssystem
    """
    register_name = models.CharField(max_length=100)
    serial_number = models.CharField(max_length=100, unique=True)
    
    # TSE (Technische Sicherheitseinrichtung)
    tse_serial_number = models.CharField(max_length=100)
    tse_provider = models.CharField(max_length=100)  # z.B. "fiskaly", "Swissbit"
    tse_activated_at = models.DateTimeField()
    
    # Meldepflicht
    tax_office_registered = models.BooleanField(default=False)
    tax_office_registration_date = models.DateField(null=True)


class CashTransaction(BaseModel):
    """
    § 146a AO: Einzelne Kassenbuchung (TSE-signiert)
    """
    register = models.ForeignKey(CashRegister, on_delete=models.PROTECT)
    
    # Transaktion
    transaction_number = models.IntegerField()
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    transaction_type = models.CharField(max_length=20)  # 'SALE', 'REFUND'
    
    # TSE-Signatur (PFLICHT!)
    tse_signature = models.CharField(max_length=500)
    tse_transaction_number = models.IntegerField()
    tse_start_time = models.DateTimeField()
    tse_finish_time = models.DateTimeField()
    
    # DSFinV-K Export
    dsfinv_k_exported = models.BooleanField(default=False)
```

**Hinweis:** Falls dein ERP **kein** Kassensystem hat (nur B2B-Rechnungen), kannst du § 146a ignorieren. **Vermerke dies aber explizit in der Dokumentation!**

---

### 7. Prüfung von Programmen (§ 87c AO)

**§ 87c AO:**  
> "Programme, die nicht von der Finanzverwaltung zur Verfügung gestellt werden, können von der Finanzverwaltung auf Einhaltung der Anforderungen überprüft werden."

> **⚠️ WICHTIGE KLARSTELLUNG:**  
> **Das Finanzamt zertifiziert KEINE Software!** Es gibt keinen "AO-TÜV" für ERP-Systeme.
>
> Die Prüfung findet **indirekt** über die Daten (§ 147 Abs. 6) im Rahmen einer Außenprüfung statt. Der Prüfer schaut sich die **Ergebnisse** (Buchungen, Exporte) an, nicht den Quellcode.

**Was das für dein ERP bedeutet:**
- ✅ **Verfahrensdokumentation** erstellen (wie funktioniert das System?)
- ✅ **Z3-Export** bereitstellen (nach dem Beschreibungsstandard)
- ✅ **Audit-Trail** implementieren (Änderungen nachvollziehbar)
- ❌ **NICHT:** Quellcode zur Zertifizierung einreichen

**ERP Implementation:**
```python
# apps/core/models.py
class SystemDocumentation(BaseModel):
    """
    § 87c AO: Verfahrensdokumentation
    
    Beschreibt, WIE das System arbeitet (nicht der Quellcode!)
    """
    document_type = models.CharField(max_length=50, choices=[
        ('SYSTEM_OVERVIEW', 'Systemübersicht'),
        ('DATA_FLOW', 'Datenfluss'),
        ('SECURITY', 'Sicherheitskonzept'),
        ('BACKUP', 'Datensicherung'),
        ('AUDIT_TRAIL', 'Änderungsprotokoll'),
    ])
    
    version = models.CharField(max_length=20)
    content = models.TextField()
    last_updated = models.DateField()
    
    # § 87c: 5 Jahre Aufbewahrung
    retention_until = models.DateField()
```

---

### 8. Elektronische Kommunikation (§§ 87a-87e AO)

**Anforderungen:**
- Qualifizierte elektronische Signatur für Steuererklärungen
- Verschlüsselung bei Übermittlung steuergeheimer Daten
- Amtlich vorgeschriebene Datensätze (ELSTER-Format)

---

### 9. Aufzeichnungspflichten (§ 90 AO)

**Verrechnungspreise bei internationalen Geschäftsbeziehungen:**
- Transaktionsmatrix
- Sachverhaltsdokumentation
- Angemessenheitsdokumentation
- Stammdokumentation (bei multinationalen Unternehmensgruppen)

**Vorlagefrist:** 30 Tage nach Anforderung

---

### 10. Datenübermittlung (§ 93c AO)

**Pflichten für mitteilungspflichtige Stellen:**
- Elektronische Übermittlung nach amtlich vorgeschriebenem Datensatz
- Informationspflicht gegenüber Steuerpflichtigen
- Aufbewahrung der übermittelten Daten (7 Jahre)

---

### 11. Missbrauchsvermeidung (§ 42 AO)

**Verbot:** Unangemessene rechtliche Gestaltungen zur Steuerumgehung

**Für ERP-System:**
- Validierung von Geschäftsvorfällen gegen typische Missbrauchsmuster
- Dokumentation der wirtschaftlichen Gründe für Gestaltungen

---

## Implementierung im ERP-System

### Archivierung (§ 147 Abs. 6 - Maschinelle Auswertbarkeit)

```python
# apps/documents/models.py
class ArchivedDocument(BaseModel):
    """
    § 147 Abs. 6 AO: Revisionssichere Archivierung
    
    ⚠️ WICHTIG: Verschlüsselung vs. Auswertbarkeit
    """
    document_type = models.CharField(max_length=50)
    document_id = models.UUIDField()
    archived_at = models.DateTimeField(auto_now_add=True)
    archived_by = models.ForeignKey(User, on_delete=models.PROTECT)
    
    # Checksumme (Unveränderbarkeit)
    content_hash = models.CharField(max_length=64)  # SHA-256
    
    # ⚠️ PROBLEM: Verschlüsselung vs. Auswertbarkeit
    # encrypted_content = models.BinaryField()  # ❌ NICHT ausreichend!
    
    # ✅ LÖSUNG: Strukturierte Daten + Verschlüsselung "At Rest"
    # Speichere Daten strukturiert (JSON), verschlüssele nur auf Disk-Ebene
    structured_data = models.JSONField()  # Für Z3-Export auswertbar
    
    # Verschlüsselung "At Rest" (Datenbankebene oder Festplattenverschlüsselung)
    # -> Daten sind verschlüsselt gespeichert, aber für Export entschlüsselbar
    
    retention_until = models.DateField()  # created_at + 10 Jahre
    
    def export_for_audit(self) -> dict:
        """
        § 147 Abs. 6 AO: Daten für Prüfer bereitstellen
        
        Daten müssen unverschlüsselt und strukturiert exportiert werden können!
        """
        return {
            'document_type': self.document_type,
            'document_id': str(self.document_id),
            'archived_at': self.archived_at.isoformat(),
            'data': self.structured_data,  # ✅ Auswertbar
            'hash': self.content_hash,
        }
```

**Wichtige Klarstellung:**
- **Verschlüsselung "At Rest"** (Festplatte/Datenbank) ist **gut** für Datenschutz
- **ABER:** Das System muss die Daten für den **Z3-Export** unverschlüsselt und strukturiert bereitstellen können
- **Lösung:** Speichere Daten strukturiert (JSON/Tabellen), verschlüssele nur auf Infrastrukturebene

---

## Wichtige Fristen

| Frist | Rechtsgrundlage | Beschreibung |
|-------|-----------------|--------------| | 10 Jahre | § 147 Abs. 3 | Aufbewahrung Bücher, Inventare, Jahresabschlüsse |
| 6 Jahre | § 147 Abs. 4 | Aufbewahrung Geschäftsbriefe |
| 30 Tage | § 90 Abs. 4 | Vorlage Verrechnungspreisdokumentation |
| 31. Juli | § 149 Abs. 2 | Abgabe Steuererklärung (mit Steuerberater) |

---

## Sanktionen bei Verstößen

- **§ 152:** Verspätungszuschlag (0,25% der festgesetzten Steuer pro Monat)
- **§ 162 Abs. 4:** Zuschlag bei Schätzung (5-10% der festgesetzten Steuer)
- **§ 370 AO:** Steuerhinterziehung (Freiheitsstrafe bis 5 Jahre oder Geldstrafe)
- **§ 378 AO:** Leichtfertige Steuerverkürzung (Geldstrafe)

---

## Compliance Checklist

### Pflicht für alle ERP-Systeme
- [ ] **§ 146:** AuditLog mit `old_value` + `new_value`
- [ ] **§ 147 Abs. 3/4:** Automatische Aufbewahrungsfristen
- [ ] **§ 147 Abs. 6:** Z3-Export (Datenüberlassung / Beschreibungsstandard) implementiert ⭐ **KRITISCH**
- [ ] **§ 146 Abs. 2a/2b:** Hosting-Standort dokumentiert
- [ ] **§ 87c:** Verfahrensdokumentation erstellt
- [ ] **§ 30:** Zugriffskontrolle für Steuerdaten

### Optional (je nach Funktionsumfang)
- [ ] **§ 146a:** TSE für Kassensystem (nur bei Barverkauf)
- [ ] **§ 90:** Verrechnungspreisdokumentation (nur bei internationalen Geschäften)
- [ ] **§ 150:** ELSTER-Schnittstelle (für automatische Steuererklärungen)

---

## Nächste Schritte

1. ✅ AO Compliance Summary gelesen
2. ⬜ **Z3-Export implementieren** (höchste Priorität!)
3. ⬜ AuditLog mit old_value/new_value erweitern
4. ⬜ Hosting-Standort dokumentieren (§ 146 Abs. 2a/2b)
5. ⬜ Verfahrensdokumentation erstellen (§ 87c)
6. ⬜ Entscheiden: Kassensystem ja/nein? (§ 146a)
7. ⬜ Externe Steuerberatung für finale Prüfung

---

**Quelle:** Abgabenordnung (AO) Stand 2025/2026  
**Hinweis:** Bei rechtlichen Fragen immer Steuerberater konsultieren.
