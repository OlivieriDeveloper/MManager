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
    # Verifica che sia stato fornito il percorso del video
    if len(sys.argv) < 2:
        print("Errore: Specifica il percorso del video come argomento")
        print("Esempio: python video_viewer.py percorso/video.mp4")
        return
    
    video_path = sys.argv[1]
    
    # Verifica che il file esista
    if not os.path.exists(video_path):
        print(f"Errore: Il file {video_path} non esiste")
        return
    
    # Apre il video
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Errore: Impossibile aprire il video {video_path}")
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
    cv2.namedWindow('Video Viewer', cv2.WINDOW_NORMAL)
    
    # Imposta la posizione della finestra sul secondo monitor
    cv2.moveWindow('Video Viewer', monitor_x, monitor_y)
    
    # Imposta la finestra a schermo intero
    cv2.setWindowProperty('Video Viewer', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    
    print("Premi 'q' per uscire")
    print("Premi 'p' per mettere in pausa/riprendere")
    
    paused = False
    
    while True:
        if not paused:
            # Legge un frame dal video
            ret, frame = cap.read()
            
            if not ret:
                # Se il video è finito, lo riavvolge
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                continue
            
            # Mostra il frame
            cv2.imshow('Video Viewer', frame)
        
        # Controlla i tasti premuti
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('p'):
            paused = not paused
    
    # Rilascia le risorse
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main() 