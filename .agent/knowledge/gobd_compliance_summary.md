# GoBD-Checkliste - Compliance Summary

## Zweck
Zusammenfassung der wichtigsten Anforderungen aus den **Grundsätzen zur ordnungsmäßigen Führung und Aufbewahrung von Büchern, Aufzeichnungen und Unterlagen in elektronischer Form sowie zum Datenzugriff (GoBD)** für das ERP-System mit Dokumentenmanagement.

**Quelle:** Bitkom GoBD-Checkliste für Dokumentenmanagement-Systeme (Version 2.0)

## Was sind die GoBD?

Die GoBD sind ein BMF-Schreiben vom **28. November 2019**, das die Anforderungen an IT-gestützte Buchführungssysteme aus Sicht der Finanzverwaltung definiert. Sie ersetzen die GoBS und GDPdU.

**Anwendbar ab:** Besteuerungszeiträume nach dem 31. Dezember 2019

**Betroffen:** Alle Unternehmen mit IT-gestützten Buchführungs- und Aufzeichnungsprozessen

## Wichtigste Änderungen in der Neufassung 2019

1. ✅ **Mobiles Scannen** mit Smartphones gleichgestellt
2. ✅ **Bildliche Erfassung im Ausland** zulässig
3. ✅ **Ersetzendes Konvertieren** unter bestimmten Voraussetzungen erlaubt
4. ✅ **Z3-Zugriff** nach Systemwechsel/Auslagerung ausreichend

## Die 6 Grundprinzipien der GoBD

### 1. Nachvollziehbarkeit (GoBD Kap. 2.1)

**Anforderung:**
- Geschäftsvorfälle müssen in ihrer Entstehung und Abwicklung lückenlos verfolgbar sein
- Progressive Prüfung: Vom Beleg zur Buchung
- Retrograde Prüfung: Von der Buchung zum Beleg

**Für DMS/ERP:**
- Protokollierung aller Erfassungsaktionen (Import, Scan, Indizierung, Archivierung)
- Versionierung bei Änderungen
- Audit-Trail mit Datum/Uhrzeit und beteiligten Personen
- Belegprinzip: Jede Buchung muss durch Beleg nachgewiesen werden

**Implementierung:**
```python
class Document(BaseModel):
    """GoBD-konformes Dokumentenmodell."""
    # Nachvollziehbarkeit
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT)
    captured_at = models.DateTimeField()  # Zeitpunkt der Erfassung
    archived_at = models.DateTimeField(null=True)
    
    # Versionierung
    version = models.IntegerField(default=1)
    previous_version = models.ForeignKey('self', null=True, on_delete=models.PROTECT)
    
    # Audit-Trail
    audit_log = models.JSONField(default=list)  # Alle Änderungen
```

> **⭐ IDW PS 880 Checkliste 1.3 - ADMIN-LOGGING:**  
> Anforderung: "Werden Eingriffe von Administratoren protokolliert?"
>
> **Problem:** AuditLog deckt User-Aktionen ab. Aber was, wenn der "Super-Admin" direkt in der Datenbank etwas ändert?
>
> **Lösung:** Gesondertes Admin-Logging!

**Implementierung - Admin-Logging:**
```python
# apps/core/models.py
class AdminAuditLog(BaseModel):
    """
    IDW PS 880 Checkliste 1.3: Protokollierung von Administrationstätigkeiten.
    
    Separate Protokollierung für Admin-Eingriffe (z.B. User-Rechte ändern, DB-Zugriff).
    """
    admin_user = models.ForeignKey(User, on_delete=models.PROTECT)
    action_type = models.CharField(max_length=50, choices=[
        ('USER_RIGHTS_CHANGED', 'Benutzerrechte geändert'),
        ('DIRECT_DB_ACCESS', 'Direkter Datenbankzugriff'),
        ('SYSTEM_CONFIG_CHANGED', 'Systemkonfiguration geändert'),
        ('BACKUP_RESTORED', 'Backup wiederhergestellt'),
        ('DATA_EXPORT', 'Datenexport durchgeführt'),
    ])
    target_user = models.ForeignKey(User, on_delete=models.PROTECT, related_name='admin_actions', null=True)
    target_object = models.CharField(max_length=200)  # z.B. "User: max.mustermann"
    old_value = models.TextField(null=True)
    new_value = models.TextField(null=True)
    reason = models.TextField()  # Pflicht!
    ip_address = models.GenericIPAddressField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Admin-Audit-Log'
```

### 2. Vollständigkeit (GoBD Kap. 2.2.1)

**Anforderung:**
- Alle Geschäftsvorfälle müssen vollzählig und lückenlos aufgezeichnet werden
- Einzelaufzeichnungspflicht
- Keine Verdichtung oder Zusammenfassung

**Für DMS/ERP:**
- Lückenlose Erfassung aller rechnungslegungsrelevanten Dokumente
- Vollständige Erfassung von E-Mails inkl. Anhängen
- Transaktionskontrolle bei Datenübernahme
- Vermeidung doppelter Erfassung

**Checkliste:**
- [ ] Vollständige Erfassung aller Belege (Einzelaufzeichnung)
- [ ] **Plausibilitätskontrollen bei Eingabe** (IDW PS 880 Checkliste 2.2)
- [ ] Zählen von Belegen und Abgleich
- [ ] **Lückenanalyse + Erzwingung lückenloser Nummernkreise** (IDW PS 880 Checkliste 2.1)
- [ ] Keine Löschmöglichkeit vor Ende der Aufbewahrungsfrist
- [ ] Historisierung von Stammdaten

> **⭐ IDW PS 880 Checkliste 2.2 - PLAUSIBILITÄTSKONTROLLEN:**  
> Anforderung: "Werden Eingaben automatisch auf Plausibilität geprüft (z. B. zulässige Wertebereiche, logische Zusammenhänge)?"
>
> **Problem:** System akzeptiert aktuell technisch alles, solange das Format stimmt.  
> **Lösung:** ERP muss "Fachlichkeit" prüfen!

**Implementierung - Input Validation:**
```python
# apps/finance/validators.py
from datetime import date, timedelta
from django.core.exceptions import ValidationError

def validate_journal_entry(entry) -> None:
    """
    IDW PS 880 / GoBD Checkliste 2.2: Plausibilitätsprüfungen
    Verhindert "Unsinnige" Eingaben vor der Speicherung.
    """
    # 1. Datums-Check
    if entry.booking_date > date.today() + timedelta(days=1):
        raise ValidationError("Buchungen in der fernen Zukunft sind unplausibel.")
    
    # 2. Betrags-Check
    if entry.amount <= 0:
        raise ValidationError("Betrag muss positiv sein (Haben/Soll steuert Vorzeichen).")
        
    # 3. Konten-Logik
    if entry.account == entry.contra_account:
        raise ValidationError("Soll- und Habenkonto dürfen nicht identisch sein.")
    
    # 4. Periodenabgrenzung
    if entry.fiscal_period < 1 or entry.fiscal_period > 12:
        raise ValidationError("Ungültige Periode (muss 1-12 sein).")
    
    # 5. IBAN-Check (bei Bankbuchungen)
    if entry.account.startswith('1200'):  # Bankkonto
        if not validate_iban(entry.contra_account_iban):
            raise ValidationError("Ungültige IBAN.")


def validate_invoice(invoice) -> None:
    """
    Plausibilitätsprüfungen für Rechnungen.
    """
    # USt-ID Format prüfen
    if invoice.customer.vat_id:
        if not validate_vat_id_format(invoice.customer.vat_id):
            raise ValidationError("Ungültiges USt-ID Format.")
    
    # Rechnungsdatum vs. Leistungsdatum
    if invoice.service_date > invoice.invoice_date:
        raise ValidationError("Leistungsdatum darf nicht nach Rechnungsdatum liegen.")
    
    # Zahlungsziel plausibel?
    if invoice.due_date < invoice.invoice_date:
        raise ValidationError("Fälligkeitsdatum vor Rechnungsdatum ist unplausibel.")
```

### 3. Richtigkeit (GoBD Kap. 2.2.2)

**Anforderung:**
- Geschäftsvorfälle müssen in Übereinstimmung mit den tatsächlichen Verhältnissen abgebildet werden
- Bildliche Übereinstimmung bei Eingangsdokumenten
- Inhaltliche Übereinstimmung bei Ausgangsdokumenten

**Für DMS/ERP:**
- Korrekte Erfassung der Belege (keine Verfälschung)
- Zuverlässige Indexierung
- Fehlerhandling bei fehlerhaften Belegen

**Implementierung:**
```python
def validate_document_integrity(document: Document) -> bool:
    """
    Prüft Integrität eines Dokuments.
    """
    # Checksumme prüfen
    calculated_hash = hashlib.sha256(document.content).hexdigest()
    if calculated_hash != document.checksum:
        raise IntegrityError("Dokument wurde verändert!")
    
    # Bildliche Übereinstimmung bei Scans
    if document.is_scanned:
        if not validate_scan_quality(document):
            raise ValidationError("Scan-Qualität unzureichend!")
    
    return True
```

### 4. Zeitgerechte Belegsicherung (GoBD Kap. 2.2.3)

**Anforderung:**
- Belege sind zeitnah einer Belegsicherung zuzuführen
- Schutz vor Verlust und Manipulation

**Für DMS/ERP:**
- Archivierung zum frühestmöglichen Zeitpunkt
- Automatische Archivierung nach Erfassung
- Datumsfeld für Archivierungszeitpunkt

**Empfehlung:**
- Eingangsrechnungen: Archivierung innerhalb von 10 Tagen nach Eingang
- Ausgangsrechnungen: Archivierung unmittelbar nach Erstellung

### 5. Ordnung (GoBD Kap. 2.2.4)

**Anforderung:**
- Aufzeichnungen müssen geordnet sein
- Eindeutige Identifizierung und Auffindbarkeit
- Sachgerechte Ablage

**Für DMS/ERP:**
- Eindeutige Indexierung (z.B. Belegnummer, Datum, Lieferant)
- Suchfunktionen
- Logische Ordnungsstruktur

**Implementierung:**
```python
class DocumentIndex(models.Model):
    """Indexdaten für schnelle Suche."""
    document = models.OneToOneField(Document, on_delete=models.CASCADE)
    
    # Pflichtindexfelder
    document_type = models.CharField(max_length=50)  # Rechnung, Beleg, etc.
    document_number = models.CharField(max_length=100, unique=True)
    document_date = models.DateField()
    
    # Optionale Indexfelder
    supplier = models.CharField(max_length=200, blank=True)
    customer = models.CharField(max_length=200, blank=True)
    amount = models.DecimalField(max_digits=14, decimal_places=2, null=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['document_type', 'document_date']),
            models.Index(fields=['document_number']),
        ]
```

### 6. Unveränderbarkeit (GoBD Kap. 2.2.5)

**Anforderung:**
- Aufzeichnungen dürfen nicht nachträglich verändert werden
- Änderungen müssen nachvollziehbar sein (Versionierung)

**Für DMS/ERP:**
- Technische Unveränderbarkeit durch Archivierungssystem
- Versionierung bei Änderungen
- Protokollierung aller Änderungen

**Implementierung:**
```python
def archive_document(document: Document) -> ArchivedDocument:
    """
    Archiviert Dokument unveränderbar.
    """
    # Checksumme berechnen
    checksum = hashlib.sha256(document.content).hexdigest()
    
    # Unveränderbar archivieren
    archived = ArchivedDocument.objects.create(
        document_id=document.id,
        content_hash=checksum,
        encrypted_content=encrypt(document.content),
        archived_at=timezone.now(),
        archived_by=document.created_by,
        retention_until=calculate_retention_date(document)
    )
    
    # Original als "archiviert" markieren
    document.is_archived = True
    document.archived_reference = archived.id
    document.save()
    
    return archived

def modify_document(document: Document, new_content: bytes, user: User) -> Document:
    """
    Ändert Dokument mit Versionierung.
    """
    # Neue Version erstellen
    new_version = Document.objects.create(
        content=new_content,
        version=document.version + 1,
        previous_version=document,
        created_by=user,
        # ... weitere Felder
    )
    
    # Audit-Log
    AuditLog.objects.create(
        document=new_version,
        action='MODIFY',
        user=user,
        changes={'previous_version': document.id}
    )
    
    return new_version
```

---

## Internes Kontrollsystem (IKS) ⭐ **IDW PS 880 CHECKLISTE 1.1**

> **⭐ IDW PS 880 Checkliste 1.1 - FUNKTIONSTRENNUNG:**  
> Anforderung: "Ist eine Funktionstrennung eingerichtet (z. B. Trennung von Erfassung und Freigabe)?"
>
> **4-Augen-Prinzip:** Derjenige, der die Rechnung erfasst, darf sie **nicht** auch freigeben/bezahlen!

### Funktionstrennung / 4-Augen-Prinzip

**Implementierung:**
```python
# apps/finance/models.py
class InvoiceApproval(BaseModel):
    """
    IDW PS 880 / GoBD Checkliste 1.1: Funktionstrennung
    4-Augen-Prinzip: Erfasser != Freigeber
    """
    invoice = models.ForeignKey('sales.Invoice', on_delete=models.PROTECT)
    
    # Der Erfasser
    created_by = models.ForeignKey(User, related_name='created_invoices', on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Der Freigeber (muss eine andere Person sein!)
    approved_by = models.ForeignKey(
        User, 
        related_name='approved_invoices', 
        on_delete=models.PROTECT, 
        null=True, 
        blank=True
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    
    # Status
    status = models.CharField(max_length=20, choices=[
        ('DRAFT', 'Entwurf'),
        ('PENDING_APPROVAL', 'Wartet auf Freigabe'),
        ('APPROVED', 'Freigegeben'),
        ('REJECTED', 'Abgelehnt'),
    ], default='DRAFT')
    
    rejection_reason = models.TextField(blank=True)
    
    def clean(self):
        """IKS Regel: Niemand darf seine eigenen Rechnungen freigeben."""
        if self.approved_by and self.approved_by == self.created_by:
            raise ValidationError(
                "IKS-Verstoß: Funktionstrennung verletzt. "
                "Erfasser darf nicht Freigeber sein."
            )
    
    def approve(self, user: User):
        """Gibt Rechnung frei (mit IKS-Check)."""
        if user == self.created_by:
            raise ValidationError("Sie dürfen Ihre eigenen Rechnungen nicht freigeben!")
        
        self.approved_by = user
        self.approved_at = timezone.now()
        self.status = 'APPROVED'
        self.save()
        
        # Audit-Log
        AuditLog.objects.create(
            content_object=self,
            action='APPROVE',
            user=user,
            new_values={'status': 'APPROVED'}
        )


# apps/finance/models.py
class PaymentApproval(BaseModel):
    """
    4-Augen-Prinzip für Zahlungen.
    
    Trennung: Zahlungsanweisung erstellen != Zahlung freigeben
    """
    payment = models.ForeignKey('finance.Payment', on_delete=models.PROTECT)
    
    # Zahlungsanweisung erstellt von
    created_by = models.ForeignKey(User, related_name='created_payments', on_delete=models.PROTECT)
    
    # Zahlung freigegeben von (muss andere Person sein!)
    approved_by = models.ForeignKey(
        User, 
        related_name='approved_payments', 
        on_delete=models.PROTECT, 
        null=True
    )
    approved_at = models.DateTimeField(null=True)
    
    # Zahlung ausgeführt von (kann gleich approved_by sein)
    executed_by = models.ForeignKey(
        User, 
        related_name='executed_payments', 
        on_delete=models.PROTECT, 
        null=True
    )
    executed_at = models.DateTimeField(null=True)
    
    def clean(self):
        """IKS: Ersteller != Freigeber."""
        if self.approved_by and self.approved_by == self.created_by:
            raise ValidationError(
                "IKS-Verstoß: Sie dürfen Ihre eigenen Zahlungen nicht freigeben!"
            )
```

### Lückenlosigkeit der Nummernkreise

> **⭐ IDW PS 880 Checkliste 2.1 - LÜCKENLOSE NUMMERNKREISE:**  
> Anforderung: "Ist sichergestellt, dass Belegnummern lückenlos und fortlaufend vergeben werden?"
>
> **Status in Summary:** "Gap Detection required" ist gut, aber Checkliste fordert oft **technische Erzwingung** (Auto-Increment) statt nur nachträglicher Prüfung.

**Implementierung:**
```python
# apps/core/models.py
class NumberRange(BaseModel):
    """
    IDW PS 880 Checkliste 2.1: Lückenlose Nummernkreise.
    
    Erzwingt lückenlose, fortlaufende Belegnummern.
    """
    name = models.CharField(max_length=50, unique=True)  # z.B. "INVOICE_2024"
    prefix = models.CharField(max_length=10)  # z.B. "RE-"
    current_number = models.IntegerField(default=1)
    year = models.IntegerField()
    
    # Locking für Concurrency
    is_locked = models.BooleanField(default=False)
    
    class Meta:
        unique_together = [['prefix', 'year']]
    
    def get_next_number(self) -> str:
        """
        Gibt nächste Nummer zurück (atomar, lückenlos).
        
        Nutzt SELECT FOR UPDATE für Concurrency-Safety.
        """
        from django.db import transaction
        
        with transaction.atomic():
            # Lock Row
            number_range = NumberRange.objects.select_for_update().get(id=self.id)
            
            # Nächste Nummer
            next_num = number_range.current_number
            number_range.current_number += 1
            number_range.save()
            
            # Format: RE-2024-00001
            return f"{number_range.prefix}{number_range.year}-{next_num:05d}"


# apps/sales/models.py
class Invoice(BaseModel):
    """
    Rechnung mit lückenloser Nummerierung.
    """
    invoice_number = models.CharField(max_length=100, unique=True, editable=False)
    
    def save(self, *args, **kwargs):
        """Generiert lückenlose Rechnungsnummer beim Erstellen."""
        if not self.invoice_number:
            # Hole Nummernkreis für aktuelles Jahr
            number_range, created = NumberRange.objects.get_or_create(
                prefix='RE-',
                year=date.today().year,
                defaults={'current_number': 1}
            )
            
            # Lückenlose Nummer
            self.invoice_number = number_range.get_next_number()
        
        super().save(*args, **kwargs)
```

**Checkliste IKS:**
- [ ] **Funktionstrennung implementiert** (Erfasser != Freigeber)
- [ ] **4-Augen-Prinzip für Rechnungen**
- [ ] **4-Augen-Prinzip für Zahlungen**
- [ ] **Lückenlose Nummernkreise erzwungen** (Auto-Increment)
- [ ] **Admin-Logging für privilegierte Aktionen**
- [ ] **Plausibilitätskontrollen bei Eingabe**

---

## Besondere Anforderungen für DMS

### Mobiles Scannen (GoBD Kap. 3.2)

**Erlaubt:**
- Erfassung mit Smartphones, Tablets
- Erfassung im Ausland
- Verbringen von Papierbelegen ins Ausland zur Digitalisierung

**Anforderungen:**
- Bildliche Übereinstimmung
- Lesbarkeit
- Vollständigkeit
- Verfahrensdokumentation

### Ersetzendes Konvertieren (GoBD Kap. 2.3)

**Voraussetzungen für Vernichtung des Originals:**
- Keine inhaltliche Veränderung
- Kein Verlust an Informationen
- Maschinelle Auswertbarkeit bleibt erhalten
- Verfahrensdokumentation vorhanden

**Beispiel:** PDF → PDF/A (Langzeitarchivierung)

**Nicht erlaubt:** Vernichtung von Papierbelegen nach Scannen (außer bei ersetzender Konvertierung)

### E-Mail-Archivierung (GoBD Kap. 4.4)

**Pflicht:**
- Geschäftliche E-Mails sind aufbewahrungspflichtig
- E-Mails inkl. Anhänge vollständig archivieren
- Keine Manipulation möglich

**Implementierung:**
```python
def archive_email(email: EmailMessage) -> ArchivedEmail:
    """
    Archiviert E-Mail GoBD-konform.
    """
    # E-Mail mit allen Anhängen erfassen
    archived = ArchivedEmail.objects.create(
        subject=email.subject,
        sender=email.from_email,
        recipients=email.to,
        body=email.body,
        received_at=email.date,
        archived_at=timezone.now()
    )
    
    # Anhänge archivieren
    for attachment in email.attachments:
        ArchivedAttachment.objects.create(
            email=archived,
            filename=attachment.name,
            content=attachment.content,
            content_type=attachment.content_type
        )
    
    return archived
```

## Datenzugriff der Finanzbehörden (GoBD Kap. 5)

### Drei Zugriffsarten (Z1, Z2, Z3)

**Z1 - Unmittelbarer Zugriff:**
- Prüfer arbeitet selbst am System
- Lesender Zugriff auf alle Daten

**Z2 - Mittelbarer Zugriff:**
- Unternehmen führt Auswertungen durch
- Prüfer gibt Suchkriterien vor

**Z3 - Datenüberlassung (Datenträger oder Datenaustauschplattform):**
- Daten werden auf Datenträger übergeben
- Standardformat (z.B. Z3-Export)

**Für ERP-System:**
```python
def export_gobd_data(start_date: date, end_date: date) -> bytes:
    """
    Exportiert Daten für Betriebsprüfung (Z3).
    """
    # Alle relevanten Daten im Zeitraum
    documents = Document.objects.filter(
        document_date__gte=start_date,
        document_date__lte=end_date
    )
    
    # konform zum Beschreibungsstandard
    export_data = {
        'documents': [
            {
                'id': doc.id,
                'type': doc.document_type,
                'number': doc.document_number,
                'date': doc.document_date.isoformat(),
                'amount': str(doc.amount),
                'file': doc.file.url
            }
            for doc in documents
        ]
    }
    
    # Als XML exportieren
    return generate_index_xml(export_data)
```

## Verfahrensdokumentation (GoBD Kap. 6)

**Pflicht:** Jedes IT-System muss dokumentiert sein!

**Inhalt:**
1. **Allgemeine Beschreibung**
   - Zweck des Systems
   - Organisatorische Einbindung
   - Anwenderkreis

2. **Anwenderdokumentation**
   - Bedienungsanleitung
   - Arbeitsanweisungen

3. **Technische Systemdokumentation**
   - Systemarchitektur
   - Schnittstellen
   - Datenmodell

4. **Betriebsdokumentation**
   - Datensicherung
   - Archivierung
   - Notfallkonzept

5. **Änderungshistorie**
   - Alle Änderungen dokumentieren
   - Versionierung

**Beispiel-Struktur:**
```
/docs/verfahrensdokumentation/
├── 01_Allgemeine_Beschreibung.md
├── 02_Anwenderdokumentation.md
├── 03_Technische_Dokumentation.md
├── 04_Betriebsdokumentation.md
├── 05_Aenderungshistorie.md
└── Anlagen/
    ├── Datenmodell.pdf
    ├── Schnittstellenbeschreibung.pdf
    └── Berechtigungskonzept.pdf
```

## Aufbewahrungsfristen

| Dokument | Frist | Rechtsgrundlage |
|----------|-------|-----------------|
| Bücher, Inventare, Jahresabschlüsse | 10 Jahre | § 147 Abs. 3 AO |
| Buchungsbelege, Rechnungen | 10 Jahre | § 147 Abs. 3 AO |
| Geschäftsbriefe | 6 Jahre | § 147 Abs. 4 AO |
| Sonstige Unterlagen | 6 Jahre | § 147 Abs. 4 AO |

**Fristbeginn:** Ende des Kalenderjahres, in dem die letzte Eintragung erfolgte

## Sanktionen bei Verstößen

- **Verwerfung der Buchführung** → Schätzung der Besteuerungsgrundlagen
- **Zuschlag bei Schätzung:** 5-10% der festgesetzten Steuer (§ 162 Abs. 4 AO)
- **Verspätungszuschlag:** 0,25% pro Monat (§ 152 AO)
- **Steuerhinterziehung:** Freiheitsstrafe bis 5 Jahre (§ 370 AO)

## GoBD-Checkliste für ERP-System

### Allgemein
- [ ] Verfahrensdokumentation erstellt und aktuell
- [ ] Alle 6 Grundprinzipien umgesetzt
- [ ] Audit-Logging implementiert
- [ ] Versionierung bei Änderungen
- [ ] Aufbewahrungsfristen eingehalten

### Erfassung
- [ ] Vollständige Erfassung aller Belege
- [ ] Zeitnahe Archivierung
- [ ] Bildliche Übereinstimmung bei Scans
- [ ] Korrekte Indexierung

### Archivierung
- [ ] Unveränderbare Speicherung
- [ ] Langzeitformate (z.B. PDF/A)
- [ ] Keine Löschung vor Fristablauf
- [ ] Checksummen-Prüfung

### Zugriff
- [ ] Datenzugriff Z1/Z2/Z3 möglich
- [ ] Z3-Export implementiert
- [ ] Suchfunktionen vorhanden
- [ ] Berechtigungskonzept

### E-Mail
- [ ] Geschäftliche E-Mails archiviert
- [ ] Anhänge vollständig erfasst
- [ ] Unveränderbare Speicherung

### Journalangaben (GoBD 2024 Update)
- [ ] Kontoart (Aktiva/Passiva...) erfasst?
- [ ] Kontotyp (Bilanz/GuV...) erfasst?
- [ ] Eindeutige Transaktions-ID vorhanden?

## Zusammenspiel mit AO und DSGVO

**AO (Aufbewahrungspflichten):**
- GoBD konkretisiert § 146-147 AO
- Aufbewahrungsfristen: 6-10 Jahre

**DSGVO (Datenschutz):**
- Löschpflicht nach DSGVO vs. Aufbewahrungspflicht nach AO
- **Lösung:** Aufbewahrungspflichten gehen vor (Art. 17 Abs. 3 lit. b DSGVO)
- Nach Ablauf: Löschung nach DSGVO

## Nächste Schritte

1. ✅ GoBD_Checkliste.md gelesen
2. ⬜ Verfahrensdokumentation erstellen
3. ⬜ Audit-Logging implementieren
4. ⬜ Versionierung implementieren
5. ⬜ Archivierungskonzept entwickeln
6. ⬜ Z3-Export implementieren
7. ⬜ E-Mail-Archivierung implementieren

---

**Quelle:** `.agent/knowledge/GoBD_Checkliste.md` (Bitkom, Version 2.0)  
**Hinweis:** Bei rechtlichen Fragen Steuerberater konsultieren.
