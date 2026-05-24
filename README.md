# README — Applicazione WebCam OpenCV

## Descrizione del Progetto
Questo software in Python sfrutta la libreria OpenCV per elaborare in tempo reale il flusso video della webcam, offrendo un'ampia gamma di filtri digitali ed effetti avanzati di computer vision. L'interfaccia interattiva consente all'utente, tramite semplici scorciatoie da tastiera, di trasformare l'immagine con filtri ed effetti, applicare algoritmi di tracciamento facciale (per posizionare accessori grafici come cappelli o occhiali sul volto) o avviare minigiochi basati sui movimenti del corpo. L'applicazione include inoltre funzionalità integrate per catturare istantanee e salvare video direttamente sul computer.

---

## Requisiti di Sistema
* **Sistema Operativo:** Windows 10/11, macOS, o Linux (incluso Raspberry Pi OS).
* **Versione Python:** Python 3.8 o superiore *(Testato e ottimizzato per architetture multi-versione)*.
* **Hardware Richiesto:** Una webcam (integrata, USB o modulo camera Raspberry Pi) funzionante.
* **Gestione Piattaforme:** Automatizzata via script. Il file `requirements.txt` adatta dinamicamente le versioni di OpenCV e NumPy in base alla versione di Python rilevata per evitare conflitti di dipendenze.

---

## Installazione Step-by-Step

Segui questi passaggi partendo da zero per configurare l'ambiente e installare i componenti necessari.

### 1. Organizza i file del progetto
Assicurati di avere tutti i file all'interno della stessa cartella sul tuo computer con la seguente struttura:
```text
Progetto/
│
├── main.py
├── effects.py
├── filters.py
├──assets
    ├──barba.png
    ├──cappello3.png
    ├──occhiali.png
├──requirements.txt

```
### 2. Apri il terminale (o prompt dei comandi)
* **Windows:** Premi il tasto `Windows`, digita `cmd` e premi Invio.
* **macOS/Linux:** Apri l'applicazione `Terminale`.

### 3. Spostati nella cartella del progetto
Usa il comando `cd` seguito dal percorso della cartella in cui hai salvato i file. 
*Esempio:*
```bash
cd percorso/della/tua/cartella/il_tuo_progetto
```
### 4. Installa le librerie richieste
Esegui il seguente comando per installare automaticamente OpenCV, NumPy, ecc sul tuo sistema :
```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 5. Come avviare l'applicazione
Una volta completata l'installazione, rimani nel terminale all'interno della cartella del progetto ed esegui il comando:
```
python main.py
```
### 6. Raspberry PI
Preparazione del Sistema Operativo 

Prima di lanciare lo script o configurare l'ambiente su Raspberry Pi OS, assicurati che il sistema operativo disponga dei moduli core di isolamento e delle librerie grafiche native di C++ richieste da OpenCV. Apri il terminale del Raspberry e digita:
```
sudo apt update && sudo apt install -y python3-pip python3-venv libgl1-mesa-glx libglib2.0-0
```

### Tasti Gestione Programma
|  Tasto  | Azione         | Descrizione                                                                                                    |
|:-------:|:---------------|:---------------------------------------------------------------------------------------------------------------|
|  **Q**  | Esci           | Chiude applicazione ed eventualmente termina registrazione                                                     |
|  **S**  | Screen         | Esegue screenshot con filtro applicato. Salvato nella cartella  nella cartella `outputImages`                  |
|  **R**  | Registrazione  | Registra lo schermo con filtro applicato (no microfono). Salvato nella cartella  nella cartella `outputVideos` |
|  **X**  | Mod automatica | Attiva/Disattiva modalità di autoscorrimento dei filtri ogni 3 sec                                             |
|  **Y**  | Sfocatura      | Attiva/Disattiva sfocatura su tutto il frame tranne la faccia                                                  |
| **< >** | Pagine         | Scorrimento della pagine per i filtri                                                                          |

### Effetti e Utility
| Tasto | Azione     | Descrizione |
|:-----:|:-----------| :--- |
| **0** |   Normale         |Ripristina il flusso video originale della webcam. |
| **1** |    Grigio        | Trasforma l'immagine in scala di grigi.|
| **2** |  Negativo          |Inverte i colori del frame (effetto negativo fotografico). |
| **3** |  Seppia          | Applica una tonalità calda stile foto vintage.|
| **4** |      Termico      |Simula una mappa di calore (Heatmap) basata sulla luminosità. |
| **5** |     Solarizza       |Altera i profili di luce creando inversioni di contrasto cromatico. |
| **6** |  Cartoon          |Trasforma il video in un disegno in stile fumetto (Colori fluidi + bordi). |
| **7** |    Lavagna        |Rileva i contorni trasformando il frame in un disegno con gessetto bianco su ardesia. |
| **8** |     Pixel       |Applica una pixelazione stile retro-gaming (effetto mosaico). |
| **9** |Matrix            |Genera la pioggia digitale di caratteri verdi in stile Matrix. |
| **A** | Specchio O |Specchia l'immagine lungo l'asse orizzontale. |
| **B** | Specchio V |Specchia l'immagine lungo l'asse verticale (effetto sottosopra). |
| **C** | Specchio T |Combina lo specchio orizzontale e verticale contemporaneamente. |
| **D** | Duplica    |Moltiplica il frame sdoppiando lo schermo. |
| **E** | Crazy      |Distorce i colori e le forme in modo psichedelico e caotico. |
| **F** | Glitch     |Simula un segnale video corrotto analogico con aberrazione cromatica e strappi orizzontali. |
| **G** | Movimento  |Sensore di sicurezza: colora di rosso acceso solo i pixel che si stanno muovendo. |
| **H** | Ghost      |Crea una scia semitrasparente fluida (effetto fantasma) che segue i movimenti. |
| **J** | Occhiali   |Disegna gli occhiali (occhiali.png) sopra gli occhi rilevati. |
| **K** | Cappello   |Posiziona un cappello (cappello.png) esattamente sopra la testa. |
| **L** | Barba      |Applica una barba finta (barba.png) seguendo la posizione del mento. |
| **M** | Vignetta   |Scurisce i bordi del frame concentrando la luce al centro dell'immagine. |
| **N** | Blur Mosso |Applica un effetto cinetico di movimento (Motion Blur) direzionale in diagonale. |
| **Z** | Gioco      | Attiva un minigioco interattivo che traccia il movimento del tuo naso sullo schermo!|
