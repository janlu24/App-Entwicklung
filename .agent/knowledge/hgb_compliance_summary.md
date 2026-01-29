# HGB-Compliance-Zusammenfassung für ERP-Systeme

## Zweck des Dokuments
Dieses Dokument fasst die wichtigsten Anforderungen des deutschen Handelsgesetzbuchs (HGB) zusammen, die für die Entwicklung von ERP-Systemen relevant sind, mit Fokus auf Buchführung, Rechnungslegung und Bilanzierungspflichten.

> **Entwickler-Hinweis**: Dieses Dokument erklärt, **WARUM** bestimmte Anforderungen existieren (rechtliche Grundlage).  
> Für das **WIE** (die technische Umsetzung im Code), siehe:
> - **[gobd_implementation_guide.md](./gobd_implementation_guide.md)** - Vollständige Code-Beispiele und Implementierungsmuster
> - **[compliance_documentation_overview.md](./compliance_documentation_overview.md)** - Navigationshilfe für alle Compliance-Dokumente

---

## 1. Buchführungsgrundsätze (§§ 238-263)

### § 238 - Buchführungspflicht

**Rechtliche Anforderung:**
> "Jeder Kaufmann ist verpflichtet, Bücher zu führen und in diesen seine Handelsgeschäfte und die Lage seines Vermögens nach den Grundsätzen ordnungsmäßiger Buchführung ersichtlich zu machen."

**ERP-Implementierung:**
- **Verpflichtend**: Jeder Kaufmann muss Bücher führen, die alle Geschäftsvorfälle und die Vermögenslage nach den Grundsätzen ordnungsmäßiger Buchführung (GoB) klar ausweisen.
- **Systemanforderung**: Das ERP muss eine strukturierte, vollständige und nachvollziehbare Erfassung aller Geschäftsvorfälle erzwingen.

**Wichtige Pflichten (§ 238 Abs. 1-2):**
1. Bücher und Aufzeichnungen müssen in einer lebenden Sprache geführt werden (Deutsch oder mit verfügbarer Übersetzung).
2. Eintragungen müssen vollständig, richtig, zeitgerecht und geordnet sein.
3. Keine Eintragung darf so verändert werden, dass der ursprüngliche Inhalt nicht mehr feststellbar ist.
4. Die Buchführung muss so beschaffen sein, dass sich ein sachverständiger Dritter innerhalb angemessener Zeit einen Überblick über die Geschäftsvorfälle und die Lage des Unternehmens verschaffen kann.

**Technische Umsetzung:**
```python
# Core Model Anforderungen
class BaseModel(models.Model):
    """
    § 238 HGB Compliance: Nachvollziehbarkeit & Unveränderbarkeit
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT)
    last_modified_at = models.DateTimeField(auto_now=True)
    last_modified_by = models.ForeignKey(User, on_delete=models.PROTECT, null=True)
    version = models.IntegerField(default=1)  # Versionierung
    
    # Soft Delete (§ 257 HGB: 10 Jahre Aufbewahrung)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    deleted_by = models.ForeignKey(User, on_delete=models.PROTECT, null=True)
    
    class Meta:
        abstract = True
```

---

## 2. Aufbewahrungsfristen (§ 257 HGB)

### § 257 - Aufbewahrung von Unterlagen

**Rechtliche Anforderung:**
Kaufleute müssen folgende Unterlagen aufbewahren:

**10 Jahre Aufbewahrung (§ 257 Abs. 1 Nr. 1-4):**
1. **Handelsbücher** (Bücher, Inventare, Eröffnungsbilanzen, Jahresabschlüsse, Lageberichte, Konzernabschlüsse)
2. **Buchungsbelege**
3. **Empfangene Handelsbriefe**
4. **Wiedergaben der abgesandten Handelsbriefe** (Kopien)

**6 Jahre Aufbewahrung (§ 257 Abs. 1 Nr. 5):**
- Sonstige Unterlagen, soweit sie für die Besteuerung von Bedeutung sind (z.B. Arbeitsanweisungen, Organisationsunterlagen)

**Berechnung der Aufbewahrungsfrist (§ 257 Abs. 5):**
> "Die Aufbewahrungsfrist beginnt mit dem Schluss des Kalenderjahres, in dem die letzte Eintragung in das Buch gemacht, das Inventar, die Eröffnungsbilanz, der Jahresabschluss oder der Lagebericht aufgestellt, der Handelsbrief empfangen oder abgesandt worden oder der Buchungsbeleg entstanden ist..."

**ERP-Implementierung:**

```python
# apps/documents/models.py
class Document(BaseModel):
    """
    § 257 HGB: Aufbewahrungspflichten
    """
    document_type = models.CharField(max_length=50, choices=[
        ('INVOICE_IN', 'Eingangsrechnung'),      # 10 Jahre
        ('INVOICE_OUT', 'Ausgangsrechnung'),     # 10 Jahre
        ('RECEIPT', 'Beleg'),                    # 10 Jahre
        ('CONTRACT', 'Vertrag'),                 # 10 Jahre
        ('EMAIL', 'Handelsbrief (E-Mail)'),      # 10 Jahre
        ('WORK_INSTRUCTION', 'Arbeitsanweisung'), # 6 Jahre
        ('OTHER', 'Sonstige'),
    ])
    
    document_date = models.DateField(db_index=True)
    fiscal_year = models.IntegerField(db_index=True)
    
    # § 257 HGB: Dynamische Aufbewahrungsfrist
    retention_until = models.DateField(db_index=True)
    deletion_blocked = models.BooleanField(default=True)
    
    # ⚠️ WICHTIG: Retention kann sich verlängern!
    retention_extended = models.BooleanField(default=False)
    retention_extension_reason = models.CharField(max_length=200, blank=True, choices=[
        ('AUDIT', 'Laufende Betriebsprüfung'),
        ('LITIGATION', 'Rechtsstreit'),
        ('TAX_INVESTIGATION', 'Steuerliche Ermittlung'),
        ('OTHER', 'Sonstige'),
    ])
    
    def calculate_retention_period(self):
        """
        § 257 Abs. 5 HGB: Frist beginnt am Ende des Kalenderjahres
        
        WICHTIG: Frist ist ereignisgebunden, nicht statisch!
        """
        if self.document_type in ['INVOICE_IN', 'INVOICE_OUT', 'RECEIPT', 'CONTRACT', 'EMAIL']:
            retention_years = 10
        else:
            retention_years = 6
        
        # Frist beginnt am 31.12. des Belegdatums
        year_end = date(self.document_date.year, 12, 31)
        base_retention = year_end + relativedelta(years=retention_years)
        
        # Prüfe: Verlängerung notwendig?
        if self.retention_extended:
            # Retention bleibt aktiv bis Extension aufgehoben wird
            self.deletion_blocked = True
        else:
            self.retention_until = base_retention
            self.deletion_blocked = (date.today() < base_retention)
```

**Konflikt mit DSGVO:**
- **HGB**: Zwingende Aufbewahrung für 10 Jahre
- **DSGVO Art. 17**: Recht auf Löschung ("Recht auf Vergessenwerden")
- **Lösung**: Datensperrung (Blocking) statt Löschung (siehe `dsgvo_privacy_by_design.md`)

---

## 3. Jahresabschluss (§§ 242-256a)

### § 242 - Pflicht zur Aufstellung von Bilanz und Inventar

**Rechtliche Anforderung:**
1. **Eröffnungsbilanz**: Zu Beginn des Handelsgewerbes
2. **Jahresbilanz** (Jahresabschluss): Zum Schluss eines jeden Geschäftsjahres
3. **Inventar**: Genaues Verzeichnis aller Vermögensgegenstände und Schulden

**§ 243 - Aufstellungsgrundsatz:**
> "Der Jahresabschluss ist nach den Grundsätzen ordnungsmäßiger Buchführung aufzustellen."

**Bestandteile des Jahresabschlusses (§ 242 Abs. 3):**
- **Bilanz**
- **Gewinn- und Verlustrechnung (GuV)**
- **Anhang** - für Kapitalgesellschaften

### § 246 - Vollständigkeit und Verrechnungsverbot

**Wichtige Prinzipien:**
1. **Vollständigkeit**: Der Jahresabschluss hat sämtliche Vermögensgegenstände, Schulden, Rechnungsabgrenzungsposten sowie Aufwendungen und Erträge zu enthalten.
2. **Verrechnungsverbot**: Posten der Aktivseite dürfen nicht mit Posten der Passivseite, Aufwendungen nicht mit Erträgen verrechnet werden.

**ERP-Implementierung:**

```python
# apps/finance/services.py
def generate_balance_sheet(fiscal_year: int, user: User) -> dict:
    """
    § 242, § 246 HGB: Bilanz nach GoB
    
    Vollständigkeit: Alle Vermögensgegenstände und Schulden
    Verrechnungsverbot: Keine Saldierung
    """
    # Aktiva (Assets)
    assets = {
        'anlagevermoegen': get_fixed_assets(fiscal_year),
        'umlaufvermoegen': get_current_assets(fiscal_year),
        'rechnungsabgrenzungsposten': get_prepaid_expenses(fiscal_year),
    }
    
    # Passiva (Liabilities & Equity)
    liabilities = {
        'eigenkapital': get_equity(fiscal_year),
        'rueckstellungen': get_provisions(fiscal_year),
        'verbindlichkeiten': get_liabilities(fiscal_year),
        'rechnungsabgrenzungsposten': get_deferred_income(fiscal_year),
    }
    
    # § 246 Abs. 2: Verrechnungsverbot prüfen
    if has_offsetting_violations(assets, liabilities):
        raise ValidationError("§ 246 HGB: Verrechnungsverbot verletzt!")
    
    return {
        'aktiva': assets,
        'passiva': liabilities,
        'fiscal_year': fiscal_year,
        'created_by': user,
        'created_at': timezone.now(),
    }
```

---

## 4. Bewertungsvorschriften (§§ 252-256a)

### § 252 - Allgemeine Bewertungsgrundsätze

**Grundlegende Prinzipien (§ 252 Abs. 1):**

1. **Unternehmensfortführung (Going Concern)**
   - Bei der Bewertung ist von der Fortführung der Unternehmenstätigkeit auszugehen.

2. **Bilanzidentität**
   - Die Wertansätze in der Eröffnungsbilanz des Geschäftsjahrs müssen mit denen der Schlussbilanz des vorhergehenden Geschäftsjahrs übereinstimmen.

3. **Einzelbewertung**
   - Die Vermögensgegenstände und Schulden sind einzeln zu bewerten.

4. **Vorsichtsprinzip**:
   - **Realisationsprinzip**: Gewinne sind nur zu berücksichtigen, wenn sie am Abschlussstichtag realisiert sind.
   - **Imparitätsprinzip**: Alle vorhersehbaren Risiken und Verluste, die bis zum Abschlussstichtag entstanden sind, müssen berücksichtigt werden.

5. **Periodenabgrenzung**
   - Aufwendungen und Erträge sind unabhängig vom Zeitpunkt der Zahlung im Jahresabschluss zu berücksichtigen.

6. **Bewertungsstetigkeit**
   - Die angewandten Bewertungsmethoden sind beizubehalten.

**ERP-Implementierung:**

```python
# apps/finance/services.py
def value_asset(asset: Asset, valuation_date: date) -> Decimal:
    """
    § 252 HGB: Bewertungsgrundsätze
    § 253 HGB: Zugangs- und Folgebewertung
    """
    # § 253 Abs. 1: Anschaffungs- oder Herstellungskosten
    acquisition_cost = asset.acquisition_cost
    
    # § 253 Abs. 3: Planmäßige Abschreibung
    depreciation = calculate_depreciation(
        cost=acquisition_cost,
        useful_life=asset.useful_life,
        method=asset.depreciation_method,  # Linear, degressiv
        start_date=asset.acquisition_date,
        valuation_date=valuation_date
    )
    
    book_value = acquisition_cost - depreciation
    
    # § 253 Abs. 4: Niederstwertprinzip (Lower of Cost or Market)
    market_value = get_market_value(asset, valuation_date)
    
    if market_value < book_value:
        # Außerplanmäßige Abschreibung erforderlich
        return market_value
    
    return book_value
```

### § 253 - Zugangs- und Folgebewertung

**Wichtige Regeln:**

**Vermögensgegenstände (§ 253 Abs. 1):**
- Bewertung zu **Anschaffungs-** oder **Herstellungskosten**.
- **Abschreibung** bei Vermögensgegenständen mit begrenzter Nutzungsdauer.

**Verbindlichkeiten (§ 253 Abs. 1 Satz 2):**
- Bewertung zum **Erfüllungsbetrag**.

**Niederstwertprinzip (§ 253 Abs. 4):**
- Bei Umlaufvermögen sind Abschreibungen vorzunehmen, um diese mit einem niedrigeren Wert anzusetzen, der sich aus einem Börsen- oder Marktpreis ergibt.

### § 256 - Verbrauchsfolgeverfahren ⭐ **KEY ERP FEATURE**

**Rechtliche Anforderung:**
> "Bei der Bewertung gleichartiger Vermögensgegenstände des Vorratsvermögens kann unterstellt werden, dass die zuerst oder dass die zuletzt angeschafften oder hergestellten Vermögensgegenstände zuerst oder zuletzt verbraucht oder veräußert worden sind."

**Zulässige Methoden:**
1. **FIFO (First-In, First-Out)**: Älteste Bestände werden zuerst verbraucht.
2. **LIFO (Last-In, First-Out)**: Neueste Bestände werden zuerst verbraucht.
3. **Durchschnittsbewertung**: Gewogener Durchschnitt aller Zugänge.

**ERP-Relevanz:**
- **Kritisch für Bestandsbewertung**: Wenn 100 Einheiten verkauft werden, welche Kosten werden angesetzt? Die alten günstigen oder die neuen teuren?
- **Steuerliche Auswirkung**: LIFO vs. FIFO kann den Gewinn erheblich beeinflussen.
- **Systemanforderung**: ERP muss Historie tracken und konsistente Methode anwenden.

**ERP-Implementierung:**

```python
# apps/inventory/models.py
class Product(BaseModel):
    """
    § 256 HGB: Verbrauchsfolgeverfahren
    """
    name = models.CharField(max_length=200)
    sku = models.CharField(max_length=50, unique=True)
    
    # § 256 HGB: Bewertungsmethode (muss konsistent angewendet werden!)
    valuation_method = models.CharField(max_length=20, choices=[
        ('FIFO', 'First-In, First-Out'),
        ('LIFO', 'Last-In, First-Out'),
        ('AVERAGE', 'Durchschnittspreis'),
    ], default='FIFO')
    
    # § 252 Abs. 1 Nr. 6: Bewertungsstetigkeit
    valuation_method_changed_at = models.DateField(null=True)
    valuation_method_change_reason = models.TextField(blank=True)

class StockLayer(BaseModel):
    """
    § 256 HGB: Lagerschichten für FIFO/LIFO
    
    Jeder Wareneingang erzeugt eine neue Schicht.
    """
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    warehouse = models.ForeignKey('Warehouse', on_delete=models.PROTECT)
    
    # Schichtinformationen
    purchase_date = models.DateField(db_index=True)
    unit_cost = models.DecimalField(max_digits=14, decimal_places=2)
    
    # Bestand
    quantity_received = models.DecimalField(max_digits=14, decimal_places=3)
    quantity_remaining = models.DecimalField(max_digits=14, decimal_places=3)
    
    # Beleg-Referenz
    purchase_document = models.ForeignKey('documents.Document', on_delete=models.PROTECT)
    
    class Meta:
        ordering = ['purchase_date']  # FIFO: älteste zuerst

# apps/inventory/services.py
def calculate_cogs_fifo(product: Product, quantity_sold: Decimal) -> Decimal:
    """
    § 256 HGB: FIFO - Älteste Schichten zuerst verbrauchen
    """
    layers = StockLayer.objects.filter(
        product=product,
        quantity_remaining__gt=0
    ).order_by('purchase_date')  # Älteste zuerst
    
    total_cost = Decimal('0')
    remaining_to_consume = quantity_sold
    
    for layer in layers:
        if remaining_to_consume <= 0:
            break
        
        consumed_from_layer = min(layer.quantity_remaining, remaining_to_consume)
        total_cost += consumed_from_layer * layer.unit_cost
        
        # Schicht reduzieren
        layer.quantity_remaining -= consumed_from_layer
        layer.save()
        
        remaining_to_consume -= consumed_from_layer
    
    return total_cost

def calculate_cogs_lifo(product: Product, quantity_sold: Decimal) -> Decimal:
    """
    § 256 HGB: LIFO - Neueste Schichten zuerst verbrauchen
    """
    layers = StockLayer.objects.filter(
        product=product,
        quantity_remaining__gt=0
    ).order_by('-purchase_date')  # Neueste zuerst
    
    total_cost = Decimal('0')
    remaining_to_consume = quantity_sold
    
    for layer in layers:
        if remaining_to_consume <= 0:
            break
        
        consumed_from_layer = min(layer.quantity_remaining, remaining_to_consume)
        total_cost += consumed_from_layer * layer.unit_cost
        
        layer.quantity_remaining -= consumed_from_layer
        layer.save()
        
        remaining_to_consume -= consumed_from_layer
    
    return total_cost

def calculate_cogs_average(product: Product, quantity_sold: Decimal) -> Decimal:
    """
    § 240 Abs. 4 HGB: Gruppenbewertung (Gewogener Durchschnitt)
    (Oft alternativ zu § 256 Verbrauchsfolgeverfahren genutzt)
    """
    total_quantity = StockLayer.objects.filter(
        product=product
    ).aggregate(total=Sum('quantity_remaining'))['total'] or Decimal('0')
    
    total_value = sum(
        layer.quantity_remaining * layer.unit_cost
        for layer in StockLayer.objects.filter(product=product)
    )
    
    if total_quantity > 0:
        average_cost = total_value / total_quantity
        return quantity_sold * average_cost
    
    return Decimal('0')
```

**Wichtige Hinweise:**
- **Stetigkeit (§ 252 Abs. 1 Nr. 6)**: Einmal gewählt, muss die Methode beibehalten werden.
- **Änderung benötigt Begründung**: Wechsel von FIFO zu LIFO muss dokumentiert werden.
- **Steuerliche Implikationen**: LIFO ist handelsrechtlich erlaubt, steuerlich ggf. eingeschränkt.

### § 256a - Währungsumrechnung

**Rechtliche Anforderung:**
> "Vermögensgegenstände, die in fremder Währung zu bewerten sind, sind zum Devisenkassamittelkurs am Abschlussstichtag umzurechnen."

**Wichtige Regeln:**
1. **Vermögensgegenstände in Fremdwährung**: Umrechnung zum Devisenkassamittelkurs am Bilanzstichtag.
2. **Realisationsprinzip**: Unrealisierte Gewinne werden nicht ausgewiesen, unrealisierte Verluste müssen ausgewiesen werden (§ 252 Abs. 1 Nr. 4).

**ERP-Implementierung:**

```python
# apps/finance/models.py
class ExchangeRate(BaseModel):
    """
    § 256a HGB: Wechselkurse für Währungsumrechnung
    """
    from_currency = models.CharField(max_length=3)  # EUR
    to_currency = models.CharField(max_length=3)    # USD
    rate_date = models.DateField(db_index=True)
    
    # Devisenkassamittelkurs (spot rate)
    spot_rate = models.DecimalField(max_digits=10, decimal_places=6)
    
    # Quelle (z.B. EZB, Bundesbank)
    source = models.CharField(max_length=50)
    
    class Meta:
        unique_together = ['from_currency', 'to_currency', 'rate_date']

class ForeignCurrencyAsset(BaseModel):
    """
    § 256a HGB: Vermögensgegenstand in Fremdwährung
    """
    asset_type = models.CharField(max_length=50)
    currency = models.CharField(max_length=3)
    
    # Ursprungswert
    original_amount = models.DecimalField(max_digits=14, decimal_places=2)
    original_rate = models.DecimalField(max_digits=10, decimal_places=6)
    original_eur_value = models.DecimalField(max_digits=14, decimal_places=2)
    
    # Aktueller Wert (zum Bilanzstichtag)
    current_rate = models.DecimalField(max_digits=10, decimal_places=6)
    current_eur_value = models.DecimalField(max_digits=14, decimal_places=2)
    
    # § 252 Abs. 1 Nr. 4: Imparitätsprinzip
    unrealized_gain = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal('0'))
    unrealized_loss = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal('0'))

# apps/finance/services.py
def revalue_foreign_currency_items(balance_sheet_date: date) -> dict:
    """
    § 256a HGB: Währungsumrechnung zum Bilanzstichtag
    """
    assets = ForeignCurrencyAsset.objects.filter(is_deleted=False)
    
    total_unrealized_losses = Decimal('0')
    total_unrealized_gains = Decimal('0')
    
    for asset in assets:
        # Aktuellen Wechselkurs abrufen
        current_rate = get_exchange_rate(
            from_currency='EUR',
            to_currency=asset.currency,
            rate_date=balance_sheet_date
        )
        
        # Neuer EUR-Wert
        new_eur_value = asset.original_amount / current_rate
        
        # Differenz berechnen
        difference = new_eur_value - asset.original_eur_value
        
        # § 252 Abs. 1 Nr. 4: Imparitätsprinzip
        if difference > 0:
            # Unrealisierter Gewinn → NICHT erfassen
            asset.unrealized_gain = difference
            asset.unrealized_loss = Decimal('0')
            # Wert bleibt bei Anschaffungskosten
            asset.current_eur_value = asset.original_eur_value
        else:
            # Unrealisierter Verlust → MUSS erfasst werden
            asset.unrealized_loss = abs(difference)
            asset.unrealized_gain = Decimal('0')
            # Wert wird abgeschrieben
            asset.current_eur_value = new_eur_value
            total_unrealized_losses += abs(difference)
        
        asset.current_rate = current_rate
        asset.save()
    
    return {
        'total_unrealized_losses': total_unrealized_losses,
        'total_unrealized_gains': total_unrealized_gains,
        'revaluation_date': balance_sheet_date,
    }
```

**Checkliste Währungsumrechnung:**
- [ ] Wechselkurse automatisch von zuverlässiger Quelle (EZB, Bundesbank) abgerufen
- [ ] Alle Fremdwährungsposten zum Bilanzstichtag neu bewertet
- [ ] Unrealisierte Verluste erfasst (Imparitätsprinzip)
- [ ] Unrealisierte Gewinne NICHT erfasst (Realisationsprinzip)
- [ ] Währungsumrechnung im Anhang dokumentiert

---

## 5. Inventur (§§ 240-241)

### § 240 - Pflicht zur Aufstellung des Inventars

**Rechtliche Anforderung:**
> "Jeder Kaufmann hat zu Beginn seines Handelsgewerbes seine Grundstücke, seine Forderungen und Schulden, den Betrag seines baren Geldes sowie seine sonstigen Vermögensgegenstände genau zu verzeichnen..."

**Jahresinventur (§ 240 Abs. 2):**
- Muss zum Schluss eines jeden Geschäftsjahres aufgestellt werden.
- Muss alle Vermögensgegenstände und Schulden mit **Menge und Wert** enthalten.

**Körperliche Bestandsaufnahme (§ 241 Abs. 1):**
- Vorräte müssen durch **körperliche Bestandsaufnahme** (Zählen, Wiegen, Messen) erfasst werden.

**ERP-Implementierung:**

```python
# apps/inventory/models.py
class InventoryCount(BaseModel):
    """
    § 240, § 241 HGB: Inventur
    """
    inventory_date = models.DateField(db_index=True)
    fiscal_year = models.IntegerField()
    count_type = models.CharField(max_length=20, choices=[
        ('ANNUAL', 'Jahresinventur (§ 240 Abs. 2)'),
        ('OPENING', 'Eröffnungsinventur (§ 240 Abs. 1)'),
        ('SPOT_CHECK', 'Stichprobeninventur (§ 241 Abs. 2)'),
    ])
    
    status = models.CharField(max_length=20, choices=[
        ('PLANNED', 'Geplant'),
        ('IN_PROGRESS', 'Laufend'),
        ('COMPLETED', 'Abgeschlossen'),
        ('APPROVED', 'Genehmigt'),
    ])

class InventoryCountItem(BaseModel):
    """
    Einzelne Inventurposition
    """
    count = models.ForeignKey(InventoryCount, on_delete=models.PROTECT)
    product = models.ForeignKey('Product', on_delete=models.PROTECT)
    
    # § 240 Abs. 1: "genau zu verzeichnen"
    counted_quantity = models.DecimalField(max_digits=14, decimal_places=3)
    system_quantity = models.DecimalField(max_digits=14, decimal_places=3)
    variance = models.DecimalField(max_digits=14, decimal_places=3)
    
    # § 240 Abs. 1: "mit dem Werte anzusetzen"
    unit_value = models.DecimalField(max_digits=14, decimal_places=2)
    total_value = models.DecimalField(max_digits=14, decimal_places=2)
    
    counted_by = models.ForeignKey(User, on_delete=models.PROTECT)
    counted_at = models.DateTimeField()
```

### § 241 Abs. 2 - Permanente Inventur ⭐ **KEY ERP FEATURE**

**Rechtliche Anforderung:**
> "Die Aufstellung des Inventars ist innerhalb der einem ordnungsmäßigen Geschäftsgang entsprechenden Zeit zu bewirken. Das Inventar braucht nicht zu einem bestimmten Stichtag aufgestellt zu werden, wenn durch angemessene Stichproben festgestellt wird, dass der Buchbestand mit dem tatsächlichen Bestand übereinstimmt."

**ERP-Vorteil:**
- **Keine Betriebsschließung**: Anstatt das Lager am 31.12. zu schließen, ermöglicht das ERP eine **permanente Bestandsführung**.
- **Anforderung**: Das System muss exakte Lagerbestandsaufzeichnungen führen ("Buchbestand") und **regelmäßige Stichproben** ermöglichen.
- **Nutzen**: Großes Verkaufsargument für ERP-Systeme - vermeidet Betriebsunterbrechungen.

**ERP-Implementierung:**

```python
# apps/inventory/models.py
class StockMovement(BaseModel):
    """
    § 241 Abs. 2 HGB: Lagerbuchführung für permanente Inventur
    
    Jede Warenbewegung wird erfasst → Buchbestand = Ist-Bestand
    """
    product = models.ForeignKey('Product', on_delete=models.PROTECT)
    warehouse = models.ForeignKey('Warehouse', on_delete=models.PROTECT)
    
    movement_type = models.CharField(max_length=20, choices=[
        ('IN', 'Wareneingang'),
        ('OUT', 'Warenausgang'),
        ('TRANSFER', 'Umlagerung'),
        ('ADJUSTMENT', 'Korrektur'),
    ])
    
    quantity = models.DecimalField(max_digits=14, decimal_places=3)
    unit_cost = models.DecimalField(max_digits=14, decimal_places=2)
    
    # Fortgeschriebener Bestand (running balance)
    balance_after = models.DecimalField(max_digits=14, decimal_places=3)
    
    # Beleg-Referenz (§ 239 Abs. 2: Belegpflicht)
    document = models.ForeignKey('documents.Document', on_delete=models.PROTECT)
    
    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['product', 'warehouse', 'created_at']),
        ]

class CycleCount(BaseModel):
    """
    § 241 Abs. 2 HGB: Stichprobeninventur
    
    Regelmäßige Stichproben zur Validierung des Buchbestands
    """
    product = models.ForeignKey('Product', on_delete=models.PROTECT)
    warehouse = models.ForeignKey('Warehouse', on_delete=models.PROTECT)
    
    # Buchbestand vs. Ist-Bestand
    book_quantity = models.DecimalField(max_digits=14, decimal_places=3)
    counted_quantity = models.DecimalField(max_digits=14, decimal_places=3)
    variance = models.DecimalField(max_digits=14, decimal_places=3)
    
    # Toleranzprüfung
    within_tolerance = models.BooleanField()
    tolerance_threshold = models.DecimalField(max_digits=5, decimal_places=2)  # %
    
    # Korrektur bei Abweichung
    adjustment_created = models.BooleanField(default=False)
    adjustment = models.ForeignKey(StockMovement, on_delete=models.SET_NULL, null=True)

# apps/inventory/services.py
def validate_permanent_inventory_eligibility(company: Company) -> bool:
    """
    § 241 Abs. 2 HGB: Prüfung, ob permanente Inventur zulässig
    
    Voraussetzungen:
    1. Lagerbuchführung vorhanden (alle Bewegungen erfasst)
    2. Regelmäßige Stichproben durchgeführt
    3. Abweichungen innerhalb Toleranz
    """
    # Prüfe: Lückenlose Erfassung
    has_complete_tracking = check_stock_movement_completeness(company)
    
    # Prüfe: Regelmäßige Cycle Counts
    has_regular_counts = check_cycle_count_frequency(company)
    
    # Prüfe: Abweichungen akzeptabel
    variances_acceptable = check_variance_tolerance(company)
    
    return all([has_complete_tracking, has_regular_counts, variances_acceptable])
```

**Checkliste Permanente Inventur:**
- [ ] Alle Warenbewegungen in Echtzeit erfasst
- [ ] Stichproben (Cycle Counts) regelmäßig durchgeführt
- [ ] Abweichungen dokumentiert und untersucht
- [ ] Lagerbestands-Korrekturen verbucht, wenn Buchbestand ≠ Ist-Bestand
- [ ] System generiert Audit-Trail für alle Korrekturen

---

## 6. Handelsbriefe (§ 257 Abs. 1 Nr. 3-4)

### Definition "Handelsbrief"

**Rechtlicher Umfang:**
- Jegliche **Geschäftskorrespondenz** (Briefe, E-Mails, Faxe), die ein Handelsgeschäft betrifft.
- Dazu gehören: Bestellungen, Auftragsbestätigungen, Rechnungen, Lieferscheine, Reklamationen, Verträge.

**Aufbewahrungspflicht:**
- **Empfangene Handelsbriefe**: 10 Jahre (§ 257 Abs. 1 Nr. 3)
- **Abgesandte Handelsbriefe (Kopien)**: 10 Jahre (§ 257 Abs. 1 Nr. 4)

**ERP-Implementierung:**

```python
# apps/documents/models.py
class CommercialLetter(BaseModel):
    """
    § 257 Abs. 1 Nr. 3-4 HGB: Handelsbriefe
    """
    direction = models.CharField(max_length=10, choices=[
        ('INBOUND', 'Empfangen (§ 257 Abs. 1 Nr. 3)'),
        ('OUTBOUND', 'Abgesandt (§ 257 Abs. 1 Nr. 4)'),
    ])
    
    letter_type = models.CharField(max_length=50, choices=[
        ('ORDER', 'Bestellung'),
        ('ORDER_CONFIRMATION', 'Auftragsbestätigung'),
        ('INVOICE', 'Rechnung'),
        ('DELIVERY_NOTE', 'Lieferschein'),
        ('COMPLAINT', 'Reklamation'),
        ('CONTRACT', 'Vertrag'),
        ('EMAIL', 'E-Mail (geschäftlich)'),
    ])
    
    sender = models.CharField(max_length=200)
    recipient = models.CharField(max_length=200)
    subject = models.CharField(max_length=500)
    content = models.TextField()
    
    # § 257 Abs. 5: Aufbewahrungsfrist
    letter_date = models.DateField(db_index=True)
    retention_until = models.DateField()  # letter_date.year + 10 Jahre
    
    # Archivierung
    file_path = models.CharField(max_length=500)
    checksum = models.CharField(max_length=64)  # SHA-256
```

---

## 7. Größenklassen und Offenlegungspflichten (§§ 267-267a)

> **⚠️ Update April 2024**: Schwellenwerte wurden durch EU-Richtlinie angehoben (in DE umgesetzt April 2024).

### § 267a - Kleinstkapitalgesellschaften (Micro-Entities)

**Kriterien (§ 267a Abs. 1):**

| Kriterium | Schwellenwert (2024) | Bisher (bis 2024) |
|-----------|----------------------|-------------------|
| **Bilanzsumme** | ≤ 450.000 € | ≤ 350.000 € |
| **Umsatzerlöse** | ≤ 900.000 € | ≤ 700.000 € |
| **Arbeitnehmer** | ≤ 10 | ≤ 10 |

**Schwellenwert-Regel**: Mindestens 2 von 3 Kriterien müssen an zwei aufeinanderfolgenden Abschlussstichtagen erfüllt sein.

**Erleichterungen:**
- Verkürzte Bilanz
- Keine GuV erforderlich (optional)
- Kein Anhang erforderlich
- Keine Prüfung erforderlich

### § 267 - Größenklassen

**Kriterien (§ 267 Abs. 1-3) - Stand April 2024:**

| Größenklasse | Bilanzsumme | Umsatzerlöse | Arbeitnehmer |
|--------------|-------------|--------------|--------------|
| **Kleine** | ≤ 7.500.000 € | ≤ 15.000.000 € | ≤ 50 |
| **Mittelgroße** | ≤ 25.000.000 € | ≤ 50.000.000 € | ≤ 250 |
| **Große** | > 25.000.000 € | > 50.000.000 € | > 250 |

**Schwellenwert-Regel (§ 267 Abs. 4):**
- Eine Gesellschaft überschreitet/unterschreitet eine Größenklasse, wenn an **zwei aufeinanderfolgenden Abschlussstichtagen** jeweils **mindestens 2 der 3 Kriterien** erfüllt/nicht erfüllt sind.

**Offenlegungspflichten:**

| Größe | Bilanz | GuV | Anhang | Prüfung | Offenlegung |
|-------|--------|-----|--------|---------|-------------|
| Klein | Verkürzt | Verkürzt | Optional | Nein* | Eingeschränkt |
| Mittel | Voll | Voll | Ja | Ja | Voll |
| Groß | Voll | Voll | Ja | Ja | Voll |

*Kleine Gesellschaften sind von der Prüfung befreit, sofern es sich nicht um Kapitalgesellschaften handelt (GmbH, AG), wobei auch hier Ausnahmen gelten.

**ERP-Implementierung:**

```python
# apps/core/services.py
def determine_size_class(company: Company, fiscal_year: int) -> str:
    """
    § 267, § 267a HGB: Größenklassen (Stand: April 2024)
    
    WICHTIG: Schwellenwerte wurden im April 2024 angehoben!
    Das System muss konfigurierbar sein für historische Daten.
    """
    current_year = get_balance_sheet_data(company, fiscal_year)
    previous_year = get_balance_sheet_data(company, fiscal_year - 1)
    
    # Schwellenwerte (konfigurierbar für historische Auswertungen)
    thresholds = get_size_class_thresholds(fiscal_year)
    
    def check_criteria(data, thresholds):
        total_assets = data['total_assets']
        revenue = data['revenue']
        employees = data['avg_employees']
        
        # § 267a: Kleinstkapitalgesellschaften
        micro_count = sum([
            total_assets <= thresholds['micro']['assets'],     # 450k (2024)
            revenue <= thresholds['micro']['revenue'],         # 900k (2024)
            employees <= thresholds['micro']['employees']      # 10
        ])
        
        # § 267 Abs. 1: Kleine Kapitalgesellschaften
        small_count = sum([
            total_assets <= thresholds['small']['assets'],     # 7.5M (2024)
            revenue <= thresholds['small']['revenue'],         # 15M (2024)
            employees <= thresholds['small']['employees']      # 50
        ])
        
        # § 267 Abs. 2: Mittelgroße Kapitalgesellschaften
        medium_count = sum([
            total_assets <= thresholds['medium']['assets'],    # 25M (2024)
            revenue <= thresholds['medium']['revenue'],        # 50M (2024)
            employees <= thresholds['medium']['employees']     # 250
        ])
        
        # § 267 Abs. 4: Mindestens 2 von 3 Kriterien
        if micro_count >= 2:
            return 'MICRO'
        elif small_count >= 2:
            return 'SMALL'
        elif medium_count >= 2:
            return 'MEDIUM'
        else:
            return 'LARGE'
    
    current_class = check_criteria(current_year, thresholds)
    previous_class = check_criteria(previous_year, thresholds)
    
    # § 267 Abs. 4: Zwei aufeinanderfolgende Abschlussstichtage
    if current_class == previous_class:
        return current_class
    else:
        # Beibehaltung der bisherigen Größenklasse
        return company.current_size_class

def get_size_class_thresholds(fiscal_year: int) -> dict:
    """
    Historische Schwellenwerte für Größenklassen.
    
    WICHTIG: Für Vergleichbarkeit bei Betriebsprüfungen!
    """
    if fiscal_year >= 2024:
        # Neue Werte ab April 2024
        return {
            'micro': {'assets': 450_000, 'revenue': 900_000, 'employees': 10},
            'small': {'assets': 7_500_000, 'revenue': 15_000_000, 'employees': 50},
            'medium': {'assets': 25_000_000, 'revenue': 50_000_000, 'employees': 250},
        }
    else:
        # Alte Werte bis März 2024
        return {
            'micro': {'assets': 350_000, 'revenue': 700_000, 'employees': 10},
            'small': {'assets': 6_000_000, 'revenue': 12_000_000, 'employees': 50},
            'medium': {'assets': 20_000_000, 'revenue': 40_000_000, 'employees': 250},
        }
```

---

## 8. Buchungsbelege (§ 257 Abs. 1 Nr. 4)

### Definition "Buchungsbeleg"

**Rechtliche Anforderung:**
- Jeder Buchung muss ein **Beleg** zugrunde liegen ("Keine Buchung ohne Beleg").
- Belege müssen **10 Jahre** aufbewahrt werden.

**Belegarten:**
1. **Fremdbelege**: Eingangsrechnungen, Quittungen, Bankauszüge
2. **Eigenbelege**: Gehaltslisten, Abschreibungspläne, Umbuchungsbelege

**Hinweis zur E-Rechnung (ab 2025):** 
Auch wenn das HGB formatneutral ist, müssen Buchungsbelege im B2B-Bereich ab 01.01.2025 zunehmend im strukturierten Format (ZUGFeRD/XRechnung) vorliegen und im Originalformat archiviert werden (siehe auch ao_integration_checklist.md).

**ERP-Implementierung:**

```python
# apps/finance/models.py
class JournalEntry(BaseModel):
    """
    § 238, § 239 HGB: Buchungssatz mit Belegpflicht
    """
    transaction_id = models.UUIDField(unique=True, default=uuid.uuid4)
    
    # § 239 Abs. 2: Buchung muss Beleg referenzieren
    document = models.ForeignKey(
        'documents.Document',
        on_delete=models.PROTECT,
        help_text="§ 257 Abs. 1 Nr. 4 HGB: Buchungsbeleg"
    )
    document_number = models.CharField(max_length=100, db_index=True)
    document_date = models.DateField(db_index=True)
    
    # Buchungsdaten
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    description = models.TextField()
    booking_date = models.DateField(db_index=True)
    
    # Konten
    account = models.CharField(max_length=20)
    contra_account = models.CharField(max_length=20)
    
    # § 238 Abs. 2: Zeitgerechte Erfassung (GoBD: täglich bar, 10 Tage unbar)
    transaction_date = models.DateField(db_index=True, help_text="Geschäftsvorfall-Datum")
    days_until_booking = models.IntegerField(editable=False)
    
    def save(self, *args, **kwargs):
        # Berechne Verzögerung
        if self.transaction_date and self.booking_date:
            self.days_until_booking = (self.booking_date - self.transaction_date).days
        super().save(*args, **kwargs)
    
    # § 238 Abs. 2: Keine Buchung ohne Beleg
    class Meta:
        constraints = [
            models.CheckConstraint(
                check=~models.Q(document__isnull=True),
                name='hgb_buchung_requires_beleg'
            )
        ]
```

---

## 9. Sprachanforderungen (§ 239 Abs. 1)

### § 239 - Führung der Handelsbücher

**Rechtliche Anforderung:**
> "Die Eintragungen in Büchern und die sonst erforderlichen Aufzeichnungen müssen in einer lebenden Sprache gemacht werden."

**Zulässige Sprachen:**
- **Deutsch** (Standard)
- **Andere lebende Sprachen**, mit der Pflicht zur Übersetzung auf Verlangen der Finanzbehörde.

**Verboten:**
- Tote Sprachen (z.B. Latein)
- Codes oder Ziffern ohne Schlüssel

**ERP-Implementierung:**

```python
# apps/core/models.py
class CompanySettings(BaseModel):
    """
    § 239 Abs. 1 HGB: Sprache der Buchführung
    """
    company = models.OneToOneField(Company, on_delete=models.CASCADE)
    
    accounting_language = models.CharField(
        max_length=5,
        default='de',
        choices=[
            ('de', 'Deutsch'),
            ('en', 'Englisch'),
            ('fr', 'Französisch'),
            # Weitere lebende Sprachen
        ],
        help_text="§ 239 Abs. 1 HGB: Lebende Sprache"
    )
    
    # Wenn nicht Deutsch: Übersetzungspflicht
    requires_translation = models.BooleanField(default=False)
    
    def save(self, *args, **kwargs):
        if self.accounting_language != 'de':
            self.requires_translation = True
        super().save(*args, **kwargs)
```

**Technischer Hinweis: Status-Codes & Abkürzungen**

> **§ 239 Verbot von "Codes ohne Schlüssel"**: Wenn Ihr ERP Status-Codes verwendet (z.B. `status_id=5`), MÜSSEN Sie eine dauerhafte Legende pflegen, die Codes zu Bedeutungen zuordnet.

**Kritische Anforderung:**
- **Historische Konsistenz**: Die Bedeutung von `status_id=5` darf sich NIEMALS ändern.
- **Dauerhafte Legende**: Status-Code-Tabellen müssen über die gesamte Aufbewahrungsfrist erhalten bleiben.
- **Keine verwaisten Codes**: Jeder Code in der Datenbank muss einen Eintrag in der Legende haben.

**ERP-Implementierung:**

```python
# apps/core/models.py
class StatusCodeLegend(BaseModel):
    """
    § 239 Abs. 1 HGB: Codes müssen dauerhaft entschlüsselbar sein
    
    WICHTIG: Einträge dürfen NIEMALS gelöscht werden!
    """
    code_category = models.CharField(max_length=50)  # 'invoice_status', 'payment_status'
    code_value = models.IntegerField()
    code_meaning_de = models.CharField(max_length=200)
    code_meaning_en = models.CharField(max_length=200, blank=True)
    
    # Gültigkeit (für historische Codes)
    valid_from = models.DateField()
    valid_until = models.DateField(null=True, blank=True)
    
    # § 239: Codes dürfen nicht gelöscht werden!
    is_deprecated = models.BooleanField(default=False)
    deprecated_reason = models.TextField(blank=True)
    
    class Meta:
        unique_together = ['code_category', 'code_value', 'valid_from']
        constraints = [
            models.CheckConstraint(
                check=models.Q(is_deleted=False),
                name='hgb_status_codes_never_deleted'
            )
        ]
```

---

## 10. Unveränderbarkeit (§ 239 Abs. 3)

### § 239 Abs. 3 - Verbot der unprotokollierten Änderung

**Rechtliche Anforderung:**
> "Eine Eintragung oder eine Aufzeichnung darf nicht in einer Weise verändert werden, dass der ursprüngliche Inhalt nicht mehr feststellbar ist."

**Kernprinzip:**
- **Der ursprüngliche Inhalt muss immer feststellbar sein**.
- Korrekturen sind erlaubt, müssen aber nachvollziehbar sein (Storno & Neubuchung).

**Hinweis:** Für eine lückenlose Protokollierung (auch bei Hintergrund-Tasks) empfiehlt sich die Nutzung von Model-Signals (pre_save/post_save) statt reiner Middleware.

**ERP-Implementierung:**

```python
# apps/core/middleware.py
class AuditLogMiddleware:
    """
    § 239 Abs. 3 HGB: Unveränderbarkeit durch Audit Trail
    """
    def process_request(self, request):
        # Vor jeder Änderung: Alten Zustand speichern
        if request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            original_state = capture_current_state(request)
            request._original_state = original_state

    def process_response(self, request, response):
        if hasattr(request, '_original_state'):
            new_state = capture_new_state(request, response)
            
            AuditLog.objects.create(
                content_object=get_affected_object(request),
                action=request.method,
                user=request.user,
                old_values=request._original_state,
                new_values=new_state,
                timestamp=timezone.now(),
                ip_address=get_client_ip(request)
            )
        
        return response

# apps/finance/models.py
class JournalEntry(BaseModel):
    """
    § 239 Abs. 3: Keine direkte Änderung erlaubt
    """
    is_locked = models.BooleanField(default=False)
    locked_at = models.DateTimeField(null=True)
    
    def save(self, *args, **kwargs):
        # § 239 Abs. 3: Gesperrte Buchungen dürfen nicht geändert werden
        if self.pk and self.is_locked:
            raise ValidationError(
                "§ 239 Abs. 3 HGB: Gesperrte Buchung darf nicht geändert werden. "
                "Verwenden Sie eine Stornobuchung."
            )
        super().save(*args, **kwargs)
    
    def reverse(self, user: User, reason: str) -> 'JournalEntry':
        """
        § 239 Abs. 3 konforme Stornierung
        """
        reversal = JournalEntry.objects.create(
            document=self.document,
            amount=-self.amount,  # Umkehrung
            description=f"STORNO: {self.description} | Grund: {reason}",
            booking_date=timezone.now().date(),
            account=self.contra_account,  # Konten tauschen
            contra_account=self.account,
            created_by=user,
            reversal_of=self,  # Referenz zur Originalbuchung
        )
        
        # Original sperren
        self.is_locked = True
        self.locked_at = timezone.now()
        self.save()
        
        return reversal
```

---

## 11. Integration mit GoBD und AO

### Verhältnis zwischen HGB, GoBD und AO

| Vorschrift | Umfang | Autorität | Fokus |
|------------|--------|-----------|-------|
| **HGB** | Handelsrecht | Bundesgesetz | Buchführungsgrundsätze, Bilanzierung |
| **GoBD** | Steuerliche Buchführung | BMF-Schreiben | Elektronische Aufzeichnungen, Datenzugriff |
| **AO** | Steuerrecht | Bundesgesetz | Steuerpflichten, Aufbewahrung, Mitwirkung |

**Hierarchie:**
1. **HGB** (§§ 238-263): Fundament für alle kaufmännischen Aufzeichnungen
2. **AO** (§§ 140-147): Steuerspezifische Erweiterungen (z.B. ELSTER, Aufbewahrungsdetails)
3. **GoBD**: Technische Umsetzungshinweise für elektronische Systeme

**Wichtige Überschneidungen:**

| Anforderung | HGB | GoBD | AO |
|-------------|-----|------|----|
| Aufbewahrungsfrist | § 257 (10 Jahre) | Rz. 109-111 | § 147 (10 Jahre) |
| Nachvollziehbarkeit | § 238 | Rz. 44-56 | § 145 |
| Unveränderbarkeit | § 239 Abs. 3 | Rz. 102-108 | § 146 |
| Vollständigkeit | § 246 | Rz. 57-68 | § 140 |

**ERP-Strategie:**
- **HGB implementieren** als Basis für alle Buchhaltungslogik.
- **Erweitern mit GoBD** für technische Anforderungen (Audit Trail, Exportformate).
- **AO integrieren** für steuerspezifische Features (ELSTER, Z3 Datenzugriff).

---

## 12. HGB Compliance Checkliste

### Kernanforderungen

- [ ] **§ 238**: Alle Geschäftsvorfälle werden vollständig, richtig und zeitgerecht erfasst
- [ ] **§ 239 Abs. 1**: Buchführungssprache ist eine lebende Sprache (Deutsch oder mit Übersetzung)
- [ ] **§ 239 Abs. 3**: Keine Änderung von Einträgen ohne Nachvollziehbarkeit (Audit Log)
- [ ] **§ 240**: Jährliches Inventar mit Menge und Wert erstellt
- [ ] **§ 241**: Körperliche Bestandsaufnahme für Vorräte
- [ ] **§ 242**: Bilanz und GuV jährlich erstellt
- [ ] **§ 246**: Vollständigkeit des Jahresabschlusses, kein Saldierungsverbot verletzt
- [ ] **§ 252**: Bewertungsgrundsätze angewendet (Going Concern, Vorsicht, Stetigkeit)
- [ ] **§ 253**: Vermögensgegenstände zu Anschaffungskosten, Verbindlichkeiten zum Erfüllungsbetrag bewertet
- [ ] **§ 257**: Aufbewahrungsfristen durchgesetzt (10 Jahre für Bücher, Belege, Briefe)
- [ ] **§ 267**: Größenklassenbestimmung für Offenlegungspflichten

### Technische Umsetzung

- [ ] `BaseModel` mit Audit-Feldern (`created_at`, `created_by`, `version`, Soft Delete)
- [ ] `AuditLog` Model für alle CRUD-Operationen
- [ ] `Document` Model mit Berechnung der Aufbewahrungsfrist
- [ ] `JournalEntry` Model mit zwingender Belegreferenz
- [ ] `InventoryCount` Model für § 240/241 Compliance
- [ ] `CommercialLetter` Model für § 257 Nr. 3-4 Compliance
- [ ] Middleware für automatisches Audit-Logging
- [ ] Service Layer für Bilanzerstellung (§ 242, § 246)
- [ ] Bewertungslogik für Vermögensgegenstände (§ 253)
- [ ] Größenklassenbestimmung (§ 267)

### Datenschutz (HGB vs. DSGVO)

- [ ] Konfliktlösung: Sperrung statt Löschung für aufbewahrungspflichtige Daten
- [ ] `User.is_blocked` Flag für DSGVO-Löschanträge während der Aufbewahrungsfrist
- [ ] Automatischer Lösch-Scheduler nach Ablauf der Aufbewahrungsfrist
- [ ] Datenminimierung für gesperrte User (Entfernung nicht notwendiger Daten)

---

## 13. Referenzen

### Primärquellen
- **HGB (Handelsgesetzbuch)**: Volltext in `.agent/knowledge/HGB.md`
- **GoBD**: Siehe `gobd_official_summary.md` und `gobd_implementation_guide.md`
- **AO**: Siehe `ao_integration_checklist.md`
- **DSGVO**: Siehe `dsgvo_privacy_by_design.md`

### Schlüsselabschnitte für ERP-Entwicklung
- **§§ 238-239**: Buchführungspflichten
- **§§ 240-241**: Inventur
- **§§ 242-256a**: Jahresabschluss
- **§ 257**: Aufbewahrungsfristen
- **§§ 267-267a**: Größenklassen

### Implementierungsleitfäden
- `gobd_implementation_guide.md`: Technische Umsetzung von GoBD + HGB
- `ao_integration_checklist.md`: Steuerspezifische Erweiterungen
- `dsgvo_privacy_by_design.md`: Datenschutz-Compliance

---

## Dokumenten-Metadaten

- **Quelle**: HGB.md
- **Erstellt**: 2026-01-25
- **Zweck**: Wissensdatenbank für HGB-Compliance in der ERP-Systementwicklung
- **Verwandte Dokumente**: 
  - `gobd_official_summary.md`
  - `gobd_implementation_guide.md`
  - `ao_integration_checklist.md`
  - `dsgvo_privacy_by_design.md`
