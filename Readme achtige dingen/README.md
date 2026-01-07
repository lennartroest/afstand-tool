# Adres Afstand Tool - Nederland

Een webapplicatie om adressen te beheren en afstanden tussen adressen te berekenen op een interactieve kaart van Nederland.

## 📋 Functionaliteiten

- ✅ Adressen toevoegen en beheren
- ✅ Excel bestanden importeren (batch import)
- ✅ Automatische adres aanvulling (autocomplete)
- ✅ Interactieve kaart met markers
- ✅ Afstandsberekening tussen adressen
- ✅ Visualisatie van dichtstbijzijnde adres
- ✅ Tabel met alle afstanden

## 🚀 Hoe anderen toegang geven

### Optie 1: GitHub Pages (Gratis & Eenvoudig) ⭐ AANBEVOLEN

**Voordelen:**
- Volledig gratis
- Eenvoudig te delen via een URL
- Automatische updates
- Geen server nodig

**Stappen:**

1. **Maak een GitHub account** (als je die nog niet hebt)
   - Ga naar https://github.com
   - Maak een gratis account

2. **Maak een nieuwe repository**
   - Klik op "New repository"
   - Geef het een naam (bijv. "adres-afstand-tool")
   - Kies "Public" (voor gratis hosting)
   - Vink "Add a README file" aan
   - Klik "Create repository"

3. **Upload de bestanden**
   - Klik op "uploading an existing file"
   - Sleep alle bestanden uit de map `8. Adres Afstand Tool` naar GitHub:
     - `index.html`
     - `addressManager.js`
     - `logo.png` (optioneel)
   - Klik "Commit changes"

4. **Activeer GitHub Pages**
   - Ga naar "Settings" in je repository
   - Scroll naar "Pages" in het linker menu
   - Bij "Source" kies "Deploy from a branch"
   - Kies "main" branch en "/ (root)" folder
   - Klik "Save"
   - Wacht 1-2 minuten

5. **Deel de URL**
   - Je krijgt een URL zoals: `https://jouwgebruikersnaam.github.io/adres-afstand-tool/`
   - Deel deze URL met anderen!

**Bijwerken:**
- Upload gewoon nieuwe versies van de bestanden naar GitHub
- De website update automatisch binnen 1-2 minuten

---

### Optie 2: Netlify Drop (Gratis & Zeer Eenvoudig)

**Voordelen:**
- Super eenvoudig (geen account nodig voor eerste keer)
- Direct live
- Automatische HTTPS

**Stappen:**

1. Ga naar https://app.netlify.com/drop
2. Sleep de hele map `8. Adres Afstand Tool` naar het upload gebied
3. Wacht tot upload klaar is
4. Je krijgt direct een URL (bijv. `https://random-name-123.netlify.app`)
5. Deel deze URL met anderen!

**Voor permanente URL:**
- Maak een gratis Netlify account
- Kies een custom naam voor je site

---

### Optie 3: Vercel (Gratis)

**Voordelen:**
- Zeer snel
- Automatische deployments
- Goede performance

**Stappen:**

1. Ga naar https://vercel.com
2. Maak een account (kan met GitHub)
3. Klik "Add New Project"
4. Upload de map `8. Adres Afstand Tool`
5. Klik "Deploy"
6. Deel de URL met anderen!

---

### Optie 4: Lokale Server (Voor intern gebruik)

Als je een interne server hebt of de tool alleen binnen je organisatie wilt gebruiken:

**Met Python (eenvoudigste):**
```bash
# Navigeer naar de map
cd "8. Adres Afstand Tool"

# Start een lokale server (Python 3)
python -m http.server 8000

# Of met Python 2
python -m SimpleHTTPServer 8000
```

Dan is de tool bereikbaar op: `http://localhost:8000`

**Met Node.js:**
```bash
# Installeer http-server (eenmalig)
npm install -g http-server

# Start server
cd "8. Adres Afstand Tool"
http-server -p 8000
```

**Voor netwerk toegang:**
- Vervang `localhost` met je IP-adres
- Anderen kunnen dan `http://jouw-ip-adres:8000` gebruiken
- Zorg dat firewall poort 8000 toestaat

---

### Optie 5: OneDrive/SharePoint Delen (Voor CQT intern)

Aangezien je OneDrive gebruikt:

1. **Deel de map via OneDrive**
   - Rechtsklik op de map `8. Adres Afstand Tool`
   - Kies "Delen"
   - Stel in wie toegang heeft
   - Kopieer de link

2. **Maak een HTML bestand dat direct opent**
   - Anderen kunnen het bestand downloaden
   - Open `index.html` in hun browser
   - **Let op:** Ze moeten alle bestanden downloaden (niet alleen index.html)

**Nadeel:** Elke gebruiker heeft zijn eigen data (localStorage)

---

## 📝 Belangrijke Opmerkingen

### Data Opslag
- De tool gebruikt **localStorage** in de browser
- Dit betekent dat elke gebruiker zijn eigen adressen heeft
- Adressen worden niet gedeeld tussen gebruikers
- Als je gedeelde data wilt, is een backend/server nodig

### Excel Bestand Formaat
Voor batch import moet het Excel bestand deze structuur hebben:

| Naam/Label | Volledig Adres |
|------------|----------------|
| Kantoor Amsterdam | Damrak 1, 1012 LG Amsterdam |
| Kantoor Rotterdam | Coolsingel 40, 3011 AD Rotterdam |

### Browser Vereisten
- Moderne browser (Chrome, Firefox, Edge, Safari)
- Internetverbinding (voor kaart en geocoding)
- JavaScript ingeschakeld

### Logo
- Plaats `logo.png` in dezelfde map als `index.html`
- Als het logo niet wordt gevonden, wordt het automatisch verborgen

---

## 🔧 Technische Details

### Gebruikte Technologieën
- **Leaflet** - Kaart visualisatie
- **OpenStreetMap** - Kaart data
- **Nominatim API** - Geocoding (adres → coördinaten)
- **SheetJS (xlsx)** - Excel bestand parsing
- **LocalStorage** - Lokale data opslag

### Bestanden Structuur
```
8. Adres Afstand Tool/
├── index.html          (Hoofdbestand)
├── addressManager.js   (Adresbeheer module)
├── logo.png           (Logo - optioneel)
└── README.md          (Deze file)
```

---

## ❓ Veelgestelde Vragen

**Q: Werkt dit zonder internet?**
A: Nee, de kaart en geocoding hebben internet nodig.

**Q: Kan ik de adressen delen tussen gebruikers?**
A: Nee, elke gebruiker heeft zijn eigen data. Voor gedeelde data is een backend nodig.

**Q: Is er een limiet op het aantal adressen?**
A: Technisch gezien is er een limiet van ~5-10MB aan localStorage data, wat duizenden adressen kan zijn.

**Q: Kan ik de tool aanpassen?**
A: Ja, alle code is in `index.html` en `addressManager.js`. Pas aan naar wens!

---

## 📞 Support

Voor vragen of problemen, controleer:
1. Browser console voor foutmeldingen (F12)
2. Of alle bestanden correct zijn geüpload
3. Of je internetverbinding werkt

---

**Aanbevolen hosting:** GitHub Pages voor de beste balans tussen eenvoud en functionaliteit.

