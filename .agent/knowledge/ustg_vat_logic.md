# UStG (Umsatzsteuer) - Logic & Implementation Guide

## Zweck
Definition der Steuerfindungslogik (Tax Determination) für das ERP-System basierend auf dem Umsatzsteuergesetz (UStG).
Ziel ist die korrekte Ermittlung von Steuersatz, Steuerart und Hinweispflichten auf Rechnungen.

**Rechtsgrundlage:** UStG (Deutschland), MwStSystRL (EU)
**Zielgruppe:** Backend-Entwickler, Tax-Engineers

---

## 1. Die Steuer-Entscheidungsmatrix (Tax Determination Engine)
Ein ERP darf Steuersätze nicht hardcoden. Es muss sie dynamisch ermitteln basierend auf 4 Faktoren:

1.  **Absender:** Wo startet die Lieferung/Leistung? (Meist DE)
2.  **Empfänger:** Wo endet sie? (DE, EU, Drittland)
3.  **Kunden-Status:** B2B (Unternehmer) oder B2C (Privat)?
4.  **Art der Leistung:** Lieferung (Ware) oder sonstige Leistung (Service)?

### Entscheidungsbaum (Vereinfacht für DE-Unternehmen)

| Zielort | Kunde | Leistung | Steuer-Regel | UStG Referenz |
| :--- | :--- | :--- | :--- | :--- |
| **Inland (DE)** | B2B/B2C | Alle | **19% / 7%** (Regelsteuersatz) | § 12 UStG |
| **EU-Ausland** | **B2B** | Ware | **Steuerfrei** (Innergem. Lieferung) | § 4 Nr. 1b i.V.m. § 6a UStG |
| **EU-Ausland** | **B2B** | Service | **Reverse Charge** (Steuerschuldumkehr) | § 13b UStG |
| **EU-Ausland** | **B2C** | Ware | **OSS** (Steuersatz des Ziellandes!) | § 3c UStG (Fernverkauf) |
| **Drittland** | Alle | Ware | **Steuerfrei** (Ausfuhrlieferung) | § 4 Nr. 1a i.V.m. § 6 UStG |
| **Drittland** | B2B | Service | **Nicht steuerbar** in DE (Reverse Charge) | § 3a Abs. 2 UStG |

---

## 2. Pflichtangaben auf Rechnungen (§ 14 UStG)
Damit der Kunde Vorsteuer ziehen kann, muss die Rechnung formal korrekt sein.

**Zwingende technische Felder:**
1.  **Leistungszeitpunkt:** Datum der Lieferung oder Leistung (Darf vom Rechnungsdatum abweichen!).
    * *ERP-Logik:* Wenn `delivery_date` != `invoice_date`, muss der Satz "Leistungsdatum entspricht Rechnungsdatum" entfallen und das Datum explizit gedruckt werden.
2.  **USt-ID (VAT ID):** Bei EU-Geschäften (B2B) zwingend eigene UND fremde ID.
3.  **Hinweistexte:** Zwingend bei Steuerbefreiungen.

### Code-Mapping für Hinweistexte
```python
TAX_EXEMPTION_REASONS = {
    'INTRA_COMMUNITY_SUPPLY': 'Steuerfreie innergemeinschaftliche Lieferung (§ 4 Nr. 1b UStG)',
    'EXPORT_DELIVERY': 'Steuerfreie Ausfuhrlieferung (§ 4 Nr. 1a UStG)',
    'REVERSE_CHARGE': 'Steuerschuldnerschaft des Leistungsempfängers (Reverse Charge)',
    'SMALL_BUSINESS': 'Kein Umsatzsteuerausweis aufgrund Anwendung der Kleinunternehmerregelung (§ 19 UStG)',
}
```

---

## 3. Reverse Charge Verfahren (§ 13b UStG)
Der Leistungsempfänger (Kunde) schuldet die Steuer, nicht der Leistende. Die Rechnung wird Netto ausgestellt.

**Wann wendet das ERP das an?**

1.  B2B-Dienstleistungen ins EU-Ausland.
2.  Bauleistungen an andere Bauunternehmer.
3.  Lieferung bestimmter Gegenstände (Schrott, Elektronik ab 5.000€ - je nach Land).

**Implementierung:** Das System benötigt ein Flag am 'TaxKey' (Steuerschlüssel), das `is_reverse_charge = True` setzt.

---

## 4. Validierung von USt-Identifikationsnummern (VIES)
Bei innergemeinschaftlichen Lieferungen (steuerfrei) besteht eine Prüfpflicht. Ist die USt-ID des Kunden ungültig, haftet der Lieferant für die Steuer (19%).

**Anforderung:**
-   Qualifizierte Prüfung (Nummer + Name + Adresse)
-   Dokumentation der Prüfung (Audit Trail)

**Implementierung:**
```python
# apps/tax/services.py
def validate_vat_id(vat_id: str) -> dict:
    """
    Prüft USt-ID via BZSt oder EU VIES API.
    Wichtig für § 6a UStG Nachweis.
    """
    # 1. Format Check (Regex)
    if not validate_format(vat_id):
        raise ValidationError("Ungültiges Format")
        
    # 2. VIES API Call (SOAP/REST)
    result = vies_client.check_vat(vat_id)
    
    # 3. Protokollierung (Beweissicherung!)
    VatCheckLog.objects.create(
        vat_id=vat_id,
        is_valid=result.valid,
        request_id=result.request_identifier, # Wichtig für Beweis
        checked_at=timezone.now()
    )
    
    return result
```

---

## 5. Datenmodellierung für Steuern

### 5.1 Tax Key (Steuerschlüssel)
Verwende DATEV-kompatible Logik, aber moderne Architektur.

```python
# apps/finance/models.py
class TaxRule(BaseModel):
    """
    Definiert, wie und wo versteuert wird.
    """
    name = models.CharField(max_length=100) # z.B. "Innergem. Lieferung"
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2) # 0.00
    
    # Buchungslogik
    is_reverse_charge = models.BooleanField(default=False)
    is_intra_community = models.BooleanField(default=False)
    is_export = models.BooleanField(default=False)
    
    # Für DATEV-Export
    datev_tax_key = models.CharField(max_length=4) # z.B. "4" oder "40"
    
    # Pflichttext auf Rechnung
    invoice_note = models.CharField(max_length=200, blank=True)

class TaxDeterminationLog(BaseModel):
    """
    Protokolliert, warum das System welche Steuer gewählt hat.
    Wichtig für Betriebsprüfungen.
    """
    invoice = models.ForeignKey('sales.Invoice', on_delete=models.CASCADE)
    origin_country = models.CharField(max_length=2)
    destination_country = models.CharField(max_length=2)
    customer_is_company = models.BooleanField()
    product_type = models.CharField(max_length=20) # GOOD / SERVICE
    
    applied_rule = models.ForeignKey(TaxRule, on_delete=models.PROTECT)
```

---

## 6. Checkliste UStG-Implementierung

Bevor Code gemerged wird, prüfe:

- [ ] **Stammdaten:** USt-ID Feld am Kunden (mit Validierung)
- [ ] **Produkte:** Unterscheidung Ware/Dienstleistung (Flag am Produkt)
- [ ] **Tax Engine:** Logik für DE / EU / Drittland implementiert
- [ ] **Rechnungslayout:** Dynamische Hinweistexte je nach Steuerfall
- [ ] **Leistungsdatum:** Separates Feld zur Rechnungsdatum
- [ ] **Kleinunternehmer:** Globales Setting für § 19 UStG (Deaktiviert USt-Berechnung)

---
