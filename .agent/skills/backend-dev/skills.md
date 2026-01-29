## Tech-Stack & Implementierungsdetails

### State Machines (Viewflow)
Wenn du Modelle mit einem Status (z.B. Invoice, Order) erstellst, nutze dieses Pattern:

```python
from django.db import models
from viewflow.fsm import State, transition

class Invoice(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'draft', 'Entwurf'
        PAID = 'paid', 'Bezahlt'

    status = models.CharField(choices=Status.choices, default=Status.DRAFT, max_length=20)

    @transition(field=status, source=Status.DRAFT, target=Status.PAID)
    def mark_as_paid(self):
        # Hier Logik einfügen (z.B. Journal Entry erstellen)
        pass
```


### AI Tool Registrierung (Registry Pattern)
Damit die AI deine Service-Funktionen nutzen kann, darfst du sie nicht in der AI-Engine importieren. Stattdessen "markierst" du sie in deiner App.

**Muster für `apps/{app_name}/services.py`:**

```python
from apps.ai_engine.registry import register_tool
from .models import Invoice

@register_tool(
    name="create_invoice",
    description="Erstellt einen neuen Rechnungsentwurf. Benötigt customer_id und line_items."
)
def create_invoice(user, customer_id: int, items: list):
    # 1. Permission Check (WICHTIG!)
    if not user.has_perm('sales.add_invoice'):
        raise PermissionError("Benutzer nicht berechtigt")

    # 2. Business Logic
    # ... Implementierung ...
```


### Auth Model Implementierung
Wenn du das User-Modell erstellst, nutze exakt dieses Pattern, um den Username zu entfernen:

```python
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from .managers import CustomUserManager

class User(AbstractBaseUser, PermissionsMixin):
    username = None  # Entfernt das Feld aus der DB
    email = models.EmailField(unique=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    objects = CustomUserManager()
    
    # ... Rest der Implementierung
```


### Asynchrone Tasks (Celery)
Wenn du langlaufende Prozesse hast (z.B. AI-Analyse einer Rechnung), lagere sie aus.

**Muster für `apps/{app}/tasks.py`:**
```python
from celery import shared_task
from .services import calculate_complex_report

@shared_task
def task_generate_report(report_id: int):
    # Rufe die Logik aus services.py auf (NIEMALS Logik im Task selbst schreiben!)
    calculate_complex_report(report_id)
```