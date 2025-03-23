import re
import requests 
import xml.etree.ElementTree as ET
import json 
from db import PostgresDatabase

pg = PostgresDatabase(host='db', database='Bundestag', user='postgres', password='ziewfgru86gtewi77f7gti7etgwf78i')

API_KEY = "N5YmJIw.yoTxYm1RIv7EcGOpXlPm6IZKRIPxCg3YgB"
BASE_URL = "https://search.dip.bundestag.de/api/v1/"

def fetch_all_members():
    if pg.has_rows('members'):
        print("Daten in Tabelle 'members' sind bereits vorhanden. Abbruch der Funktion.")
        return

    api_url = f"{BASE_URL}person"
    params = {
        "apikey": API_KEY,
        "size": 100  # Anzahl der Einträge pro Seite
    }
    cursor = None

    try:
        while True:
            if cursor:
                params["cursor"] = cursor

            response = requests.get(api_url, params=params)
            response.raise_for_status()
            data = response.json()

            persons = data.get('documents', [])
            for person in persons:
                try:
                    pg.execute_query("""
                    INSERT INTO members (id, nachname, vorname, typ, wahlperiode, aktualisiert, titel, datum, basisdatum) VALUES
                    (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO NOTHING;
                    """, (
                        person.get('id'),
                        person.get('nachname'),
                        person.get('vorname'),
                        person.get('typ'),
                        person.get('wahlperiode'),
                        person.get('aktualisiert'),
                        person.get('titel'),
                        person.get('datum'),
                        person.get('basisdatum')
                    ))
                except Exception as e:
                    print(f"Error inserting member {person.get('id')}: {e}")

            # Aktualisiere den Cursor
            new_cursor = data.get('cursor')
            if new_cursor == cursor:
                print("Alle Mitglieder wurden abgerufen.")
                break
            else:
                cursor = new_cursor

    except Exception as e:
        print(f"Ein Fehler ist aufgetreten: {e}")


        
def get_abgeordnete():
    if pg.has_rows('abgeordnete'):
        print("Daten in Tabelle 'abgeordnete' sind bereits vorhanden. Abbruch der Funktion.")
        return
        
    def convert_date_for_postgres(date_str):
        date_str = date_str.split('.')
        return f'{date_str[2]}-{date_str[1]}-{date_str[0]}'
    
    try:
        # Parse the XML file
        tree = ET.parse('MDB_STAMMDATEN.XML')
        root = tree.getroot()

        for mdb in root.findall('MDB'):
            try:
                # Extract all relevant fields
                id = mdb.find('ID').text
                nachname = mdb.find('.//NACHNAME').text if mdb.find('.//NACHNAME') is not None else None
                vorname = mdb.find('.//VORNAME').text if mdb.find('.//VORNAME') is not None else None
                anrede_titel = mdb.find('.//ANREDE_TITEL').text if mdb.find('.//ANREDE_TITEL') is not None else None
                akad_titel = mdb.find('.//AKAD_TITEL').text if mdb.find('.//AKAD_TITEL') is not None else None
                geburtsdatum = mdb.find('.//GEBURTSDATUM').text
                geburtsdatum = convert_date_for_postgres(geburtsdatum) if geburtsdatum else None
                geburtsort = mdb.find('.//GEBURTSORT').text if mdb.find('.//GEBURTSORT') is not None else None
                geburtsland = mdb.find('.//GEBURTSLAND').text if mdb.find('.//GEBURTSLAND') is not None else None
                sterbedatum = mdb.find('.//STERBEDATUM').text
                sterbedatum = convert_date_for_postgres(sterbedatum) if sterbedatum else None
                geschlecht = mdb.find('.//GESCHLECHT').text if mdb.find('.//GESCHLECHT') is not None else None
                familienstand = mdb.find('.//FAMILIENSTAND').text if mdb.find('.//FAMILIENSTAND') is not None else None
                religion = mdb.find('.//RELIGION').text if mdb.find('.//RELIGION') is not None else None
                beruf = mdb.find('.//BERUF').text if mdb.find('.//BERUF') is not None else None
                partei_kurz = mdb.find('.//PARTEI_KURZ').text if mdb.find('.//PARTEI_KURZ') is not None else None
                
                # Extract Wahlperioden as a list of JSON objects
                wahlperioden = []
                for wp in mdb.findall('.//WAHLPERIODE'):
                    wahlperiode = {
                        'WP': wp.find('WP').text if wp.find('WP') is not None else None,
                        'MDBWP_VON': wp.find('MDBWP_VON').text if wp.find('MDBWP_VON') is not None else None,
                        'MDBWP_BIS': wp.find('MDBWP_BIS').text if wp.find('MDBWP_BIS') is not None else None,
                        'WKR_NUMMER': wp.find('WKR_NUMMER').text if wp.find('WKR_NUMMER') is not None else None,
                        'WKR_NAME': wp.find('WKR_NAME').text if wp.find('WKR_NAME') is not None else None,
                        'WKR_LAND': wp.find('WKR_LAND').text if wp.find('WKR_LAND') is not None else None,
                        'MANDATSART': wp.find('MANDATSART').text if wp.find('MANDATSART') is not None else None,
                    }
                    wahlperioden.append(wahlperiode)

                # Convert Wahlperioden to JSON string for storage
                wahlperioden_json = json.dumps(wahlperioden)

                # Insert all data into PostgreSQL
                pg.execute_query("""
                INSERT INTO abgeordnete (
                    id, nachname, vorname, anrede_titel, akad_titel, geburtsdatum, geburtsort, geburtsland,
                    sterbedatum, geschlecht, familienstand, religion, beruf, partei_kurz, wahlperioden
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO NOTHING;
                """, (
                    id, nachname, vorname, anrede_titel, akad_titel, geburtsdatum, geburtsort, geburtsland,
                    sterbedatum, geschlecht, familienstand, religion, beruf, partei_kurz, wahlperioden_json
                ))

            except Exception as e:
                print(f"Error inserting MDB ID {id}: {e}")
    except Exception as e:
        print(f"Error reading MDB_STAMMDATEN.XML: {e}")

def fetch_rede_and_heckling_comments():
    if pg.has_rows('zwischenruf') and pg.has_rows('reden'):
        print("Daten in den Tabellen 'zwischenruf' und 'reden' sind bereits vorhanden. Abbruch der Funktion.")
        return

    def extract_valid_comments(comments):
        # Entferne `\xa0` direkt aus den Kommentaren
        comments = [comment.replace(u'\xa0', u' ') for comment in comments]
        comments = list(map(lambda x: x[1:-1], comments))  # Entferne äußere Klammern
        comments = list(map(lambda x: x.split('–'), comments))  # Auftrennen bei Gedankenstrich
        flattened_comments = [item.strip() for sublist in comments for item in sublist]  # Flach machen und trimmen
        valid_pattern = r'^(?:(?:Prof\.|Dr\.|Dipl\.-Ing\.)\s)?([a-zA-Z]+\s[a-zA-Z]+(?:\s[a-zA-Z]+){0,2})\s\[(.*?)\]:\s(.*)$'
        return list(filter(lambda x: re.match(valid_pattern, x), flattened_comments))

    def split_info(comment):
        personen_info, content = comment.split(':', 1)  # Trenne am ersten Doppelpunkt
        personen_info = personen_info.split('[')[0].strip()  # Entferne Inhalt in Klammern und trimmen
        titles_to_remove = {'Dr.', 'Prof.', 'Dipl.', '-Ing.', 'von'}
        name_parts = [part for part in personen_info.split(' ') if part and part not in titles_to_remove]
        vorname = ' '.join(name_parts[:-1]) if len(name_parts) > 1 else ""
        nachname = name_parts[-1] if len(name_parts) > 0 else ""
        return [vorname, nachname, content.strip()]

    def get_abgeordnete_id(vorname, nachname, id=None):
        try:
            if id:
                result = pg.execute_query(
                    """
                    SELECT id FROM abgeordnete
                    WHERE id = %s
                    LIMIT 1;
                    """,
                    (id,)
                )
                if result:
                    return result[0][0]
            result = pg.execute_query(
                """
                SELECT id FROM abgeordnete
                WHERE vorname = %s AND nachname = %s
                LIMIT 1;
                """,
                (vorname, nachname)
            )
            if result:
                return result[0][0]

            result = pg.execute_query(
                """
                SELECT id FROM members
                WHERE vorname = %s AND nachname = %s
                LIMIT 1;
                """,
                (vorname, nachname)
            )
            if result:
                return result[0][0]

            return 0
        except Exception as e:
            print(f"Error fetching ID for {vorname} {nachname}: {e}")
            return 0

    try:
        api_url = "https://search.dip.bundestag.de/api/v1/plenarprotokoll"
        params = {
            "f.datum.start": "1950-01-01",
            "apikey": API_KEY
        }
        cursor = None
        total_documents = 0
        itter = 0
        
        while True:
            if cursor:
                params["cursor"] = cursor

            response = requests.get(api_url, params=params)
            response.raise_for_status()
            data = response.json()

            if total_documents == 0:
                total_documents = data.get("numFound", 0)
                
            documents = data.get("documents", [])

            for item in documents:
                protokoll_datum = item.get("datum")

                if not protokoll_datum:
                    continue

                protokoll_datum = f"{protokoll_datum[:4]}-{protokoll_datum[5:7]}-{protokoll_datum[8:10]}"

                fundstelle = item.get("fundstelle")
                if fundstelle and "xml_url" in fundstelle:
                    xml_url = fundstelle["xml_url"]

                    try:
                        xml_response = requests.get(xml_url)
                        xml_response.raise_for_status()
                        tree = ET.ElementTree(ET.fromstring(xml_response.content))
                        root = tree.getroot()

                        for rede in root.findall(".//rede"):
                            redner_elem = rede.find(".//redner")
                            redner_id = None
                            redner_vorname = ""
                            redner_nachname = ""

                            if redner_elem is not None:
                                redner_id_from_elem = redner_elem.get("id")
                                name_elem = redner_elem.find("name")

                                if name_elem is not None:
                                    redner_vorname = name_elem.find("vorname").text if name_elem.find("vorname") is not None else ""
                                    redner_nachname = name_elem.find("nachname").text if name_elem.find("nachname") is not None else ""
                                    redner_id = get_abgeordnete_id(redner_vorname, redner_nachname, redner_id_from_elem)

                                    if not redner_id:
                                        continue

                            rede_inhalt = []
                            zwischenrufe = []

                            for elem in rede:
                                if elem.tag == "p":
                                    klasse = elem.get("klasse", "")

                                    if klasse in {"J", "O", "J_1"}:
                                        rede_inhalt.append(elem.text.strip() if elem.text else "")

                                elif elem.tag == "kommentar" and elem.text:
                                    zwischenrufe.append(elem.text.strip())

                            if not rede_inhalt:
                                continue
                            
                            if redner_id == 0:
                                continue

                            rede_text = "\n".join(rede_inhalt)
                            if len(rede_text) < 500:
                                continue

                            rede_id = rede.get("id")
                            try:
                                pg.execute_query(
                                    """
                                    INSERT INTO reden (id, redner_id, inhalt, datum)
                                    VALUES (%s, %s, %s, %s)
                                    ON CONFLICT (id) DO NOTHING;
                                    """,
                                    (rede_id, redner_id, rede_text, protokoll_datum)
                                )
                            except Exception as e:
                                print(f"Fehler beim Einfügen der Rede {rede_id}: {e}")
                            
                            
                            zwischenrufe = extract_valid_comments(zwischenrufe)
                            for kommentar in zwischenrufe:
                                try:
                                    
                                    vorname, nachname, inhalt = split_info(kommentar)
                                    zwischenrufer_id = get_abgeordnete_id(vorname, nachname)
                                    if not zwischenrufer_id:
                                        continue
                                    pg.execute_query(
                                        """
                                        INSERT INTO zwischenruf (zwischenrufer_id, rede_id, datum, inhalt)
                                        VALUES (%s, %s, %s, %s)
                                        ON CONFLICT DO NOTHING;
                                        """,
                                        (zwischenrufer_id, rede_id, protokoll_datum, inhalt)
                                    )
                                except Exception as e:
                                    print(f"Fehler beim Einfügen des Zwischenrufs: {e}")
                    except Exception as e:
                        print(f"Fehler beim Verarbeiten der Datei {xml_url}: {e}")

            print(f'PROGRESS - {(itter * 100) / total_documents}')        
            itter += 100

            cursor_new = data.get("cursor")
            if cursor_new == cursor:
                print("Alle Dokumente wurden abgerufen.")
                break
            else:
                cursor = cursor_new
        

    except Exception as e:
        print(f"Ein Fehler ist aufgetreten: {e}")

def main():
    print('fetching all members:')
    fetch_all_members()
    print('done')
    print('-' * 100)
    print('fetching all politishians')
    get_abgeordnete()
    print('done')
    print('-' * 100)
    print('fetching all reden and zwischenrufe')
    fetch_rede_and_heckling_comments()
    print('done')

if __name__ == '__main__': 
    main()
