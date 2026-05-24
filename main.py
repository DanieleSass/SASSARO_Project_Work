import cv2
import datetime #per gestire salvataggio foto e video
import time #gestisce tipo fps ecc
import effects  #altri file
import filters
import ui
import os


def main():

    cattura = cv2.VideoCapture(0)
    cv2.namedWindow("Webcam", cv2.WINDOW_NORMAL)    #finestra "flessibile"

    #valor iniziali di default
    filtroAttuale = "normale"   #memorizza il filtro tra diversi frame
    sfocatura = False   #attivabile con Y

    in_registrazione = False
    video_writer = None
    timer_feedback_screen = 0   #contatore di fotogrammi-indicatore per stabilire tempo tra uno screen e l' altro

    #gestione scorrimento pagine dei filtri
    pagina_attuale = 0
    filtri_per_pagina = 5

    #serve per fare in modo che anche quando c'è un solo filtro in più faccia len(..)+4 in modo tale da creare pagina in più
    #è più "efficiente" rispetto a lavorare con virgole ed altre operazioni per arrotondare x eccesso
    max_pagine = (len(ui.TUTTI_FILTRI) + filtri_per_pagina - 1) // filtri_per_pagina    #formula x calcolare tutte le pagine

    MAPPA_TASTI = {
        ord('0'): "normale",
        ord('1'): "grigio",
        ord('2'): "negativo",
        ord('3'): "seppia",
        ord('4'): "termico",
        ord('5'): "solarizza",
        ord('6'): "cartoon",
        ord('7'): "lavagna",
        ord('8'): "pixel",
        ord('9'): "matrix",

        #specchi e cose simili
        ord('a'): "specchio o", ord('A'): "specchio o",
        ord('b'): "specchio v", ord('B'): "specchio v",
        ord('c'): "specchio t", ord('C'): "specchio t",
        ord('d'): "duplica", ord('D'): "duplica",

        #effetti relativi a distorsioni o cose che corrompono tutto
        ord('e'): "crazy", ord('E'): "crazy",
        ord('f'): "glitch", ord('F'): "glitch",
        ord('g'): "movimento", ord('G'): "movimento",
        ord('h'): "ghost", ord('H'): "ghost",
        ord('n'): "blur mosso", ord('N'): "blur mosso",

        #effetti x cui serve riconoscimento facciale/oculare
        ord('j'): "occhiali", ord('J'): "occhiali",
        ord('k'): "cappello", ord('K'): "cappello",
        ord('l'): "barba", ord('L'): "barba",

        #random
        ord('m'): "vignetta", ord('M'): "vignetta",

        #specie di minigioco
        ord('z'): "gioco", ord('Z'): "gioco"
    }

    #modalità di autoscorrimento
    modalita_automatica = False
    ultimo_cambio_tempo = time.time()   #inizializzazione all'inizio serve se attivo mod automatica , salva orario attuale per capire quando passano i 3 ss
    intervallo_cambio = 3.0  #ogni quanti secondi cambia un filtro in modalità automatica

    #faccio lista prendendo lista da ui.py
    #escludo "gioco" seguendo ordine visivo dei filtri della barra grafica
    lista_filtri_auto = [
        nome_filtro.lower()
        for _, nome_filtro in ui.TUTTI_FILTRI       #li mette tutti in minuscol tranne gioco
            if nome_filtro.lower() not in ["gioco"]
    ]
    indice_filtro_auto = 0  #partirà dal primo

    while True:
        start_time = time.time()    #serve per calcolare fps
        ret, frame = cattura.read()
        if not ret: #se operazione di leettura non riuscita allora esci
            break

        frame = cv2.flip(frame, 1)  #lo inverte rispetto asse y

        #rilevamento facce che poi mostra in alto a destra
        grigio = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)    #trasforma in scala di grigi->algoritmi più efficienti

        #con scala di riduzione dell' immagine a 1.3, fa tante immagini ogni volta ridotte del 30% per trovare volti anche molto grandi (vicini alla fotocamera)
        #5->accetta la faccia solo se ci sono almeno 5 rettangoli di rilevamento sovrapposti
        facce_rilevate = effects.riconoscimentoFaccia.detectMultiScale(grigio, 1.3, 5)
        n_facce = len(facce_rilevate)

        #prende il tasto di input e prende solo l'ultima parte per essere compatibile con diversi OS ecc
        #prende solo ultimi 8 bit, in modo tale da renderlo compatibile con tutti i sistemi
        tasto = cv2.waitKey(1) & 0xFF

        if tasto == ord('q') or tasto == ord('Q'):
            break

        #scorre le pagine dei filtri
        #pagina sinistra
        if tasto == ord('<'):
            pagina_attuale = (pagina_attuale - 1) % max_pagine  #se era alla 0 e torna indietro, allora va all'ultima -1%max_pagine=ultima pagina
        #pagina destra
        elif tasto == ord('>'):
            pagina_attuale = (pagina_attuale + 1) % max_pagine  #se eri all' ultima e vai avanti allora torni alla prima (numero 0)

        if tasto == ord('y') or tasto == ord('Y'):  #mette la sfuocatura o la toglie
            sfocatura = not sfocatura

        if tasto == ord('x') or tasto == ord('X'):  #attiva la modalita automatica o la toglie
            modalita_automatica = not modalita_automatica
            if modalita_automatica:
                ultimo_cambio_tempo = time.time()   #salva il tempo corrente perchè da qua in poi inizierà a contare i 3s

                #se premiamo X e stavamo visualizzando manualmente un filtro valido
                #l'indice si allinea e il ciclo automatico partirà sa quel filtro in poi
                if filtroAttuale in lista_filtri_auto:  #quindi tutti tranne il gioco (ma messo così è più scalabilre rispetto a controllare solo !="gioco")
                    indice_filtro_auto = lista_filtri_auto.index(filtroAttuale) #trova indice del filtro attuale così da ripartire da quello subito dopo e non dallo 0 ogni volta
                else:
                    indice_filtro_auto = -1     #se avevo selezionato "gioco"->dopo ripartirà da 0


        #controlla solo se è ora di cambiare filtro
        if modalita_automatica:
            tempo_corrente = time.time()    #prende il tempo
            if tempo_corrente - ultimo_cambio_tempo >= intervallo_cambio:   #controlla se è >=3secondi  ->eventualmente cambia filtro

                indice_filtro_auto = (indice_filtro_auto + 1) % len(lista_filtri_auto)  #scorrimento ciclico col %
                #rispetto a qualche riga sopra quando indice_ecc=-1 in questo caso verrebbe messo a 0, e quindi partirebbe dallo 0

                filtroAttuale = lista_filtri_auto[indice_filtro_auto]   #aggiorna il filtro attuale
                ultimo_cambio_tempo = tempo_corrente    #e salva ultimo timestamp


        #mod automatica già attivo a io cerco di cambiare filtro manualmente
        #cambio filtro manualmente
        if tasto in MAPPA_TASTI:    #controlla se esiste come chiave nel dizionario
            filtroAttuale = MAPPA_TASTI[tasto]  #prende il valore associato alla chiave

            #se cambio filtro manualmente mentre mod automatica è attiva
            #trova posizione del nuovo filtro nella lista automatica
            if filtroAttuale in lista_filtri_auto:  #controlla sostanzialmente se non è gioco
                indice_filtro_auto = lista_filtri_auto.index(filtroAttuale) #prende il corrispettivo indice
            else:
                indice_filtro_auto = -1  #se metto gioco allora diventa -1
            ultimo_cambio_tempo = time.time()   #reseetto il timer così da vedere il filtro x 3 secondi

        #applico il filtro
        if filtroAttuale == "gioco":
            frame = effects.GiocoNaso(frame)
        elif filtroAttuale == "grigio":
            frame = cv2.cvtColor(filters.ScalaGrigi(frame), cv2.COLOR_GRAY2BGR)
        elif filtroAttuale == "negativo":
            frame = filters.Negativo(frame)
        elif filtroAttuale == "seppia":
            frame = filters.Seppia(frame)
        elif filtroAttuale == "termico":
            frame = filters.EffettoTermicoHeatMap(frame)
        elif filtroAttuale == "pixel":
            frame = filters.Pixelate(frame)
        elif filtroAttuale == "cartoon":
            frame = filters.Cartoon(frame)
        elif filtroAttuale == "crazy":
            frame = filters.Crazy(frame)
        elif filtroAttuale == "vignetta":
            frame = filters.Vignetta(frame)
        elif filtroAttuale == "solarizza":
            frame = filters.Solarizzazione(frame)
        elif filtroAttuale == "duplica":
            frame = filters.Duplica(frame)
        elif filtroAttuale == "ghost":
            frame = filters.Ghost(frame)
        elif filtroAttuale == "blur mosso":
            frame = filters.MotionBlurSimulato(frame)
        elif filtroAttuale == "specchio v":
            frame = filters.SpecchioVerticale(frame)
        elif filtroAttuale == "specchio o":
            frame = filters.SpecchioOrizzontale(frame)
        elif filtroAttuale == "specchio t":
            frame = filters.SpecchioTotale(frame)
        elif filtroAttuale == "movimento":
            frame = filters.RilevamentoMovimento(frame)
        elif filtroAttuale == "matrix":
            frame = filters.Matrix(frame)
        elif filtroAttuale == "glitch":
            frame = filters.Glitch(frame)
        elif filtroAttuale == "lavagna":
            frame = filters.EffettoLavagna(frame)
        elif filtroAttuale == "barba":
            frame = effects.Barba(frame, facce_rilevate)
        elif filtroAttuale == "cappello":
            frame = effects.Cappello(frame, facce_rilevate)
        elif filtroAttuale == "occhiali":
            frame = effects.Occhiali(frame, facce_rilevate)

        #sfondo sfuocato, facce no
        if sfocatura:
            frame = effects.MotionBlur(frame, facce_rilevate)

        #disegna etichette sopra le facce se presenti
        if n_facce > 0:
            frame = ui.EtichettaPersonalizzata(frame, facce_rilevate)

        #screen dopo applicazione del filtro
        if tasto == ord('s') or tasto == ord('S'):
            cartella_output="outputImages"
            #se la cartella non esiste la crea
            if not os.path.exists(cartella_output):
                os.makedirs(cartella_output)
            nome = f"outputImages/IMG_{datetime.datetime.now().strftime('%H%M%S')}.jpg"
            cv2.imwrite(nome, frame)
            timer_feedback_screen = 15  #mostra avviso che immagine è stata scattata

        #idem x screen
        if tasto == ord('r') or tasto == ord('R'):
            cartella_video_output="outputVideos"

            #se cartella non esiste crea
            if not os.path.exists(cartella_video_output):
                os.makedirs(cartella_video_output)

            if not in_registrazione:    #vuol dire che non stavo registrando e quindi voglio iniziare la registrazione
                nome = f"outputVideos/VID_{datetime.datetime.now().strftime('%H%M%S')}.mp4"
                fourcc = cv2.VideoWriter_fourcc(*'mp4v')    #parametro serve per renderlo più leggere e comprimerlo

                #inizializza il videowriter=20=numero di fps; frame.shape[1]ecc sono le dimensioni del frame da passare obbligatoriamente al metodo
                video_writer = cv2.VideoWriter(nome, fourcc, 20.0, (frame.shape[1], frame.shape[0]))
                in_registrazione = True #segna che il video è partito
            else:   #vuole fermare il video

                #smette di scrivere nel video   e lo salva
                video_writer.release()
                video_writer = None #lo annulla per efficienza e controlli più sicuri sotto
                in_registrazione = False    #e resetta stato di registrazione

        # Rendering video registrato
        if in_registrazione and video_writer:
            video_writer.write(frame)   #scrive effettivamente dentro al video il frame attuale

        fps = 1.0 / (time.time() - start_time)  #calcola il tempo che ci ha messo x fare tutto questo
        ui.DisegnaHUD(frame, filtroAttuale, n_facce, fps, in_registrazione, pagina_attuale, sfocatura, modalita_automatica, intervallo_cambio)

        if in_registrazione:
            ui.DisegnaRec(frame)    #disegno indicatore video

        if timer_feedback_screen > 0:   #indicatore grafico dello screen
            ui.DisegnaFeedbackScreenshot(frame) #mostra notifica screen
            timer_feedback_screen -= 1  #diminusce ad ogni ciclo

        cv2.imshow("Webcam", frame) #mostra la videocamera con il frame modificatao

    cattura.release()   #spegne cam e rilascia risorse
    if video_writer:
        video_writer.release()  #se si stava registrando e si chiude tutto allora interrompe e salva il video
    cv2.destroyAllWindows() #chiude le finestre grafiche


if __name__ == '__main__':
    main()