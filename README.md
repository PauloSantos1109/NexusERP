# 🚀 NEXUS ERP - Sistema di Gestione Inventario

**NEXUS ERP** è un'applicazione desktop robusta e moderna sviluppata in Python per la gestione dei magazzini e il controllo delle vendite. Il sistema presenta un'interfaccia "Dark Mode" ad alto contrasto, focalizzata sull'usabilità e sulla precisione dei dati.

## ✨ Funzionalità Principali

- **Pannello Inventario Intelligente:** Elenco dinamico con filtri per categoria, sottocategoria e intervalli di prezzo/quantità.
- **Calcolo del Profitto Automatizzato:** Durante la registrazione dei prodotti, il prezzo di vendita viene calcolato in tempo reale in base alla percentuale di profitto desiderata.
- **Interfaccia Blindata:** Stilizzazione personalizzata tramite QSS (Qt Style Sheets) per garantire coerenza visiva su diversi sistemi operativi.
- **Navigazione Fluida:** Sidebar interattiva con icone dinamiche di FontAwesome (tramite QtAwesome).
- **Gestione Completa (CRUD):** Inserimento, cancellazione, ricerca e visualizzazione dei prodotti con calcoli del valore totale in magazzino.

## 🛠️ Tecnologie Utilizzate

* **Python 3.x**
* **PySide6:** Interfaccia grafica professionale (Qt per Python).
* **QtAwesome:** Icone vettoriali dinamiche.
* **SQLite:** Database relazionale leggero e integrato.
* **QSS:** Design e stilizzazione dei componenti.

## 📈 Logica di Business (Margine di Profitto)

Il sistema automatizza la determinazione del prezzo di vendita attraverso la formula:

$$PrezzoVendido = Costo \times (1 + \frac{Profitto\%}{100})$$

Ciò garantisce che il margine operativo sia rispettato senza errori di calcolo manuale durante la registrazione.

## 📦 Installazione ed Esecuzione

1. **Clona la repository:**
   ```bash
   git clone [https://github.com/tuo-utente/nexus-erp.git](https://github.com/tuo-utente/nexus-erp.git)
   cd nexus-erp
    ```

2. **Installa le dipendenze:**
    ```
    pip install PySide6 qtawesome
    ```

3. **Avvia il sistema:**
    ```
    python main.py
    ```

## 📂 Struttura del Progetto
    estoque-app/
    
    ├── main.py                # Ponto de entrada do sistema
    ├── ui/                    # Telas e componentes da interface
    │   ├── main_window.py      # Janela principal e lógica do estoque
    │   ├── vendas_window.py    # Módulo de vendas (PDV)
    │   └── dashboard_window.py # Métricas e indicadores
    ├── services/              # Regras de negócio e persistência
    │   └── estoque_service.py  # Conexão com banco de dados e filtros SQL
    └── database/


## ⚙️ Configurazione Filtri Predefiniti
Il sistema è configurato in modo che, all'avvio, il filtro della categoria sia impostato su "Tutti", garantendo che nessun prodotto venga nascosto accidentalmente durante il primo caricamento dei dati.

---


### Suggerimento:
Se vuoi mantenere il progetto internazionale, è comune lasciare il file principale come `README.md` in inglese e creare versioni come `README.it.md` (italiano) ou `README.pt-br.md` (portoghese). 
