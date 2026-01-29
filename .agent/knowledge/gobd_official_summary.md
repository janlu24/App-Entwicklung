# GoBD - Offizielles BMF-Schreiben (Konsolidierte Fassung)

## Dokumentenübersicht

**Quelle:** Bundesministerium der Finanzen (BMF)  
**Ursprungsfassung:** 28. November 2019 (BStBl I S. 1269)  
**Aktuelle Änderung:** 11. März 2024  
**Gültig ab:** 1. April 2024  
**Anwendbar auf:** Besteuerungszeiträume nach dem 31. Dezember 2019

**Vollständiger Titel:**  
*Grundsätze zur ordnungsmäßigen Führung und Aufbewahrung von Büchern, Aufzeichnungen und Unterlagen in elektronischer Form sowie zum Datenzugriff (GoBD)*

## Was sind die GoBD?

Die GoBD sind **verbindliche Verwaltungsanweisungen** der Finanzverwaltung, die die Anforderungen an IT-gestützte Buchführungs- und Aufzeichnungssysteme konkretisieren. Sie ersetzen die früheren GoBS (Grundsätze ordnungsmäßiger DV-gestützter Buchführungssysteme) und GDPdU (Grundsätze zum Datenzugriff und zur Prüfbarkeit digitaler Unterlagen).

**Rechtsgrundlagen:**
- § 140 AO: Nutzbarmachung außersteuerlicher Buchführungspflichten
- §§ 145-147 AO: Ordnungsvorschriften für Buchführung und Aufzeichnungen
- §§ 238 ff. HGB: Handelsrechtliche Grundsätze ordnungsmäßiger Buchführung (GoB)

## 1. Anwendungsbereich

### 1.1 Wer ist betroffen?

**Alle Unternehmen**, die:
- Buchführungspflichtig sind (nach HGB oder AO)
- Steuerliche Aufzeichnungspflichten haben
- DV-Systeme für Buchführung/Aufzeichnungen einsetzen

**Auch freiwillig:** Nach § 146 Abs. 6 AO gelten die GoBD auch für freiwillig elektronisch geführte Bücher.

### 1.2 Welche Systeme sind betroffen?

**DV-System (Rz. 20):** Alle Hard- und Software zur elektronischen Datenverarbeitung, mit denen Daten:
- Erfasst, erzeugt, empfangen werden
- Verarbeitet, gespeichert, übermittelt werden

**Beispiele:**
- Finanzbuchhaltung, Anlagenbuchhaltung, Lohnbuchhaltung
- Kassensysteme, Warenwirtschaftssysteme
- Fakturierungssysteme, Zeiterfassung
- Dokumenten-Management-Systeme (DMS)
- Archivsysteme
- Cloud-basierte Systeme

**Wichtig:** Es kommt nicht auf die Bezeichnung oder Größe des Systems an!

### 1.3 Welche Daten sind betroffen?

**Aufzeichnungs- und aufbewahrungspflichtig (Rz. 3-5):**
- Bücher (Handelsbücher, Journal, Hauptbuch)
- Aufzeichnungen (Grund(buch)aufzeichnungen, Belege)
- Unterlagen zu Geschäftsvorfällen
- Alle Unterlagen zum Verständnis und zur Überprüfung

**In allen Formaten:**
- Daten, Datensätze
- Elektronische Dokumente
- Papierform (soweit relevant)

## 2. Verantwortlichkeit (Rz. 21)

**Steuerpflichtiger ist allein verantwortlich** für:
- Ordnungsmäßigkeit elektronischer Bücher und Aufzeichnungen
- Eingesetzte Verfahren
- Einhaltung der Ordnungsvorschriften

**Gilt auch bei Auslagerung** (z.B. an Steuerberater, Rechenzentrum, Cloud-Anbieter)!

## 3. Die 6 Grundprinzipien der GoBD

### 3.1 Nachvollziehbarkeit und Nachprüfbarkeit (Rz. 30-35)

**Anforderung:**
- Geschäftsvorfälle müssen in ihrer Entstehung und Abwicklung lückenlos verfolgbar sein
- **Progressive Prüfung:** Vom Beleg → Buchung → Konto → Bilanz → Steuererklärung
- **Retrograde Prüfung:** Von der Steuererklärung → Bilanz → Konto → Buchung → Beleg

**Für ERP-System:**
```python
class Transaction(BaseModel):
    """GoBD-konforme Transaktion mit vollständiger Nachvollziehbarkeit."""
    # Progressive Prüfbarkeit
    document_id = models.UUIDField()  # Beleg
    journal_entry_id = models.UUIDField()  # Buchung
    account_id = models.UUIDField()  # Konto
    
    # Retrograde Prüfbarkeit
    tax_return_line = models.CharField(max_length=50, null=True)
    balance_sheet_position = models.CharField(max_length=50, null=True)
    
    # Audit-Trail
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT)
    
    # Verfahrensdokumentation
    processing_log = models.JSONField(default=list)
```

**Verfahrensdokumentation (Rz. 34, 151-155):**
- Aussagekräftig und vollständig
- Für sachverständigen Dritten verständlich
- Historisch nachvollziehbar (Versionierung)
- Muss während gesamter Aufbewahrungsfrist vorhanden sein

> **⭐ ERP-FEATURE:** Das System sollte helfen, diese Dokumentation zu erstellen!  
> **Versionierung von Systemeinstellungen:** Wenn du die MwSt-Logik änderst, muss das System speichern:  
> "Bis 31.12. war Logik A aktiv, ab 01.01. Logik B"
>
> **Export-Funktion:** Modul oder Export "Verfahrensdokumentation", das die Konfiguration des Systems menschenlesbar ausgibt.

### 3.2 Vollständigkeit (Rz. 36-43)

**Anforderung:**
- Alle Geschäftsvorfälle vollzählig und lückenlos aufzeichnen
- **Einzelaufzeichnungspflicht** (§ 146 Abs. 1 AO)
- Keine Verdichtung oder Zusammenfassung

**Ausnahmen (Rz. 39):**
- Offene Ladenkasse bei Bargeschäften (§ 146 Abs. 1 Satz 3 AO)
- Nur wenn **technisch, betriebswirtschaftlich und praktisch unmöglich**

**Bei elektronischen Aufzeichnungssystemen:** Einzelaufzeichnungspflicht gilt **immer**!

**Kontrollen (Rz. 40):**
```python
def ensure_completeness(transactions: list[Transaction]) -> bool:
    """
    Stellt Vollständigkeit sicher.
    """
    # Erfassungskontrollen
    if not all(t.document_id for t in transactions):
        raise ValidationError("Fehlende Belegnummern!")
    
    # Plausibilitätskontrollen
    for t in transactions:
        if t.amount <= 0:
            raise ValidationError(f"Ungültiger Betrag: {t.amount}")
    
    # Lückenanalyse
    doc_numbers = sorted([t.document_number for t in transactions])
    for i in range(len(doc_numbers) - 1):
        if doc_numbers[i+1] - doc_numbers[i] > 1:
            logger.warning(f"Lücke zwischen {doc_numbers[i]} und {doc_numbers[i+1]}")
    
    # Mehrfachbelegungsanalyse
    if len(doc_numbers) != len(set(doc_numbers)):
        raise ValidationError("Doppelte Belegnummern!")
    
    return True
```

**Verboten (Rz. 41, 43):**
- Mehrfache Aufzeichnung desselben Geschäftsvorfalls
- Unterdrückung von Geschäftsvorfällen (z.B. Bon-Abbruch ohne Registrierung)

### 3.3 Richtigkeit (Rz. 44)

**Anforderung:**
- Geschäftsvorfälle in Übereinstimmung mit tatsächlichen Verhältnissen
- Wahrheitsgemäße Aufzeichnung
- Zutreffende Kontierung

**Für ERP-System:**
```python
def validate_transaction_accuracy(transaction: Transaction) -> bool:
    """
    Prüft Richtigkeit einer Transaktion.
    """
    # Inhaltliche Übereinstimmung
    if transaction.amount != transaction.document.total_amount:
        raise ValidationError("Betrag stimmt nicht mit Beleg überein!")
    
    # Kontierung prüfen
    if not is_valid_account(transaction.account_id):
        raise ValidationError("Ungültige Kontierung!")
    
    # Steuersatz prüfen
    if transaction.tax_rate not in VALID_TAX_RATES:
        raise ValidationError(f"Ungültiger Steuersatz: {transaction.tax_rate}")
    
    return True
```

### 3.4 Zeitgerechte Buchungen und Aufzeichnungen (Rz. 45-52)

**Anforderung:**
- Zeitnaher Zusammenhang zwischen Vorgang und Erfassung
- **Bare Geschäftsvorfälle:** Täglich (§ 146 Abs. 1 Satz 2 AO)
- **Unbare Geschäftsvorfälle:** Innerhalb von 10 Tagen

**Periodengerechte Zuordnung (Rz. 51):**
- Jeder Geschäftsvorfall der richtigen Abrechnungsperiode zuordnen

**Bei DV-Systemen (Rz. 52):**
- Erfassung unmittelbar nach Eingang/Entstehung
- Unprotokollierte Änderung nach Erfassung **nicht mehr zulässig**!

**⭐ FESTSCHREIBUNG (Rz. 88ff) - KRITISCH:**
> **Spätestens zum Ablauf des Folgemonats** (bei USt-Voranmeldung) müssen Buchungen **"festgeschrieben"** (nicht mehr änderbar) sein.
>
> **ERP-Feature:** `JournalEntry` braucht ein Feld `posted_at` (Festschreibedatum).  
> Das System muss einen **"Monatsabschluss-Lauf"** erzwingen, der alle vorläufigen Buchungen sperrt.  
> Ein reines "AuditLog" reicht hier **nicht** – der Status muss von "Draft" auf "Posted/Locked" wechseln.

**Implementierung:**
```python
def record_transaction(data: dict, user: User) -> Transaction:
    """
    Erfasst Transaktion zeitgerecht.
    """
    transaction = Transaction.objects.create(
        # Erfassungsdatum
        captured_at=timezone.now(),
        captured_by=user,
        
        # Belegdatum
        document_date=data['document_date'],
        
        # Buchungsdatum (kann später sein)
        booking_date=data.get('booking_date', timezone.now().date()),
        
        # Geschäftsjahr
        fiscal_year=get_fiscal_year(data['document_date']),
        
        # Weitere Felder
        **data
    )
    
    # Audit-Log
    AuditLog.objects.create(
        transaction=transaction,
        action='CREATE',
        user=user,
        timestamp=timezone.now()
    )
    
    return transaction
```

### 3.5 Ordnung (Rz. 53-57)

**Anforderung:**
- Systematische Erfassung
- Übersichtliche, eindeutige, nachvollziehbare Buchungen
- Geordnete Aufbewahrung

**Ordnungsprinzipien:**
- Zeitfolge (Journal)
- Sachgruppen (Konten)
- Belegnummern
- Alphabetisch

**Für ERP-System:**
```python
class DocumentIndex(models.Model):
    """Indexierung für geordnete Ablage."""
    document = models.OneToOneField(Document, on_delete=models.CASCADE)
    
    # Pflichtfelder
    document_type = models.CharField(max_length=50)  # Rechnung, Beleg, etc.
    document_number = models.CharField(max_length=100, unique=True)
    document_date = models.DateField()
    
    # Ordnungskriterien
    supplier = models.CharField(max_length=200, blank=True)
    customer = models.CharField(max_length=200, blank=True)
    fiscal_year = models.IntegerField()
    fiscal_period = models.IntegerField()
    
    # Sachliche Zuordnung
    account = models.CharField(max_length=20)
    cost_center = models.CharField(max_length=20, blank=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['document_type', 'document_date']),
            models.Index(fields=['document_number']),
            models.Index(fields=['fiscal_year', 'fiscal_period']),
        ]
```

### 3.6 Unveränderbarkeit (Rz. 58-60, 107-112)

**Anforderung (§ 146 Abs. 4 AO, § 239 Abs. 3 HGB):**
- Ursprünglicher Inhalt muss feststellbar bleiben
- Änderungen müssen protokolliert werden
- Keine nachträglichen Veränderungen ohne Nachweis

> **⚠️ PRAXIS-HINWEIS:**  
> **Hash-Chains** (Blockchain-Ansatz) sind oft **"Over-Engineering"** für GoBD!  
> Ein einfaches **"Festschreibekennzeichen"** (Datenbank-Flag `is_locked=True`) plus **Audit-Log** genügt meistens.  
> Hash-Chains sind nett, aber machen **Korrekturen (Storno)** technisch komplex.

**Protokollierung von Änderungen:**
```python
def modify_transaction(transaction: Transaction, new_data: dict, user: User) -> Transaction:
    """
    Ändert Transaktion mit vollständiger Protokollierung.
    """
    # Alte Werte sichern
    old_values = {
        'amount': transaction.amount,
        'account': transaction.account,
        'description': transaction.description,
        # ... weitere Felder
    }
    
    # Änderung protokollieren
    ChangeLog.objects.create(
        transaction=transaction,
        changed_by=user,
        changed_at=timezone.now(),
        old_values=old_values,
        new_values=new_data,
        reason=new_data.get('change_reason', '')
    )
    
    # Neue Werte setzen
    for key, value in new_data.items():
        setattr(transaction, key, value)
    
    transaction.version += 1
    transaction.last_modified_at = timezone.now()
    transaction.last_modified_by = user
    transaction.save()
    
    return transaction
```

**Historisierung von Stammdaten (Rz. 111):**
```python
class TaxRate(BaseModel):
    """Steuersatz mit Historisierung."""
    rate = models.DecimalField(max_digits=5, decimal_places=2)
    valid_from = models.DateField()
    valid_until = models.DateField(null=True)
    
    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(valid_until__isnull=True) | models.Q(valid_until__gte=models.F('valid_from')),
                name='valid_date_range'
            )
        ]
    
    @classmethod
    def get_rate_for_date(cls, date: date) -> Decimal:
        """Gibt den gültigen Steuersatz für ein Datum zurück."""
        rate = cls.objects.filter(
            valid_from__lte=date,
            models.Q(valid_until__isnull=True) | models.Q(valid_until__gte=date)
        ).first()
        
        if not rate:
            raise ValueError(f"Kein gültiger Steuersatz für {date}")
        
        return rate.rate
```

**Verboten (Rz. 112):**
- Einsatz von Zappern, Phantomware
- Backoffice-Produkte für unprotokollierte Änderungen
- Manipulationsprogramme

## 4. Belegwesen (Rz. 61-81)

### 4.1 Belegprinzip (Rz. 61)

**Anforderung:**
- Jeder Geschäftsvorfall muss durch Beleg nachgewiesen werden
- Urschrift oder Kopie
- Bei fehlendem Fremdbeleg: Eigenbeleg erstellen

**Belegfunktion:**
- Nachweis des Zusammenhangs zwischen Realität und Buchung
- Grundvoraussetzung für Beweiskraft der Buchführung

### 4.2 Belegsicherung (Rz. 67-70)

**Anforderung:**
- Zeitnah gegen Verlust sichern
- Möglichst unmittelbar nach Eingang/Entstehung

**Papierbelege:**
- Laufende Nummerierung
- Ablage in Ordnern
- Barcode-Vergabe + bildliche Erfassung

**Elektronische Belege:**
- Automatische Nummerierung
- Unveränderbare Speicherung

**Implementierung:**
```python
def secure_document(document: Document) -> SecuredDocument:
    """
    Sichert Dokument zeitnah.
    """
    # Checksumme berechnen
    checksum = hashlib.sha256(document.content).hexdigest()
    
    # Unveränderbar speichern
    secured = SecuredDocument.objects.create(
        document_id=document.id,
        content_hash=checksum,
        encrypted_content=encrypt(document.content),
        secured_at=timezone.now(),
        secured_by=document.created_by,
        retention_until=calculate_retention_date(document)
    )
    
    # Audit-Log
    AuditLog.objects.create(
        document=document,
        action='SECURE',
        timestamp=timezone.now(),
        checksum=checksum
    )
    
    return secured
```

### 4.3 Zuordnung Beleg ↔ Buchung (Rz. 71-74, 76ff) ⭐ **GUID ERFORDERLICH**

**Anforderung (Rz. 76ff):**
- Eindeutige Zuordnungsmerkmale (Index, Belegnummer, Dokumenten-ID)
- Progressive und retrograde Prüfbarkeit
- **Ein sachverständiger Dritter muss sich vom Beleg zur Buchung und von der Buchung zum Beleg bewegen können**

> **⭐ KRITISCH:** Du brauchst zwingend eine **GUID (Globally Unique Identifier)** oder einen **Index**,  
> der Belegdatei (PDF) und Datenbankeintrag **unzertrennlich** verknüpft.
>
> **Wenn der Beleg extern liegt** (z.B. S3 Bucket), muss der Link **stabil** sein ("Index-Management").

**Implementierung:**
```python
class JournalEntry(BaseModel):
    """Buchung mit Belegzuordnung."""
    # Eindeutige Belegnummer
    document_number = models.CharField(max_length=100)
    
    # ⭐ GUID-Verknüpfung zum Beleg (PFLICHT!)
    document = models.ForeignKey(Document, on_delete=models.PROTECT)
    document_guid = models.UUIDField()  # Redundant für Stabilität
    
    # Zusätzliche Identifikationsmerkmale
    document_date = models.DateField()
    supplier = models.CharField(max_length=200)
    
    # Buchungsdaten
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    account = models.CharField(max_length=20)
    contra_account = models.CharField(max_length=20)
    
    # Eindeutige Geschäftsvorfall-ID (Rz. 94)
    transaction_id = models.UUIDField(unique=True, default=uuid.uuid4)
```

### 4.4 Besonderheiten bei DV-gestützten Prozessen (Rz. 80-81)

**Automatikbuchungen:**
- Dokumentation der programminternen Vorschriften
- Nachweis des autorisierten Änderungsverfahrens
- Nachweis der Anwendung des genehmigten Verfahrens

**Beispiel: AfA-Buchungen**
```python
class AssetDepreciation(BaseModel):
    """Automatische AfA-Buchungen."""
    asset = models.ForeignKey(Asset, on_delete=models.PROTECT)
    
    # Ursprungsbeleg (Anschaffung)
    acquisition_document = models.ForeignKey(Document, on_delete=models.PROTECT)
    
    # AfA-Parameter
    acquisition_cost = models.DecimalField(max_digits=14, decimal_places=2)
    useful_life_years = models.IntegerField()
    depreciation_method = models.CharField(max_length=20)  # linear, degressive
    
    # Automatische Berechnung
    annual_depreciation = models.DecimalField(max_digits=14, decimal_places=2)
    
    def create_monthly_entries(self, year: int):
        """Erstellt monatliche AfA-Buchungen."""
        monthly_amount = self.annual_depreciation / 12
        
        for month in range(1, 13):
            JournalEntry.objects.create(
                document=self.acquisition_document,
                document_number=f"AfA-{self.asset.id}-{year}-{month:02d}",
                amount=monthly_amount,
                account='4830',  # AfA-Konto
                contra_account='0410',  # Anlagekonto
                description=f"AfA {self.asset.name} {year}/{month:02d}",
                transaction_type='AUTO_DEPRECIATION'
            )
```

## 5. Aufzeichnung der Geschäftsvorfälle (Rz. 82-99)

### 5.1 Grund(buch)aufzeichnungen (Rz. 85-89)

**Anforderung:**
- Fortlaufende Aufzeichnung in zeitlicher Reihenfolge
- Belegsicherung und Unverlierbarkeit

**Pflichtinhalte (Rz. 85):**
- Eindeutige Belegnummer
- Buchungsbetrag
- Währung (bei Fremdwährung: Wechselkurs)
- Erläuterung des Geschäftsvorfalls
- Belegdatum
- Erfassungsdatum

**Digitale Grund(buch)aufzeichnungen (Rz. 87-89):**
- Verbuchung im Hauptsystem bis Ablauf des Folgemonats
- Kontrollen: Erfassung, Übertragung, Verarbeitung
- Historisierung von Stammdaten, Bewegungsdaten, Metadaten

### 5.2 Journal (Rz. 90-94)

**Journalfunktion:**
- Vollständige, zeitgerechte, formal richtige Erfassung
- Nachweis der tatsächlichen Verarbeitung

**Pflichtangaben (Rz. 94) - ERWEITERT durch BMF 2024:**
- Eindeutige Belegnummer
- Buchungsbetrag
- Währung und Wechselkurs
- Erläuterung des Geschäftsvorfalls
- Belegdatum
- Buchungsdatum
- Erfassungsdatum
- Autorisierung
- Buchungsperiode/Voranmeldungszeitraum
- Umsatzsteuersatz, Steuerschlüssel, Umsatzsteuerbetrag
- Umsatzsteuerkonto, USt-ID, Steuernummer
- Konto und Gegenkonto
- **NEU: Kontoart** (Aktiva, Passiva, Kapital, Aufwand, Ertrag, sonstige)
- **NEU: Kontotyp** (Bilanz, GuV, Debitor, Kreditor, steuerlicher Gewinn, sonstige)
- Buchungsschlüssel
- Soll- und Haben-Betrag
- Eindeutige Identifikationsnummer des Geschäftsvorfalls

**Implementierung:**
```python
class JournalEntry(BaseModel):
    """GoBD-konformer Journaleintrag."""
    # Belegnummer
    document_number = models.CharField(max_length=100)
    
    # Beträge
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    currency = models.CharField(max_length=3, default='EUR')
    exchange_rate = models.DecimalField(max_digits=10, decimal_places=6, default=Decimal('1.0'))
    
    # Beschreibung
    description = models.TextField()
    
    # Datumsangaben
    document_date = models.DateField()
    booking_date = models.DateField()
    captured_at = models.DateTimeField(auto_now_add=True)
    
    # Autorisierung
    authorized_by = models.ForeignKey(User, null=True, on_delete=models.PROTECT)
    
    # Perioden
    fiscal_year = models.IntegerField()
    fiscal_period = models.IntegerField()
    tax_period = models.CharField(max_length=7)  # YYYY-MM
    
    # Umsatzsteuer
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2)
    tax_code = models.CharField(max_length=10)
    tax_amount = models.DecimalField(max_digits=14, decimal_places=2)
    tax_account = models.CharField(max_length=20)
    vat_id = models.CharField(max_length=20, blank=True)
    tax_number = models.CharField(max_length=20, blank=True)
    
    # Konten
    account = models.CharField(max_length=20)
    contra_account = models.CharField(max_length=20)
    
    # NEU: Kontoart und Kontotyp (BMF 2024)
    account_category = models.CharField(
        max_length=20,
        choices=[
            ('ASSET', 'Aktiva'),
            ('LIABILITY', 'Passiva'),
            ('EQUITY', 'Kapital'),
            ('EXPENSE', 'Aufwand'),
            ('REVENUE', 'Ertrag'),
            ('OTHER', 'Sonstige'),
        ]
    )
    account_type = models.CharField(
        max_length=20,
        choices=[
            ('BALANCE_SHEET', 'Bilanz'),
            ('PL', 'GuV'),
            ('DEBTOR', 'Debitor'),
            ('CREDITOR', 'Kreditor'),
            ('TAX_PROFIT', 'Steuerlicher Gewinn'),
            ('OTHER', 'Sonstige'),
        ]
    )
    
    # Buchungsschlüssel
    posting_key = models.CharField(max_length=10, blank=True)
    
    # Soll/Haben
    debit_amount = models.DecimalField(max_digits=14, decimal_places=2)
    credit_amount = models.DecimalField(max_digits=14, decimal_places=2)
    
    # Eindeutige Geschäftsvorfall-ID
    transaction_id = models.UUIDField(unique=True, default=uuid.uuid4)
```

### 5.3 Hauptbuch (Kontenfunktion) (Rz. 95-99)

**Anforderung:**
- Geschäftsvorfälle nach Sach- und Personenkonten geordnet
- Eröffnungs- und Abschlussbuchungen enthalten
- Kontensummen/Salden fortschreiben

**Zuordnungstabellen (Rz. 97):**
- Bei unterschiedlichen Ordnungskriterien zwischen Systemen
- Elektronische Mappingtabellen vorhalten

## 6. Internes Kontrollsystem (IKS) (Rz. 100-102)

**Pflicht:**
- Kontrollen einrichten, ausüben, protokollieren

**Kontrollen:**
- Zugangs- und Zugriffsberechtigungen
- Funktionstrennungen
- Erfassungskontrollen (Fehlerhinweise, Plausibilitätsprüfungen)
- Abstimmungskontrollen
- Verarbeitungskontrollen
- Schutzmaßnahmen gegen Verfälschung

**Implementierung:**
```python
class AccessControl(BaseModel):
    """Zugriffskontrolle."""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    resource = models.CharField(max_length=100)
    permission = models.CharField(max_length=50)  # READ, WRITE, DELETE
    granted_at = models.DateTimeField(auto_now_add=True)
    granted_by = models.ForeignKey(User, related_name='granted_permissions', on_delete=models.PROTECT)

class ControlLog(BaseModel):
    """Protokollierung von Kontrollen."""
    control_type = models.CharField(max_length=50)
    result = models.CharField(max_length=20)  # PASSED, FAILED
    details = models.JSONField()
    executed_at = models.DateTimeField(auto_now_add=True)
```

## 7. Datensicherheit (Rz. 103-106)

**Pflicht:**
- Schutz gegen Verlust (Unauffindbarkeit, Vernichtung, Diebstahl)
- Schutz gegen unberechtigte Eingaben und Veränderungen

**Verfahrensdokumentation:**
- Beschreibung der Datensicherung
- Abhängig von Komplexität des Unternehmens

## 8. Aufbewahrung (Rz. 113-144)

### 8.1 Aufbewahrungsfristen

**§ 147 Abs. 3 AO: 10 Jahre**
- Bücher, Inventare, Jahresabschlüsse
- Buchungsbelege, Rechnungen

**§ 147 Abs. 4 AO: 6 Jahre**
- Geschäftsbriefe
- Sonstige Unterlagen

**Fristbeginn:** Ende des Kalenderjahres der letzten Eintragung

### 8.2 Aufbewahrung elektronischer Unterlagen (Rz. 118-124)

**§ 147 Abs. 2 AO - Anforderungen:**
- Bildliche Übereinstimmung (bei empfangenen Dokumenten)
- Inhaltliche Übereinstimmung (bei anderen Unterlagen)
- Jederzeit lesbar
- Jederzeit verfügbar
- Unverzüglich lesbar machbar
- Maschinell auswertbar

**Wichtig (Rz. 119):**
- Elektronisch entstandene/eingegangene Daten **müssen** elektronisch aufbewahrt werden
- Ausschließliche Aufbewahrung in Papierform **nicht zulässig**!

**Ausnahme (Rz. 120):**
- Elektronisch erstellte, in Papierform versandte Geschäftsbriefe dürfen nur in Papierform aufbewahrt werden

### 8.3 Maschinelle Auswertbarkeit (Rz. 125-129)

**Anforderung:**
- Mathematisch-technische Auswertungen ermöglichen
- Volltextsuche ermöglichen
- Nachverfolgung von Verknüpfungen

**Verboten (Rz. 129):**
- Reduzierung bestehender maschineller Auswertbarkeit
- Umwandlung PDF/A → TIFF/JPG (XML-Daten gehen verloren!)
- Umwandlung Grund(buch)aufzeichnungen → PDF
- Umwandlung Journaldaten → PDF

**Zulässig:**
- Umwandlung in anderes Format, wenn maschinelle Auswertbarkeit **nicht** eingeschränkt wird

### 8.4 Bildliche Erfassung (Scannen) (Rz. 130, 136-141)

**Erlaubt:**
- Scannen mit verschiedenen Geräten (Smartphones, Tablets, Scanner)
- Mobiles Scannen im Ausland (§ 146 Abs. 2 AO)

**Anforderungen:**
- Bildliche Übereinstimmung mit Original
- Lesbarkeit
- Vollständigkeit
- Verfahrensdokumentation

**Organisationsanweisung (Rz. 136):**
- Wer darf erfassen?
- Wann wird erfasst?
- Welches Schriftgut wird erfasst?
- Qualitätskontrolle auf Lesbarkeit und Vollständigkeit
- Fehlerprotokollierung

> **⚠️ WICHTIGE KLARSTELLUNG - TR-RESISCAN:**  
> Die GoBD verweisen **nicht zwingend** auf BSI TR-RESISCAN (das ist für Behörden).  
> Für Unternehmen reicht ein **dokumentiertes Verfahren** ("Organisationsanweisung").  
> Das ERP muss **nicht** TR-RESISCAN zertifiziert sein, es muss nur den Prozess unterstützen:  
> **Scannen → Prüfen → Protokollieren**

**Vernichtung von Papierbelegen (Rz. 140):**
- Nach bildlicher Erfassung zulässig
- Außer: Aufbewahrungspflicht im Original (z.B. notarielle Urkunden)

**Implementierung:**
```python
def scan_document(paper_document: PaperDocument, user: User) -> ScannedDocument:
    """
    Scannt Papierdokument GoBD-konform.
    """
    # Scannen
    image = scan_image(paper_document)
    
    # Qualitätskontrolle
    if not is_readable(image):
        raise ValidationError("Scan nicht lesbar!")
    
    if not is_complete(image):
        raise ValidationError("Scan unvollständig!")
    
    # OCR (optional)
    ocr_text = perform_ocr(image) if paper_document.requires_ocr else None
    
    # Speichern
    scanned = ScannedDocument.objects.create(
        original_document=paper_document,
        image=image,
        ocr_text=ocr_text,
        scanned_at=timezone.now(),
        scanned_by=user,
        scan_device=get_device_info(),
        quality_checked=True
    )
    
    # Protokollierung
    ScanLog.objects.create(
        document=scanned,
        action='SCAN',
        user=user,
        timestamp=timezone.now(),
        quality_ok=True
    )
    
    return scanned
```

### 8.5 Systemwechsel und Auslagerung (Rz. 142-144)

**Anforderung:**
- Quantitativ und qualitativ gleichwertige Überführung
- Keine inhaltliche Änderung
- Dokumentation der Änderungen
- Gleiche Auswertungsmöglichkeiten wie im Produktivsystem

**Andernfalls:**
- Ursprüngliche Hard- und Software für Aufbewahrungsfrist vorhalten!

**Verboten (Rz. 144):**
- Aufbewahrung nur als Datenextrakte, Reports oder Druckdateien

## 9. Datenzugriff der Finanzbehörden (Rz. 158-178)

### 9.1 Drei Zugriffsarten (§ 147 Abs. 6 AO)

**Wichtige Änderung 2024 (Rz. 164):**
> Nach Systemwechsel/Auslagerung: Nach Ablauf des 5. Kalenderjahres nur noch **Z3-Zugriff** erforderlich!

#### Z1 - Unmittelbarer Zugriff (Rz. 165)

**Finanzbehörde:**
- Arbeitet selbst am System
- Nur-Lesezugriff
- Nutzt Hard- und Software des Steuerpflichtigen

**Kein Fernzugriff!**

#### Z2 - Mittelbarer Zugriff (Rz. 166)

**Steuerpflichtiger:**
- Wertet Daten nach Vorgaben der Finanzbehörde aus
- Finanzbehörde führt dann Nur-Lesezugriff durch

#### Z3 - Datenüberlassung (Rz. 167-169) - **GEÄNDERT 2024** ⭐ **INDEX.XML PFLICHT**

**Wichtige Änderungen:**
- Nicht mehr "Datenträgerüberlassung", sondern **"Datenüberlassung"**
- Überlassung kann erfolgen:
  - Auf Datenträger **ODER**
  - Über Datenaustauschplattform der Finanzbehörde (§ 87a Abs. 1 AO)
- Verlangen kann **bereits vor Prüfungsbeginn** mit Prüfungsanordnung erfolgen (§ 197 Abs. 3 AO)

> **⭐ KRITISCHE ANFORDERUNG - BESCHREIBUNGSSTANDARD:**  
> Ein reiner **CSV-Export reicht NICHT**!  
> Das ERP muss eine **index.xml** generieren, die dem Prüfprogramm (IDEA) erklärt:  
> - "Spalte A ist das Datum"  
> - "Spalte B ist der Betrag"  
> - "Spalte C ist die Belegnummer"  
>
> **Ohne index.xml kann die Finanzbehörde die Daten nicht auswerten!**

**Datenverarbeitung (Rz. 168 - NEU):**
- Verarbeitung und Aufbewahrung auf mobilen Datenverarbeitungssystemen der Finanzbehörde zulässig
- Unabhängig vom Einsatzort
- Aufbewahrung bis Unanfechtbarkeit der Verwaltungsakte (§ 147 Abs. 7 AO)

**Rückgabe/Löschung (Rz. 169):**
- Spätestens nach Bestandskraft der Bescheide
- Daten löschen
- Datenträger zurückgeben

### 9.2 Mitwirkungspflichten (Rz. 171-178)

**Steuerpflichtiger muss:**
- Finanzbehörde unterstützen
- Kosten tragen (§ 147 Abs. 6 Satz 3 AO)
- Alle zur Auswertung notwendigen Informationen bereitstellen

**Strukturinformationen (Rz. 176):**
- Dateiherkunft (eingesetztes System)
- Dateistruktur
- Datenfelder
- Zeichensatztabellen
- Interne und externe Verknüpfungen

**In maschinell auswertbarer Form!** (→ **index.xml**)

### 9.3 Digitale Schnittstellen (Rz. 178 - **AKTUALISIERT 2024**)

**Verfügbar auf www.bzst.de:**
- **DSFinV-K:** Digitale Schnittstelle Finanzverwaltung für Kassensysteme
- **DLS:** Digitale LohnSchnittstelle
- **Beschreibungsstandard:** XML-basierte Bereitstellungshilfe

**Wichtig (§ 158 Abs. 2 Nr. 2 AO - NEU 2024):**
> Werden elektronische Daten **nicht** nach den vorgeschriebenen digitalen Schnittstellen zur Verfügung gestellt, kann die Buchführung verworfen werden!

## 10. Verfahrensdokumentation (Rz. 151-155)

### 10.1 Inhalt

**Allgemeine Beschreibung:**
- Zweck des Systems
- Organisatorische Einbindung
- Anwenderkreis

**Anwenderdokumentation:**
- Bedienungsanleitung
- Arbeitsanweisungen

**Technische Systemdokumentation:**
- Systemarchitektur
- Schnittstellen
- Datenmodell
- Bedeutung von Abkürzungen, Ziffern, Buchstaben, Symbolen (§ 146 Abs. 3 Satz 3 AO)

**Betriebsdokumentation:**
- Datensicherung
- Archivierung
- Notfallkonzept

**IKS-Beschreibung:**
- Zugangs- und Zugriffskontrollen
- Funktionstrennungen
- Kontrollen

**Änderungshistorie:**
- Versionierung
- Nachvollziehbare Änderungen

### 10.2 Anforderungen

**Verständlich:**
- Für sachverständigen Dritten
- In angemessener Zeit nachprüfbar

**Vollständig:**
- Inhalt, Aufbau, Ablauf, Ergebnisse des DV-Verfahrens

**Aktuell:**
- Entspricht eingesetzter Version
- Historisch nachvollziehbar

**Aufbewahrung:**
- Solange Aufbewahrungsfrist für Unterlagen läuft

### 10.3 Rechtsfolgen (Rz. 155)

**Fehlende/ungenügende Verfahrensdokumentation:**
- Nur formeller Mangel, wenn Nachvollziehbarkeit/Nachprüfbarkeit nicht beeinträchtigt
- Kann aber zur Verwerfung der Buchführung führen!

---

## 10.4 Zertifizierung (Kap. 12 GoBD) ⭐ **WICHTIGE KLARSTELLUNG**

> **⚠️ ES GIBT KEIN "GoBD-ZERTIFIKAT"!**
>
> **Testate von Wirtschaftsprüfern (IDW PS 880)** existieren zwar, haben aber **keine rechtliche Bindungswirkung** gegenüber dem Finanzamt!
>
> **Das Finanzamt zertifiziert keine Software!** Es gibt keinen "GoBD-TÜV".
>
> **Spare Geld:** Investiere nicht in "Pseudo-Zertifikate", sondern in:
> - Vollständige Verfahrensdokumentation
> - Korrekte Implementierung der 6 Grundprinzipien
> - Z1/Z2/Z3-Datenzugriff
> - Audit-Trail und Versionierung

## 11. Wichtige Änderungen durch BMF-Schreiben 2024

### 11.1 Beweiskraft der Buchführung (Rz. 11)

**NEU: § 158 Abs. 2 Nr. 2 AO**
- Buchführung kann verworfen werden, wenn elektronische Daten **nicht nach vorgeschriebenen digitalen Schnittstellen** zur Verfügung gestellt werden

### 11.2 Kleinunternehmer (Rz. 15)

**Aktualisiert:**
- Jahresumsatz: Vorjahresgrenze nach § 19 Abs. 1 Satz 1 UStG (aktuell: 22.000 €)
- Anforderungen mit Blick auf Unternehmensgröße bewerten

### 11.3 Einzelaufzeichnungspflicht (Rz. 39)

**Klarstellung:**
- Bei Vorliegen der Voraussetzungen des § 146 Abs. 1 Satz 3 AO ist Zumutbarkeit nicht gesondert zu prüfen

### 11.4 Kassensysteme (Rz. 43)

**Hinweis auf § 146a Abs. 2 AO:**
- Unterdrückung von Geschäftsvorfällen unzulässig
- Bezug auf Kassensicherungsverordnung

### 11.5 Journalangaben (Rz. 94)

**NEU: Pflichtangaben erweitert:**
- Kontoart (Aktiva, Passiva, Kapital, Aufwand, Ertrag, sonstige)
- Kontotyp (Bilanz, GuV, Debitor, Kreditor, steuerlicher Gewinn, sonstige)

### 11.6 Datenüberlassung statt Datenträgerüberlassung

**Modernisierung:**
- Nicht mehr nur Datenträger
- Auch Datenaustauschplattformen der Finanzbehörde
- Verlangen bereits vor Prüfungsbeginn möglich

### 11.7 Verlagerung ins Ausland (Rz. 136)

**Erweitert:**
- Nicht nur Genehmigung nach § 146 Abs. 2a AO
- Auch Anzeige nach § 146 Abs. 2b AO

### 11.8 Systemwechsel (Rz. 164)

**Erleichterung:**
- Nach 5 Jahren nur noch Z3-Zugriff erforderlich
- Ursprüngliche Hard-/Software muss nicht mehr vorgehalten werden

## 12. Sanktionen bei Verstößen

### 12.1 Verwerfung der Buchführung (§ 158 AO)

**Folgen:**
- Schätzung der Besteuerungsgrundlagen (§ 162 AO)
- Zuschlag bei Schätzung: 5-10% der festgesetzten Steuer (§ 162 Abs. 4 AO)

**Gründe:**
- Formelle Mängel mit sachlichem Gewicht
- Sachliche Unrichtigkeit
- **NEU:** Keine Bereitstellung nach digitalen Schnittstellen (§ 158 Abs. 2 Nr. 2 AO)

### 12.2 Verspätungszuschlag (§ 152 AO)

- 0,25% der festgesetzten Steuer pro Monat
- Mindestens 25 € pro Monat

### 12.3 Ordnungswidrigkeiten (§§ 378-384 AO)

- Verletzung von Buchführungspflichten
- Geldbuße bis 25.000 €

### 12.4 Steuerstraftaten (§§ 370-376 AO)

- Steuerhinterziehung: Freiheitsstrafe bis 5 Jahre oder Geldstrafe
- In besonders schweren Fällen: Freiheitsstrafe bis 10 Jahre

## 13. Implementierungscheckliste für ERP-System

### Allgemein
- [ ] Verfahrensdokumentation erstellt und aktuell
- [ ] Alle 6 Grundprinzipien umgesetzt
- [ ] IKS implementiert und dokumentiert
- [ ] Datensicherungskonzept vorhanden
- [ ] Aufbewahrungsfristen eingehalten

### Nachvollziehbarkeit
- [ ] Progressive Prüfbarkeit: Beleg → Buchung → Konto → Bilanz
- [ ] Retrograde Prüfbarkeit: Bilanz → Konto → Buchung → Beleg
- [ ] Audit-Logging für alle Änderungen
- [ ] Versionierung implementiert

### Vollständigkeit
- [ ] Einzelaufzeichnungspflicht umgesetzt
- [ ] Erfassungskontrollen (Plausibilitätsprüfungen)
- [ ] Lückenanalyse bei Belegnummern
- [ ] Keine Löschmöglichkeit vor Fristablauf
- [ ] Historisierung von Stammdaten

### Richtigkeit
- [ ] Validierung bei Dateneingabe
- [ ] Checksummen-Prüfung bei Dokumenten
- [ ] Korrekte Kontierung sichergestellt

### Zeitgerechtigkeit
- [ ] Bare Geschäftsvorfälle: Tägliche Erfassung
- [ ] Unbare Geschäftsvorfälle: Erfassung innerhalb 10 Tagen
- [ ] Periodengerechte Zuordnung
- [ ] Erfassungsdatum protokolliert

### Ordnung
- [ ] Eindeutige Indexierung
- [ ] Suchfunktionen vorhanden
- [ ] Logische Ordnungsstruktur
- [ ] Kontenplan implementiert

### Unveränderbarkeit
- [ ] Unveränderbare Speicherung nach Erfassung
- [ ] Protokollierung aller Änderungen
- [ ] Versionierung bei Änderungen
- [ ] Historisierung von Stammdaten

### Belegwesen
- [ ] Belegprinzip umgesetzt
- [ ] Zeitnahe Belegsicherung
- [ ] Zuordnung Beleg ↔ Buchung
- [ ] Scan-Funktion mit Qualitätskontrolle

### Aufbewahrung
- [ ] Elektronische Aufbewahrung elektronischer Belege
- [ ] Maschinelle Auswertbarkeit gewährleistet
- [ ] Langzeitformate (z.B. PDF/A)
- [ ] Aufbewahrungsfristen: 6/10 Jahre

### Datenzugriff
- [ ] Z1-Zugriff möglich (Nur-Lesezugriff)
- [ ] Z2-Zugriff möglich (Auswertungen nach Vorgaben)
- [ ] Z3-Zugriff möglich (Datenüberlassung)
- [ ] Digitale Schnittstellen implementiert (DSFinV-K, DLS)
- [ ] Strukturinformationen maschinell auswertbar

### Journalangaben (inkl. BMF 2024)
- [ ] Alle Pflichtangaben nach Rz. 94 erfasst
- [ ] **Kontoart** erfasst (Aktiva, Passiva, Kapital, Aufwand, Ertrag)
- [ ] **Kontotyp** erfasst (Bilanz, GuV, Debitor, Kreditor, steuerlicher Gewinn)
- [ ] Eindeutige Geschäftsvorfall-ID (Transaction-ID)

## 14. Zusammenspiel mit AO und DSGVO

**AO (Aufbewahrungspflichten):**
- GoBD konkretisiert §§ 146-147 AO
- Aufbewahrungsfristen: 6-10 Jahre
- Datenzugriff: § 147 Abs. 6 AO

**DSGVO (Datenschutz):**
- Löschpflicht nach DSGVO vs. Aufbewahrungspflicht nach AO
- **Lösung:** Aufbewahrungspflichten gehen vor (Art. 17 Abs. 3 lit. b DSGVO)
- Nach Ablauf der Aufbewahrungsfrist: Löschung nach DSGVO

## 15. Wichtige Fristen

| Frist | Rechtsgrundlage | Beschreibung |
|-------|-----------------|--------------|
| Täglich | § 146 Abs. 1 Satz 2 AO | Kasseneinnahmen und -ausgaben |
| 10 Tage | Rz. 47 | Unbare Geschäftsvorfälle |
| 1 Monat | Rz. 87 | Verbuchung im Hauptsystem |
| 10 Jahre | § 147 Abs. 3 AO | Bücher, Inventare, Jahresabschlüsse, Belege |
| 6 Jahre | § 147 Abs. 4 AO | Geschäftsbriefe, sonstige Unterlagen |
| 5 Jahre | Rz. 164 | Nach Systemwechsel: Nur noch Z3-Zugriff |

## 16. Anwendungsregelung

**GoBD 2019:**
- Gültig ab 1. Januar 2020
- Für Besteuerungszeiträume nach 31. Dezember 2019

**GoBD 2024 (Änderung):**
- Gültig ab 1. April 2024
- Für Besteuerungszeiträume nach 31. Dezember 2024

**Nicht mehr unterstützte Formate ab 2025:**
- EBCDIC feste Länge
- EBCDIC variable Länge
- Lotus 123
- ASCII-Druckdateien
- AS/400 Datensatzbeschreibungen (FDF)

## 17. Nächste Schritte für ERP-Implementierung

1. ✅ GoBD.md und GoBD_Zusatz.md gelesen
2. ⬜ Verfahrensdokumentation erstellen
3. ⬜ Audit-Logging implementieren
4. ⬜ Versionierung implementieren
5. ⬜ Historisierung von Stammdaten
6. ⬜ Digitale Schnittstellen implementieren (DSFinV-K, DLS)
7. ⬜ Datenzugriff Z1/Z2/Z3 vorbereiten
8. ⬜ Scan-Funktion mit Qualitätskontrolle
9. ⬜ IKS dokumentieren
10. ⬜ Datensicherungskonzept erstellen

---

**Quelle:** `.agent/knowledge/GoBD.md` und `.agent/knowledge/GoBD_Zusatz.md`  
**Hinweis:** Bei rechtlichen Fragen Steuerberater konsultieren. Die GoBD sind verbindliche Verwaltungsanweisungen der Finanzverwaltung.
