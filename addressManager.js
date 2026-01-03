/**
 * Adresbeheer Module
 * Beheert het opslaan, laden en beheren van adressen
 */

class AddressManager {
    constructor() {
        this.storageKey = 'savedAddresses';
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
     * Haal alle adressen op
     */
    getAllAddresses() {
        return this.addresses;
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
}

// Export voor gebruik in andere modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = AddressManager;
}

