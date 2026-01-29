# SEPA & Payment Standards - Implementation Guide

## Zweck
Technische Spezifikation für den unbaren Zahlungsverkehr im ERP-System.
Fokus auf SEPA-Überweisungen (SCT) und SEPA-Lastschriften (SDD) gemäß ISO 20022.

**Standard:** ISO 20022 XML
**Spezifikation:** DFÜ-Abkommen der Deutschen Kreditwirtschaft (Anlage 3)
**Zielgruppe:** Backend-Entwickler, Payment-Engineers

---

## 1. Unterstützte Formate (ISO 20022)

Deutsche Banken nutzen spezifische "Pain"-Formate (Pain = **Pa**yment **In**itiation).

| Typ | Format | XML-Schema (XSD) | Verwendungszweck |
| :--- | :--- | :--- | :--- |
| **Überweisung** | SEPA Credit Transfer | `pain.001.001.03` | Lieferanten bezahlen |
| **Lastschrift** | SEPA Direct Debit | `pain.008.001.02` | Geld von Kunden einziehen |
| **Kontoauszug** | CAMT | `camt.053.001.02` | Zahlungseingänge buchen |

**Wichtig:** Verwende keine generischen ISO-Generatoren, sondern solche, die die "DK-Spezifikationen" (Deutsche Kreditwirtschaft) unterstützen (z.B. keine Umlaute in bestimmten Feldern, spezifische Header).

---

## 2. Stammdaten-Anforderungen

### 2.1 IBAN & BIC
- **IBAN:** Validierung verpflichtend (Länge, Länderkennzeichen, Prüfziffer modulo-97).
- **BIC:** Nur noch für Drittstaaten zwingend, im SEPA-Raum oft optional ("IBAN only"), aber für das ERP empfohlen.

### 2.2 Gläubiger-Identifikationsnummer (Creditor ID)
Jedes Unternehmen, das Lastschriften einzieht, braucht eine Gläubiger-ID (z.B. `DE98ZZZ09999999999`).
- **Muss in den Firmeneinstellungen hinterlegt sein.**
- Wird in jedem `pain.008` XML im Header benötigt.

---

## 3. SEPA-Mandatsverwaltung (Mandate Management)

Ohne gültiges Mandat darf keine Lastschrift gezogen werden. Das ERP muss Mandate verwalten.

### 3.1 Datenmodell

```python
# apps/finance/models.py
class SepaMandate(BaseModel):
    """
    Verwaltung von SEPA-Lastschriftmandaten.
    """
    customer = models.ForeignKey('sales.Customer', on_delete=models.PROTECT)
    
    # Mandatsreferenz (Muss eindeutig sein!)
    mandate_reference = models.CharField(max_length=35, unique=True)
    
    # Typ
    mandate_type = models.CharField(choices=[
        ('CORE', 'Basislastschrift (B2C/B2B)'),
        ('B2B', 'Firmenlastschrift (Nur B2B - keine Rückgabe!)'),
    ])
    
    # Status
    status = models.CharField(choices=[
        ('ACTIVE', 'Aktiv'),
        ('CANCELLED', 'Widerrufen'),
        ('EXPIRED', 'Abgelaufen (36 Monate inaktiv)'),
    ])
    
    signature_date = models.DateField()
    last_used_date = models.DateField(null=True, blank=True)
    
    # Sequenz-Logik (Erste vs. Folgelastschrift)
    sequence_type = models.CharField(choices=[
        ('FRST', 'Erstlastschrift'),
        ('RCUR', 'Folgelastschrift'),
        ('OOFF', 'Einmallastschrift'),
        ('FNAL', 'Letzte Lastschrift'),
    ], default='FRST')

    def update_sequence_after_debit(self):
        """Nach erfolgreicher Lastschrift auf RCUR setzen."""
        if self.sequence_type == 'FRST':
            self.sequence_type = 'RCUR'
            self.save()
```

### 3.2 Pre-Notification (Vorabankündigung)

Der Kunde muss informiert werden, bevor abgebucht wird.
-   **Frist:** In der Regel 14 Tage vor Fälligkeit (verkürzbar durch AGB auf 1-2 Tage).
-   **ERP-Feature:** Das System muss eine E-Mail/Brief generieren: "Wir buchen Betrag X am [Datum] unter der Mandatsreferenz [Ref] und Gläubiger-ID [ID] ab."

---

## 4. Verwendungszweck (Remittance Information)

Strukturiert vs. Unstrukturiert.

**Empfehlung für ERP:** Nutze Unstructured (`<Ustrd>`) aber standardisiert: `Rechnung RE-2024-001 Kd-Nr 10050`
So können Banken und Buchhaltungssysteme die Zahlung automatisch zuordnen.

---

## 5. Implementierung XML-Generator
Nutze eine Bibliothek wie `sepaxml` (Python), aber validiere gegen DK-Schema.

```python
# apps/payments/services.py
from sepaxml import SepaDD

def generate_sepa_direct_debit_xml(
    invoices: list[Invoice],
    execution_date: date,
    company_config: CompanySettings
) -> str:
    """
    Erstellt pain.008 XML für Lastschrifteinzug.
    """
    sepa = SepaDD(
        config={
            "name": company_config.company_name,
            "IBAN": company_config.iban,
            "BIC": company_config.bic,
            "batch": True,
            "creditor_id": company_config.creditor_id,
            "currency": "EUR",
        }, 
        schema="pain.008.001.02" # DK Standard
    )
    
    for inv in invoices:
        mandate = inv.customer.active_mandate
        
        sepa.add_payment(
            payment={
                "name": inv.customer.name,
                "IBAN": inv.customer.iban,
                "BIC": inv.customer.bic,
                "amount": int(inv.total_amount * 100), # Cents!
                "type": mandate.sequence_type, # FRST/RCUR
                "collection_date": execution_date,
                "mandate_id": mandate.mandate_reference,
                "date_of_signature": mandate.signature_date,
                "description": f"Rechnung {inv.invoice_number}",
                "end_to_end_id": f"INV-{inv.id}" # Eindeutige ID für Tracking
            }
        )
        
        # Sequenz updaten (FRST -> RCUR)
        mandate.update_sequence_after_debit()
        
    return sepa.export()
```

---

## 6. Checkliste Zahlungsverkehr

Bevor Code gemerged wird, prüfe:

- [ ] **IBAN-Validierung** bei Eingabe (Modulo 97)
- [ ] **Gläubiger-ID** in Firmeneinstellungen
- [ ] **Mandatsverwaltung** (Status, Datum, Sequenztyp FRST/RCUR)
- [ ] **XML-Export** (pain.001 für Überweisungen, pain.008 für Lastschriften)
- [ ] **Pre-Notification** (Auto-Mail an Kunden vor Abbuchung)
- [ ] **End-to-End-ID** generieren (für automatischen Abgleich beim Import)

---
