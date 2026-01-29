"""
Views für die AI Engine App.

Diese App ist der zentrale Router für KI-gesteuerte Interaktionen.
"""

from django.http import HttpResponse
from django.template.loader import render_to_string
from apps.sales.views import chat_invoice_preview


def chat_endpoint(request):
    """
    Zentraler Chat-Endpoint für KI-Interaktionen.
    
    WICHTIG: Dies ist ein einfacher Prototyp ohne echte KI-Integration.
    Nutzt einfache String-Matching-Logik.
    
    Logik:
    - Wenn Nachricht "Rechnung" enthält → Invoice-Preview anzeigen
    - Sonst → Fehlermeldung
    
    Returns:
        HttpResponse: HTML-Partial für den Chat
    """
    # User-Nachricht aus POST-Daten
    user_message = request.POST.get('message', '').strip()
    
    # Einfache Keyword-Erkennung (case-insensitive)
    if 'rechnung' in user_message.lower():
        # Delegiere an Sales-View
        return chat_invoice_preview(request)
    
    # Fallback: Nicht verstanden
    html = render_to_string('ai_engine/partials/chat_message_error.html', {
        'message': 'Das habe ich nicht verstanden. Versuchen Sie: "Rechnung erstellen"',
    })
    
    return HttpResponse(html)
