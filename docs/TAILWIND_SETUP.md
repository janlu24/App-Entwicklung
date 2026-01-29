# Tailwind CSS Build-Pipeline

## ✅ Setup abgeschlossen

Die Tailwind CSS Build-Pipeline ist vollständig eingerichtet und einsatzbereit.

## 📁 Dateien

### Konfiguration
- **`tailwind.config.js`** - Tailwind-Konfiguration
  - Scannt alle Templates (`./templates/**/*.html`)
  - Scannt App-Templates (`./apps/**/templates/**/*.html`)
  - Scannt Python-Dateien für Klassen in Strings

### CSS-Dateien
- **`core/static/core/css/input.css`** - Source-Datei (versioniert)
  - Enthält `@tailwind` Direktiven
  - Platz für Custom Styles in `@layer` Blöcken
  
- **`core/static/core/css/output.css`** - Kompilierte Datei (NICHT versioniert)
  - Wird automatisch generiert
  - In `.gitignore` ausgeschlossen

### Package.json Scripts
- **`npm run dev`** - Watch-Modus (empfohlen für Development)
- **`npm run build`** - Einmaliges Build (minifiziert für Produktion)

## 🚀 Verwendung

### Development (Watch-Modus)

Starten Sie den Tailwind-Compiler im Watch-Modus:

```bash
npm run dev
```

Der Compiler läuft im Hintergrund und kompiliert automatisch bei Änderungen an:
- HTML-Templates
- Python-Dateien
- `input.css`

**Wichtig:** Lassen Sie diesen Prozess während der Entwicklung laufen!

### Produktion

Für Produktion-Builds (minifiziert):

```bash
npm run build
```

Dies erstellt eine optimierte, minifizierte CSS-Datei.

## 🔧 Workflow

### Typischer Development-Workflow

1. **Terminal 1:** Django Dev-Server
   ```bash
   python manage.py runserver
   ```

2. **Terminal 2:** Tailwind Watch
   ```bash
   npm run dev
   ```

3. **Entwickeln:** Ändern Sie Templates/CSS
4. **Browser:** Automatisches Reload (HTMX) oder manuelles Refresh

### Custom Styles hinzufügen

Bearbeiten Sie `core/static/core/css/input.css`:

```css
@layer components {
  .btn-primary {
    @apply px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700;
  }
}
```

Der Compiler erkennt Änderungen automatisch (im Watch-Modus).

## 📦 Template-Integration

Das kompilierte CSS wird in `templates/base.html` eingebunden:

```django
{% load static %}
<!DOCTYPE html>
<html>
<head>
    <link href="{% static 'core/css/output.css' %}" rel="stylesheet">
</head>
```

## ⚠️ Wichtige Hinweise

### .gitignore
Die kompilierte `output.css` ist in `.gitignore` ausgeschlossen:
- ✅ Jeder Entwickler kompiliert lokal
- ✅ Keine Merge-Konflikte
- ✅ Kleinere Repository-Größe

### Deployment
Für Produktion müssen Sie `npm run build` im Deployment-Prozess ausführen:

```bash
# Beispiel: Dockerfile oder CI/CD
npm install
npm run build
python manage.py collectstatic --noinput
```

### Purge/Tree-Shaking
Tailwind entfernt automatisch ungenutzte Klassen basierend auf dem `content`-Array in `tailwind.config.js`. Stellen Sie sicher, dass alle Template-Pfade korrekt sind!

## 🎨 Design-System

### Farben
- **Primary:** `blue-600` (#2563eb)
- **Background:** `slate-50` (#f8fafc)
- **Text:** `slate-900` (#0f172a)
- **Border:** `slate-200` (#e2e8f0)

### Abstände
- **Standard:** `gap-6`, `p-6` (1.5rem)
- **Kompakt:** `gap-4`, `p-4` (1rem)

### Rundungen
- **Cards:** `rounded-xl` (0.75rem)
- **Buttons:** `rounded-lg` (0.5rem)

### Schatten
- **Subtil:** `shadow-sm`
- **Prominent:** `shadow-2xl`

## 🐛 Troubleshooting

### CSS-Änderungen werden nicht übernommen
1. Prüfen Sie, ob `npm run dev` läuft
2. Prüfen Sie die Konsole auf Fehler
3. Hard-Refresh im Browser (Ctrl+Shift+R)

### Klassen werden nicht generiert
1. Prüfen Sie `tailwind.config.js` → `content`-Array
2. Stellen Sie sicher, dass Template-Pfade korrekt sind
3. Neustart von `npm run dev`

### "Unknown at rule @tailwind" Lint-Fehler
Diese Fehler sind normal! Der CSS-Linter kennt Tailwind-Direktiven nicht. Sie werden beim Build korrekt verarbeitet.

## 📚 Weitere Ressourcen

- [Tailwind CSS Dokumentation](https://tailwindcss.com/docs)
- [Tailwind mit Django](https://tailwindcss.com/docs/guides/django)
- [Customization](https://tailwindcss.com/docs/configuration)
