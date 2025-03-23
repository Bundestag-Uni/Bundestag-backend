# Bundestag-backend
## Sccraper
Der Scraper leitet die Abfrage der Bundestags Daten
Starte den Container mit sudo docker start `container_id` 

## Übersicht
Die Bundestag-Datenbank enthält mehrere Tabellen, die strukturierte Informationen zu Mitgliedern des Bundestages, deren Zwischenrufen sowie weiteren relevanten Details speichern.

---

## Tabellenübersicht

### 1. `members`
Diese Tabelle enthält Informationen über die Mitglieder des Bundestages, einschließlich deren Namen, Titel und weiterer Metadaten.
- **Spalten:**
  - `id` (PK): Eindeutige Kennung des Mitglieds.
  - `nachname` (VARCHAR(255)): Nachname des Mitglieds.
  - `vorname` (VARCHAR(255)): Vorname des Mitglieds.
  - `typ` (VARCHAR(255)): Typ des Mitglieds (z. B. aktiv, ehemalig, etc.).
  - `wahlperiode` (INTEGER): Wahlperiode, in der das Mitglied tätig war.
  - `aktualisiert` (TIMESTAMP): Letztes Aktualisierungsdatum.
  - `titel` (VARCHAR(255)): Titel des Mitglieds.
  - `datum` (DATE): Datum der Aufnahme oder Änderung.
  - `basisdatum` (DATE): Basisdatum.

---

### 2. `abgeordnete`
Diese Tabelle dokumentiert zusätzliche Details zu Abgeordneten im Bundestag.
- **Spalten:**
  - `id` (PK): Eindeutige Kennung des Abgeordneten.
  - `nachname` (VARCHAR(255)): Nachname des Abgeordneten.
  - `vorname` (VARCHAR(255)): Vorname des Abgeordneten.
  - `anrede_titel` (VARCHAR(255)): Titel und Anrede (z. B. Dr., Prof.).
  - `akad_titel` (VARCHAR(255)): Akademischer Titel.
  - `geburtsdatum` (DATE): Geburtsdatum.
  - `geburtsort` (VARCHAR(255)): Geburtsort.
  - `geburtsland` (VARCHAR(255)): Geburtsland.
  - `sterbedatum` (DATE): Sterbedatum (falls zutreffend).
  - `geschlecht` (VARCHAR(50)): Geschlecht.
  - `familienstand` (VARCHAR(255)): Familienstand.
  - `religion` (VARCHAR(255)): Religion.
  - `beruf` (VARCHAR(255)): Beruf.
  - `partei_kurz` (VARCHAR(50)): Kürzel der Partei.
  - `wahlperioden` (JSONB): Liste der Wahlperioden in JSON-Format.

---

### 3. `reden`
Diese Tabelle speichert die Reden der Mitglieder während der Bundestagsdebatten.
- **Spalten:**
  - `id` (PK): Eindeutige Kennung der Rede.
  - `redner_id` (FK): Verweis auf das Mitglied oder den Abgeordneten, der die Rede gehalten hat.
  - `inhalt` (TEXT): Inhalt der Rede.
  - `datum` (DATE): Datum der Rede.

---

### 4. `zwischenruf`
Diese Tabelle speichert Zwischenrufe und andere Kommentare während der Bundestagsdebatten.
- **Spalten:**
  - `id` (PK): Eindeutige Kennung des Zwischenrufs.
  - `zwischenrufer_id` (FK): Verweis auf das Mitglied oder den Abgeordneten, der den Zwischenruf gemacht hat.
  - `rede_id` (FK): Verweis auf die Rede, auf die sich der Zwischenruf bezieht.
  - `datum` (DATE): Datum des Zwischenrufs.
  - `inhalt` (TEXT): Inhalt des Zwischenrufs.

---

### 4. `reden_efficiency`
Diese Tabelle beinhaltet die Reden effizienz der Reden
- **Spalten:**
  - `id` (PK): Eindeutige Kennung der dazugehörigen Rede.
  - `num_tokens`: Tokenzahl des Grafen
  - `num_nodes`: Anzahl der Entitäten des Grafen
  - `num_edges`: Anzahl der Vernetzungen des Grafen
  - `efficiency`:  Nodes * Edges / Tokens
 








