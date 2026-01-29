"""
Service Layer für die Users App.

Dieses Modul wird Business-Logik für Benutzerverwaltung,
Authentifizierung und RBAC (Role-Based Access Control) enthalten.

Alle Business-Logik muss hier implementiert werden, nicht in Views.
"""

from typing import Optional
from django.contrib.auth import get_user_model

User = get_user_model()


# Placeholder für zukünftige Service-Funktionen
# Beispiel:
# def create_user_with_role(email: str, password: str, role: str) -> User:
#     """Erstellt einen neuen Benutzer und weist ihm eine Rolle/Gruppe zu."""
#     pass
