/**
 * Adresbeheer Module
 * Beheert het opslaan, laden en beheren van adressen
 */

class AddressManager {
    constructor() {
        this.storageKey = 'savedAddresses';
        this.sharedAddresses = []; // Gedeelde adressen vanuit GitHub
        this.addresses = this.loadAddresses();
    }

    /**
     * Laad opgeslagen adressen uit localStorage
     */
    loadAddresses() {
        const stored = localStorage.getItem(this.storageKey);
        if (stored) {
            try {
                return JSON.parse(stored);
            } catch (e) {
                console.error('Fout bij laden van adressen:', e);
                return [];
            }
        }
        return [];
    }

    /**
     * Sla adressen op in localStorage
     */
    saveAddresses() {
        try {
            localStorage.setItem(this.storageKey, JSON.stringify(this.addresses));
            return true;
        } catch (e) {
            console.error('Fout bij opslaan van adressen:', e);
            return false;
        }
    }

    /**
     * Voeg een nieuw adres toe
     * @param {Object} address - Adres object met naam, straat, huisnummer, postcode, plaats
     */
    addAddress(address) {
        const newAddress = {
            id: Date.now().toString(),
            naam: address.naam || '',
            straat: address.straat || '',
            huisnummer: address.huisnummer || '',
            postcode: address.postcode || '',
            plaats: address.plaats || '',
            latitude: address.latitude || null,
            longitude: address.longitude || null,
            bu: address.bu || null, // Business Unit
            toegevoegdOp: new Date().toISOString()
        };
        
        this.addresses.push(newAddress);
        this.saveAddresses();
        return newAddress;
    }

    /**
     * Verwijder een adres
     * @param {string} id - ID van het adres
     */
    removeAddress(id) {
        this.addresses = this.addresses.filter(addr => addr.id !== id);
        this.saveAddresses();
        return true;
    }

    /**
     * Update een adres
     * @param {string} id - ID van het adres
     * @param {Object} updates - Object met te updaten velden
     */
    updateAddress(id, updates) {
        const index = this.addresses.findIndex(addr => addr.id === id);
        if (index !== -1) {
            this.addresses[index] = { ...this.addresses[index], ...updates };
            this.saveAddresses();
            return this.addresses[index];
        }
        return null;
    }

    /**
     * Laad gedeelde adressen vanuit een URL (bijv. GitHub Raw)
     */
    async loadSharedAddresses(url) {
        try {
            console.log('Fetching gedeelde adressen van:', url);
            const response = await fetch(url, {
                cache: 'no-cache', // Altijd de nieuwste versie ophalen
                headers: {
                    'Accept': 'application/json'
                }
            });
            
            console.log('Response status:', response.status, response.statusText);
            
            if (response.ok) {
                const data = await response.json();
                console.log('Gedeelde adressen data ontvangen:', data);
                
                // Valideer dat het een array is
                if (!Array.isArray(data)) {
                    console.error('Gedeelde adressen is geen array:', data);
                    return false;
                }
                
                // Markeer als gedeeld
                this.sharedAddresses = data.map(addr => ({
                    ...addr,
                    source: 'shared'
                }));
                
                console.log(`${this.sharedAddresses.length} gedeelde adressen geladen`);
                return true;
            } else {
                console.error('HTTP fout:', response.status, response.statusText);
                // Probeer de response tekst te lezen voor meer info
                const text = await response.text();
                console.error('Response body:', text);
                return false;
            }
        } catch (error) {
            console.error('Fout bij laden van gedeelde adressen:', error);
            console.error('Error details:', {
                message: error.message,
                stack: error.stack,
                url: url
            });
            return false;
        }
    }

    /**
     * Haal alle adressen op (zowel lokaal als gedeeld)
     */
    getAllAddresses() {
        // Combineer gedeelde en lokale adressen, voorkom duplicaten
        const allAddresses = [...this.sharedAddresses];
        const localIds = new Set(this.sharedAddresses.map(a => a.id));
        
        this.addresses.forEach(addr => {
            // Voeg alleen toe als het niet al in gedeelde lijst staat
            if (!localIds.has(addr.id)) {
                allAddresses.push({
                    ...addr,
                    source: 'local'
                });
            }
        });
        
        return allAddresses;
    }

    /**
     * Haal alleen lokale adressen op
     */
    getLocalAddresses() {
        return this.addresses;
    }

    /**
     * Haal alleen gedeelde adressen op
     */
    getSharedAddresses() {
        return this.sharedAddresses;
    }

    /**
     * Haal een adres op basis van ID
     * @param {string} id - ID van het adres
     */
    getAddress(id) {
        return this.addresses.find(addr => addr.id === id);
    }

    /**
     * Geef een volledig adres string terug
     * @param {Object} address - Adres object
     */
    getFullAddressString(address) {
        const parts = [];
        if (address.straat) parts.push(address.straat);
        if (address.huisnummer) parts.push(address.huisnummer);
        if (address.postcode) parts.push(address.postcode);
        if (address.plaats) parts.push(address.plaats);
        return parts.join(' ') + ', Nederland';
    }

    /**
     * Geef een korte adres string terug voor weergave (alleen postcode + plaats)
     * @param {Object} address - Adres object
     */
    getDisplayAddressString(address) {
        const parts = [];
        if (address.postcode) parts.push(address.postcode);
        if (address.plaats) parts.push(address.plaats);
        return parts.join(' ');
    }

    /**
     * Haal alle unieke BU's op uit alle adressen
     */
    getAllBUs() {
        const allAddresses = this.getAllAddresses();
        const bus = new Set();
        allAddresses.forEach(addr => {
            if (addr.bu) {
                bus.add(addr.bu);
            }
        });
        return Array.from(bus).sort();
    }
}

// Export voor gebruik in andere modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = AddressManager;
}
