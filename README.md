# Monitor Manager

**Monitor Manager** è un'applicazione leggera che consente di effettuare lo **streaming di sorgenti video** (come webcam, fotocamere virtuali OBS o altri dispositivi di acquisizione) direttamente su un **monitor esterno** collegato al computer. È ideale per presentazioni, videoproduzioni, test di qualità immagine o semplicemente per estendere il feed video a un secondo schermo.

## 🖥️ Funzionalità principali

- 🔌 Supporta webcam fisiche e virtuali (es. OBS Virtual Camera)
- 🖼️ Visualizzazione a schermo intero sul monitor selezionato
- 🎛️ Selezione e gestione dinamica della sorgente video
- 🧭 Rilevamento automatico dei monitor collegati
- ⚙️ Interfaccia semplice e minimale

## 🚀 Requisiti

- **Sistema operativo:** Windows 10/11, Linux o macOS
- **Python 3.8+**
- Librerie Python necessarie (vedi installazione)

## 📦 Installazione

1. Clona il repository:
   ```bash
   git clone https://github.com/tuo-username/monitor-manager.git
   cd monitor-manager
   ```

2. Installa le dipendenze:
   ```bash
   pip install -r requirements.txt
   ```

   _Le principali dipendenze includono:_
   - `opencv-python`
   - `PyQt5` (o `tkinter` per GUI semplificata)
   - `screeninfo` (per la gestione multi-monitor)

## ▶️ Utilizzo

Esegui il programma con:

```bash
python monitor_manager.py
```

1. Seleziona la **sorgente video** desiderata dall'elenco.
2. Scegli il **monitor esterno** su cui visualizzare il video.
3. Avvia lo streaming premendo **"Start"**.

Puoi interrompere lo streaming in qualsiasi momento con il tasto **"Stop"** o chiudendo la finestra.

## 📷 Esempi di utilizzo

- **Registi e videomaker**: vedere l’output della camera OBS su un secondo schermo
- **Conferenze e presentazioni**: proiettare una webcam sullo schermo secondario
- **Testing hardware**: visualizzare e confrontare la qualità di più dispositivi video
- **Sale del Regno dei Testimoni di Gova**: trasmettere contenuti video su monitor secondari per migliorare la visibilità durante le adunanze

## 🛠️ To-do

- [ ] Supporto per più sorgenti contemporaneamente (picture-in-picture)
- [ ] Opzione per crop, zoom e rotazione immagine
- [ ] Supporto hotkey per avvio/arresto rapido
- [ ] Modalità borderless su monitor selezionato

## 📄 Licenza

Distribuito sotto la licenza GPL. Vedi `LICENSE` per i dettagli.

---

Made with ❤️ by [Leonardo Olivieri]
``


*Nota: Questo programma è stato progettato per l'utilizzo nelle Sale del Regno dei Testimoni di Geova per lo streaming su monitor secondari.*
