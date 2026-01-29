# GoBD-Implementierungsleitfaden für Entwickler

## Zweck
Dieser Leitfaden ist die **zentrale technische Referenz** für die Implementierung von GoBD-konformen Funktionen im ERP-System. Er übersetzt die rechtlichen Anforderungen (aus HGB, GoBD, AO) in konkrete Code-Muster und Architektur-Vorgaben.

**Zielgruppe:** Backend-Entwickler (Django/Python)
**Status:** Lebendes Dokument (Living Document)

---

## 🏛️ Architektur-Invariante

> **⚠️ KRITISCHE REGEL:**  
> **Keine Buchung ohne Beleg! Keine Änderung ohne Protokoll!**

---

## 1. Datenmodell-Basis (Foundation)

### 1.1 Das `BaseModel`
Jedes Model, das geschäftsrelevante Daten speichert, MUSS von `BaseModel` erben.

```python
# core/models.py
import uuid
from django.db import models
from django.utils import timezone

class BaseModel(models.Model):
    """
    Abstrakte Basisklasse für GoBD-Konformität.
    
    Implementiert:
    - Eindeutige Identifikation (UUID)
    - Nachvollziehbarkeit (Created/Modified)
    - Versionierung
    - Soft-Delete (WICHTIG für Aufbewahrungspflicht!)
    """
    id = models.UUIDField(
        primary_key=True, 
        default=uuid.uuid4, 
        editable=False
    )
    
    # Audit-Felder (Systemseitig)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    created_by = models.ForeignKey(
        'users.User', 
        on_delete=models.PROTECT,
        related_name='created_%(class)s_set',
        null=True
    )
    
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        'users.User', 
        on_delete=models.PROTECT,
        related_name='updated_%(class)s_set',
        null=True
    )
    
    # Versionierung für Optimistic Locking & Audit
    version = models.IntegerField(default=1)
    
    # Soft Delete (statts physischem Löschen)
    is_deleted = models.BooleanField(default=False, db_index=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    deleted_by = models.ForeignKey(
        'users.User',
        on_delete=models.PROTECT,
        null=True,
        related_name='deleted_%(class)s_set'
    )

    class Meta:
        abstract = True
        ordering = ['-created_at']

    def delete(self, user=None, force=False):
        """
        Soft-Delete Standard-Implementierung.
        Force=True nur für Aufräumarbeiten (z.B. DSGVO nach Fristablauf).
        """
        if force:
            super().delete()
        else:
            self.is_deleted = True
            self.deleted_at = timezone.now()
            self.deleted_by = user
            self.save()
```

### 1.2 Der Audit-Log (`AuditLog`)
Änderungsprotokollierung nach § 146 Abs. 1 AO / GoBD Rz. 31.

```python
# core/models.py
class AuditLog(models.Model):
    """
    Zentrales Änderungsprotokoll (Unveränderbarkeit).
    Muss revisionssicher gespeichert werden (Write-Once-Read-Many ideal).
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    
    # Wer hat was gemacht?
    user = models.ForeignKey('users.User', on_delete=models.PROTECT, null=True)
    ip_address = models.GenericIPAddressField(null=True)
    
    # Welches Objekt?
    model_name = models.CharField(max_length=100)
    object_id = models.UUIDField()
    action = models.CharField(max_length=50)  # CREATE, UPDATE, DELETE, VIEW, EXPORT
    
    # Was wurde geändert?
    changes = models.JSONField(null=True)  # {'field': {'old': 'A', 'new': 'B'}}
    
    # Hash-Verkettung für Manipulationssicherheit (Blockchain-Prinzip)
    previous_hash = models.CharField(max_length=64, null=True)
    hash = models.CharField(max_length=64)

    class Meta:
        indexes = [
            models.Index(fields=['model_name', 'object_id']),
            models.Index(fields=['timestamp']),
        ]
```

---

## 2. Finanzbuchhaltung (Core Finance)

### 2.1 Der Buchungssatz (`JournalEntry`)
Erfüllt BMF-Anforderungen 2024.

```python
# apps/finance/models.py
class JournalEntry(BaseModel):
    """
    GoBD-konformer Buchungssatz.
    """
    # 1. Beleg-Referenz (Zwingend!)
    document = models.ForeignKey(
        'documents.Document', 
        on_delete=models.PROTECT,
        related_name='journal_entries'
    )
    
    # 2. Buchungsdatum vs. Festschreibedatum
    booking_date = models.DateField(db_index=True)  # Datum der Erfassung
    service_date = models.DateField()               # Datum der Leistung
    validation_date = models.DateTimeField(null=True) # Datum der Festschreibung (Journalisierung)
    
    # 3. Beträge
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    currency = models.CharField(max_length=3, default='EUR')
    
    # 4. Kontierung
    account_debit = models.ForeignKey('Account', on_delete=models.PROTECT, related_name='debit_entries')
    account_credit = models.ForeignKey('Account', on_delete=models.PROTECT, related_name='credit_entries')
    
    # 5. BMF 2024 Anforderungen (Rz. 94 - PFLICHTFELDER)
    tax_key = models.ForeignKey('TaxKey', on_delete=models.PROTECT, null=True)
    posting_text = models.CharField(max_length=200) 
    
    # Neue Klassifizierungen gem. GoBD-Ergänzung 2024
    # Diese Werte müssen fest im System hinterlegt sein (Choices/Enums)
    account_type = models.CharField(
        max_length=20,
        choices=[
            ('BALANCE', 'Bilanz'),
            ('PL', 'GuV'),
            ('DEBTOR', 'Debitor'),
            ('CREDITOR', 'Kreditor'),
            ('TAX', 'Steuerlicher Gewinn/Außerbilanziell'),
            ('OTHER', 'Sonstige')
        ],
        help_text="Kontotyp gemäß GoBD Rz. 94 (neu 2024)"
    )
    
    account_kind = models.CharField(
        max_length=20,
        choices=[
            ('ASSET', 'Aktiva'),
            ('LIABILITY', 'Passiva'),
            ('EQUITY', 'Eigenkapital'),
            ('EXPENSE', 'Aufwand'),
            ('REVENUE', 'Ertrag'),
            ('OTHER', 'Sonstige')
        ],
        help_text="Kontoart gemäß GoBD Rz. 94 (neu 2024)"
    )
    
    # 6. Unveränderbarkeit
    is_locked = models.BooleanField(default=False)
    
    def save(self, *args, **kwargs):
        if self.is_locked:
            raise ValidationError("Änderung an festgeschriebener Buchung verboten!")
        super().save(*args, **kwargs)
```

---

## 3. Dokumenten-Management (DMS)

### 3.1 Das Dokument (`Document`)
Erfüllt Aufbewahrungspflichten (§ 147 AO).

```python
# apps/documents/models.py
class Document(BaseModel):
    file = models.FileField(upload_to='documents/%Y/%m/')
    
    # Metadaten für Suche & Prüfung
    doc_type = models.CharField(choices=DocumentType.choices) # Rechnung, Lieferschein...
    doc_date = models.DateField()
    doc_number = models.CharField(max_length=100)
    
    # Integritätssicherung
    checksum_sha256 = models.CharField(max_length=64, editable=False)
    
    # Aufbewahrungsfrist
    retention_until = models.DateField()
    
    def save(self, *args, **kwargs):
        # Hash berechnen vor Speichern
        if self.file:
            self.checksum_sha256 = calculate_sha256(self.file)
        
        # Frist berechnen (z.B. 10 Jahre für Rechnungen)
        if not self.retention_until:
            self.retention_until = calculate_retention_date(self.doc_type, self.doc_date)
            
        super().save(*args, **kwargs)
```

---

## 4. Implementierungs-Muster (Best Practices)

### 4.1 Service Layer Pattern
**Business-Logik gehört NICHT in Views!**

```python
# apps/invoices/services.py
@transaction.atomic
def create_invoice(user: User, data: dict) -> Invoice:
    """
    Erstellt Rechnung und generiert Buchungssatz + Audit Log.
    """
    # 1. Rechnung erstellen
    invoice = Invoice.objects.create(...)
    
    # 2. PDF generieren & als Dokument archivieren
    pdf_content = generate_pdf(invoice)
    doc = Document.objects.create(
        file=ContentFile(pdf_content, name=f'{invoice.number}.pdf'),
        doc_type='INVOICE_OUT',
        # ...
    )
    invoice.document = doc
    invoice.save()
    
    # 3. Offene-Posten-Buchung (Vollständigkeit!)
    JournalEntry.objects.create(
        document=doc,
        account_debit=get_account('Receivables'),
        account_credit=get_account('Revenue'),
        amount=invoice.total,
        posting_text=f"Rechnung {invoice.number}"
    )
    
    # 4. Audit Log (Explizit oder via Signals)
    log_action(user, 'INVOICE_CREATED', invoice)
    
    return invoice
```

---

## 5. Export-Schnittstellen (Prüfung)

### 5.1 Z3-Zugriff (Datenüberlassung)
Zwingend erforderlich für Betriebsprüfungen (IDEA-Format oder Beschreibungsstandard).

**Implementierung:**
- CSV-Export aller steuerrelevanten Tabellen
- `index.xml` Beschreibungsdatei (nach "GoBD / § 147 AO" / GoBD-Standard)
- Funktion: `services.export.create_z3_package(year)`

### 5.2 Verfahrensdokumentation
Das System muss helfen, die Verfahrensdokumentation zu generieren.
- **Modulbeschreibung**: Welche Module sind aktiv?
- **Versionshistorie**: Wann wurde welche Version eingesetzt?
- **User-Rollen**: Wer darf was?

---

## 6. Checkliste für Code-Reviews (Compliance)

Bevor Code gemerged wird, prüfe:

- [ ] **Erbt das neue Model von `BaseModel`?**
- [ ] **Gibt es für schreibende Aktionen einen Service?** (Keine Logik in Views!)
- [ ] **Werden Transaktionen (`@transaction.atomic`) genutzt?** (Datenkonsistenz)
- [ ] **Ist `delete()` geschützt?** (Soft-Delete statt Hard-Delete für Stammdaten)
- [ ] **Gibt es Tests für die Berechnungslogik?**
- [ ] **Werden Beträge als `Decimal` (nicht Float) gespeichert?**

---

## Quellen & Referenzen
- **GoBD 2019**: BMF-Schreiben vom 28.11.2019
- **AO § 146 / § 147**: Buchführung und Aufbewahrung
- **HGB § 238 ff.**: Handelsrechtliche Grundlagen

---

**Ende des Leitfadens**
