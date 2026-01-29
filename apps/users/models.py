"""
User Models für das AI-First ERP System.

Dieses Modul enthält das Custom User Model, das email-basierte Authentifizierung
anstelle von Username verwendet, wie in den Architektur-Richtlinien spezifiziert.
"""

from django.contrib.auth.models import AbstractUser
from django.db import models

from .managers import CustomUserManager


class User(AbstractUser):
    """
    Custom User Model für das ERP-System.
    
    Hauptmerkmale:
    - Email-basierte Authentifizierung (kein Username-Feld)
    - Trennung zwischen User (Auth) und Employee (HR-Daten)
    - Grundlage für RBAC (Role-Based Access Control)
    
    Hinweis: Dies muss in settings.py als AUTH_USER_MODEL = 'users.User'
    gesetzt werden, bevor die erste Migration ausgeführt wird.
    """
    
    # Username-Feld vollständig entfernen (None entfernt es aus dem DB-Schema)
    username = None
    
    # Email ist erforderlich und muss eindeutig sein
    email = models.EmailField(
        unique=True,
        help_text="Email-Adresse für Login und Kommunikation."
    )
    
    # Email als primäres Authentifizierungsfeld verwenden
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']  # Erforderlich für createsuperuser
    
    # Unseren Custom Manager für email-basierte User-Erstellung verwenden
    objects = CustomUserManager()
    
    class Meta:
        verbose_name = "Benutzer"
        verbose_name_plural = "Benutzer"
        ordering = ['email']
    
    def __str__(self) -> str:
        """Gibt Email als String-Repräsentation zurück."""
        return self.email
