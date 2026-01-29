# core/compliance_constants.py
"""
Gesetzliche Schwellenwerte und Fristen für deutsches Handels- und Steuerrecht.

Diese Konstanten dienen als Single Source of Truth für Compliance-Anforderungen
und werden von mehreren Apps (Finance, Sales, Users) verwendet.

Quellen:
- HGB (Handelsgesetzbuch)
- AO (Abgabenordnung)
- GoBD (Grundsätze zur ordnungsmäßigen Führung und Aufbewahrung von Büchern)
- DSGVO (Datenschutz-Grundverordnung)

WICHTIG: Diese Datei enthält ausschließlich Konstanten (Read-Only-Werte).
Jegliche Logik zur Verarbeitung dieser Werte (Berechnungen, Validierungen)
muss in den jeweiligen services.py der Apps implementiert werden.
"""

# ============================================================================
# HGB & AO: Aufbewahrungsfristen
# ============================================================================
HGB_RETENTION_YEARS_BOOKS: int = 10
"""Aufbewahrungsfrist für Bücher, Inventare, Bilanzen, Belege (§ 257 HGB)."""

HGB_RETENTION_YEARS_LETTERS: int = 6
"""Aufbewahrungsfrist für Handelsbriefe (§ 257 HGB)."""

# ============================================================================
# HGB: Größenklassen (§ 267, § 267a HGB)
# ============================================================================
HGB_MICRO_TURNOVER_LIMIT: int = 900_000
"""Umsatzgrenze für Kleinstkapitalgesellschaften (§ 267a HGB) in EUR."""

HGB_MICRO_BALANCE_LIMIT: int = 450_000
"""Bilanzsummengrenze für Kleinstkapitalgesellschaften (§ 267a HGB) in EUR."""

HGB_SMALL_TURNOVER_LIMIT: int = 15_000_000
"""Umsatzgrenze für kleine Kapitalgesellschaften (§ 267 Abs. 1 HGB) in EUR."""

# ============================================================================
# GoBD: Zeitgerechtheit & Festschreibung
# ============================================================================
GOBD_CASH_BOOKING_DAYS: int = 1
"""Maximale Frist für Kassenbuchungen (tägliche Erfassung, GoBD Rz. 71)."""

GOBD_NON_CASH_BOOKING_DAYS: int = 10
"""Maximale Frist für unbare Geschäftsvorfälle (zeitnahe Erfassung, GoBD Rz. 72)."""

GOBD_LOCKING_PERIOD_OFFSET_MONTHS: int = 1
"""Festschreibung bis Ende des Folgemonats (GoBD Rz. 111)."""

# ============================================================================
# DSGVO: Datenschutz & Sperrfristen
# ============================================================================
GDPR_AUTOMATIC_LOCK_DAYS: int = 365 * 3
"""Beispiel: Automatische Sperrung inaktiver Kundendaten nach 3 Jahren (Art. 5 Abs. 1 lit. e DSGVO)."""
