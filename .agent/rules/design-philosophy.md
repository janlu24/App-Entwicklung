---
trigger: always_on
---

# Design-System Philosophie ("Ruhiger Fokus")

## 1. Visuelle Einfachheit ("Apple-Like")
- **Ziel:** Kognitive Belastung reduzieren. Nur zeigen, was notwendig ist.
- **Reflex:** Bevor du einen Rahmen oder eine Linie hinzufügst, frage dich: *"Kann ich das mit Whitespace lösen?"*

## 2. Hierarchie durch Abstand
- **Regel:** Rahmen (`border-gray-200`) vermeiden wo möglich.
- **Lösung:** Großzügigen Whitespace nutzen, um Inhaltsbereiche zu trennen.
  - Standard-Abstand: `gap-6`, `p-6`.

## 3. Weichheit & Tiefe
- **Form:** `rounded-xl` für Container/Cards nutzen. Scharfe Ecken vermeiden.
- **Tiefe:** Subtile Schatten (`shadow-sm`) nutzen, um Hierarchie ohne visuelle Unruhe zu erzeugen.

## 4. Datendichte (Tabellen)
- **Kontext:** ERP-Systeme benötigen hohe Datendichte in Listen.
- **Regel:** Innerhalb von Tabellen vertikales Padding reduzieren (`py-2`).
- **Balance:** Das Layout *um* die Tabelle herum großzügig halten, um den Fokus zu wahren.

## 5. Barrierefreiheit & Kontrast-Richtlinien (Verpflichtend)

### 1. Kontrast-Compliance
- **Strenge Regel:** Niemals grauen Text auf grauem Hintergrund platzieren.
- **Prüfung:** Immer Kontrastverhältnisse prüfen, besonders im Dark Mode. Text muss gegen `bg-slate-900` lesbar sein.

### 2. Formulare & Eingaben
- **Strenge Regel:** Keine Placeholder-Only Inputs.
- **Anforderung:** Jede Eingabe MUSS entweder haben:
  - Ein sichtbares `<label>` Element.
  - ODER ein klares Icon kombiniert mit einem validen `aria-label` Attribut.

### 3. Tastatur-Navigation
- **Fokus:** Alle interaktiven Elemente (Buttons, Links, Inputs) MÜSSEN einen sichtbaren Fokus-Status haben (wie im UI Skill definiert), um reine Tastaturnutzung zu unterstützen.