"""
View-Funktionen für das Core-Modul.

Dieses Modul enthält nur Infrastruktur-Views (z.B. Dashboard, Login).
KEINE Geschäftslogik hier - diese gehört in die jeweiligen Apps.
"""

from django.shortcuts import render
from django.http import HttpRequest, HttpResponse


def dashboard_view(request: HttpRequest) -> HttpResponse:
    """
    Dashboard-Ansicht - Zentrale Übersicht für authentifizierte Benutzer.
    
    Args:
        request: HTTP-Request-Objekt
        
    Returns:
        HttpResponse mit gerendertem Dashboard-Template
    """
    # In Zukunft: Daten aus verschiedenen Services aggregieren
    # Beispiel: sales_stats = sales_service.get_monthly_stats(user=request.user)
    
    context = {
        # Placeholder-Daten - werden später durch echte Service-Calls ersetzt
    }
    
    return render(request, 'dashboard.html', context)
