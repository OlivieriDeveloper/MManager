import cv2
import numpy as np
import win32api
import win32con
import ctypes
from ctypes import wintypes

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
    # Apre la fotocamera virtuale (solitamente è l'indice 1 o 2)
    cap = cv2.VideoCapture(1)
    
    if not cap.isOpened():
        print("Errore: Impossibile aprire la fotocamera virtuale")
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
    cv2.namedWindow('OBS Virtual Camera', cv2.WINDOW_NORMAL)
    
    # Imposta la posizione della finestra sul secondo monitor
    cv2.moveWindow('OBS Virtual Camera', monitor_x, monitor_y)
    
    # Imposta la finestra a schermo intero
    cv2.setWindowProperty('OBS Virtual Camera', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    
    while True:
        # Legge un frame dalla fotocamera
        ret, frame = cap.read()
        
        if not ret:
            print("Errore: Impossibile leggere il frame")
            break
        
        # Mostra il frame
        cv2.imshow('OBS Virtual Camera', frame)
        
        # Se viene premuto 'q', esce dal ciclo
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        
    
    # Rilascia le risorse
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
