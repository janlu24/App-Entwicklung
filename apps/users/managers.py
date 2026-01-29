"""
Benutzer-Manager für email-basierte Authentifizierung.

Dieser Manager ersetzt Djangos Standard-UserManager, um Email
als primäres Authentifizierungsfeld anstelle von Username zu unterstützen.
"""

from typing import Optional
from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext_lazy as _


class CustomUserManager(BaseUserManager):
    """
    Custom User Manager, bei dem Email der eindeutige Identifier
    für die Authentifizierung ist (anstelle von Username).
    """

    def create_user(
        self,
        email: str,
        password: Optional[str] = None,
        **extra_fields
    ):
        """
        Erstellt und speichert einen regulären Benutzer mit der angegebenen Email und Passwort.
        
        Args:
            email: Email-Adresse des Benutzers (erforderlich, wird für Login verwendet)
            password: Passwort des Benutzers (optional für initiale Erstellung)
            **extra_fields: Zusätzliche Felder wie first_name, last_name
            
        Returns:
            User: Die erstellte Benutzer-Instanz
            
        Raises:
            ValueError: Wenn keine Email angegeben wurde
        """
        if not email:
            raise ValueError(_('The Email field must be set'))
        
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(
        self,
        email: str,
        password: Optional[str] = None,
        **extra_fields
    ):
        """
        Erstellt und speichert einen Superuser mit der angegebenen Email und Passwort.
        
        Setzt automatisch is_staff=True und is_superuser=True.
        
        Args:
            email: Email-Adresse des Superusers (erforderlich)
            password: Passwort des Superusers (erforderlich aus Sicherheitsgründen)
            **extra_fields: Zusätzliche Felder wie first_name, last_name
            
        Returns:
            User: Die erstellte Superuser-Instanz
            
        Raises:
            ValueError: Wenn is_staff oder is_superuser nicht True sind
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))

        return self.create_user(email, password, **extra_fields)
