# Invoice Preview Partial - Dokumentation

## 📁 Dateien

### 1. `apps/sales/templates/sales/partials/invoice_preview.html`
**Zweck:** Kompakte Rechnungs-Vorschau für den Chat-Stream

**Features:**
- ✅ **ENTWURF-Badge** (Compliance: Kennzeichnung als Draft)
- ✅ **Kompaktes Design** (optimiert für Chat-Spalte, w-96)
- ✅ **Währungsformatierung** (z.B. "19,00 €")
- ✅ **HTMX-Integration** (Buttons für Buchen & Bearbeiten)

### 2. `apps/sales/templates/sales/partials/chat_message_ai.html`
**Zweck:** Wrapper für KI-Antworten mit optionaler Invoice-Preview

## 🎨 Design

### Layout-Struktur

```
┌─────────────────────────────────────┐
│ [Icon] Rechnung RE-2026-001  ENTWURF│
│        29.01.2026                   │
├─────────────────────────────────────┤
│ Empfänger                           │
│ Müller GmbH                         │
│                                     │
│ Positionen                          │
│ • Beratung    2 × 100,00 € 200,00 €│
│ • Support     1 × 50,00 €   50,00 €│
│                                     │
│ Netto                      250,00 € │
│ USt. 19%                    47,50 € │
│ ─────────────────────────────────── │
│ Gesamt                     297,50 € │
├─────────────────────────────────────┤
│ [Buchen & Senden] [Bearbeiten]     │
└─────────────────────────────────────┘
```

### Farb-Schema

- **Header:** Gradient Slate (50-100)
- **ENTWURF-Badge:** Amber (100/800)
- **Primär-Button:** Blue (600/700)
- **Sekundär-Button:** White + Border

## 📝 Verwendung

### Beispiel 1: In Django View

```python
from django.shortcuts import render
from apps.sales.models import Invoice

def create_invoice_preview(request):
    """
    Erstellt eine Rechnungs-Vorschau für den Chat.
    """
    invoice = Invoice.objects.create_draft(
        recipient=customer,
        items=[
            {'description': 'Beratung', 'quantity': 2, 'unit_price': 100.00},
            {'description': 'Support', 'quantity': 1, 'unit_price': 50.00},
        ]
    )
    
    context = {
        'message': 'Ich habe einen Rechnungsentwurf für Sie erstellt:',
        'invoice': invoice,
        'timestamp': timezone.now(),
    }
    
    return render(request, 'sales/partials/chat_message_ai.html', context)
```

### Beispiel 2: Standalone Preview

```python
def show_invoice_preview(request, invoice_id):
    """
    Zeigt nur die Invoice-Preview (ohne Chat-Wrapper).
    """
    invoice = Invoice.objects.get(id=invoice_id)
    
    return render(request, 'sales/partials/invoice_preview.html', {
        'invoice': invoice
    })
```

### Beispiel 3: HTMX Response

```python
from django.http import HttpResponse

def ai_chat_response(request):
    """
    KI-Antwort mit Invoice-Preview.
    """
    # KI erstellt Rechnung basierend auf User-Input
    invoice = create_invoice_from_ai_input(request.POST.get('message'))
    
    html = render_to_string('sales/partials/chat_message_ai.html', {
        'message': 'Ich habe die Rechnung erstellt. Bitte überprüfen Sie die Details:',
        'invoice': invoice,
        'timestamp': timezone.now(),
    })
    
    return HttpResponse(html)
```

## 🔧 Erforderliche Context-Variablen

### Für `invoice_preview.html`:

```python
{
    'invoice': {
        'id': 123,                          # Invoice ID
        'number': 'RE-2026-001',            # Rechnungsnummer
        'date': datetime.date(2026, 1, 29), # Rechnungsdatum
        'recipient': {
            'name': 'Max Mustermann',       # Empfänger Name
            'company': 'Mustermann GmbH',   # Optional: Firma
        },
        'items': [
            {
                'description': 'Beratung',  # Positionsbeschreibung
                'quantity': 2,              # Menge
                'unit_price': 100.00,       # Einzelpreis (Decimal)
                'total': 200.00,            # Gesamt (Decimal)
            },
        ],
        'subtotal': 250.00,                 # Netto (Decimal)
        'vat_rate': 19,                     # USt-Satz (Integer)
        'vat_amount': 47.50,                # USt-Betrag (Decimal)
        'total': 297.50,                    # Brutto (Decimal)
    }
}
```

### Für `chat_message_ai.html`:

```python
{
    'message': 'KI-Antwort Text',           # String
    'invoice': {...},                       # Optional: Invoice-Objekt
    'timestamp': datetime.datetime.now(),   # Zeitstempel
}
```

## 🎯 HTMX-Endpunkte

Die Buttons im Template erwarten folgende Endpunkte:

### 1. Buchen & Senden
```
POST /sales/invoices/{invoice.id}/finalize/
```
**Aktion:** Finalisiert die Rechnung und sendet sie an den Kunden
**Response:** Chat-Nachricht mit Bestätigung

### 2. Bearbeiten
```
GET /sales/invoices/{invoice.id}/edit/
```
**Aktion:** Öffnet Bearbeitungs-Formular im Main-Stage
**Response:** Vollständiges Rechnungs-Formular

## ✅ Compliance-Checks

### ENTWURF-Kennzeichnung ✅
- Badge mit "ENTWURF" in Amber (auffällig)
- Verhindert Verwechslung mit finalen Rechnungen

### Währungsformatierung ✅
- Django Template Filter: `|floatformat:2`
- Format: "19,00 €" (deutsches Format)

### Unveränderbarkeit ❌ (Noch nicht implementiert)
- Nach "Buchen & Senden" muss die Rechnung unveränderbar werden
- Service-Layer muss State-Transition implementieren

## 🚀 Nächste Schritte

1. **Service-Layer erstellen:**
   - `apps/sales/services.py`
   - `create_invoice_draft()`
   - `finalize_invoice()`

2. **Views erstellen:**
   - `/sales/invoices/{id}/finalize/`
   - `/sales/invoices/{id}/edit/`

3. **Invoice Model erweitern:**
   - FSM für Status (Draft → Finalized)
   - Validation für Pflichtfelder

4. **Chat-Backend:**
   - `/ai/chat/` Endpoint
   - KI-Integration für Rechnungserstellung

## 📚 Weitere Dokumentation

- **Design-System:** `templates/README.md`
- **Compliance:** `.agent/knowledge/gobd_implementation_guide.md`
- **UStG-Logik:** `.agent/knowledge/ustg_vat_logic.md`
