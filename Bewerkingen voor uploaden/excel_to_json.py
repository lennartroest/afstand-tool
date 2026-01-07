import pandas as pd
import json
from datetime import datetime
import os
import re
import requests
import time
import sys
from difflib import SequenceMatcher

# Stel encoding in voor Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Pad naar de Excel bestanden
excel_path = r'alle medewerker adressen.xlsx'
afas_export_path = r'afas export.xlsx'

def similarity(a, b):
    """Bereken similarity ratio tussen twee strings (0.0 tot 1.0)"""
    return SequenceMatcher(None, str(a).lower(), str(b).lower()).ratio()

def normalize_naam(naam):
    """Normaliseer naam voor matching: verwijder leestekens, maak lowercase"""
    if pd.isna(naam):
        return ""
    naam = str(naam).lower().strip()
    # Verwijder leestekens en extra spaties
    naam = re.sub(r'[^\w\s]', '', naam)
    naam = re.sub(r'\s+', ' ', naam)
    return naam

def find_best_match(target_naam, naam_list, min_similarity=0.6):
    """Vind beste match voor target_naam in naam_list"""
    if not target_naam or pd.isna(target_naam):
        return None, 0.0
    
    target_normalized = normalize_naam(target_naam)
    best_match = None
    best_score = 0.0
    
    for naam in naam_list:
        if pd.isna(naam):
            continue
        naam_normalized = normalize_naam(naam)
        score = similarity(target_normalized, naam_normalized)
        if score > best_score:
            best_score = score
            best_match = naam
    
    if best_score >= min_similarity:
        return best_match, best_score
    return None, best_score

def find_oe_naam(target_naam, oe_mapping, min_similarity=0.5):
    """Vind OE naam voor target_naam via fuzzy matching in oe_mapping
    Gebruikt alleen geformatteerde namen voor matching
    """
    if not target_naam or pd.isna(target_naam) or not oe_mapping:
        return None, 0.0
    
    target_normalized = normalize_naam(target_naam)
    best_oe_naam = None
    best_score = 0.0
    
    for norm_key, oe_naam in oe_mapping.items():
        score = similarity(target_normalized, norm_key)
        
        if score > best_score:
            best_score = score
            best_oe_naam = oe_naam
    
    if best_score >= min_similarity:
        return best_oe_naam, best_score
    return None, best_score

def load_afas_oe_mapping():
    """Lees AFAS export en maak mapping van medewerker naar OE naam"""
    print("\n[INFO] Lezen van AFAS export bestand voor OE namen...")
    
    try:
        # Probeer verschillende engines
        df_afas = None
        try:
            df_afas = pd.read_excel(afas_export_path, engine='openpyxl')
        except:
            try:
                df_afas = pd.read_excel(afas_export_path)
            except Exception as e:
                print(f"[WAARSCHUWING] Kon AFAS export niet lezen: {e}")
                return {}
        
        print(f"[INFO] AFAS export gelezen: {len(df_afas)} rijen")
        
        # Kolom B (index 1) = medewerker, Kolom C (index 2) = Status dienstverband, Kolom L (index 11) = OE naam
        if len(df_afas.columns) < 12:
            print(f"[WAARSCHUWING] AFAS export heeft niet genoeg kolommen (verwacht minstens 12, gevonden {len(df_afas.columns)})")
            return {}
        
        medewerker_col = df_afas.columns[1]  # Kolom B
        status_col = df_afas.columns[2]  # Kolom C
        oe_col = df_afas.columns[11]  # Kolom L
        
        print(f"[INFO] Gebruik kolom '{medewerker_col}' voor medewerker namen")
        print(f"[INFO] Gebruik kolom '{status_col}' voor status dienstverband")
        print(f"[INFO] Gebruik kolom '{oe_col}' voor OE namen")
        
        # Filter op "in dienst" (case-insensitive)
        # Maak een kopie van de dataframe met alleen regels waar status "in dienst" is
        df_afas_filtered = df_afas.copy()
        if status_col in df_afas_filtered.columns:
            # Filter op regels waarbij status dienstverband "in dienst" bevat (case-insensitive)
            df_afas_filtered = df_afas_filtered[
                df_afas_filtered[status_col].astype(str).str.lower().str.contains('in dienst', na=False)
            ]
            print(f"[INFO] Gefilterd op 'in dienst': {len(df_afas_filtered)} rijen over (van {len(df_afas)} totaal)")
        else:
            print(f"[WAARSCHUWING] Kolom '{status_col}' niet gevonden, gebruik alle rijen")
        
        # Maak mapping: geformatteerde medewerker naam -> OE naam
        oe_mapping = {}
        for idx, row in df_afas_filtered.iterrows():
            medewerker = row[medewerker_col]
            oe_naam = row[oe_col]
            
            if pd.notna(medewerker) and pd.notna(oe_naam):
                medewerker_str = str(medewerker).strip()
                oe_str = str(oe_naam).strip()
                if medewerker_str and oe_str:
                    # Formatteer de naam
                    geformatteerde_naam = format_naam(medewerker_str)
                    
                    # Sla alleen geformatteerde naam op als key
                    if geformatteerde_naam:
                        normalized_geformatteerd = normalize_naam(geformatteerde_naam)
                        if normalized_geformatteerd not in oe_mapping:
                            oe_mapping[normalized_geformatteerd] = oe_str
        
        print(f"[INFO] {len(oe_mapping)} medewerker->OE mappings gevonden (alleen geformatteerde namen)")
        return oe_mapping
        
    except Exception as e:
        print(f"[WAARSCHUWING] Fout bij lezen AFAS export: {e}")
        return {}

def parse_address_string(full_address):
    """Parse een volledig adres string naar componenten
    Formaat: "Straatnaam Huisnummer, Postcode Plaats"
    """
    if not full_address or pd.isna(full_address):
        return None, None, None, None
    
    full_address = str(full_address).strip()
    
    # Probeer postcode te vinden (NL formaat: 4 cijfers + spatie + 2 letters)
    postcode_match = re.search(r'\b(\d{4}\s+[A-Z]{2})\b', full_address, re.IGNORECASE)
    postcode = None
    plaats = None
    address_part = full_address
    
    if postcode_match:
        postcode = postcode_match.group(1).strip().upper()
        # Alles na de postcode is meestal de plaats
        after_postcode = full_address[postcode_match.end():].strip()
        if after_postcode:
            plaats = after_postcode.strip()
        
        # Alles voor de postcode is het adres deel
        address_part = full_address[:postcode_match.start()].strip()
    
    # Verwijder komma aan het einde als die er is
    address_part = address_part.rstrip(',')
    
    # Parse straat en huisnummer uit address_part
    # Formaat: "Straatnaam Huisnummer" of "Straatnaam Huisnummer toevoeging"
    # Zoek het laatste nummer (met optionele letter/toevoeging) als huisnummer
    # Pattern: nummer gevolgd door optioneel spatie + letter/toevoeging, aan het einde
    huisnummer_match = re.search(r'\s+(\d+[a-zA-Z]?)(?:\s+([a-z]+))?\s*$', address_part, re.IGNORECASE)
    
    if huisnummer_match:
        huisnummer = huisnummer_match.group(1)
        # Als er een toevoeging is (zoals "24 b"), voeg die toe aan huisnummer
        if huisnummer_match.group(2):
            huisnummer = f"{huisnummer} {huisnummer_match.group(2)}"
        straat = address_part[:huisnummer_match.start()].strip()
    else:
        # Fallback: zoek alleen nummer aan het einde
        huisnummer_match = re.search(r'\s+(\d+[a-zA-Z]?)\s*$', address_part)
        if huisnummer_match:
            huisnummer = huisnummer_match.group(1)
            straat = address_part[:huisnummer_match.start()].strip()
        else:
            huisnummer = None
            straat = address_part
    
    return straat, huisnummer, postcode, plaats

def format_naam(naam_string):
    """Formatteer naam: gebruik voornaam + tussenvoegsel + achternaam
    Bijvoorbeeld: "Rietschoten, T.A.J. van (Tijn)" -> "Tijn van Rietschoten"
    Als de naam niet tussen haakjes staat, blijft deze ongewijzigd.
    """
    if not naam_string or pd.isna(naam_string):
        return None
    
    naam = str(naam_string).strip()
    
    # Zoek naam tussen haakjes, bijvoorbeeld "(Tijn)" in "Rietschoten, T.A.J. van (Tijn)"
    haakjes_match = re.search(r'\(([^)]+)\)', naam)
    
    if haakjes_match:
        # Haal de voornaam tussen haakjes
        voornaam = haakjes_match.group(1).strip()
        
        # Zoek het deel voor de haakjes
        deel_voor_haakjes = naam[:haakjes_match.start()].strip()
        
        # Parse achternaam en tussenvoegsel
        achternaam = ""
        tussenvoegsel = ""
        
        if ',' in deel_voor_haakjes:
            # Formaat: "Achternaam, Initialen tussenvoegsel"
            delen = deel_voor_haakjes.split(',', 1)
            achternaam = delen[0].strip()
            deel_na_komma = delen[1].strip() if len(delen) > 1 else ""
            
            # Zoek tussenvoegsels in het deel na de komma
            # Veelvoorkomende tussenvoegsels: van, de, den, der, ten, ter, van der, van de, etc.
            # Splits op woorden en zoek tussenvoegsels
            woorden = deel_na_komma.split()
            tussenvoegsels_lijst = []
            tussenvoegsel_woorden = {'van', 'de', 'den', 'der', 'ten', 'ter'}
            
            # Zoek alle tussenvoegsels (meestal aan het einde, voor de haakjes)
            for i, woord in enumerate(woorden):
                # Verwijder leestekens voor vergelijking
                woord_clean = re.sub(r'[^\w]', '', woord.lower())
                if woord_clean in tussenvoegsel_woorden:
                    # Check of het een combinatie is zoals "van der"
                    tussenvoegsel_deel = woord
                    if i + 1 < len(woorden):
                        volgende_woord_clean = re.sub(r'[^\w]', '', woorden[i + 1].lower())
                        if woord_clean == 'van' and volgende_woord_clean in {'der', 'de', 'den'}:
                            tussenvoegsel_deel = f"{woord} {woorden[i + 1]}"
                            tussenvoegsels_lijst.append(tussenvoegsel_deel)
                            break  # Stop na eerste combinatie
                    tussenvoegsels_lijst.append(tussenvoegsel_deel)
            
            # Neem het laatste tussenvoegsel (meestal het meest relevante)
            if tussenvoegsels_lijst:
                tussenvoegsel = tussenvoegsels_lijst[-1].strip()
        else:
            # Geen komma, probeer eerste woord als achternaam
            woorden = deel_voor_haakjes.split()
            if woorden:
                achternaam = woorden[0]
        
        # Combineer: voornaam + tussenvoegsel + achternaam
        delen = [voornaam]
        if tussenvoegsel:
            delen.append(tussenvoegsel)
        if achternaam:
            delen.append(achternaam)
        
        return " ".join(delen) if len(delen) > 1 else voornaam
    
    # Als de naam niet tussen haakjes staat, blijft deze ongewijzigd
    return naam

def find_column(df, keywords):
    """Zoek een kolom op basis van keywords (case-insensitive)"""
    for col in df.columns:
        col_lower = str(col).lower()
        for keyword in keywords:
            if keyword.lower() in col_lower:
                return col
    return None

def geocode_address(straat, huisnummer, postcode, plaats):
    """Geocode een adres naar latitude/longitude met Nominatim (OpenStreetMap)
    Werkt met volledig adres, of alleen postcode + plaatsnaam, of alleen plaatsnaam.
    Returns: (latitude, longitude) of (None, None) bij fout
    """
    if not straat and not postcode and not plaats:
        return None, None
    
    # Bouw adres string voor geocoding
    address_parts = []
    if straat:
        if huisnummer:
            address_parts.append(f"{straat} {huisnummer}")
        else:
            address_parts.append(straat)
    if postcode:
        address_parts.append(postcode)
    if plaats:
        address_parts.append(plaats)
    
    # Voeg "Nederland" toe voor betere resultaten
    address_parts.append("Nederland")
    
    address_query = ", ".join(address_parts)
    
    try:
        # Nominatim API endpoint
        url = "https://nominatim.openstreetmap.org/search"
        params = {
            "q": address_query,
            "format": "json",
            "limit": 1,
            "countrycodes": "nl"  # Beperk tot Nederland
        }
        
        headers = {
            "User-Agent": "AdresAfstandTool/1.0"  # Vereist door Nominatim
        }
        
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        if data and len(data) > 0:
            result = data[0]
            lat = float(result.get("lat", 0))
            lon = float(result.get("lon", 0))
            return lat, lon
        
        return None, None
        
    except Exception as e:
        print(f"   [WAARSCHUWING] Geocoding mislukt voor '{address_query}': {e}")
        return None, None

print("=" * 60)
print("Excel naar JSON Converter")
print("=" * 60)

# Lees AFAS export voor OE namen mapping
oe_mapping = load_afas_oe_mapping()

# Lees het Excel bestand
try:
    print(f"\n[INFO] Lezen van: {excel_path}")
    
    # Probeer verschillende engines
    df = None
    try:
        df = pd.read_excel(excel_path, engine='openpyxl')
        print("[OK] Bestand gelezen met openpyxl engine")
    except Exception as e1:
        try:
            df = pd.read_excel(excel_path)
            print("[OK] Bestand gelezen met standaard engine")
        except Exception as e2:
            print(f"[FOUT] Fout bij lezen: {e2}")
            print("\n[WAARSCHUWING] Let op: Sluit het Excel bestand in Excel voordat je dit script opnieuw uitvoert!")
            raise
    
    print(f"\n[INFO] Gevonden kolommen: {df.columns.tolist()}")
    print(f"[INFO] Aantal rijen: {len(df)}")
    print("\n[INFO] Eerste paar rijen:")
    print(df.head().to_string())
    
    # Zoek relevante kolommen
    naam_col = find_column(df, ['naam', 'name', 'label', 'medewerker', 'persoon'])
    straat_col = find_column(df, ['straat', 'street', 'adres', 'address'])
    huisnummer_col = find_column(df, ['huisnummer', 'huis', 'nummer', 'number', 'nr'])
    postcode_col = find_column(df, ['postcode', 'post', 'zip', 'pc'])
    plaats_col = find_column(df, ['plaats', 'stad', 'city', 'gemeente'])
    volledig_adres_col = find_column(df, ['volledig', 'adres', 'address', 'volledige'])
    bu_col = find_column(df, ['bu', 'business unit', 'businessunit'])
    lat_col = find_column(df, ['latitude', 'lat'])
    lng_col = find_column(df, ['longitude', 'lng', 'lon'])
    
    print(f"\n[INFO] Gevonden kolommen mapping:")
    print(f"   Naam: {naam_col}")
    print(f"   Straat: {straat_col}")
    print(f"   Huisnummer: {huisnummer_col}")
    print(f"   Postcode: {postcode_col}")
    print(f"   Plaats: {plaats_col}")
    print(f"   Volledig adres: {volledig_adres_col}")
    print(f"   BU: {bu_col}")
    print(f"   Latitude: {lat_col}")
    print(f"   Longitude: {lng_col}")
    
    # Voeg een kolom toe met geformatteerde namen
    if naam_col:
        print(f"\n[INFO] Formatteren van namen en toevoegen aan nieuwe kolom 'Naam Geformatteerd'...")
        df['Naam Geformatteerd'] = df[naam_col].apply(lambda x: format_naam(x) if pd.notna(x) else None)
        print(f"[OK] Geformatteerde namen toegevoegd")
        
        # Sla het Excel bestand op met de nieuwe kolom
        try:
            print(f"[INFO] Opslaan van Excel bestand met geformatteerde namen...")
            df.to_excel(excel_path, index=False, engine='openpyxl')
            print(f"[OK] Excel bestand opgeslagen met nieuwe kolom 'Naam Geformatteerd'")
        except Exception as e:
            print(f"[WAARSCHUWING] Kon Excel bestand niet opslaan: {e}")
            print(f"   De geformatteerde namen worden wel gebruikt voor de JSON output")
    else:
        print(f"\n[WAARSCHUWING] Geen naam kolom gevonden, kan geen geformatteerde namen toevoegen")
    
    # Converteer naar JSON formaat volgens GEDEELDE_ADRESSEN.md
    adressen = []
    
    for idx, row in df.iterrows():
        # Skip lege rijen
        if row.isna().all():
            continue
        
        # Maak een unieke ID
        adres_id = f"shared-{idx + 1}"
        
        # Haal de data uit de rij
        naam = None
        straat = None
        huisnummer = None
        postcode = None
        plaats = None
        bu = None
        latitude = None
        longitude = None
        
        # Als er een volledig adres kolom is, parse die eerst
        # Maar alleen als er geen aparte kolommen zijn voor straat/huisnummer/postcode/plaats
        has_separate_columns = (straat_col and straat_col != volledig_adres_col) or huisnummer_col or postcode_col or plaats_col
        
        if volledig_adres_col and pd.notna(row[volledig_adres_col]) and not has_separate_columns:
            parsed_straat, parsed_huisnummer, parsed_postcode, parsed_plaats = parse_address_string(row[volledig_adres_col])
            if parsed_straat:
                straat = parsed_straat
            if parsed_huisnummer:
                huisnummer = parsed_huisnummer
            if parsed_postcode:
                postcode = parsed_postcode
            if parsed_plaats:
                plaats = parsed_plaats
        
        # Gebruik geformatteerde naam als beschikbaar, anders formatteer zelf
        if 'Naam Geformatteerd' in df.columns and pd.notna(row['Naam Geformatteerd']):
            naam = row['Naam Geformatteerd']
        elif naam_col and pd.notna(row[naam_col]):
            naam = format_naam(row[naam_col])
        
        # Gebruik alleen straat kolom als het niet hetzelfde is als volledig_adres_col
        if straat_col and pd.notna(row[straat_col]) and straat_col != volledig_adres_col:
            straat = str(row[straat_col]).strip()
        elif volledig_adres_col and pd.notna(row[volledig_adres_col]) and not straat:
            # Als er geen aparte straat kolom is, parse het volledige adres
            parsed_straat, parsed_huisnummer, parsed_postcode, parsed_plaats = parse_address_string(row[volledig_adres_col])
            if parsed_straat:
                straat = parsed_straat
            if parsed_huisnummer:
                huisnummer = parsed_huisnummer
            if parsed_postcode:
                postcode = parsed_postcode
            if parsed_plaats:
                plaats = parsed_plaats
        
        if huisnummer_col and pd.notna(row[huisnummer_col]):
            huisnummer = str(row[huisnummer_col]).strip()
        if postcode_col and pd.notna(row[postcode_col]):
            postcode = str(row[postcode_col]).strip()
        if plaats_col and pd.notna(row[plaats_col]):
            plaats = str(row[plaats_col]).strip()
        if bu_col and pd.notna(row[bu_col]):
            bu = str(row[bu_col]).strip()
        
        # Zoek OE naam via fuzzy matching met AFAS export
        # Gebruik alleen geformatteerde naam voor matching
        if oe_mapping and naam:
            geformatteerde_naam = str(naam).strip()
            
            if geformatteerde_naam:
                oe_naam, match_score = find_oe_naam(geformatteerde_naam, oe_mapping, min_similarity=0.5)
                
                if oe_naam:
                    # Overschrijf BU alleen als deze leeg is of als de match zeer goed is
                    if not bu or pd.isna(bu) or str(bu).strip() == "":
                        bu = oe_naam
                        if match_score < 0.9:
                            print(f"   [INFO] OE naam gekoppeld voor '{geformatteerde_naam[:50]}...' -> '{oe_naam}' (match score: {match_score:.2f})")
                    elif match_score >= 0.95:
                        # Zeer goede match, overschrijf bestaande BU
                        bu = oe_naam
        
        if lat_col and pd.notna(row[lat_col]):
            try:
                latitude = float(row[lat_col])
            except:
                pass
        if lng_col and pd.notna(row[lng_col]):
            try:
                longitude = float(row[lng_col])
            except:
                pass
        
        # Als naam niet gevonden, gebruik eerste niet-numerieke kolom
        if not naam:
            for col in df.columns:
                if col not in [straat_col, huisnummer_col, postcode_col, plaats_col, volledig_adres_col, bu_col, lat_col, lng_col]:
                    if pd.notna(row[col]) and str(row[col]).strip():
                        naam = format_naam(row[col])
                        break
        
        # Als nog steeds geen naam, gebruik eerste kolom
        if not naam:
            for col in df.columns:
                if pd.notna(row[col]) and str(row[col]).strip():
                    naam = format_naam(row[col])
                    break
        
        # Bewaar originele plaats voor geocoding
        plaats_origineel = plaats or ""
        
        # Maak adres object
        adres = {
            "id": adres_id,
            "naam": naam or f"Adres {idx + 1}",
            "straat": straat or "",
            "huisnummer": str(huisnummer) if huisnummer else "",
            "postcode": str(postcode) if postcode else "",
            "plaats": plaats_origineel,
            "plaats_origineel": plaats_origineel,  # Bewaar originele plaats voor geocoding
            "source": "shared",
            "toegevoegdOp": datetime.now().isoformat() + "Z"
        }
        
        # Voeg BU toe als beschikbaar
        if bu:
            adres["bu"] = bu
        
        # Voeg latitude/longitude toe als beschikbaar
        if latitude is not None:
            adres["latitude"] = latitude
        if longitude is not None:
            adres["longitude"] = longitude
        
        adressen.append(adres)
    
    # Voeg coördinaten toe via geocoding voor adressen die die nog niet hebben
    print(f"\n[INFO] Controleren en toevoegen van coördinaten via geocoding...")
    adressen_zonder_coordinaten = [a for a in adressen if "latitude" not in a or "longitude" not in a]
    
    if adressen_zonder_coordinaten:
        print(f"[INFO] {len(adressen_zonder_coordinaten)} adressen zonder coördinaten gevonden. Geocoding wordt uitgevoerd...")
        print("[INFO] Let op: Dit kan even duren vanwege rate limiting (1 request/seconde)")
        
        for idx, adres in enumerate(adressen_zonder_coordinaten, 1):
            straat = adres.get("straat", "")
            huisnummer = adres.get("huisnummer", "")
            postcode = adres.get("postcode", "")
            plaats = adres.get("plaats_origineel", "")  # Gebruik originele plaats voor geocoding
            
            if straat or postcode or plaats:
                # Bouw een leesbare adres string voor de output
                adres_delen = []
                if straat:
                    if huisnummer:
                        adres_delen.append(f"{straat} {huisnummer}")
                    else:
                        adres_delen.append(straat)
                if postcode:
                    adres_delen.append(postcode)
                if plaats:
                    adres_delen.append(plaats)
                adres_string = ", ".join(adres_delen) if adres_delen else "onbekend"
                
                print(f"   [{idx}/{len(adressen_zonder_coordinaten)}] Geocoding: {adres_string}")
                
                # Probeer eerst met volledig adres (als beschikbaar)
                lat, lon = geocode_address(straat, huisnummer, postcode, plaats)
                
                # Als dat faalt en plaatsnaam heeft meerdere woorden, probeer zonder laatste woord
                # (om provincie-afkortingen zoals "GLD" te verwijderen)
                if not lat and not lon and plaats:
                    plaats_woorden = plaats.strip().split()
                    if len(plaats_woorden) > 1:
                        plaats_zonder_laatste = " ".join(plaats_woorden[:-1])
                        print(f"      [INFO] Probeer opnieuw zonder laatste woord van plaatsnaam ('{plaats_woorden[-1]}')...")
                        lat, lon = geocode_address(straat, huisnummer, postcode, plaats_zonder_laatste)
                        time.sleep(1)  # Extra wachttijd tussen retry
                
                # Als dat nog steeds faalt en we hebben een straat maar ook postcode + plaats, 
                # probeer dan alleen met postcode + plaats (zonder laatste woord als dat mogelijk is)
                if not lat and not lon and straat and postcode and plaats:
                    plaats_woorden = plaats.strip().split()
                    if len(plaats_woorden) > 1:
                        plaats_zonder_laatste = " ".join(plaats_woorden[:-1])
                        print(f"      [INFO] Probeer met alleen postcode + plaats (zonder '{plaats_woorden[-1]}')...")
                        lat, lon = geocode_address(None, None, postcode, plaats_zonder_laatste)
                        time.sleep(1)  # Extra wachttijd tussen retry
                    else:
                        print(f"      [INFO] Probeer opnieuw met alleen postcode + plaats...")
                        lat, lon = geocode_address(None, None, postcode, plaats)
                        time.sleep(1)  # Extra wachttijd tussen retry
                
                if lat and lon:
                    adres["latitude"] = lat
                    adres["longitude"] = lon
                    print(f"      [OK] Coördinaten toegevoegd: {lat}, {lon}")
                else:
                    print(f"      [FOUT] Geen coördinaten gevonden")
                
                # Rate limiting: wacht 1 seconde tussen requests (Nominatim policy)
                if idx < len(adressen_zonder_coordinaten):
                    time.sleep(1)
            else:
                print(f"   [{idx}/{len(adressen_zonder_coordinaten)}] Adres onvolledig, overgeslagen")
    else:
        print("[OK] Alle adressen hebben al coördinaten!")
    
    # Verwijder plaats_origineel uit alle adres objecten (alleen gebruikt voor geocoding)
    for adres in adressen:
        if "plaats_origineel" in adres:
            del adres["plaats_origineel"]
    
    # Schrijf naar JSON bestand
    output_path = 'adressen.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(adressen, f, indent=2, ensure_ascii=False)
    
    print(f"\n[OK] JSON bestand aangemaakt: {output_path}")
    print(f"[INFO] Totaal aantal adressen: {len(adressen)}")
    print(f"\n[TIP] Upload dit bestand naar GitHub volgens de instructies in GEDEELDE_ADRESSEN.md")
    
except PermissionError as e:
    print(f"\n[FOUT] Het Excel bestand is waarschijnlijk open in Excel!")
    print("   Sluit het Excel bestand en probeer het opnieuw.")
    print(f"   Details: {e}")
except FileNotFoundError as e:
    print(f"\n[FOUT] Bestand niet gevonden!")
    print(f"   Zorg dat '{excel_path}' in dezelfde map staat als dit script.")
    print(f"   Details: {e}")
except Exception as e:
    print(f"\n[FOUT] {e}")
    import traceback
    traceback.print_exc()

