"""
URL-Konfiguration für die AI Engine App.
"""

from django.urls import path
from apps.ai_engine import views

app_name = 'ai_engine'

urlpatterns = [
    path('chat/', views.chat_endpoint, name='chat'),
]
