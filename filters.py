import cv2
def ScalaGrigi(frame):
    grigia = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    bordi = cv2.Canny(grigia, 50, 150)
    #return bordi
    return grigia

def Negativo(frame):
    return 255-frame

def Seppia(frame):
    pass

def Solarizzazione(frame):
    pass

def EffettoTermicoHeatMap(frame):
    pass