import cv2
import numpy as np
import random

#caricamento immagini una sola volta
barba = cv2.imread("assets/barba.png", cv2.IMREAD_UNCHANGED)
cappello = cv2.imread("assets/cappello3.png", cv2.IMREAD_UNCHANGED)
occhiali = cv2.imread("assets/occhiali.png", cv2.IMREAD_UNCHANGED)

#stati globali per tracciamento, scia video e logica di gioco
riconoscimentoFaccia = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
riconoscimentoOcchi = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')

#cose relative al gioco
gioco_punteggio = 0
gioco_palla_x = 320
gioco_palla_y = 0
gioco_palla_velocita = 6



#funzione di appoggio per barba, cappello e occhali

#parametri sono coordinate e grandezza dell' immagine da sovrappore
def ApplicaEffetto(frame, img, x, y, larghezza, altezza):
    if img is None:     #immagine non presente/corrotta
        return frame

    h_f, w_f = frame.shape[:2]

    #o se va anche leggermente oltre i bordi esce
    if y < 0 or x < 0 or y + altezza > h_f or x + larghezza > w_f:
        return frame

    #le ridimensiona in base alla faccia
    piccola = cv2.resize(img, (larghezza, altezza))

    if piccola.shape[2] == 4:  #controlla se ha 4 canali (r,g,b, e trasparenza(alpha)
        colori_asset = piccola[:, :, :3]    #prende i 3 canali rgb

        #prende il 4 canale e lo normalizza->valori tra 0 e 1
        #np... serve per renderla tridimensionale (mantiene costante tutto quello prima e aggiunge un nuovo asse)
        mask = (piccola[:, :, 3] / 255.0)[..., np.newaxis]

        #parte della faccia/fronte/occhi ecc
        zona_interessata = frame[y:y + altezza, x:x + larghezza]

        #formula matematica della media ponderata, dopo valorizza tutto tra 0 255
        #pixel opac (parte della immagine non trasparente)->rimane quello ->quindi mette immagine
        #pixel trasparente->parte della mia faccia
        frame[y:y + altezza, x:x + larghezza] = (mask * colori_asset + (1.0 - mask) * zona_interessata).astype(np.uint8)
    else:
        frame[y:y + altezza, x:x + larghezza] = piccola[:, :, :3]

    return frame


#mette cappello sopra le teste rilevate
def Cappello(frame, facce_rilevate):
    if cappello is None:
        return frame
    for (x, y, w, h) in facce_rilevate:     #calcola altezza, larghezza, e posizioni immagini e lo mette nel frame
        w_cap = int(w * 1.4)    #larghezza
        h_cap = int(h * 0.85)   #altezza
        x_cap = x - (w_cap - w) // 2        #cappello centrato, calcola la parte in eccesso, divide in 2 per farlo simmetrico, e lo sposta leggermente verso sinistra, così da renderlo centrato
        y_cap = y - h_cap + int(h * 0.10)   #dal bordo superiore della faccia va in su dell' altezza del cappello e poi scente leggermente
        frame = ApplicaEffetto(frame, cappello, x_cap, y_cap, w_cap, h_cap)
    return frame


#mette barba nei menti rilevati
def Barba(frame, facce_rilevate):
    if barba is None:
        return frame
    for (x, y, w, h) in facce_rilevate:
        w_barba = int(w * 1.05)
        h_barba = int(h * 0.65)
        x_barba = x - (w_barba - w) // 2    #idem
        y_barba = y + (h // 2)      #in particolare parte da metà faccia in giu
        frame = ApplicaEffetto(frame, barba, x_barba, y_barba, w_barba, h_barba)
    return frame

#mette occhiali negli occhi rilevati
def Occhiali(frame, facce_rilevate):
    if occhiali is None:
        return frame
    proporzione = occhiali.shape[0] / occhiali.shape[1]     #altezza/larghezza
    grigio = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)    #mettei in bianco e nero

    for (x, y, w, h) in facce_rilevate:
        #roi=region of interest, prende solo la parte che sicuramente comprende gli occhi->no falsi positivi e più veloce piuttosto di guardare intero frame
        roi_grigio = grigio[y:y + int(h * 0.6), x:x + w]

        #ogni volta riduce immagine di 15%
        #almeno 4 rettangoli si devono sovrapporre per validare gli occhi
        #dimensione minima x evitare di scambiare punti per occhi
        occhi = riconoscimentoOcchi.detectMultiScale(roi_grigio, 1.15, 4, minSize=(30, 30))

        if len(occhi) >= 2: #se ha trovato occhi

            #riordinati da sx a dx,
            #lambda ecc,: si basa su coordinata 0=X quindi il primo sarà quello con la x più a bass, quindi quello a sx
            occhi = sorted(occhi, key=lambda o: o[0])

            x1, y1, w1, h1 = occhi[0]   #occhio a destra
            x2, y2, w2, h2 = occhi[-1] #occhio più a sinistra di tutti

            #trova centro centro del primo occhio, quello del secondo occhio, fa la media normalizzando e lo somma alla coordinata della faccia
            centro_occhi_x = x + (x1 + w1 // 2 + x2 + w2 // 2) // 2
            centro_occhi_y = y + (y1 + h1 // 2 + y2 + h2 // 2) // 2 #idem per la y

            #calcola quanti pixel di distanza ci sono tra il centro dell'occhio dx e il centro dell'occhio sx
            distanza_occhi = (x2 + w2 // 2) - (x1 + w1 // 2)
            w_occ = int(distanza_occhi * 2.1)   #moltiplica larghezza di occhiali x renderli + lunghi
            h_occ = int(w_occ * proporzione)    #moltuiplica x il fattore moltiplicativo standard così da non distorcere immagine

            #sposta il punto di inizio dell immagine in su a sinistra in modo tale da centrarlo
            #prende centro degli  occhi e torna indietro verso sinistra di metà larghezza degli occhiali
            x_occ = centro_occhi_x - (w_occ // 2)
            y_occ = centro_occhi_y - (h_occ // 2)

            frame = ApplicaEffetto(frame, occhiali, x_occ, y_occ, w_occ, h_occ)
        else:   #non trova almeno 2 occhi
            #fa una stima sulla base della proporzioni umane, con relative formule per provare a stimare posizione degli occhiali
            w_occ = int(w * 0.95)
            h_occ = int(w_occ * proporzione)
            x_occ = x + (w - w_occ) // 2
            y_occ = y + int(h * 0.4) - (h_occ // 2)
            frame = ApplicaEffetto(frame, occhiali, x_occ, y_occ, w_occ, h_occ)

    return frame


#sfoca tutto tranne le facce
def MotionBlur(frame, facce_rilevate):
    #sfoca tutto
    frame_sfocato = cv2.GaussianBlur(frame, (45, 45), 0)
    if len(facce_rilevate) == 0:    #risparmio di potenza e calcoli
        return frame_sfocato

    maschera = np.zeros(frame.shape, dtype=np.uint8)    #matrice di tutti 0

    #controlla se l'img ha solo 2 dimensioni (altezza, larghezza)->sarebbe in scala di grigi
    #shape=altezza,larghezza dell img, (numero di canali: 1/3/4 di solito-> bianco-nero /a colori /trasparenza)
    if len(frame.shape) == 2:
        colore_ellisse = 255  #singolo numero x bianco puto
    else:
        colore_ellisse = (255, 255, 255)  #rgb x bianco puro

    for (x, y, w, h) in facce_rilevate:
        centro = (x + w // 2, y + h // 2)   #centro della faccia
        assi = (int(w * 0.65), int(h * 0.8))    #assi dell' ellisse che contiene la faccia non sfocata, moltiplico perchè sennàò sarebbe troppo piccolo

        #sulla maschera nero, a partire dal centro dell' ellisse entro gli assi,0=angolo di rotazione dell'ellis=non rutotato
        #altro 0=disegna a partire da estremo sull' asse x fino a fare un giro di 360 gradi->disegnalo tutto
        #lo disegna di biano puto, con -1 riempio la figura e non faccio solo i bordi
        cv2.ellipse(maschera, centro, assi, 0, 0, 360, colore_ellisse, -1)

    #bianco resta bianco, nero resta nero, ma il confine tra bianco e nero si sfuma
    maschera_sfumata = cv2.GaussianBlur(maschera, (51, 51), 0)

    #la normalizzo e la metto tra 0 e 1
    maschera_norm = maschera_sfumata / 255.0

    #unisce il frame nitidi, quello sfocato
    #sulla faccia (prima parte->frame*maschera_...=frame*1)->resta faccia nitida
    #frame_sfocato+(1-...)=frame_sfocato(1-1)=frame_s*0=0->cancella il video sfocato
    #combinate fa 100%+0%->faccia nitida

    #sullo sfondo prima parte->frame*0=cancella parte nitida
    #frame_s*(1-0)=frame_s*1=->video sfocato
    #combinate=sfondo sfocato

    #idem x parti sfocate prima con gaussianblur
    #riconverte poi in rgb con valori 0-255
    return (frame * maschera_norm + frame_sfocato * (1.0 - maschera_norm)).astype(np.uint8)


#bisogna prendere una pallina che cade, il mirino è il proprio naso, il gioco aumenta di difficoltà
#perchè la pallina diventa sempre più veloce
def GiocoNaso(frame):
    global gioco_punteggio, gioco_palla_x, gioco_palla_y, gioco_palla_velocita
    h_f, w_f = frame.shape[:2]  #altezza e larghezza del frame
    raggio_palla = 20
    raggio_naso = 12

    grigio = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)    #converte in grigio e cerca la faccia
    volti = riconoscimentoFaccia.detectMultiScale(grigio, scaleFactor=1.3, minNeighbors=5, minSize=(100, 100))

    if len(volti) > 0:
        (x, y, w, h) = volti[0] #cerca, attraverso formule, di trovare il naso
        naso_x = x + (w // 2)
        naso_y = y + int(h * 0.55)

        #cerchio rosso pieno grande 12 pixel
        cv2.circle(frame, (naso_x, naso_y), raggio_naso, (0, 0, 255), -1)
        #cerchio bianco vuoto largo 16 pixel =circa effetto mirino
        cv2.circle(frame, (naso_x, naso_y), raggio_naso + 4, (255, 255, 255), 2)


        #uso teorema di pitagora applicato ai cerchio
        #calcola distanza^2 tra naso e palla->non fa radice, piuttosto controlla tutto ^2 (vedi if sotto)
        dist_quadrata = (naso_x - gioco_palla_x) ** 2 + (naso_y - gioco_palla_y) ** 2

        #se la distanza è<somma dei raggi->cerchi si intersecano-> collisione
        if dist_quadrata < (raggio_palla + raggio_naso) ** 2:
            gioco_punteggio += 1    #aumenta puntaggio
            gioco_palla_x = random.randint(50, w_f - 50)    #spawna una nuova palla
            gioco_palla_y = 0   #a partre da bordo in alto
            gioco_palla_velocita += 1   #aumenta la velocita

    gioco_palla_y += gioco_palla_velocita   #fa scendere la palla della propria velocita

    if gioco_palla_y > h_f:     #se arriva al bordo sotto del video
        gioco_palla_x = random.randint(50, w_f - 50)    #rigenera la palla come sopra
        gioco_palla_y = 0
        gioco_palla_velocita = max(6, gioco_palla_velocita - 1) #velocità almeno 6 sennò troppo lento

    #disegna palla di colore giallo e riempita
    cv2.circle(frame, (gioco_palla_x, gioco_palla_y), raggio_palla, (0, 255, 255), -1)
    #con bordo nero
    cv2.circle(frame, (gioco_palla_x, gioco_palla_y), raggio_palla, (0, 0, 0), 2)

    #sfondo per leggere il punteggio di colore nero e riempito
    cv2.rectangle(frame, (10, 10), (220, 55), (0, 0, 0), -1)
    #scrive il punteggio con coordinate 20,42, font=0.9, scritto in verde, con lettere smooth e non righe "seghettate"
    cv2.putText(frame, f"SCORE: {gioco_punteggio}", (20, 42), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2,
                cv2.LINE_AA)

    return frame