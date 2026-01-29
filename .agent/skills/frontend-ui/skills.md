### Implementierung des Command Centers

Wenn du das Chat-Interface baust, musst du die JSON-Antworten der AI parsen.

**JavaScript Logik (Pseudocode):**
```javascript
function handleAIResponse(response) {
  const { message, component, data } = response;

  // 1. Text anzeigen
  chatWindow.append(message);

  // 2. Komponente rendern
  if (component) {
    const targetDiv = document.getElementById('widget-area');
    if (component === 'data-grid') {
      // Mount React Island
      mountReactGrid(targetDiv, data);
    } else {
      // Trigger HTMX load
      htmx.ajax('GET', `/components/${component}/`, { target: targetDiv, values: data });
    }
  }
}
```


## Farbpalette (Nordic Petrol Theme)

**Strenge Anforderung:** Nutze KEINE Hex-Codes (z.B. `#0F766E`). Nutze Tailwind-Klassen zur Sicherstellung des Dark Mode Supports.

### 1. Markenidentität
- **Primärmarke:** `bg-teal-700` (Genutzt für Header, Aktive Zustände).
- **Primäraktion (Buttons):** `bg-teal-600 hover:bg-teal-700 text-white shadow-sm`.
- **Sekundäraktion:**
  - Hell: `bg-white border-slate-200 text-slate-700 hover:bg-slate-50`.
  - Dunkel: `dark:bg-slate-800 dark:border-slate-700 dark:text-slate-200 dark:hover:bg-slate-700`.

### 2. Hintergrund-Strategie (Hell vs. Dunkel)
*Ziel: Augenbelastung reduzieren. Vermeide reines Schwarz im Dark Mode.*

| Element | Light Mode | Dark Mode | Hinweis |
| :--- | :--- | :--- | :--- |
| **Page BG** | `bg-slate-50` | `bg-slate-900` | Tiefes Blaugrau, kein Schwarz. |
| **Cards/Surface** | `bg-white` | `bg-slate-800` | Heller als BG für Erhabenheit. |
| **Inputs** | `bg-white border-slate-200` | `bg-slate-900 border-slate-700` | Eingelassener Look. |

### 3. Statusfarben (Barrierefreiheit)
**Regel:** Nutze niemals Farbe allein zur Bedeutungsvermittlung (füge Icons hinzu).

- **Erfolg:** `text-emerald-700 bg-emerald-50` (Dunkel: `text-emerald-400 bg-emerald-900/30`)
- **Warnung:** `text-amber-700 bg-amber-50` (Dunkel: `text-amber-400 bg-amber-900/30`)
- **Fehler:** `text-rose-700 bg-rose-50` (Dunkel: `text-rose-400 bg-rose-900/30`)


## Typografie (Font: Inter)

### 1. Font Standards
- **Familie:** `Inter` (Standard Sans).
- **Kritische Anforderung:** Nutze immer `tabular-nums` für Data Grids, Rechnungen oder Preisanzeigen. Dies stellt sicher, dass Zahlen vertikal ausgerichtet sind.

### 2. Type Scale
| Element | Tailwind Classes | Hinweis |
| :--- | :--- | :--- |
| **Headings** | `text-2xl font-semibold tracking-tight text-slate-900 dark:text-slate-50` | Modernes, enges Tracking. |
| **Body** | `text-base text-slate-600 dark:text-slate-400` | Hohe Lesbarkeit. |
| **Daten/Tabellen** | `text-sm font-medium text-slate-700 dark:text-slate-300 tabular-nums` | **Muss tabular-nums nutzen.** |


## UI Komponenten & Pattern

### 1. Der "Glass" Header (Apple Ästhetik)
**Verwendung:** Nur obere Navigationsleiste.
- **Klassen:** `bg-white/80 dark:bg-slate-900/80 backdrop-blur-md border-b border-slate-200/50 dark:border-slate-700/50 sticky top-0 z-50`

### 2. Buttons & Interaktionen
- **Radius:** `rounded-lg` (Modern aber professionell).
- **Fokus-Zustände (Barrierefreiheit):** `focus:ring-2 focus:ring-teal-500 focus:ring-offset-2 dark:focus:ring-offset-slate-900`.
- **Transitionen:** Wende `transition-all duration-200 ease-in-out` auf ALLE interaktiven Elemente an, um harte Wechsel zu vermeiden.

### 3. Cards & Container ("Inseln")
**Verwendung:** Hauptinhalt-Wrapper.
- **Klassen:** `bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm p-6`.

### 4. Datentabellen (ERP Core)
**Verwendung:** Listen von Rechnungen, Benutzern, Produkten.

| Teil | Tailwind Klassen |
| :--- | :--- |
| **Header** | `text-xs font-semibold uppercase tracking-wider text-slate-500 bg-slate-50/50 dark:bg-slate-800/50 border-b border-slate-200 dark:border-slate-700` |
| **Zeilen** | `border-b border-slate-100 dark:border-slate-800 hover:bg-slate-50 dark:hover:bg-slate-700/50 transition-colors` |
| **Hinweis** | Stelle hohe Datendichte (wenig Padding) innerhalb der Tabellenzellen sicher. |


## Command Center (Chat UI)
*Der zentrale Interaktionspunkt. Muss sich wie eine "Spotlight"-Suche anfühlen.*

### 1. Eingabefeld
- **Layout:** Zentriert, Max-width `3xl`.
- **Klassen:** `h-14 rounded-2xl shadow-md border-0 ring-1 ring-slate-200 dark:ring-slate-700 focus:ring-2 focus:ring-teal-500 text-lg px-6`.

### 2. Nachrichten-Bubbles
| Sender | Tailwind Klassen | Form-Logik |
| :--- | :--- | :--- |
| **User** | `bg-slate-100 dark:bg-slate-700 text-slate-800 dark:text-slate-200 rounded-2xl rounded-tr-sm` | Oben-Rechts scharf um Herkunft anzuzeigen. |
| **AI** | `bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 shadow-sm text-slate-800 dark:text-slate-200 rounded-2xl rounded-tl-sm` | Oben-Links scharf. |