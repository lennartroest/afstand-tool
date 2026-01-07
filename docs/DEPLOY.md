# Quick Deploy Guide - Snelle Start

## 🚀 Snellste Methode: Netlify Drop (2 minuten)

1. Ga naar: https://app.netlify.com/drop
2. Sleep de hele map `8. Adres Afstand Tool` naar het upload gebied
3. Klaar! Je krijgt direct een URL

---

## 📦 GitHub Pages (5 minuten)

### Stap 1: Repository Maken
1. Ga naar https://github.com/new
2. Repository naam: `adres-afstand-tool`
3. Kies "Public"
4. Klik "Create repository"

### Stap 2: Bestanden Uploaden
1. Klik "uploading an existing file"
2. Upload deze bestanden:
   - `index.html`
   - `addressManager.js`
   - `logo.png` (als je die hebt)
3. Klik "Commit changes"

### Stap 3: Pages Activeren
1. Ga naar Settings → Pages
2. Source: "Deploy from a branch"
3. Branch: "main", Folder: "/ (root)"
4. Klik "Save"

### Stap 4: Wacht 1-2 minuten
Je site is live op: `https://jouwgebruikersnaam.github.io/adres-afstand-tool/`

---

## 💻 Lokale Server (Voor Testen)

Open PowerShell/Command Prompt in de map en voer uit:

```bash
python -m http.server 8000
```

Open dan: http://localhost:8000

---

## 📋 Checklist voor Deployment

- [ ] Alle bestanden zijn aanwezig:
  - [ ] `index.html`
  - [ ] `addressManager.js`
  - [ ] `logo.png` (optioneel)
- [ ] Test de tool lokaal eerst
- [ ] Controleer of logo wordt getoond (als aanwezig)
- [ ] Test Excel upload functionaliteit
- [ ] Deel de URL met gebruikers

---

## ⚠️ Belangrijk

- **Internet nodig:** De tool heeft internet nodig voor kaarten en geocoding
- **Data is lokaal:** Elke gebruiker heeft zijn eigen adressen
- **Geen backend:** Alles draait in de browser

