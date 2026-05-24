import cv2
import numpy as np
import random

#stati globali riutilizzati per evitare allocazioni continue in memoria
matrix_posizioni_y = None   #lista globale x tenere traccia altezza della pioggia matrix
#->se fotocamera ridimensionata->matrix_pos_y e tinta_verde_cached devono essere ricalcolate
matrix_caratteri = [str(x) for x in range(10)] + ['X', 'V', 'M', 'O', 'K', '#', '*', '%', '$', '@']
dim_font_matrix = 11    #dimensioni caratteri->va a definire quante colonne ci saranno
tinta_verde_cached = None   #matrice un po verde per fare effetto matrix

#cache per le vignette per evitare di rifare calcoli
_cache_w, _cache_h = 0, 0
_maschera_vignetta = None

#variabili locali specifiche per i filtri temporali e spaziali

framePrecedente = None

#per motion blur sotto simulato
kernel_motion_blur = None   #piccola matrice di numeri che indica come mixare i pixel per avere x effetto

#funzione di appoggio
def Ottieni_maschera_vignetta(w, h):
    #global pk è da modificare e non solo da leggere
    global _cache_w, _cache_h, _maschera_vignetta
    if w != _cache_w or h != _cache_h:

        #vettori che hanno valori che sono basati sulla campana di gauss,
        kernel_x = cv2.getGaussianKernel(w, w / 2)  #orizzontale larga x e con morbidezza nell appiatirsi stablita dal 2 param
        kernel_y = cv2.getGaussianKernel(h, h / 2)  #verticale alta h ecc

        #.T =trasporta=ruota striscia di numeri, in particolare modo ne ruota una concretamente così che viene
        #fuori moltiplcazioni tra verticale e orizzontale->matrice
        #dove valore max al centro e mentre si va verso gli angoli diminuisce
        mask = kernel_y * kernel_x.T

        #faccio in modo che tutti i valori siano tra 0 e 1 (1 al centro , 0 negli angoli)
        #e le salvo globalmente così da non doverle ricalcolare dopo
        #se la dimensione del frame (modificare dimensione fotocamera) non è cambiata(vedi if sopra)
        _maschera_vignetta = mask / mask.max()
        _cache_w, _cache_h = w, h
    return _maschera_vignetta


#trasforma immagine in scala di grigi
def ScalaGrigi(frame):
    return cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

#fa immagine al contrario
def Negativo(frame):
    return cv2.bitwise_not(frame)

#applica colori stile foto del 1800
def Seppia(frame):
    filtro = np.array([
        [0.272, 0.534, 0.131],  #nuovi valori per blu
        [0.349, 0.686, 0.168],  #nuovi valori per verde
        [0.393, 0.769, 0.189]  #nuovi valori per rosso
    ])
    #x esempio x fare il nuovo blu, prende un po di blu vecchio, verde vecchio,rosso vecchio
    #nuovo blu =bluvecchio*0.272+verdevecchio*0.534+rossovecchio*0.131
    return cv2.transform(frame, filtro)


#mette in risalto i pixel più chiari invertendone il colore
def Solarizzazione(frame):
    #prende i pacchetti più chiari di 128
    #prende pixel x pixel e controlla singolarmente ogni canale (rgb)
    pixel_chiari = frame >= 128

    #qua modifico canale x canale, nel filtro sotto creo una nuova matrice in automatico con comando

    #crea copia
    risultato = frame.copy()

    #poi solo nei canali rgb stabiliti sopra per ogni pixel inverte
    #solo nei pixel chiari nverte il colore (bianco->nero)
    risultato[pixel_chiari] = 255 - frame[pixel_chiari]
    return risultato

#crea mappa termica della foto
def EffettoTermicoHeatMap(frame):

    filtro = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)    #trasforma in scala di grigi

    #pixel scuri(tende a 0)->blu
    #pixel chiari(tende a 255)->rosso
    #in mezzo il verde
    return cv2.applyColorMap(filtro, cv2.COLORMAP_JET)

#specchia immagine lungo asse y
def SpecchioVerticale(frame):
    return cv2.flip(frame, 1)

#specchia immagine lungo asse x
def SpecchioOrizzontale(frame):
    return cv2.flip(frame, 0)

#specchia immagine lungo asse y e x
def SpecchioTotale(frame):
    return cv2.flip(frame, -1)

#fa effetto mosaico rendendo l'immagine un insieme di pixel
def Pixelate(frame):
    h, w = frame.shape[:2]  #altezza, larghezza

    #rimpiccolisce immagine (che era grande) in una 64*64, inter_linear serve per farlo nel modo più smooth possibile
    temp = cv2.resize(frame, (64, 64), interpolation=cv2.INTER_LINEAR)

    #e ora la riporto a grandezza normale così ho un 64*64 ma a grandezza standard
    return cv2.resize(temp, (w, h), interpolation=cv2.INTER_NEAREST)

#crea linea immaginaria a metà schermo e tutto quello a sinistra viene ribaltato nella metà a destra
def Duplica(frame):
    h, w = frame.shape[:2]  #altezza, larghezza
    meta_w = w // 2     #trova la metà

    #[:x}->da inizio fino a x   [x:]->da x fino a fine

    #prende tutte le righe ([:, ...] i 2 punti intende tutte le righe) fino a metà
    #larghezza ([:, meta_w:])e flippa immagine, così sembra che la parte da un lato (sx) sia
    #copiata e incollata capovolta dall' altro lato (dx)

    #prende la prima metà e la copia flippata nella seconda metà (dx)
    frame[:, meta_w:] = cv2.flip(frame[:, :meta_w], 1)
    return frame

#effetto cartoon con colori appiattiti e bordi in risalto
def Cartoon(frame):
    colori = frame
    for _ in range(3):
        #sfoca immagine ma mantiene i bordi precisi
        #d=diametro attorno al quale fare la media dei colori (misurato in pixel)
        #sigmacolor=cerca somiglianza tra colori->sfoca 2 pixel solo se hanno i colori non troppo diversi
        #sigmaspace=controlla "distanza" nello spazio->fino a quanto cercare pixel da sfocare->relativo a sfocatura->
        #->quanto prenderli in considerazione man mano che si va verso i bordi del quadrato d*d
        colori = cv2.bilateralFilter(colori, d=5, sigmaColor=65, sigmaSpace=65)

    #dal frame originale trasforma in scala di grigi (più rapido e veloce per trovare i bordi dopo)
    grigio = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    #correggi errori visivi o rumore che rende immagine brutta
    #ksize x forza dispari->prende matrice ksize*ksize di pixel per trovare colore medio
    grigio_blur = cv2.medianBlur(grigio, 5)

    #trova linee di contorno->immagine nera con bordi bianchi
    #i numeri params sono soglie min e max
    #< di soglia min=non è unu bordo ->nero
    #> di soglia max=bordo sicuro ->bordo bianco
    #min<x<max =è un bordo solo se vicino a un bordo sicuro (>soglia max)

    #per calcolare valore da mettere nella soglia controlla forza di salto tra 2 pixel per stabilire se sono simili o no
    bordi = cv2.Canny(grigio_blur, 50, 150)
    #inverte i colori da bianco a nero
    bordi_neri = cv2.bitwise_not(bordi)

    #riporta immagine di bordi a 3 canali bgr in modo tale da metterla insieme all'immagine filtrata a colori
    bordi_bgr = cv2.cvtColor(bordi_neri, cv2.COLOR_GRAY2BGR)

    #dove i bordi sono bianchi(255)->AND mette colore originale
    #dove i bordi sono neri(0)->AND azzera tutto e stampa il bordo nero

    #and positiva solo se entrambi sono "attivi" controlla pixel x pixel e canale x canale
    return cv2.bitwise_and(colori, bordi_bgr)

#bordi e angolo oscurati
def Vignetta(frame):
    h, w = frame.shape[:2]
    #con [..., np.newaxis] aggiungo 3 dimensione virtuale (=1) perchè la funzione mi restituisce matrice
    mask = Ottieni_maschera_vignetta(w, h)[..., np.newaxis]

    #moltiplica i pixel per la maschera (valori tra 0-1)
    #al centro immagine viene moltiplicata x1=identica
    #nei bordi x numeri vicini a 0->colori si scuriscono
    #forzandolo a stare entro 255 (astype ecc)
    return (frame * mask).astype(np.uint8)


#sfrutta lo stesso concetto della vignetta ma mandandolo in overflow
#effetto molto strano
def Crazy(frame):
    h, w = frame.shape[:2]
    mask = Ottieni_maschera_vignetta(w, h)[..., np.newaxis]
    return (frame * mask*5).astype(np.uint8)


#effeetto pioggia di caratteri su sfondo verde come in matrix
def Matrix(frame):
    global matrix_posizioni_y, tinta_verde_cached
    h, w = frame.shape[:2]
    #global non serve x dim_font_matrix perchè è solo da leggere non da modificare
    colonne = w // dim_font_matrix  #divide  larghezzza x dim carattere (11) =numero tot colonne

    #lista globale x tenere traccia altezza della pioggia matrix
    if matrix_posizioni_y is None or len(matrix_posizioni_y) != colonne:
        #se all' inizio non è valorizzata oppure il numero di colonne globali è diverso rispetto a quello calcolato->
        #->fotocamera ridimensionata, allora ripopola tutto->sennò rischio crush oltre i limiti di matrice
        # , lo fa con valori casuali tra ... x fare in modo che scenda in maniera randomica
        matrix_posizioni_y = [random.randint(-30, 0) for _ in range(colonne)]

    #stesso controllo id prima
    if tinta_verde_cached is None or tinta_verde_cached.shape != frame.shape:
        tinta_verde_cached = np.zeros_like(frame)   #la riempie di 0->nero
        #prendi tutte le righe, le colonne e il canale 1 (BGR->verde)->diventa verde
        tinta_verde_cached[:, :, 1] = 150

    #aggiunge il velo verde al mio frame, frame originale al 75% (è il peso)->leggermente trasparente
    #seconda immagine->con relativo peso
    #gamma->luminisotà aggiuntiva
    sfondo_matrix = cv2.addWeighted(frame, 0.75, tinta_verde_cached, 0.25, 0)

    for i in range(colonne):
        carattere = random.choice(matrix_caratteri) #prende un carattere random
        x = i * dim_font_matrix     #crea la coordinata sulla base delle colonne
        y = matrix_posizioni_y[i] * dim_font_matrix     #altezza della pioggia, prendendolo dalla matrice che si era salvata globalmente (ovviamente moltiplicato x fattore di scala9

        if 0 < y < h:   #se goccia visibile all' interno dello schermo (potrebbe essere sia sopra che sotto)->gocce partono da sopra
            #lo disegna di verde puro (vedi bgr), con font piccolo (0.35), e linee smussate (cv2.LineAA)
            cv2.putText(sfondo_matrix, carattere, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 255, 0), 1, cv2.LINE_AA)

            #numero random > x
            if random.random() > 0.85:
                #copre la lettera con un oclore tendente al bianco
                #disegna di biancio
                cv2.putText(sfondo_matrix, carattere, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (230, 255, 230), 1,
                            cv2.LINE_AA)

        matrix_posizioni_y[i] += 1  #aumenta posizione di quella goccia (lettera) in quella colonna

        #se goccia arrivata alla fine oppure piccola prob faccio ripartire da capo
        if y > h or random.random() > 0.95:
            matrix_posizioni_y[i] = random.randint(-10, 0)

    return sfondo_matrix


#effeto televisione rotta anni 1950, con interferenze ecc
def Glitch(frame):

    #composto da diversi effetti indipendenti ma uniti
    h, w = frame.shape[:2]
    shift = 12
    frame_glitch = frame.copy()

    #effetto duplicato/sdoppiato

    #prende il rosso, e li fa scivolare tutti a sinistra di 12 pixel (se escono a sinistra rientrano dal bordo di destra)
    #axis=1 spostamento orizzontale
    frame_glitch[:, :, 2] = np.roll(frame[:, :, 2], -shift, axis=1)
    #idem per blu
    frame_glitch[:, :, 0] = np.roll(frame[:, :, 0], shift, axis=1)


    #righe stile vecchi schermi

    #idea random di farle ogni tanto (stabilito dai numeri sotto)
    #parti da riga 0, arriva fino ad h, e prendi righe ogni 4 righe (0,4,8 ec) e moltiplica x0.6->rende tutto più scuro
    frame_glitch[0:h:4, :, :] = (frame_glitch[0:h:4, :, :] * 0.6).astype(np.uint8)
    #fa lo stesso per riga 1,5,9 ecc
    frame_glitch[1:h:4, :, :] = (frame_glitch[1:h:4, :, :] * 0.6).astype(np.uint8)


    #effetto interferenza
    #randomico
    if random.random() > 0.85:
        #prende riga orizzontale a caso
        y_inizio = random.randint(0, h - 30)
        #prende spessore a caso
        spessore = random.randint(10, 30)
        #prende direzione a caso (di quanti pixel e in che direzione)
        direzione = random.randint(-25, 25)

        #prende in quella strisci più lo spessore, spigengolo a destra/sinistra di un toto
        #(prendi le righe da x a x+spessore, tutte le colonne e tutti i canali)
        frame_glitch[y_inizio:y_inizio + spessore, :, :] = np.roll(
            frame_glitch[y_inizio:y_inizio + spessore, :, :], direzione, axis=1
        )

    return frame_glitch

#disegno bianco su sfondo nero
def EffettoLavagna(frame):
    #scala di grigi
    grigio = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    #pulisce da imperfezioni sfocando immagine con pennello 5x5
    sfocato = cv2.GaussianBlur(grigio, (5, 5), 0)

    #canny si basa su sbalzo di luminosità tra pixel
    #imposta soglie
    #<30 colorato di nero
    #>100 ->sbalzo elevato->colorato di biano
    #tra 30 e 100 accetta solo se vicino a bordo forte
    bordi = cv2.Canny(sfocato, 30, 100)
    #canny da matrice di pixel bianchi su pixel neri (risultato già pronto)

    return cv2.cvtColor(bordi, cv2.COLOR_GRAY2BGR)  #riconverte in rgb

#rileva qualsiasi movimento (ovviamente sopra una certa soglia per evitare di prendere in considerazionei il rumore)
def RilevamentoMovimento(frame):
    global framePrecedente
    grigio = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)    #metto in scala di grigi
    grigio = cv2.GaussianBlur(grigio, (21, 21), 0)  #sfoco per evitare di prendere dettagli troppo piccoli (singoli capelli)

    #stessi controlli di sopra (al primo frame x esempio) o se cambio dimensione (crasherebbe in differenza assoluta tra matrici)
    if framePrecedente is None or framePrecedente.shape != grigio.shape:
        framePrecedente = grigio
        return frame

    #calcola differenza (immobile->differenza=0->nero)
    diff_frame = cv2.absdiff(framePrecedente, grigio)

    #controlla se c'è differenza minima (sotto tresh(25)) per esempio rumore->pixel diventa nero=0 (zero di default), altrimenti bianco=255
    #[1] è perchè da 2 output però prendo solo immagine modificata
    thresh_frame = cv2.threshold(diff_frame, 25, 255, cv2.THRESH_BINARY)[1]
    #movimento->bianco fermo ->nero



    #espande per 2 volte (iterazioni) i punti bianchi (di default il bianco 255 vale di più del nero)
    #a tutti i pixel vicini per coprire area che

    #più complessivamente si è mossa in totale
    thresh_frame = cv2.dilate(thresh_frame, None, iterations=2)

    maschera_colore = cv2.cvtColor(thresh_frame, cv2.COLOR_GRAY2BGR)    #riconverte a rgb
    #ma comunque immagine resta in bianco e nero(dal punto di vista del codice però è a colori)

    #per ogni pixel:
    #nero e rosso->0=nero
    #bianco e rosso->rosso (0,0,255)
    zona_rossa = cv2.bitwise_and(maschera_colore, (0, 0, 255))  #immagine nera con zone rosse che indicano movimento

    #sfondo nero divante bianco; sagoma bianca diventa nera
    maschera_inversa = cv2.bitwise_not(maschera_colore)
    #movimento->bianco fermo ->nero

    #sulle parti in movimento c'è parte nera
    sfondo_pulito = cv2.bitwise_and(frame, maschera_inversa)

    #unisce la parte in movimento nera con la parte in movimento rossa
    frame_output = cv2.add(sfondo_pulito, zona_rossa)

    framePrecedente = grigio    #per controllare se ci sono stati movimenti
    return frame_output

#crea un effetto scia grazie alla sovapposizione del frame precedente
def Ghost(frame):
    global framePrecedente
    if framePrecedente is None or framePrecedente.shape != frame.shape:
        framePrecedente = frame.copy()
        return frame

    #frame attuale pesa il 20% mentre quello precedente 80%, dst=... -> il risultato della fusione va a sovrascrivere
    #il ormai veccho framePrecedente
    cv2.addWeighted(frame, 0.20, framePrecedente, 0.80, 0, dst=framePrecedente)
    return framePrecedente

#motion blur in diagonale quindi effetto movimento e sfocato
def MotionBlurSimulato(frame, dimensione_kernel=15):
    global kernel_motion_blur

    if kernel_motion_blur is None:

        #matrice di tutti 0 tranne la diagonale y=-x valorizzata a 1
        kernel_motion_blur = np.eye(dimensione_kernel)

        #divide tutta la matrice per 15 per fare in modo che la somma totale faccia 1 e non n>1 (nel mio caso moltiplicato x15)
        kernel_motion_blur = kernel_motion_blur / dimensione_kernel

    #applica matrice ad immagine
    #-1 per manetenere la stessa profondità di colore ->rimane invariata
    #prende riga 15x15 e la fa scorrere sopra ogni singolo pixel
    #in particolare confronta la tabella 15x15 con un determinato pixel messo al centro e tutti quelli che gli stanno attorno
    #e dopo fa opereazioni sulla matrice
    return cv2.filter2D(frame, -1, kernel_motion_blur)