# AO Integration Checklist - ERP System

**Zweck:** Integration steuerrechtlicher Anforderungen (Abgabenordnung)  
**Zielgruppe:** Backend-Entwickler (Django/Python)  
**Status:** Living Document

**Referenz:** [ao_compliance_summary.md](./ao_compliance_summary.md) - Vollständige AO-Anforderungen

---

## Quick Reference: AO-Kernthemen

| Thema | Rechtsgrundlage | Technische Umsetzung | Priorität |
|-------|-----------------|----------------------|-----------|
| **Z3-Datenexport (Z3-Datenüberlassung)** | § 147 Abs. 6 AO | XML + CSV Export | 🔴 **HÖCHSTE** |
| **ELSTER-Schnittstelle** | § 150 AO | API-Integration, XML-Export | 🔴 HOCH |
| **E-Rechnungspflicht (B2B) ab 2025 (§ 14 UStG) ⭐ **NEU** | 🔴 HOCH |
| **Aufbewahrungsfristen** | § 147 AO | Automatische Berechnung | 🔴 HOCH |
| **Steuergeheimnis** | § 30 AO | Zugriffskontrolle, Verschlüsselung | 🔴 HOCH |
| **Verrechnungspreise** | § 90 AO | Dokumentations-Modul | 🟡 MITTEL |
| **Mitwirkungspflichten** | § 93c AO | Datenübermittlung | 🟡 MITTEL |
| **Missbrauchsvermeidung** | § 42 AO | Validierung, Plausibilitätsprüfung | 🟢 NIEDRIG |

---

## 1. ELSTER-Schnittstelle (§ 150 AO)

### 1.1 Anforderung

**§ 150 AO:** Steuererklärungen elektronisch nach amtlich vorgeschriebenem Datensatz übermitteln.

**Betroffene Steuererklärungen:**
- Umsatzsteuer-Voranmeldung (monatlich/quartalsweise)
- Lohnsteuer-Anmeldung (monatlich)
- Jahressteuererklärungen (USt, KSt, ESt)
- E-Bilanz (§ 5b EStG)

### 1.2 Technische Integration

```python
# apps/tax/services.py
from decimal import Decimal
from datetime import date
import xml.etree.ElementTree as ET

def generate_elster_xml(
    tax_period: str,  # Format: "YYYY-MM"
    user: User
) -> str:
    """
    Generiert ELSTER-XML für Umsatzsteuer-Voranmeldung.
    
    Rechtsgrundlage: § 150 AO, § 18 UStG
    """
    # Daten aus Finanzbuchhaltung abrufen
    entries = JournalEntry.objects.filter(
        tax_period=tax_period,
        account__startswith='17'  # USt-Konten
    )
    
    # Kennzahlen berechnen
    kz_81 = calculate_tax_base(entries, rate=Decimal('19'))  # Steuerpflichtige Umsätze 19%
    kz_86 = calculate_tax_base(entries, rate=Decimal('7'))   # Steuerpflichtige Umsätze 7%
    kz_35 = calculate_tax_amount(entries, rate=Decimal('19')) # Steuer 19%
    kz_36 = calculate_tax_amount(entries, rate=Decimal('7'))  # Steuer 7%
    
    # ELSTER-XML generieren
    root = ET.Element('Elster')
    # ... XML-Struktur nach ELSTER-Schema
    
    xml_string = ET.tostring(root, encoding='unicode')
    
    # Audit-Log
    AuditLog.objects.create(
        action='ELSTER_EXPORT',
        user=user,
        new_values={'period': tax_period}
    )
    
    return xml_string


def submit_to_elster(
    xml_data: str,
    certificate_path: str,
    user: User
) -> dict:
    """
    Übermittelt Daten an ELSTER.
    
    Anforderung: Qualifizierte elektronische Signatur (§ 87a AO)
    """
    # Zertifikat laden
    cert = load_certificate(certificate_path)
    
    # XML signieren
    signed_xml = sign_xml(xml_data, cert)
    
    # An ELSTER senden
    response = requests.post(
        'https://www.elster.de/elsterweb/...',
        data=signed_xml,
        headers={'Content-Type': 'application/xml'}
    )
    
    # Protokollierung
    ElsterSubmission.objects.create(
        user=user,
        xml_data=xml_data,
        response_code=response.status_code,
        response_data=response.text,
        submitted_at=timezone.now()
    )
    
    return {
        'success': response.status_code == 200,
        'transfer_ticket': extract_ticket(response.text)
    }
```

### 1.3 Datenmodell

```python
# apps/tax/models.py
class ElsterSubmission(BaseModel):
    """
    ELSTER-Übermittlung (§ 150 AO).
    """
    # Steuererklärungstyp
    declaration_type = models.CharField(max_length=20, choices=[
        ('UStVA', 'Umsatzsteuer-Voranmeldung'),
        ('LStA', 'Lohnsteuer-Anmeldung'),
        ('UStJE', 'Umsatzsteuer-Jahreserklärung'),
        ('EBILANZ', 'E-Bilanz'),
    ])
    
    # Zeitraum
    tax_period = models.CharField(max_length=7)  # YYYY-MM
    fiscal_year = models.IntegerField()
    
    # Übermittlung
    xml_data = models.TextField()
    submitted_at = models.DateTimeField()
    
    # ELSTER-Antwort
    transfer_ticket = models.CharField(max_length=50, unique=True)
    response_code = models.IntegerField()
    response_data = models.TextField()
    
    # Status
    status = models.CharField(max_length=20, choices=[
        ('DRAFT', 'Entwurf'),
        ('SUBMITTED', 'Übermittelt'),
        ('ACCEPTED', 'Angenommen'),
        ('REJECTED', 'Abgelehnt'),
    ])
    
    class Meta:
        ordering = ['-submitted_at']
```

### 1.4 Checkliste

- [ ] ELSTER-Zertifikat beantragt
- [ ] XML-Generator implementiert
- [ ] Signatur-Funktion implementiert
- [ ] API-Anbindung getestet
- [ ] Fehlerbehandlung implementiert
- [ ] Automatische Übermittlung (Cronjob)
- [ ] Benachrichtigung bei Fehler

---

## 1a. E-Rechnungspflicht (B2B) ab 2025 (§ 14 UStG) ⭐ **NEU**

### 1a.1 Anforderung (Wachstumschancengesetz)

**Ab 01.01.2025** besteht für inländische B2B-Geschäfte eine grundsätzliche Empfangspflicht für elektronische Rechnungen.
* **Papierrechnungen/PDF:** Vorrang entfällt.
* **Pflichtformat:** Strukturierter Datensatz (EN 16931) -> **XRechnung** oder **ZUGFeRD** (ab Version 2.x).
* **Übergangsfristen:** Für den *Versand* gelten Übergangsfristen (2025-2027), aber der *Empfang* muss ab Tag 1 (01.01.2025) möglich sein!

### 1a.2 Technische Integration

Das ERP-System muss eingehende Rechnungen nicht nur als Bild (PDF), sondern als Datensatz verarbeiten können.

```python
# apps/sales/services/e_invoicing.py
def process_incoming_invoice(file_upload):
    """
    Verarbeitet eingehende Rechnung (Hybrid: PDF + XML).
    Prüft auf ZUGFeRD / XRechnung (CII/UBL).
    """
    if is_zugferd_pdf(file_upload):
        # 1. Extrahiere XML aus PDF-Anhang
        xml_content = extract_zugferd_xml(file_upload)
        
        # 2. Parse Rechnungsdaten (Strukturierte Daten haben Vorrang!)
        invoice_data = parse_en16931_xml(xml_content)
        
        # 3. Erstelle Eingangrechnung
        create_vendor_invoice(invoice_data)
        
    elif is_xrechnung_xml(file_upload):
        # Reine XML-Verarbeitung
        invoice_data = parse_en16931_xml(file_upload)
        create_vendor_invoice(invoice_data)
        
    else:
        # Fallback: OCR / Manuelle Erfassung (alte PDF/Papier)
        process_standard_pdf(file_upload)
```

### 1a.3 Checkliste

- [ ] ZUGFeRD/XRechnung Parser implementiert (EN 16931 Konformität)
- [ ] E-Mail-Ingest kann factur-x.xml und xrechnung.xml erkennen
- [ ] Visualisierung der XML-Daten für den User (Lesbarkeit sicherstellen)
- [ ] Archivierung: XML-Datensatz muss als Original archiviert werden (nicht nur das PDF!)

---

## 2. Aufbewahrungsfristen (§ 147 AO)

### 2.1 Anforderung

**§ 147 Abs. 3 AO:** 10 Jahre
- Bücher, Inventare, Jahresabschlüsse
- Buchungsbelege, Rechnungen

**§ 147 Abs. 4 AO:** 6 Jahre
- Geschäftsbriefe
- Sonstige Unterlagen

**Fristbeginn:** Ende des Kalenderjahres der letzten Eintragung

### 2.2 Automatische Berechnung

```python
# apps/documents/services.py
from datetime import date, timedelta

def calculate_retention_date(document: Document) -> date:
    """
    Berechnet Aufbewahrungsfrist nach § 147 AO.
    """
    # Dokumenttyp bestimmt Frist
    retention_years = {
        'INVOICE_IN': 10,
        'INVOICE_OUT': 10,
        'RECEIPT': 10,
        'CONTRACT': 6,
        'EMAIL': 6,
        'OTHER': 6,
    }.get(document.document_type, 6)
    
    # Fristbeginn: Ende des Kalenderjahres
    year_end = date(document.document_date.year, 12, 31)
    
    # Fristende: + retention_years
    retention_until = date(year_end.year + retention_years, 12, 31)
    
    return retention_until


def check_deletion_allowed(document: Document) -> bool:
    """
    Prüft, ob Löschung erlaubt ist.
    
    KONFLIKT: § 147 AO vs. Art. 17 DSGVO
    Lösung: AO geht vor (Art. 17 Abs. 3 lit. b DSGVO)
    """
    today = date.today()
    
    # Aufbewahrungsfrist noch nicht abgelaufen
    if document.retention_until > today:
        return False
    
    # Laufende Betriebsprüfung?
    if has_active_tax_audit():
        return False
    
    return True
```

### 2.3 Integration in Document-Model

```python
# apps/documents/models.py
class Document(BaseModel):
    """
    Dokument mit automatischer Aufbewahrungsfrist.
    """
    # ... (siehe gobd_implementation_guide.md)
    
    # Aufbewahrung (§ 147 AO)
    retention_until = models.DateField()
    deletion_blocked = models.BooleanField(default=False)  # Betriebsprüfung
    
    def save(self, *args, **kwargs):
        # Automatische Berechnung
        if not self.retention_until:
            self.retention_until = calculate_retention_date(self)
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        # Löschsperre prüfen
        if not check_deletion_allowed(self):
            raise ValidationError("Löschung nicht erlaubt (§ 147 AO)")
        super().delete(*args, **kwargs)
```

### 2.4 Checkliste

- [x] Automatische Berechnung implementiert
- [x] Löschsperre bei laufender Prüfung
- [ ] Cronjob für Löschung abgelaufener Dokumente
- [ ] Benachrichtigung vor Löschung
- [ ] DSGVO-Konflikt dokumentiert

### 2.5 Datenzugriff durch Finanzbehörde (§ 147 Abs. 6 AO) ⭐ **KRITISCH**

> **WICHTIGSTER TECHNISCHER PARAGRAPH FÜR ERP-SYSTEME!**

**§ 147 Abs. 6 AO:** Steuerpflichtige müssen auf Verlangen der Finanzbehörde die Daten nach amtlich vorgeschriebenem Datensatz bereitstellen.

**Drei Zugriffsmethoden:**
- **Z1:** Unmittelbarer Zugriff (nur für Kassen)
- **Z2:** Mittelbarer Zugriff (Lesezugriff vor Ort)
- **Z3:** Datenüberlassung (Export) ⭐ **PFLICHT**

**Z3-Export (Z3-Datenüberlassung) - Implementation:**

```python
# apps/tax/services.py
import xml.etree.ElementTree as ET
from datetime import date
from decimal import Decimal

def export_z3_package(
    company: Company,
    start_date: date,
    end_date: date,
    user: User
) -> str:
    """
    § 147 Abs. 6 AO: Z3-Datenexport (Beschreibungsstandard)
    
    OHNE DIESEN EXPORT FÄLLT DAS SYSTEM BEI JEDER BETRIEBSPRÜFUNG DURCH!
    """
    export_dir = create_temp_directory()
    
    # 1. Stammdaten exportieren
    export_accounts_csv(export_dir)
    export_customers_csv(export_dir)
    export_suppliers_csv(export_dir)
    export_products_csv(export_dir)
    
    # 2. Bewegungsdaten exportieren
    export_journal_entries_csv(export_dir, start_date, end_date)
    export_invoices_csv(export_dir, start_date, end_date)
    export_receipts_csv(export_dir, start_date, end_date)
    
    # 3. index.xml generieren (Beschreibungsstandard)
    generate_index_xml(export_dir, start_date, end_date)
    
    # 4. ZIP-Archiv erstellen
    zip_path = f'/exports/z3_export_{company.id}_{start_date}_{end_date}.zip'
    create_zip_archive(export_dir, zip_path)
    
    # 5. Audit-Log
    AuditLog.objects.create(
        user=user,
        action='Z3_EXPORT',
        model_name='Z3_Export',
        object_id=company.id,
        field_name='export_period',
        old_value=None,
        new_value=f'{start_date} - {end_date}'
    )
    
    return zip_path


def generate_index_xml(export_dir: str, start_date: date, end_date: date):
    """
    Generiert index.xml nach Beschreibungsstandard.
    """
    root = ET.Element('DataSet', version='1.0')
    
    # Media-Beschreibung
    media = ET.SubElement(root, 'Media')
    media.set('Name', 'Finanzbuchhaltung')
    
    # Tabelle: Konten
    table_accounts = ET.SubElement(media, 'Table')
    table_accounts.set('Name', 'Accounts')
    table_accounts.set('URL', 'accounts.csv')
    
    fields_accounts = ET.SubElement(table_accounts, 'VariableLength')
    add_index_field(fields_accounts, 'AccountNumber', 'AlphaNumeric', 20)
    add_index_field(fields_accounts, 'AccountName', 'AlphaNumeric', 200)
    add_index_field(fields_accounts, 'AccountType', 'AlphaNumeric', 50)
    
    # Tabelle: Buchungssätze
    table_journal = ET.SubElement(media, 'Table')
    table_journal.set('Name', 'JournalEntries')
    table_journal.set('URL', 'journal_entries.csv')
    
    fields_journal = ET.SubElement(table_journal, 'VariableLength')
    add_index_field(fields_journal, 'EntryID', 'AlphaNumeric', 36)
    add_index_field(fields_journal, 'BookingDate', 'Date', 10)
    add_index_field(fields_journal, 'Account', 'AlphaNumeric', 20)
    add_index_field(fields_journal, 'ContraAccount', 'AlphaNumeric', 20)
    add_index_field(fields_journal, 'Amount', 'Numeric', 14, 2)
    add_index_field(fields_journal, 'Description', 'AlphaNumeric', 500)
    add_index_field(fields_journal, 'DocumentNumber', 'AlphaNumeric', 100)
    
    # Tabelle: Rechnungen
    table_invoices = ET.SubElement(media, 'Table')
    table_invoices.set('Name', 'Invoices')
    table_invoices.set('URL', 'invoices.csv')
    
    fields_invoices = ET.SubElement(table_invoices, 'VariableLength')
    add_index_field(fields_invoices, 'InvoiceNumber', 'AlphaNumeric', 50)
    add_index_field(fields_invoices, 'InvoiceDate', 'Date', 10)
    add_index_field(fields_invoices, 'CustomerID', 'AlphaNumeric', 36)
    add_index_field(fields_invoices, 'TotalNet', 'Numeric', 14, 2)
    add_index_field(fields_invoices, 'TotalTax', 'Numeric', 14, 2)
    add_index_field(fields_invoices, 'TotalGross', 'Numeric', 14, 2)
    
    # XML speichern
    tree = ET.ElementTree(root)
    tree.write(f'{export_dir}/index.xml', encoding='UTF-8', xml_declaration=True)


def add_index_field(
    parent: ET.Element,
    name: str,
    data_type: str,
    length: int,
    decimals: int = None
):
    """
    Fügt Feld-Definition zur index.xml / Beschreibungsstandard hinzu.
    """
    field = ET.SubElement(parent, 'VariableColumn')
    
    name_elem = ET.SubElement(field, 'Name')
    name_elem.text = name
    
    type_elem = ET.SubElement(field, 'AlphaNumeric') if data_type == 'AlphaNumeric' else ET.SubElement(field, 'Numeric')
    
    if data_type == 'Numeric' and decimals:
        type_elem.set('Accuracy', str(decimals))
    
    length_elem = ET.SubElement(field, 'MaxLength')
    length_elem.text = str(length)


def export_journal_entries_csv(export_dir: str, start_date: date, end_date: date):
    """
    Exportiert Buchungssätze als CSV.
    """
    entries = JournalEntry.objects.filter(
        booking_date__gte=start_date,
        booking_date__lte=end_date
    ).order_by('booking_date')
    
    csv_path = f'{export_dir}/journal_entries.csv'
    
    with open(csv_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f, delimiter=';')
        
        # Header
        writer.writerow([
            'EntryID', 'BookingDate', 'Account', 'ContraAccount',
            'Amount', 'Description', 'DocumentNumber'
        ])
        
        # Daten
        for entry in entries:
            writer.writerow([
                str(entry.id),
                entry.booking_date.isoformat(),
                entry.account,
                entry.contra_account,
                str(entry.amount),
                entry.description,
                entry.document_number
            ])
```

**Checkliste Z3-Export:**
- [ ] Export-Funktion implementiert
- [ ] "index.xml / Beschreibungsstandard"-XML-Generator (index.xml)
- [ ] CSV-Export für alle steuerrelevanten Tabellen
  - [ ] Accounts (Konten)
  - [ ] JournalEntries (Buchungssätze)
  - [ ] Invoices (Rechnungen)
  - [ ] Customers (Kunden)
  - [ ] Suppliers (Lieferanten)
  - [ ] Products (Artikel)
- [ ] ZIP-Archiv-Erstellung
- [ ] Audit-Logging
- [ ] Test mit IDEA-Software (Prüfsoftware der Finanzbehörden)
- [ ] Dokumentation für Anwender

---

## 3. Steuergeheimnis (§ 30 AO)

### 3.1 Anforderung

**§ 30 AO:** Amtsträger müssen Steuergeheimnis wahren.

**Für ERP-System:**
- Zugriffskontrolle auf steuerrelevante Daten
- Verschlüsselung bei Übermittlung
- Audit-Logging für Datenzugriffe

### 3.2 Zugriffskontrolle

```python
# apps/users/permissions.py
from django.contrib.auth.models import Permission

# Spezielle Permissions für steuerrelevante Daten
TAX_PERMISSIONS = [
    ('view_tax_data', 'Kann Steuerdaten einsehen'),
    ('export_tax_data', 'Kann Steuerdaten exportieren'),
    ('submit_tax_declaration', 'Kann Steuererklärungen abgeben'),
]

class TaxDataPermission:
    """
    Permission-Check für steuerrelevante Daten.
    """
    @staticmethod
    def has_permission(user: User, action: str) -> bool:
        # Superuser immer erlaubt
        if user.is_superuser:
            return True
        
        # Permission prüfen
        perm = f'tax.{action}'
        if not user.has_perm(perm):
            # Audit-Log: Unberechtigter Zugriff
            AuditLog.objects.create(
                action='ACCESS_DENIED',
                user=user,
                new_values={'permission': perm}
            )
            return False
        
        # Audit-Log: Zugriff gewährt
        AuditLog.objects.create(
            action='ACCESS_GRANTED',
            user=user,
            new_values={'permission': perm}
        )
        return True
```

### 3.3 Verschlüsselung

```python
# apps/tax/services.py
from cryptography.fernet import Fernet

def encrypt_tax_data(data: dict) -> str:
    """
    Verschlüsselt steuerrelevante Daten (§ 30 AO).
    """
    key = get_encryption_key()
    f = Fernet(key)
    
    json_data = json.dumps(data)
    encrypted = f.encrypt(json_data.encode())
    
    return encrypted.decode()


def decrypt_tax_data(encrypted_data: str) -> dict:
    """
    Entschlüsselt steuerrelevante Daten.
    """
    key = get_encryption_key()
    f = Fernet(key)
    
    decrypted = f.decrypt(encrypted_data.encode())
    return json.loads(decrypted.decode())
```

### 3.4 Checkliste

- [ ] Zugriffskontrolle implementiert
- [ ] Verschlüsselung bei Übermittlung (HTTPS)
- [ ] Verschlüsselung at rest (Datenbank)
- [ ] Audit-Logging für alle Zugriffe
- [ ] Rollenkonzept (Steuerberater, Buchhalter, etc.)

---

## 4. Verrechnungspreise (§ 90 AO)

### 4.1 Anforderung

**§ 90 Abs. 3 AO:** Aufzeichnungen über Geschäftsbeziehungen mit nahestehenden Personen.

**Dokumentationspflicht:**
- Art und Inhalt der Geschäftsbeziehung
- Wirtschaftliche und rechtliche Rahmenbedingungen
- Verrechnungspreismethode
- Angemessenheit der Verrechnungspreise

**Frist:** 30 Tage nach Anforderung durch Finanzbehörde

### 4.2 Datenmodell

```python
# apps/finance/models.py
class TransferPricingTransaction(BaseModel):
    """
    Verrechnungspreisdokumentation (§ 90 AO).
    """
    # Geschäftsbeziehung
    related_party = models.ForeignKey('companies.Company', on_delete=models.PROTECT)
    transaction_type = models.CharField(max_length=50, choices=[
        ('GOODS', 'Warenlieferung'),
        ('SERVICE', 'Dienstleistung'),
        ('LICENSE', 'Lizenz'),
        ('LOAN', 'Darlehen'),
        ('OTHER', 'Sonstige'),
    ])
    
    # Transaktion
    transaction_date = models.DateField()
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    currency = models.CharField(max_length=3)
    
    # Verrechnungspreismethode
    pricing_method = models.CharField(max_length=50, choices=[
        ('CUP', 'Preisvergleichsmethode'),
        ('RPM', 'Wiederverkaufspreismethode'),
        ('CPM', 'Kostenaufschlagsmethode'),
        ('TNMM', 'Transaktionsbezogene Nettomargenmethode'),
        ('PSM', 'Gewinnaufteilungsmethode'),
    ])
    
    # Dokumentation
    documentation = models.TextField()
    attachments = models.JSONField(default=list)
    
    # Angemessenheitsprüfung
    arm_length_test_passed = models.BooleanField(default=False)
    arm_length_test_date = models.DateField(null=True)
    
    class Meta:
        ordering = ['-transaction_date']
```

### 4.3 Service

```python
# apps/finance/services.py
def create_transfer_pricing_doc(
    transaction: Transaction,
    user: User
) -> TransferPricingTransaction:
    """
    Erstellt Verrechnungspreisdokumentation.
    
    Rechtsgrundlage: § 90 Abs. 3 AO
    """
    # Prüfen, ob nahestehende Person
    if not is_related_party(transaction.partner):
        return None
    
    # Dokumentation erstellen
    tp_doc = TransferPricingTransaction.objects.create(
        created_by=user,
        related_party=transaction.partner,
        transaction_type=determine_type(transaction),
        transaction_date=transaction.date,
        amount=transaction.amount,
        currency=transaction.currency,
        pricing_method='CUP',  # Default
        documentation=generate_documentation(transaction)
    )
    
    # Angemessenheitsprüfung
    tp_doc.arm_length_test_passed = perform_arm_length_test(tp_doc)
    tp_doc.arm_length_test_date = timezone.now().date()
    tp_doc.save()
    
    return tp_doc
```

### 4.4 Checkliste

- [ ] Erkennung nahestehender Personen
- [ ] Automatische Dokumentationserstellung
- [ ] Verrechnungspreismethoden implementiert
- [ ] Angemessenheitsprüfung (Arm's Length Test)
- [ ] 30-Tage-Frist-Überwachung
- [ ] Export für Finanzbehörde

---

## 5. Mitwirkungspflichten (§ 93c AO)

### 5.1 Anforderung

**§ 93c AO:** Datenübermittlung durch Dritte nach amtlich vorgeschriebenem Datensatz.

**Beispiele:**
- Banken: Kontoinformationen
- Versicherungen: Versicherungsdaten
- Arbeitgeber: Lohndaten

### 5.2 Automatische Datenübermittlung

```python
# apps/finance/services.py
def submit_salary_data_to_tax_office(
    year: int,
    user: User
) -> dict:
    """
    Übermittelt Lohndaten an Finanzbehörde (§ 93c AO).
    """
    # Lohndaten abrufen
    salary_data = SalaryPayment.objects.filter(
        payment_date__year=year
    )
    
    # XML generieren (nach amtlich vorgeschriebenem Datensatz)
    xml_data = generate_salary_xml(salary_data)
    
    # Übermitteln
    response = submit_to_tax_office(xml_data)
    
    # Protokollierung
    DataSubmission.objects.create(
        submission_type='SALARY',
        year=year,
        xml_data=xml_data,
        response=response,
        submitted_by=user
    )
    
    return response
```

### 5.3 Checkliste

- [ ] Identifikation übermittlungspflichtiger Daten
- [ ] XML-Generator nach amtlichem Schema
- [ ] Automatische Übermittlung (Cronjob)
- [ ] Fehlerbehandlung
- [ ] Benachrichtigung bei Problemen

---

## 6. Missbrauchsvermeidung (§ 42 AO)

### 6.1 Anforderung

**§ 42 AO:** Missbrauch von Gestaltungsmöglichkeiten zur Steuerumgehung ist unzulässig.

**Für ERP-System:**
- Plausibilitätsprüfungen
- Warnung bei ungewöhnlichen Transaktionen
- Dokumentation der Geschäftsvorfälle

### 6.2 Validierung

```python
# apps/finance/validators.py
def validate_transaction_plausibility(transaction: Transaction) -> list[str]:
    """
    Prüft Plausibilität einer Transaktion (§ 42 AO).
    """
    warnings = []
    
    # Ungewöhnlich hoher Betrag?
    if transaction.amount > Decimal('100000'):
        warnings.append("Ungewöhnlich hoher Betrag - Dokumentation erforderlich")
    
    # Transaktion mit Steueroase?
    if is_tax_haven(transaction.partner.country):
        warnings.append("Transaktion mit Steueroase - erhöhte Dokumentationspflicht")
    
    # Ungewöhnliche Zahlungsart?
    if transaction.payment_method == 'CASH' and transaction.amount > Decimal('10000'):
        warnings.append("Barzahlung über 10.000 € - Geldwäschegesetz beachten!")
    
    # Nahestehende Person ohne Verrechnungspreisdokumentation?
    if is_related_party(transaction.partner) and not has_transfer_pricing_doc(transaction):
        warnings.append("Verrechnungspreisdokumentation fehlt (§ 90 AO)")
    
    return warnings
```

### 6.3 Checkliste

- [ ] Plausibilitätsprüfungen implementiert
- [ ] Warnsystem bei ungewöhnlichen Transaktionen
- [ ] Dokumentationspflicht-Hinweise
- [ ] Geldwäschegesetz-Integration

---

## 7. Integration-Roadmap

### Phase 1: Basis (JETZT) ⭐ **KRITISCH**
- [x] Aufbewahrungsfristen automatisch berechnen
- [ ] **Z3-Datenexport ("Z3-Datenüberlassung") implementieren** ⭐ **HÖCHSTE PRIORITÄT**
  - [ ] "index.xml / Beschreibungsstandard"-XML-Generator
  - [ ] CSV-Export für alle Tabellen
  - [ ] ZIP-Archiv-Erstellung
  - [ ] Test mit IDEA-Software
- [ ] Steuergeheimnis: Zugriffskontrolle
- [ ] Audit-Logging für steuerrelevante Daten (old_value + new_value)

### Phase 2: ELSTER
- [ ] ELSTER-Zertifikat beantragen
- [ ] XML-Generator für UStVA
- [ ] API-Anbindung testen
- [ ] Automatische Übermittlung

### Phase 3: Verrechnungspreise
- [ ] Transfer-Pricing-Modul
- [ ] Erkennung nahestehender Personen
- [ ] Angemessenheitsprüfung
- [ ] 30-Tage-Frist-Überwachung

### Phase 4: Erweitert
- [ ] E-Bilanz-Export
- [ ] Lohndaten-Übermittlung (§ 93c AO)
- [ ] Geldwäschegesetz-Integration

---

## 8. Wichtige Fristen

| Frist | Was | Rechtsgrundlage |
|-------|-----|-----------------|
| **10. Tag** | UStVA (monatlich) | § 18 Abs. 1 UStG |
| **10. Tag** | LStA (monatlich) | § 41a EStG |
| **31. Mai** | Jahressteuererklärung (ohne Steuerberater) | § 149 Abs. 2 AO |
| **31. Juli** | Jahressteuererklärung (mit Steuerberater) | § 149 Abs. 3 AO |
| **30 Tage** | Verrechnungspreisdokumentation | § 90 Abs. 4 AO |
| **10 Jahre** | Aufbewahrung Bücher/Belege | § 147 Abs. 3 AO |
| **6 Jahre** | Aufbewahrung Geschäftsbriefe | § 147 Abs. 4 AO |

---

## 9. Testing

```python
# apps/tax/tests/test_ao_compliance.py
class AOComplianceTests(TestCase):
    """
    Tests für AO-Konformität.
    """
    
    def test_retention_period_calculation(self):
        """§ 147 AO: Aufbewahrungsfrist korrekt berechnet."""
        doc = Document.objects.create(
            document_type='INVOICE_IN',
            document_date=date(2024, 6, 15)
        )
        
        # Fristende: 31.12.2034 (10 Jahre nach 2024)
        expected = date(2034, 12, 31)
        self.assertEqual(doc.retention_until, expected)
    
    def test_elster_xml_generation(self):
        """§ 150 AO: ELSTER-XML korrekt generiert."""
        xml = generate_elster_xml('2024-01', user)
        
        # XML validieren
        self.assertIn('<Elster>', xml)
        self.assertIn('<UStVA>', xml)
    
    def test_transfer_pricing_documentation(self):
        """§ 90 AO: Verrechnungspreisdokumentation erstellt."""
        transaction = create_transaction(related_party=True)
        
        tp_doc = TransferPricingTransaction.objects.get(
            transaction_date=transaction.date
        )
        
        self.assertIsNotNone(tp_doc)
        self.assertTrue(tp_doc.arm_length_test_passed)
```

---

## 10. Nächste Schritte

1. **Aufbewahrungsfristen** in Document-Model integrieren
2. **ELSTER-Zertifikat** beantragen
3. **Zugriffskontrolle** für Steuerdaten implementieren
4. **Transfer-Pricing-Modul** planen
5. **Externe Steuerberatung** für finale Prüfung

**Bei Fragen:** Immer auf ao_compliance_summary.md verweisen!
