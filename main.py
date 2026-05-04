import cv2
import datetime

from filters import ScalaGrigi, Negativo


def main():
    #con q esce
    #con s fa screen
    #con r registra video
    cattura=cv2.VideoCapture(0)
    inRegistrazione=False
    video=None  #dichiaro qua il video perchè dura più di un frame e quindi più di un ciclo
    while True:
        ret, frame = cattura.read()
        if not ret:
            break

        frame= cv2.flip(frame,1)   #la specchia perchè è storto
        frame=Negativo(frame)

        if inRegistrazione and video is not None:
            video.write(frame)  #lo aggiunge

        cv2.imshow("Webcam normale",frame)

        tasto=cv2.waitKey(1) & 0xFF
        if tasto==ord('q'):     #esce
            if video is not None:
                video.release() #se si spegne mentre il video è attivo esce e salva il file
            break
        elif tasto==ord('s'):     #screen
            tempo =datetime .datetime.now().strftime("%Y%m%d_%H%M%S")  # come parametri: anno,mese,giorno,ora,minuti,secondi
            cv2.imwrite(f"outputImages/immagine_{tempo}.jpg",frame)
        elif tasto==ord('r'):   #registra

            if inRegistrazione==False:  #non stava già registrando
                tempo=datetime .datetime.now().strftime("%Y%m%d_%H%M%S")
                nVideo=f"outputVideos/video{tempo}.mp4"
                fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                lunghezza=int(cattura.get(cv2.CAP_PROP_FRAME_WIDTH))
                altezza=int(cattura.get(cv2.CAP_PROP_FRAME_HEIGHT))
                video=cv2.VideoWriter(nVideo,fourcc,30,(lunghezza,altezza))
            else:   #aveva già iniziato e ora termina
                video.release()
                video=None

            inRegistrazione=not inRegistrazione     #inverte lo stato

    cattura.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
