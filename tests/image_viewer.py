import cv2
import numpy as np
import win32api
import ctypes
from ctypes import wintypes
import sys
import os

def get_monitor_info():
    monitors = []
    
    def callback(hMonitor, hdcMonitor, lprcMonitor, dwData):
        monitor_info = win32api.GetMonitorInfo(hMonitor)
        monitors.append(monitor_info)
        return True
    
    # Definiamo la callback come una funzione C
    MONITORENUMPROC = ctypes.WINFUNCTYPE(
        wintypes.BOOL,
        wintypes.HMONITOR,
        wintypes.HDC,
        wintypes.LPRECT,
        wintypes.LPARAM
    )
    
    callback_func = MONITORENUMPROC(callback)
    
    # Enumeriamo i monitor
    ctypes.windll.user32.EnumDisplayMonitors(
        None,
        None,
        callback_func,
        0
    )
    
    return monitors

def main():
    # Verifica che sia stato fornito il percorso dell'immagine
    if len(sys.argv) < 2:
        print("Errore: Specifica il percorso dell'immagine come argomento")
        print("Esempio: python image_viewer.py percorso/immagine.jpg")
        return
    
    image_path = sys.argv[1]
    
    # Verifica che il file esista
    if not os.path.exists(image_path):
        print(f"Errore: Il file {image_path} non esiste")
        return
    
    # Carica l'immagine
    image = cv2.imread(image_path)
    if image is None:
        print(f"Errore: Impossibile caricare l'immagine {image_path}")
        return
    
    # Ottiene le informazioni sui monitor
    monitors = get_monitor_info()
    
    if len(monitors) < 2:
        print("Errore: È necessario avere almeno 2 monitor collegati")
        return
    
    # Seleziona il secondo monitor (indice 1)
    monitor_info = monitors[1]
    monitor_x = monitor_info['Monitor'][0]
    monitor_y = monitor_info['Monitor'][1]
    
    print(f"Monitor selezionato: {monitor_info['Device']}")
    print(f"Posizione: x={monitor_x}, y={monitor_y}")
    
    # Crea la finestra
    cv2.namedWindow('Image Viewer', cv2.WINDOW_NORMAL)
    
    # Imposta la posizione della finestra sul secondo monitor
    cv2.moveWindow('Image Viewer', monitor_x, monitor_y)
    
    # Imposta la finestra a schermo intero
    cv2.setWindowProperty('Image Viewer', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    
    # Mostra l'immagine
    cv2.imshow('Image Viewer', image)
    
    print("Premi 'q' per uscire")
    
    while True:
        # Se viene premuto 'q', esce dal ciclo
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    # Chiude la finestra
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main() 