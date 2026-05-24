import cv2

#dizionario tasto->filtro
TUTTI_FILTRI = [
    ('0', 'Normale'), ('1', 'Grigio'), ('2', 'Negativo'), ('3', 'Seppia'), ('4', 'Termico'),
    ('5', 'Solarizza'), ('6', 'Cartoon'), ('7', 'Lavagna'), ('8', 'Pixel'), ('9', 'Matrix'),
    ('A', 'Specchio O'), ('B', 'Specchio V'), ('C', 'Specchio T'), ('D', 'Duplica'),
    ('E', 'Crazy'), ('F', 'Glitch'), ('G', 'Movimento'), ('H', 'Ghost'), ('N', 'Blur Mosso'),
    ('J', 'Occhiali'), ('K', 'Cappello'), ('L', 'Barba'), ('M', 'Vignetta'),
    ('Z', 'Gioco')
]

filtri_per_pagina = 5
tot_pagine = (len(TUTTI_FILTRI) + filtri_per_pagina - 1) // filtri_per_pagina  # trova il numero totale di pagine arrotondato per eccesso
font = cv2.FONT_HERSHEY_SIMPLEX

#funzione x disegnare graficamente
def DisegnaHUD(frame, filtro_corrente, n_facce, fps, in_registrazione, pagina_attuale, sfocatura, modalita_automatica,
     durata_filtro=3.0):
    h, w = frame.shape[:2]      #altezza, larghezza

    #logica delle pagine
    inizio = pagina_attuale * filtri_per_pagina     #trova indice dei filtri di quella pagina da visualizzare
    fine = inizio + filtri_per_pagina                   #trova ultimo di quei filtri
    filtri_da_mostrare = TUTTI_FILTRI[inizio:fine]  #li seleziona

    #barra filtri in basso
    #parte da bordo a sinistra (0 e alza di 65 pixel) fino agli estremi (w,h), grigio molto scuro e riempito
    cv2.rectangle(frame, (0, h - 65), (w, h), (20, 20, 20), -1)
    #traccia linea verde per effetto graifco
    cv2.line(frame, (0, h - 65), (w, h - 65), (0, 255, 0), 1)

    #informazioni relative a quella pagina
    testo_pag = f"PAG {pagina_attuale + 1}/{tot_pagine}"    #parte da 0 a contare

    cv2.putText(frame, testo_pag, (15, h - 40), font, 0.35, (0, 255, 0), 1)
    cv2.putText(frame, "[ < ]  [ > ]", (12, h - 15), font, 0.35, (150, 150, 150), 1)

    #disegno i filtri della pagina attuale
    spazio = (w - 120) // filtri_per_pagina     #toglie lo spazio dedicato a sx per "PAG X/Y) e le ><" e lo divide per trovare i pixel dedicati ad ogni filtro

    #per i da 0 a 4
    for i, (tasto, nome) in enumerate(filtri_da_mostrare):
        x_pos = 120 + (i * spazio)  #trova le coordinate di ognuno (120, 120+spazio, 120+2*spazio ecc)

        #se quello che sta disegnando è anche quello attivo
        attivo = nome.lower() == filtro_corrente.lower()
        if attivo:
            colore = (0, 255, 0)  #verde
            spessore=2
        else:
            colore = (180, 180, 180)  #grigio chiaro
            spessore=1

        #scrive il tasto da premere
        cv2.putText(frame, f"[{tasto}]", (x_pos, h - 40), font, 0.4, (0, 255, 255), 1)
        #scrive il nome del filtro
        cv2.putText(frame, nome, (x_pos, h - 15),font, 0.45, colore, spessore)

    #statistiche del box in alto a destra (fps, facce ecc)

    #rettangolo nero riempito
    cv2.rectangle(frame, (w - 190, 10), (w - 10, 130), (0, 0, 0), -1)
    #linea verde
    cv2.rectangle(frame, (w - 190, 10), (w - 10, 130), (0, 255, 0), 1)


    #mostra sempre il filtro attivo (sia in manuale che in automatico)

    #stampa filtro attivo in azzurro
    cv2.putText(frame, f"FILTRO: {filtro_corrente.upper()}", (w - 180, 32), font, 0.38, (0, 255, 255), 1)
    #e il numero di facce in bianco
    cv2.putText(frame, f"FACCE: {n_facce}", (w - 180, 53), font, 0.38, (255, 255, 255), 1)


    if fps > 20:
        col_fps = (0, 255, 0)  #verde se fluido
    else:
        col_fps = (0, 0, 255)  #rosso se sta x crashare

    cv2.putText(frame, f"FPS: {int(fps)}", (w - 180, 74), font, 0.38, col_fps, 1)

    #indicatore grafico sfocatura
    if sfocatura:
        testo_sfocatura = "SFOCATURA [Y]: ON"
        colore_sfocatura = (0, 255, 0)  #verde
    else:
        testo_sfocatura = "SFOCATURA [Y]: OFF"
        colore_sfocatura = (0, 0, 255)  #rosso

    cv2.putText(frame, testo_sfocatura, (w - 180, 97), font, 0.38, colore_sfocatura, 1, cv2.LINE_AA)

    # indicatore grafico modalità automatica
    if modalita_automatica:
        testo_auto = f"AUTO MODE [X]: ON ({int(durata_filtro)}s)"
        colore_auto = (0, 255, 0)  #verde
    else:
        testo_auto = f"AUTO MODE [X]: OFF ({int(durata_filtro)}s)"
        colore_auto = (0, 0, 255)  #rosso

    cv2.putText(frame, testo_auto, (w - 180, 118), font, 0.38, colore_auto, 1, cv2.LINE_AA)

#disegna indicatore grafico in fase di registrazione
def DisegnaRec(frame):
    cv2.circle(frame, (25, 25), 8, (0, 0, 255), -1)
    cv2.putText(frame, "REC", (42, 32), font, 0.6, (0, 0, 255), 2)

#idem x per lo screen
def DisegnaFeedbackScreenshot(frame):
    h, w = frame.shape[:2]
    #rettangolo che copre tutto lo schermo però con linea grande 15->copre solo i bordi quindi
    cv2.rectangle(frame, (0, 0), (w, h), (255, 255, 255), 15)

    testo = "SCREENSHOT SALVATO!"
    #stabilisce che ba stampato con x font e x spessore, e x con grandezza
    (t_w, t_h), _ = cv2.getTextSize(testo, font, 0.5, 2)

    #trova centro per stampare il testo in verde
    cv2.putText(frame, testo, (int((w - t_w) / 2), 50), font, 0.5, (0, 255, 0), 2)


def EtichettaPersonalizzata(frame, facce_rilevate, nome_base="PERSONA_"):

    #i parte da 0, quindi aggiungiamo 1 per avere PERSONA_01, PERSONA_02, ecc.
    for i, (x, y, w, h) in enumerate(facce_rilevate):
        testo = f"{nome_base}{i + 1:02d}"   #      :02d formatta il numero a due cifre (01, 02...)
        pos_testo = (x + 5, y - 12) #sposta leggermente a destra e in alto

        #ombra nera per effetto
        cv2.putText(frame, testo, pos_testo, font, 0.5, (0, 0, 0), 3, cv2.LINE_AA)
        #testo
        cv2.putText(frame, testo, pos_testo, font, 0.5, (0, 255, 0), 1, cv2.LINE_AA)

    return frame