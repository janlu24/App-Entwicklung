# Template-Struktur für AI-First ERP

## Übersicht

Dieses Verzeichnis enthält die Django-Templates für das AI-First ERP-System. Die Templates folgen dem Prinzip **"Conversation over Navigation"** und nutzen HTMX für ein SPA-ähnliches Erlebnis.

## Basis-Template: `base.html`

Das Haupt-Template definiert die Grundstruktur der Anwendung:

### Layout-Komponenten

1. **Sidebar (Links)** - Modul-Navigation
   - Dashboard
   - Verkauf
   - Finanzen
   - Lager
   - Einstellungen
   - Benutzer-Info (Footer)

2. **Main Stage (Mitte)** - Haupt-Inhaltsbereich
   - Header mit Breadcrumb/Seitentitel
   - AI Engine Toggle (primäres Steuerelement)
   - Content-Area (HTMX-Target: `#main-stage`)

3. **AI Engine (Rechts)** - Zentrales Steuersystem
   - Feste Spalte (w-96, ein-/ausblendbar)
   - Terminal-Style UI ("Maschinenraum")
   - HTMX-Integration für Chat-Interaktionen

## Template-Blöcke

Child-Templates können folgende Blöcke überschreiben:

```django
{% block title %}        {# Browser-Tab-Titel #}
{% block page_title %}   {# Haupt-Überschrift im Header #}
{% block page_subtitle %} {# Untertitel im Header #}
{% block content %}      {# Haupt-Inhaltsbereich #}
{% block extra_head %}   {# Zusätzliche Head-Elemente (CSS, Meta) #}
{% block extra_scripts %} {# Zusätzliche Scripts am Ende #}
```

## Verwendung

### Beispiel: Neues Modul-Template erstellen

```django
{% extends "base.html" %}

{% block title %}Verkauf - AI-First ERP{% endblock %}

{% block page_title %}Verkauf{% endblock %}
{% block page_subtitle %}Rechnungen, Angebote und Kunden{% endblock %}

{% block content %}
<div class="max-w-7xl mx-auto">
    {# Ihr Modul-Content hier #}
</div>
{% endblock %}
```

## HTMX-Integration

### Navigation

Die Sidebar-Links nutzen HTMX für SPA-Verhalten:

```html
<a href="/sales/" 
   hx-get="/sales/" 
   hx-target="#main-stage" 
   hx-push-url="true">
    Verkauf
</a>
```

### Chat-Interaktionen

Das AI Engine Panel sendet Nachrichten an `/ai/chat/`:

```html
<form hx-post="/ai/chat/" 
      hx-target="#chat-messages" 
      hx-swap="beforeend">
    <input type="text" name="message">
    <button type="submit">Senden</button>
</form>
```

## Styling-Konventionen

### Design-System ("Ruhiger Fokus")

- **Farben**: Slate-Palette für neutrale UI, Blue für primäre Aktionen
- **Abstände**: `gap-6`, `p-6` für großzügigen Whitespace
- **Rundungen**: `rounded-xl` für Cards/Container
- **Schatten**: `shadow-sm` für subtile Tiefe

### Barrierefreiheit

- ✅ Alle interaktiven Elemente haben Fokus-States
- ✅ Semantisches HTML (nav, main, aside)
- ✅ ARIA-Labels wo nötig (z.B. Icon-Buttons)
- ✅ Kontrast-Verhältnisse beachten (Text auf Hintergrund)

## Tech-Stack

- **Django Templates**: Template-Engine
- **Tailwind CSS**: Utility-First CSS (Lokales Build Setup via `npm run dev`)
- **HTMX**: AJAX-Interaktionen ohne JavaScript
- **Alpine.js**: Leichte Client-Side Interaktivität (Panel Toggle)

## Nächste Schritte

1. **Modul-Templates erstellen** (Sales, Finance, Inventory)
2. **Authentifizierung** (Login/Logout Templates)
3. **Erweiterung der AI-Fähigkeiten** (Mehr Keywords/Fähigkeiten)

## Compliance-Hinweise

- ✅ UI-Sprache: **Deutsch** (Buttons, Labels, Menüs)
- ✅ Code-Variablen: **Englisch** (IDs, Klassen)
- ✅ Keine Geschäftslogik in Templates (nur Präsentation)
