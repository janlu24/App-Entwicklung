# DSGVO (Datenschutz-Grundverordnung) - Compliance Summary

## Zweck
Zusammenfassung der wichtigsten Compliance-Anforderungen aus der DSGVO (EU 2016/679) für das ERP-System.

**Stand:** 2025/2026  
**Zielgruppe:** Entwickler, Datenschutzbeauftragte, Compliance Officers

> **⚠️ KRITISCHER KONFLIKT:**  
> **HGB/AO sagt:** "Speicher das!" (10 Jahre)  
> **DSGVO sagt:** "Lösch das!" (Datenminimierung)  
>  
> **Dieser Konflikt muss architektonisch gelöst werden!**

---

## Grundprinzipien der DSGVO (Art. 5)

### 1. Rechtmäßigkeit, Verarbeitung nach Treu und Glauben, Transparenz (Art. 5 Abs. 1 lit. a)
- Verarbeitung nur mit Rechtsgrundlage (Einwilligung, Vertrag, rechtliche Verpflichtung, etc.)
- Transparente Information der betroffenen Personen
- Nachvollziehbare Verarbeitungsprozesse

### 2. Zweckbindung (Art. 5 Abs. 1 lit. b)
- Daten nur für festgelegte, eindeutige und legitime Zwecke erheben
- Keine Weiterverarbeitung für andere Zwecke (außer kompatible Zwecke)

### 3. Datenminimierung (Art. 5 Abs. 1 lit. c)
- Nur Daten erheben, die für den Zweck erforderlich sind
- "So viel wie nötig, so wenig wie möglich"

### 4. Richtigkeit (Art. 5 Abs. 1 lit. d)
- Daten müssen sachlich richtig und aktuell sein
- Unverzügliche Löschung oder Berichtigung unrichtiger Daten

### 5. Speicherbegrenzung (Art. 5 Abs. 1 lit. e)
- Daten nur so lange speichern, wie für den Zweck erforderlich
- Löschkonzept implementieren

### 6. Integrität und Vertraulichkeit (Art. 5 Abs. 1 lit. f)
- Angemessene Sicherheit der Daten
- Schutz vor unbefugter Verarbeitung, Verlust, Zerstörung

### 7. Rechenschaftspflicht (Art. 5 Abs. 2)
- Verantwortlicher muss Einhaltung aller Grundsätze nachweisen können
- Dokumentationspflicht

---

## Rechtsgrundlagen für Verarbeitung (Art. 6) ⭐ **KRITISCH FÜR ERP**

> **⚠️ WICHTIGE KLARSTELLUNG:**  
> **"Consent is King? NEIN!"** - Im ERP-Kontext ist **Einwilligung fast nie die Rechtsgrundlage** für Kerngeschäfte!

### Rechtsgrundlagen-Hierarchie für ERP-Systeme:

| Rechtsgrundlage | Wann im ERP? | Beispiel | Widerrufbar? |
|-----------------|--------------|----------|--------------|
| **lit. c: Rechtliche Verpflichtung** | ⭐ **HAUPTSÄCHLICH** | Rechnungen (§ 257 HGB), Lohnabrechnungen (SGB) | ❌ Nein |
| **lit. b: Vertragserfüllung** | ⭐ **HÄUFIG** | Kundendaten für Auftragsabwicklung, Lieferantenverträge | ❌ Nein |
| **lit. f: Berechtigtes Interesse** | Manchmal | Bonitätsprüfung, Betrugsbekämpfung | ⚠️ Widerspruch möglich |
| **lit. a: Einwilligung** | ⚠️ **SELTEN** | Newsletter, Marketing, optionale Features | ✅ Ja, jederzeit |

### Detaillierte Erklärung:

#### 1. **Rechtliche Verpflichtung** (Art. 6 Abs. 1 lit. c) ⭐ **PRIMÄR FÜR ERP**
- **Erforderlich zur Erfüllung gesetzlicher Pflichten**
- **Beispiele:**
  - Aufbewahrung von Rechnungen (§ 257 HGB, § 147 AO) → 10 Jahre
  - Lohnabrechnungen (SGB IV)
  - Steuererklärungen (AO)
  - Sozialversicherungsmeldungen
- **NICHT widerrufbar!** (Gesetz geht vor)

#### 2. **Vertragserfüllung** (Art. 6 Abs. 1 lit. b) ⭐ **HÄUFIG**
- **Erforderlich zur Erfüllung eines Vertrags**
- **Beispiele:**
  - Kundendaten für Rechnungsstellung
  - Lieferadresse für Warenversand
  - Mitarbeiterdaten aus Arbeitsvertrag
- **NICHT widerrufbar!** (Vertrag geht vor)

#### 3. **Berechtigtes Interesse** (Art. 6 Abs. 1 lit. f)
- **Interessenabwägung erforderlich**
- **Beispiele:**
  - Bonitätsprüfung
  - Betrugsbekämpfung
  - Videoüberwachung (mit Einschränkungen)
- **Widerspruchsrecht!** (Art. 21)

#### 4. **Einwilligung** (Art. 6 Abs. 1 lit. a) ⚠️ **SELTEN IM ERP**
- **Freiwillig, informiert, eindeutig, widerrufbar**
- **Beispiele:**
  - Newsletter-Versand
  - Marketing-E-Mails
  - Optionale Features (z.B. Standortdaten)
- **Jederzeit widerrufbar!**

> **⚠️ ARCHITEKTUR-FEHLER:**  
> Wenn du deine ERP-Architektur auf "Consent-Management" aufbaust, baust du das **falsche Fundament**!  
> **Rechnungen** verarbeitest du wegen **Gesetz** (lit. c), nicht wegen Einwilligung (lit. a).  
> **Lohnabrechnungen** verarbeitest du wegen **Arbeitsvertrag** (lit. b), nicht wegen Einwilligung.

**ERP Implementation:**
```python
# apps/core/models.py
class LegalBasisChoices(models.TextChoices):
    """
    Art. 6 DSGVO: Rechtsgrundlagen (sortiert nach ERP-Relevanz!)
    """
    LEGAL_OBLIGATION = 'legal_obligation', 'Rechtliche Verpflichtung (lit. c) - HGB/AO/SGB'
    CONTRACT = 'contract', 'Vertragserfüllung (lit. b) - Kunden-/Arbeitsvertrag'
    LEGITIMATE_INTEREST = 'legitimate_interest', 'Berechtigtes Interesse (lit. f)'
    CONSENT = 'consent', 'Einwilligung (lit. a) - nur für Marketing!'
    VITAL_INTEREST = 'vital_interest', 'Lebenswichtige Interessen (lit. d)'
    PUBLIC_INTEREST = 'public_interest', 'Öffentliches Interesse (lit. e)'


class BaseModel(models.Model):
    """Basis-Modell mit DSGVO-Feldern."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT)
    
    # Art. 6 DSGVO: Rechtsgrundlage (PFLICHT!)
    legal_basis = models.CharField(
        max_length=50,
        choices=LegalBasisChoices.choices,
        default=LegalBasisChoices.LEGAL_OBLIGATION  # ⭐ Default für ERP!
    )
    legal_basis_details = models.TextField(
        blank=True,
        help_text="z.B. '§ 257 HGB - Aufbewahrungspflicht Rechnungen'"
    )
    
    # Art. 17 DSGVO: Löschfrist (nur wenn NICHT gesetzlich verpflichtet!)
    retention_until = models.DateField(null=True, blank=True)
    
    class Meta:
        abstract = True
```

---

## Besondere Kategorien personenbezogener Daten (Art. 9)

**Verbot der Verarbeitung** (außer bei Ausnahmen):
- Rassische/ethnische Herkunft
- Politische Meinungen
- Religiöse/weltanschauliche Überzeugungen
- Gewerkschaftszugehörigkeit
- Genetische Daten
- Biometrische Daten (zur eindeutigen Identifizierung)
- Gesundheitsdaten
- Sexualleben/sexuelle Orientierung

**Für ERP-System:** Gesundheitsdaten von Mitarbeitern nur mit expliziter Einwilligung oder gesetzlicher Grundlage!

---

## Betroffenenrechte (Art. 12-23)

### 1. Informationspflichten (Art. 13-14)
**Bei Direkterhebung:**
- Identität des Verantwortlichen
- Zweck der Verarbeitung
- Rechtsgrundlage
- Empfänger der Daten
- Speicherdauer
- Betroffenenrechte
- Widerrufsrecht bei Einwilligung

### 2. Auskunftsrecht (Art. 15) ⭐ **ONE-CLICK EXPORT ERFORDERLICH**

**Anforderung:**
- Betroffene Person hat Recht auf Auskunft über gespeicherte Daten
- Kostenlos (außer bei offensichtlich unbegründeten Anfragen)
- Frist: 1 Monat

> **⚠️ PROBLEM:**  
> Ein Kunde schreibt: "Sagen Sie mir alles, was Sie über mich wissen."  
> Ein Mitarbeiter muss dann händisch durch 50 Tabellen suchen? **NEIN!**

**Lösung: One-Click-Export**

```python
# apps/users/services.py
from decimal import Decimal
from datetime import date

def export_all_personal_data(user: User) -> dict:
    """
    Art. 15 DSGVO: Auskunftsrecht (One-Click-Export)
    
    Aggregiert ALLE personenbezogenen Daten über alle Module hinweg.
    """
    # 1. Stammdaten
    personal_data = {
        'user_id': str(user.id),
        'email': user.email,
        'name': user.get_full_name(),
        'created_at': user.created_at.isoformat(),
        'last_login': user.last_login.isoformat() if user.last_login else None,
    }
    
    # 2. Rechnungen (sales)
    invoices = []
    for invoice in user.customer.invoices.all():
        invoices.append({
            'invoice_number': invoice.invoice_number,
            'date': invoice.invoice_date.isoformat(),
            'total': str(invoice.total_gross),
            'status': invoice.status,
        })
    
    # 3. Bestellungen (sales)
    orders = []
    for order in user.customer.orders.all():
        orders.append({
            'order_number': order.order_number,
            'date': order.order_date.isoformat(),
            'total': str(order.total),
        })
    
    # 4. Zahlungen (finance)
    payments = []
    for payment in user.customer.payments.all():
        payments.append({
            'payment_date': payment.payment_date.isoformat(),
            'amount': str(payment.amount),
            'method': payment.payment_method,
        })
    
    # 5. Kommunikation (documents)
    communications = []
    for email in user.customer.emails.all():
        communications.append({
            'date': email.sent_at.isoformat(),
            'subject': email.subject,
            'type': 'email',
        })
    
    # 6. Einwilligungen (consent)
    consents = []
    for consent in user.consents.all():
        consents.append({
            'purpose': consent.purpose,
            'given_at': consent.given_at.isoformat(),
            'withdrawn_at': consent.withdrawn_at.isoformat() if consent.withdrawn_at else None,
            'consent_text': consent.consent_text,
        })
    
    # 7. Audit-Logs (nur eigene Aktionen)
    audit_logs = []
    for log in AuditLog.objects.filter(user=user).order_by('-timestamp')[:100]:
        audit_logs.append({
            'timestamp': log.timestamp.isoformat(),
            'action': log.action,
            'model': log.model_name,
        })
    
    # Aggregiertes Ergebnis
    return {
        'export_date': date.today().isoformat(),
        'legal_basis': 'Art. 15 DSGVO - Auskunftsrecht',
        'personal_data': personal_data,
        'invoices': invoices,
        'orders': orders,
        'payments': payments,
        'communications': communications,
        'consents': consents,
        'audit_logs': audit_logs,
    }


def generate_gdpr_export_pdf(user: User) -> bytes:
    """
    Generiert PDF-Export für Art. 15 DSGVO.
    """
    data = export_all_personal_data(user)
    
    # PDF generieren (z.B. mit ReportLab)
    pdf = generate_pdf_from_dict(data)
    
    # Audit-Log
    AuditLog.objects.create(
        user=user,
        action='GDPR_DATA_EXPORT',
        model_name='User',
        object_id=user.id,
        field_name='full_export',
        old_value=None,
        new_value='PDF generated'
    )
    
    return pdf
```

**Checkliste One-Click-Export:**
- [ ] Alle Module durchsuchen (sales, finance, inventory, etc.)
- [ ] JSON-Export implementiert
- [ ] PDF-Export implementiert
- [ ] Audit-Logging
- [ ] Test mit echten Daten
- [ ] Dokumentation für Anwender

### 3. Recht auf Berichtigung (Art. 16)
- Unverzügliche Berichtigung unrichtiger Daten

### 4. Recht auf Löschung vs. Einschränkung der Verarbeitung ⭐ **KRITISCH**

> **⚠️ WICHTIGE UNTERSCHEIDUNG:**  
> **Art. 17 (Löschen)** ≠ **Art. 18 (Einschränken)**  
> Du musst technisch zwischen **physikalischer Löschung** und **Sperrung** unterscheiden!

#### Art. 17: Recht auf Löschung ("Recht auf Vergessenwerden")

**Löschpflicht, wenn:**
- Daten nicht mehr erforderlich
- Einwilligung widerrufen
- Widerspruch eingelegt
- Daten unrechtmäßig verarbeitet
- Gesetzliche Löschpflicht

**Ausnahmen:**
- **Rechtliche Verpflichtungen** (z.B. Aufbewahrungspflichten nach AO) ⭐ **HAUPTFALL IM ERP**
- Rechtliche Ansprüche

#### Art. 18: Recht auf Einschränkung der Verarbeitung

**Sperrung statt Löschung:**
- Daten, die aufgrund HGB/AO (10 Jahre) aufbewahrt werden müssen, dürfen **nicht gelöscht** werden
- Sie müssen aber für den **normalen Zugriff gesperrt** werden
- Zugriff nur noch für Admins/Prüfer, **nicht mehr für Vertriebler**

**ERP Implementation:**

```python
# apps/users/models.py
class User(AbstractBaseUser):
    """
    Custom User Model mit DSGVO-Feldern.
    """
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    
    # Art. 18 DSGVO: Einschränkung der Verarbeitung
    processing_restricted = models.BooleanField(default=False)
    processing_restriction_reason = models.CharField(max_length=200, blank=True, choices=[
        ('RETENTION_OBLIGATION', 'Aufbewahrungspflicht (HGB/AO)'),
        ('LEGAL_DISPUTE', 'Rechtsstreit'),
        ('ACCURACY_CONTESTED', 'Richtigkeit bestritten'),
        ('OTHER', 'Sonstige'),
    ])
    processing_restriction_until = models.DateField(null=True, blank=True)
    
    # Art. 17 DSGVO: Löschung
    deletion_requested_at = models.DateTimeField(null=True, blank=True)
    deletion_approved_at = models.DateTimeField(null=True, blank=True)


# apps/users/services.py
def handle_deletion_request(user: User, reason: str) -> dict:
    """
    Art. 17 vs. Art. 18 DSGVO: Löschen vs. Einschränken
    
    Prüft Löschantrag gegen Aufbewahrungspflichten (HGB/AO).
    """
    # Prüfung auf Aufbewahrungspflichten
    retention_check = check_retention_obligations(user)
    
    if retention_check['has_obligations']:
        # Art. 18: Einschränkung der Verarbeitung (Sperrung)
        user.processing_restricted = True
        user.processing_restriction_reason = 'RETENTION_OBLIGATION'
        user.processing_restriction_until = retention_check['until']
        user.deletion_requested_at = timezone.now()
        user.save()
        
        # Pseudonymisierung (optional, aber empfohlen)
        pseudonymize_user_data(user)
        
        # Audit-Log
        AuditLog.objects.create(
            user=user,
            action='PROCESSING_RESTRICTED',
            model_name='User',
            object_id=user.id,
            field_name='processing_restricted',
            old_value='False',
            new_value='True'
        )
        
        return {
            'status': 'RESTRICTED',
            'message': f'Verarbeitung eingeschränkt bis {retention_check["until"]}',
            'reason': retention_check['reason'],
            'legal_basis': 'Art. 18 DSGVO + § 257 HGB/§ 147 AO',
        }
    else:
        # Art. 17: Vollständige Löschung
        user.deletion_approved_at = timezone.now()
        user.save()
        
        # Physikalische Löschung
        delete_user_data_permanently(user)
        
        # Audit-Log (vor Löschung!)
        AuditLog.objects.create(
            user=None,  # User wird gelöscht
            action='USER_DELETED',
            model_name='User',
            object_id=user.id,
            field_name='deletion',
            old_value=user.email,
            new_value='DELETED'
        )
        
        user.delete()
        
        return {
            'status': 'DELETED',
            'message': 'Daten vollständig gelöscht',
            'legal_basis': 'Art. 17 DSGVO',
        }


def check_retention_obligations(user: User) -> dict:
    """
    Prüft Aufbewahrungspflichten nach HGB/AO.
    """
    # Prüfe: Hat User Rechnungen/Belege?
    latest_invoice = user.customer.invoices.order_by('-invoice_date').first()
    
    if latest_invoice:
        # § 257 HGB: 10 Jahre ab Ende des Kalenderjahres
        retention_until = date(latest_invoice.invoice_date.year + 10, 12, 31)
        
        if date.today() < retention_until:
            return {
                'has_obligations': True,
                'until': retention_until,
                'reason': f'§ 257 HGB - Letzte Rechnung: {latest_invoice.invoice_number}',
            }
    
    # Prüfe: Laufende Rechtsstreite?
    if has_active_legal_disputes(user):
        return {
            'has_obligations': True,
            'until': None,  # Unbestimmt
            'reason': 'Laufender Rechtsstreit',
        }
    
    return {'has_obligations': False}


def pseudonymize_user_data(user: User):
    """
    Pseudonymisierung für Art. 18 (Einschränkung).
    
    ACHTUNG: Darf nur erfolgen, wenn historische Belege (Rechnungen) 
    die Daten als Snapshot gespeichert haben! Sonst Verletzung der GoBD.
    """
    user.first_name = f'User_{user.id[:8]}'
    user.last_name = 'ANONYMIZED'
    user.email = f'deleted_{user.id}@anonymized.local'
    user.save()
```

### 5. Recht auf Datenübertragbarkeit (Art. 20)
- Daten in strukturiertem, maschinenlesbarem Format
- Nur bei automatisierter Verarbeitung auf Basis Einwilligung/Vertrag

### 6. Widerspruchsrecht (Art. 21)
- Widerspruch gegen Verarbeitung auf Basis berechtigter Interessen
- Absolutes Widerspruchsrecht bei Direktwerbung

---

## Auftragsverarbeitung (Art. 28 DSGVO) ⭐ **KRITISCH FÜR SAAS**

> **Wenn du das ERP als Cloud-Lösung (SaaS) anbietest, bist DU der Auftragsverarbeiter für deine Kunden!**

**Anforderung:**
- **Schriftlicher Vertrag erforderlich** (Auftragsverarbeitungsvertrag/AVV, engl. DPA - Data Processing Agreement)
- Auftragsverarbeiter nur auf dokumentierte Weisung
- Vertraulichkeitsverpflichtung
- Technische und organisatorische Maßnahmen
- Unterauftragsverarbeiter nur mit Genehmigung

**ERP Implementation:**

```python
# apps/core/models.py
class DataProcessingAgreement(BaseModel):
    """
    Art. 28 DSGVO: Auftragsverarbeitungsvertrag (AVV/DPA)
    
    Für SaaS-ERP: Automatisierter DPA beim Onboarding.
    """
    customer = models.OneToOneField('customers.Customer', on_delete=models.PROTECT)
    
    # DPA-Inhalt
    dpa_version = models.CharField(max_length=20)  # z.B. "2024-01-v1"
    dpa_text = models.TextField()  # Vollständiger Vertragstext
    
    # Akzeptanz
    accepted_at = models.DateTimeField()
    accepted_by = models.ForeignKey(User, on_delete=models.PROTECT)
    accepted_via = models.CharField(max_length=50)  # 'WEB_INTERFACE', 'EMAIL', 'SIGNED_PDF'
    
    # IP-Nachweis
    ip_address = models.GenericIPAddressField()
    
    # Unterauftragsverarbeiter
    subprocessors = models.JSONField(default=list, help_text="Liste der Sub-Processors (z.B. AWS, Stripe)")
    subprocessors_approved_at = models.DateTimeField(null=True)
    
    # Technische und organisatorische Maßnahmen (TOM)
    tom_document = models.FileField(upload_to='dpa/tom/')
    
    class Meta:
        verbose_name = 'Auftragsverarbeitungsvertrag (DPA)'


# apps/core/services.py
def create_dpa_on_signup(customer: Customer, user: User, ip_address: str) -> DataProcessingAgreement:
    """
    Erstellt automatisch DPA beim Kunden-Onboarding.
    """
    dpa_text = generate_dpa_text(customer)
    
    dpa = DataProcessingAgreement.objects.create(
        customer=customer,
        dpa_version='2024-01-v1',
        dpa_text=dpa_text,
        accepted_at=timezone.now(),
        accepted_by=user,
        accepted_via='WEB_INTERFACE',
        ip_address=ip_address,
        subprocessors=[
            {'name': 'AWS', 'service': 'Cloud Hosting', 'location': 'EU (Frankfurt)'},
            {'name': 'Stripe', 'service': 'Payment Processing', 'location': 'EU'},
        ]
    )
    
    # TOM-Dokument generieren
    tom_pdf = generate_tom_document()
    dpa.tom_document.save('tom.pdf', tom_pdf)
    
    return dpa
```

**Checkliste DPA:**
- [ ] DPA-Template erstellt
- [ ] Automatische DPA-Generierung beim Onboarding
- [ ] Liste der Unterauftragsverarbeiter (Sub-Processors)
- [ ] TOM-Dokument (Technische und organisatorische Maßnahmen)
- [ ] IP-Logging für Nachweis
- [ ] Versionierung des DPA

---

## Verzeichnis von Verarbeitungstätigkeiten (Art. 30) ⭐ **EXPORT FÜR KUNDEN**

**Pflicht für Unternehmen mit > 250 Mitarbeitern** (oder bei risikoreichen Verarbeitungen)

> **⚠️ PROBLEM:**  
> Deine Kunden müssen ein Verzeichnis führen, welche Daten sie warum verarbeiten.  
> Sollen sie das händisch aus deinem ERP abtippen? **NEIN!**

**Lösung: Vorbefülltes Verarbeitungsverzeichnis**

```python
# apps/core/services.py
def generate_processing_record_for_customer(customer: Customer) -> dict:
    """
    Art. 30 DSGVO: Verzeichnis von Verarbeitungstätigkeiten
    
    Generiert vorbefülltes Verzeichnis für den Kunden (Export für DSB).
    """
    processing_activities = []
    
    # 1. Kundenverwaltung
    processing_activities.append({
        'name': 'Kundenverwaltung',
        'purpose': 'Verwaltung von Kundenstammdaten für Auftragsabwicklung',
        'legal_basis': 'Art. 6 Abs. 1 lit. b DSGVO (Vertragserfüllung)',
        'data_categories': [
            'Name, Vorname',
            'E-Mail-Adresse',
            'Telefonnummer',
            'Rechnungsadresse',
            'Lieferadresse',
        ],
        'recipients': [
            'Versanddienstleister (DHL, UPS)',
            'Zahlungsdienstleister (Stripe, PayPal)',
        ],
        'retention_period': '10 Jahre nach letzter Rechnung (§ 257 HGB)',
        'tom': 'Verschlüsselung, Zugriffskontrolle, Backup',
    })
    
    # 2. Rechnungswesen
    processing_activities.append({
        'name': 'Rechnungswesen',
        'purpose': 'Erstellung und Verwaltung von Rechnungen',
        'legal_basis': 'Art. 6 Abs. 1 lit. c DSGVO (Rechtliche Verpflichtung - § 257 HGB)',
        'data_categories': [
            'Name, Vorname',
            'Rechnungsadresse',
            'Steuernummer (bei B2B)',
            'Bankverbindung',
            'Rechnungsbeträge',
        ],
        'recipients': [
            'Steuerberater',
            'Finanzbehörden (bei Prüfung)',
        ],
        'retention_period': '10 Jahre (§ 257 HGB, § 147 AO)',
        'tom': 'Verschlüsselung, Audit-Trail, Backup',
    })
    
    # 3. Mitarbeiterverwaltung (falls vorhanden)
    if customer.has_employees:
        processing_activities.append({
            'name': 'Mitarbeiterverwaltung',
            'purpose': 'Verwaltung von Mitarbeiterdaten, Lohnabrechnung',
            'legal_basis': 'Art. 6 Abs. 1 lit. b DSGVO (Arbeitsvertrag) + lit. c (SGB IV)',
            'data_categories': [
                'Name, Vorname',
                'Geburtsdatum',
                'Sozialversicherungsnummer',
                'Bankverbindung',
                'Steuer-ID',
                'Gehaltsdaten',
            ],
            'recipients': [
                'Krankenkassen',
                'Finanzamt',
                'Sozialversicherungsträger',
            ],
            'retention_period': '10 Jahre (§ 257 HGB)',
            'tom': 'Verschlüsselung, Zugriffskontrolle, Audit-Trail',
        })
    
    return {
        'customer': customer.name,
        'generated_at': date.today().isoformat(),
        'system': 'ERP System v1.0',
        'processing_activities': processing_activities,
    }


def export_processing_record_pdf(customer: Customer) -> bytes:
    """
    Exportiert Verarbeitungsverzeichnis als PDF für Datenschutzbeauftragten.
    """
    data = generate_processing_record_for_customer(customer)
    pdf = generate_pdf_from_dict(data)
    return pdf
```

**Checkliste Verarbeitungsverzeichnis:**
- [ ] Alle Verarbeitungstätigkeiten identifiziert
- [ ] Rechtsgrundlagen dokumentiert
- [ ] Datenkategorien aufgelistet
- [ ] Empfänger benannt
- [ ] Löschfristen definiert
- [ ] Export-Funktion für Kunden

---

## Umgang mit Testdaten (Art. 5 & 32) ⭐ **ENTWICKLER-FALLE**

> **⚠️ VERBOTEN:**  
> Produktions-Datenbank auf Staging/Localhost kopieren, wenn dort Echtdaten (Namen, Adressen) drin sind!

**Problem:**
- Entwickler kopieren gerne die Produktions-DB auf den Staging-Server, um Bugs zu fixen
- Unter der DSGVO ist das **streng verboten**, wenn dort personenbezogene Daten sind

**Lösung: Anonymisierungs-Strategie**

```python
# apps/core/management/commands/anonymize_for_staging.py
from django.core.management.base import BaseCommand
from faker import Faker

class Command(BaseCommand):
    """
    Anonymisiert Produktionsdaten für Staging/Development.
    
    Usage: python manage.py anonymize_for_staging
    """
    
    def handle(self, *args, **options):
        fake = Faker('de_DE')
        
        # 1. Anonymisiere User
        for user in User.objects.all():
            user.first_name = fake.first_name()
            user.last_name = fake.last_name()
            user.email = fake.email()
            user.save()
        
        # 2. Anonymisiere Kunden
        for customer in Customer.objects.all():
            customer.name = fake.company()
            customer.address = fake.street_address()
            customer.city = fake.city()
            customer.postal_code = fake.postcode()
            customer.phone = fake.phone_number()
            customer.email = fake.company_email()
            customer.save()
        
        # 3. Anonymisiere Mitarbeiter
        for employee in Employee.objects.all():
            employee.first_name = fake.first_name()
            employee.last_name = fake.last_name()
            employee.email = fake.email()
            employee.social_security_number = fake.ssn()
            employee.save()
        
        # 4. Lösche sensible Dokumente
        Document.objects.filter(document_type='CONTRACT').delete()
        
        self.stdout.write(self.style.SUCCESS('Daten erfolgreich anonymisiert!'))


# Alternative: Seed-Data für Development
# apps/core/management/commands/seed_dev_data.py
class Command(BaseCommand):
    """
    Generiert Fake-Daten für Development.
    
    Usage: python manage.py seed_dev_data
    """
    
    def handle(self, *args, **options):
        fake = Faker('de_DE')
        
        # Erstelle 100 Fake-Kunden
        for _ in range(100):
            Customer.objects.create(
                name=fake.company(),
                address=fake.street_address(),
                city=fake.city(),
                postal_code=fake.postcode(),
                email=fake.company_email(),
            )
        
        # Erstelle 50 Fake-Rechnungen
        for _ in range(50):
            Invoice.objects.create(
                customer=Customer.objects.order_by('?').first(),
                invoice_number=fake.bothify(text='RE-####-????'),
                invoice_date=fake.date_this_year(),
                total_gross=Decimal(fake.random_int(min=100, max=10000)),
            )
        
        self.stdout.write(self.style.SUCCESS('Seed-Daten erfolgreich erstellt!'))
```

**Checkliste Testdaten:**
- [ ] Anonymisierungs-Script erstellt
- [ ] Seed-Data-Script für Development
- [ ] Dokumentation für Entwickler
- [ ] Prozess: Niemals Produktions-DB kopieren!
- [ ] CI/CD: Automatische Anonymisierung für Staging

---

## Einwilligungsverwaltung (Art. 7) ⭐ **PROTOKOLLIERUNG PFLICHT**

> **⚠️ PROBLEM:**  
> `consent_given = BooleanField()` reicht **NICHT**!  
> Wenn du Einwilligung speicherst, brauchst du **Protokollierung**: Wer hat wann, worein und wie eingewilligt?

**ERP Implementation:**

```python
# apps/core/models.py
class Consent(BaseModel):
    """
    Art. 7 DSGVO: Einwilligungen mit vollständiger Protokollierung.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='consents')
    
    # Zweck
    purpose = models.CharField(max_length=200, choices=[
        ('NEWSLETTER', 'Newsletter-Versand'),
        ('MARKETING', 'Marketing-E-Mails'),
        ('PROFILING', 'Profiling/Personalisierung'),
        ('THIRD_PARTY', 'Weitergabe an Dritte'),
        ('OTHER', 'Sonstige'),
    ])
    purpose_details = models.TextField()
    
    # Einwilligungstext (MUSS gespeichert werden!)
    consent_text = models.TextField(help_text="Vollständiger Text, dem zugestimmt wurde")
    consent_version = models.CharField(max_length=20)  # z.B. "2024-01-v1"
    
    # Zeitpunkt
    given_at = models.DateTimeField(auto_now_add=True)
    withdrawn_at = models.DateTimeField(null=True, blank=True)
    
    # Nachweis (WICHTIG!)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()  # Browser/Device
    consent_method = models.CharField(max_length=50, choices=[
        ('CHECKBOX', 'Checkbox (Web)'),
        ('DOUBLE_OPT_IN', 'Double-Opt-In (E-Mail)'),
        ('VERBAL', 'Mündlich (dokumentiert)'),
        ('WRITTEN', 'Schriftlich'),
    ])
    
    # Double-Opt-In (falls zutreffend)
    confirmation_token = models.CharField(max_length=100, blank=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    confirmation_ip = models.GenericIPAddressField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Einwilligung'
        verbose_name_plural = 'Einwilligungen'
        ordering = ['-given_at']


# apps/core/services.py
def record_consent(
    user: User,
    purpose: str,
    consent_text: str,
    ip_address: str,
    user_agent: str,
    method: str = 'CHECKBOX'
) -> Consent:
    """
    Protokolliert Einwilligung mit allen erforderlichen Nachweisen.
    """
    consent = Consent.objects.create(
        user=user,
        purpose=purpose,
        purpose_details=f'Einwilligung für {purpose}',
        consent_text=consent_text,
        consent_version='2024-01-v1',
        ip_address=ip_address,
        user_agent=user_agent,
        consent_method=method,
    )
    
    # Audit-Log
    AuditLog.objects.create(
        user=user,
        action='CONSENT_GIVEN',
        model_name='Consent',
        object_id=consent.id,
        field_name='purpose',
        old_value=None,
        new_value=purpose
    )
    
    return consent


def withdraw_consent(consent: Consent, reason: str = '') -> None:
    """
    Widerruft Einwilligung.
    """
    consent.withdrawn_at = timezone.now()
    consent.save()
    
    # Audit-Log
    AuditLog.objects.create(
        user=consent.user,
        action='CONSENT_WITHDRAWN',
        model_name='Consent',
        object_id=consent.id,
        field_name='withdrawn_at',
        old_value='None',
        new_value=timezone.now().isoformat()
    )
```

---

## Technische und organisatorische Maßnahmen (Art. 32)

**Pflicht zur Umsetzung angemessener Sicherheitsmaßnahmen:**

1. **Pseudonymisierung und Verschlüsselung**
   - Verschlüsselung sensibler Daten
   - Pseudonymisierung wo möglich

2. **Vertraulichkeit**
   - Zugriffskontrolle (RBAC)
   - Authentifizierung
   - Berechtigungskonzept

3. **Integrität**
   - Schutz vor unbefugter Änderung
   - Audit-Logging

4. **Verfügbarkeit und Belastbarkeit**
   - Backup-Konzept
   - Disaster Recovery

5. **Verfahren zur regelmäßigen Überprüfung**
   - Regelmäßige Tests
   - Sicherheitsaudits

---

## Datenschutz-Folgenabschätzung (Art. 35)

**Erforderlich bei:**
- Systematischer umfangreicher Bewertung persönlicher Aspekte (Profiling)
- Umfangreicher Verarbeitung besonderer Kategorien (Art. 9)
- Systematischer umfangreicher Überwachung öffentlich zugänglicher Bereiche

**Inhalt:**
- Beschreibung der Verarbeitungsvorgänge
- Bewertung der Notwendigkeit und Verhältnismäßigkeit
- Bewertung der Risiken
- Geplante Abhilfemaßnahmen

---

## Meldepflicht bei Datenpannen (Art. 33-34)

### Meldung an Aufsichtsbehörde (Art. 33)
- **Frist:** 72 Stunden nach Bekanntwerden
- **Inhalt:** Art der Verletzung, Kategorien betroffener Personen, wahrscheinliche Folgen, Abhilfemaßnahmen

### Benachrichtigung betroffener Personen (Art. 34)
- **Erforderlich bei:** Hohes Risiko für Rechte und Freiheiten
- **Unverzüglich** in klarer und einfacher Sprache

```python
# apps/core/models.py
class DataBreach(BaseModel):
    """Dokumentation von Datenpannen (Art. 33 DSGVO)."""
    detected_at = models.DateTimeField(auto_now_add=True)
    reported_to_authority_at = models.DateTimeField(null=True)
    affected_persons_notified_at = models.DateTimeField(null=True)
    
    description = models.TextField()
    affected_data_categories = models.JSONField()
    affected_persons_count = models.IntegerField()
    
    risk_level = models.CharField(
        max_length=20,
        choices=[('LOW', 'Niedrig'), ('MEDIUM', 'Mittel'), ('HIGH', 'Hoch')]
    )
    
    measures_taken = models.TextField()
```

---

## Bußgelder (Art. 83)

**Zwei Kategorien:**

### Kategorie 1 (bis zu 10 Mio. € oder 2% des Jahresumsatzes)
- Verstöße gegen Auftragsverarbeitung (Art. 28)
- Verstöße gegen Datensicherheit (Art. 32)
- Verstöße gegen Meldepflichten (Art. 33-34)

### Kategorie 2 (bis zu 20 Mio. € oder 4% des Jahresumsatzes)
- Verstöße gegen Grundprinzipien (Art. 5)
- Verstöße gegen Betroffenenrechte (Art. 12-22)
- Verstöße gegen Datenübermittlung in Drittländer (Art. 44-49)

---

## Zusammenspiel mit HGB/AO ⭐ **KONFLIKTLÖSUNG**

**Konflikt: Löschpflicht (DSGVO) vs. Aufbewahrungspflicht (HGB/AO)**

**Lösung:**
- Aufbewahrungspflichten nach HGB/AO gehen vor (Art. 17 Abs. 3 lit. b DSGVO)
- Nach Ablauf der Aufbewahrungsfrist: Löschung nach DSGVO
- Während Aufbewahrungsfrist: **Einschränkung der Verarbeitung** (Art. 18 DSGVO)

---

## Compliance Checklist

### Organisatorisch
- [ ] Datenschutzbeauftragten bestellen (falls erforderlich)
- [ ] Verzeichnis von Verarbeitungstätigkeiten erstellen (Art. 30) + Export für Kunden
- [ ] Datenschutz-Folgenabschätzung durchführen (Art. 35)
- [ ] **Auftragsverarbeitungsverträge (DPA) automatisiert** (Art. 28) ⭐ **FÜR SAAS**
- [ ] Datenschutzerklärung erstellen
- [ ] Prozess für Betroffenenrechte etablieren
- [ ] Prozess für Datenpannen-Meldung etablieren

### Technisch
- [ ] Verschlüsselung sensibler Daten
- [ ] Zugriffskontrolle (RBAC)
- [ ] Audit-Logging mit old_value/new_value
- [ ] Backup & Disaster Recovery
- [ ] Löschkonzept implementieren (Art. 17 vs. Art. 18!)
- [ ] Pseudonymisierung wo möglich
- [ ] **One-Click-Export (Art. 15)** ⭐ **KRITISCH**
- [ ] API für Datenlöschung (Art. 17)
- [ ] **Einwilligungsverwaltung mit Protokollierung** (Art. 7)
- [ ] Datenpannen-Management
- [ ] **Anonymisierungs-Script für Staging/Dev** ⭐ **ENTWICKLER**
- [ ] **Seed-Data für Development** ⭐ **ENTWICKLER**

### Dokumentation
- [ ] Verarbeitungsverzeichnis (mit Export-Funktion!)
- [ ] Technische und organisatorische Maßnahmen (TOM)
- [ ] Datenschutz-Folgenabschätzung
- [ ] Auftragsverarbeitungsverträge (DPA)
- [ ] Einwilligungen (mit vollständiger Protokollierung!)
- [ ] Löschkonzept

---

## Wichtige Fristen

| Frist | Rechtsgrundlage | Beschreibung |
|-------|-----------------|--------------| | 1 Monat | Art. 12 Abs. 3 | Beantwortung Betroffenenanfragen |
| 72 Stunden | Art. 33 Abs. 1 | Meldung Datenpanne an Aufsichtsbehörde |
| Unverzüglich | Art. 34 Abs. 1 | Benachrichtigung betroffener Personen |

---

## Sanktionen

- **Bußgelder:** Bis zu 20 Mio. € oder 4% des Jahresumsatzes
- **Schadensersatz:** Betroffene Personen können Schadensersatz geltend machen (Art. 82)
- **Reputationsschaden:** Negative Publicity

---

## Nächste Schritte (Priorität)

1. ⭐ **HÖCHSTE PRIORITÄT:** One-Click-Export (Art. 15) implementieren
2. Art. 17 vs. Art. 18 (Löschen vs. Einschränken) korrekt umsetzen
3. DPA (Auftragsverarbeitungsvertrag) automatisieren (für SaaS)
4. Verarbeitungsverzeichnis mit Export-Funktion
5. Einwilligungsverwaltung mit vollständiger Protokollierung
6. Anonymisierungs-Script für Staging/Development
7. Seed-Data für Development

---

**Quelle:** DSGVO (EU 2016/679) Stand 2025/2026  
**Hinweis:** Bei rechtlichen Fragen immer Datenschutzbeauftragten oder Fachanwalt konsultieren.
