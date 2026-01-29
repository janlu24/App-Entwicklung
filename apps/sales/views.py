"""
Views für die Sales App.

WICHTIG: Diese Views enthalten KEINE Geschäftslogik.
Alle Logik muss in services.py implementiert werden.
"""

from django.shortcuts import render
from django.utils import timezone
from apps.sales.services import simulate_invoice_draft


def chat_invoice_preview(request):
    """
    Erstellt eine Chat-Nachricht mit Invoice-Preview.
    
    Wird vom AI-Chat aufgerufen, wenn der User eine Rechnung erstellen möchte.
    Nutzt InMemory-Dummy-Daten (kein DB-Zugriff).
    
    Returns:
        HttpResponse: Gerendertes HTML-Partial für den Chat
    """
    # Service aufrufen (keine Logik in der View!)
    invoice = simulate_invoice_draft()
    
    # Context für Template
    context = {
        'message': 'Ich habe einen Rechnungsentwurf für Sie erstellt. Bitte überprüfen Sie die Details:',
        'invoice': invoice,
        'timestamp': timezone.now(),
    }
    
    # Render Chat-Nachricht mit Invoice-Preview
    return render(request, 'sales/partials/chat_message_ai.html', context)
