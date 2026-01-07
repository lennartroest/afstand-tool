# Gedeelde Adressenlijst Instellen

## 📋 Overzicht

De tool kan nu een gedeelde adressenlijst laden vanuit GitHub. Dit betekent dat je één centrale lijst kunt beheren die voor alle gebruikers zichtbaar is.

## 🚀 Stappen om Gedeelde Adressen In Te Stellen

### Stap 1: Upload `adressen.json` naar GitHub

1. Ga naar je GitHub repository
2. Upload het bestand `adressen.json` naar de root van je repository
3. Zorg dat het bestand in de `main` (of `master`) branch staat

### Stap 2: Controleer de URL

Je GitHub Raw URL ziet er zo uit:
```
https://raw.githubusercontent.com/JOUW-GEBRUIKERSNAAM/JOUW-REPOSITORY-NAAM/main/adressen.json
```

**Voorbeeld:**
Als je repository heet `adres-afstand-tool` en je gebruikersnaam is `janedoe`, dan is de URL:
```
https://raw.githubusercontent.com/janedoe/adres-afstand-tool/main/adressen.json
```

### Stap 3: Automatische Detectie (Werkt op GitHub Pages)

Als je tool op GitHub Pages draait (bijv. `https://jouwgebruikersnaam.github.io/adres-afstand-tool/`), dan wordt de URL **automatisch** gedetecteerd! Je hoeft niets te configureren.

### Stap 4: Handmatige Configuratie (Als Automatisch Niet Werkt)

Als automatische detectie niet werkt, pas dan de functie `getSharedAddressesUrl()` aan in `index.html`:

Zoek naar deze regel (rond regel 1200):
```javascript
function getSharedAddressesUrl() {
    // Vervang deze regel met jouw GitHub URL:
    return 'https://raw.githubusercontent.com/JOUW-GEBRUIKERSNAAM/JOUW-REPO/main/adressen.json';
}
```

## 📝 `adressen.json` Formaat

Het bestand moet een JSON array zijn met adres objecten:

```json
[
  {
    "id": "shared-1",
    "naam": "Kantoor Amsterdam",
    "straat": "Damrak",
    "huisnummer": "1",
    "postcode": "1012 LG",
    "plaats": "Amsterdam",
    "latitude": 52.379189,
    "longitude": 4.900278,
    "toegevoegdOp": "2024-01-01T00:00:00.000Z",
    "source": "shared"
  },
  {
    "id": "shared-2",
    "naam": "Kantoor Rotterdam",
    "straat": "Coolsingel",
    "huisnummer": "40",
    "postcode": "3011 AD",
    "plaats": "Rotterdam",
    "latitude": 51.9225,
    "longitude": 4.4778,
    "toegevoegdOp": "2024-01-01T00:00:00.000Z",
    "source": "shared"
  }
]
```

### Belangrijke Velden:

- **id**: Unieke identifier (gebruik bijv. "shared-1", "shared-2", etc.)
- **naam**: Naam/label van het adres
- **straat**, **huisnummer**, **postcode**, **plaats**: Adres componenten
- **latitude**, **longitude**: Coördinaten (optioneel, worden automatisch gevonden als leeg)
- **source**: Moet "shared" zijn voor gedeelde adressen

## 🔄 Adressen Toevoegen aan Gedeelde Lijst

### Methode 1: Handmatig in GitHub

1. Ga naar je GitHub repository
2. Klik op `adressen.json`
3. Klik op het potlood icoon (Edit)
4. Voeg een nieuw adres object toe aan de array
5. Klik "Commit changes"

### Methode 2: Via Excel → JSON Converter

1. Maak een Excel bestand met je adressen
2. Gebruik een online converter (bijv. https://www.convertcsv.com/csv-to-json.htm) of Python script
3. Kopieer de JSON naar `adressen.json`
4. Upload naar GitHub

### Methode 3: Gebruik de Tool + Export

1. Voeg adressen toe via de tool (lokaal)
2. Export de data (via browser console of localStorage)
3. Voeg toe aan `adressen.json`
4. Upload naar GitHub

## ✅ Hoe Werkt Het?

1. **Bij opstarten** laadt de tool automatisch `adressen.json` vanuit GitHub
2. **Gedeelde adressen** worden getoond met een "Gedeeld" badge
3. **Gedeelde adressen** kunnen niet worden verwijderd door gebruikers
4. **Lokale adressen** worden opgeslagen in de browser (localStorage)
5. **Beide lijsten** worden gecombineerd getoond

## 🔍 Troubleshooting

### Gedeelde adressen worden niet geladen

1. **Controleer de URL:**
   - Open de GitHub Raw URL in je browser
   - Je zou de JSON moeten zien

2. **Controleer het JSON formaat:**
   - Gebruik een JSON validator (bijv. https://jsonlint.com/)
   - Zorg dat het een geldige JSON array is

3. **Controleer CORS:**
   - GitHub Raw URLs zouden geen CORS problemen moeten geven
   - Als je een andere hosting gebruikt, zorg voor CORS headers

4. **Browser Console:**
   - Open Developer Tools (F12)
   - Kijk naar de Console tab voor foutmeldingen

### Adressen worden niet getoond op de kaart

- Controleer of `latitude` en `longitude` zijn ingevuld
- Als leeg, worden ze automatisch gegeocodeerd bij het laden
- Dit kan even duren bij veel adressen

## 💡 Tips

- **Gebruik unieke IDs**: Zorg dat elk adres een unieke `id` heeft
- **Update regelmatig**: Gebruikers zien automatisch updates bij het herladen van de pagina
- **Backup**: Houd een backup van je `adressen.json` bestand
- **Versiebeheer**: GitHub houdt automatisch een geschiedenis bij van wijzigingen

## 📞 Voorbeeld Workflow

1. Je voegt 10 adressen toe aan `adressen.json`
2. Je upload het bestand naar GitHub
3. Alle gebruikers zien deze 10 adressen bij het openen van de tool
4. Gebruikers kunnen nog steeds eigen adressen toevoegen (lokaal)
5. Deze lokale adressen worden niet gedeeld met anderen

---

**Klaar!** Je gedeelde adressenlijst is nu beschikbaar voor alle gebruikers! 🎉

