"""
URL-Konfiguration für das ai_erp Projekt.

Die `urlpatterns`-Liste routet URLs zu Views. Für mehr Informationen siehe:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Beispiele:
Function views
    1. Import hinzufügen:  from my_app import views
    2. URL zu urlpatterns hinzufügen:  path('', views.home, name='home')
Class-based views
    1. Import hinzufügen:  from other_app.views import Home
    2. URL zu urlpatterns hinzufügen:  path('', Home.as_view(), name='home')
Inkludieren einer anderen URLconf
    1. Importiere die include() Funktion: from django.urls import include, path
    2. URL zu urlpatterns hinzufügen:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

urlpatterns = [
    path('admin/', admin.site.urls),
]
