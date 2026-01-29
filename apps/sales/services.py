"""
Service Layer für die Sales App.

Dieses Modul wird Business-Logik enthalten für:
- Angebote (Quotes)
- Aufträge (Orders)
- Rechnungen (Invoices)
- Kundenverwaltung (Customer Management)

Alle Sales Business-Logik muss hier implementiert werden, nicht in Views.
"""

from decimal import Decimal
from typing import List, Optional
from datetime import date


def simulate_invoice_draft() -> dict:
    """
    Simuliert einen Rechnungsentwurf mit InMemory-Dummy-Daten.
    
    WICHTIG: Dies ist ein Prototyp ohne Datenbank-Anbindung.
    Nutzt Dictionaries statt Django Models.
    
    Returns:
        dict: Invoice-Daten im Format, das das Template erwartet
    """
    # Positionen berechnen
    item1_quantity = 1
    item1_unit_price = Decimal('800.00')
    item1_total = item1_quantity * item1_unit_price
    
    item2_quantity = 1
    item2_unit_price = Decimal('150.00')
    item2_total = item2_quantity * item2_unit_price
    
    # Summen berechnen
    subtotal = item1_total + item2_total
    vat_rate = 19
    vat_amount = subtotal * (Decimal(vat_rate) / Decimal('100'))
    total = subtotal + vat_amount
    
    # Invoice-Dictionary zusammenbauen
    invoice = {
        'id': 1,
        'number': 'RE-2026-001',
        'date': date.today(),
        'recipient': {
            'name': 'Beispiel GmbH',
            'company': 'Beispiel GmbH',
        },
        'items': [
            {
                'description': 'Consulting Workshop',
                'quantity': item1_quantity,
                'unit_price': item1_unit_price,
                'total': item1_total,
            },
            {
                'description': 'Reisekosten',
                'quantity': item2_quantity,
                'unit_price': item2_unit_price,
                'total': item2_total,
            },
        ],
        'subtotal': subtotal,
        'vat_rate': vat_rate,
        'vat_amount': vat_amount,
        'total': total,
    }
    
    return invoice

