import subprocess
import sys
import os
import win32api
import ctypes
from ctypes import wintypes
import time

def get_monitor_info():
    monitors = []
    
    def callback(hMonitor, hdcMonitor, lprcMonitor, dwData):
        monitor_info = win32api.GetMonitorInfo(hMonitor)
        monitors.append(monitor_info)
        return True
    
    MONITORENUMPROC = ctypes.WINFUNCTYPE(
        wintypes.BOOL,
        wintypes.HMONITOR,
        wintypes.HDC,
        wintypes.LPRECT,
        wintypes.LPARAM
    )
    
    callback_func = MONITORENUMPROC(callback)
    ctypes.windll.user32.EnumDisplayMonitors(None, None, callback_func, 0)
    return monitors

def play_media(media_path, monitor_index=1):
    # Ottiene le informazioni sui monitor
    monitors = get_monitor_info()
    
    if len(monitors) <= monitor_index:
        print(f"Errore: Il monitor {monitor_index} non esiste")
        return
    
    monitor_info = monitors[monitor_index]
    monitor_x = monitor_info['Monitor'][0]
    monitor_y = monitor_info['Monitor'][1]
    monitor_width = monitor_info['Monitor'][2] - monitor_x
    monitor_height = monitor_info['Monitor'][3] - monitor_y
    
    print(f"Monitor selezionato: {monitor_info['Device']}")
    print(f"Posizione: x={monitor_x}, y={monitor_y}")
    print(f"Dimensioni: {monitor_width}x{monitor_height}")
    
    # Determina se è un'immagine o un video
    is_image = media_path.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif'))
    
    # Costruisce il comando FFmpeg
    if is_image:
        # Per le immagini
        cmd = [
            'ffplay',
            '-noborder',  # Rimuove il bordo della finestra
            '-window_title', 'Media Viewer',
            '-x', str(monitor_width),
            '-y', str(monitor_height),
            '-window_x', str(monitor_x),
            '-window_y', str(monitor_y),
            '-loop', '0',  # Loop infinito
            media_path
        ]
    else:
        # Per i video
        cmd = [
            'ffplay',
            '-noborder',
            '-window_title', 'Media Viewer',
            '-x', str(monitor_width),
            '-y', str(monitor_height),
            '-window_x', str(monitor_x),
            '-window_y', str(monitor_y),
            '-loop', '0',  # Loop infinito
            '-autoexit',   # Esce quando il video finisce
            media_path
        ]
    
    try:
        # Esegue FFmpeg
        process = subprocess.Popen(cmd)
        print("Premi 'q' nella finestra del player per uscire")
        process.wait()
    except FileNotFoundError:
        print("Errore: FFmpeg non è installato o non è nel PATH")
        print("Per installare FFmpeg, visita: https://ffmpeg.org/download.html")
    except KeyboardInterrupt:
        process.terminate()
        print("\nProgramma terminato dall'utente")

def main():
    if len(sys.argv) < 2:
        print("Errore: Specifica il percorso del file multimediale come argomento")
        print("Esempio: python ffmpeg_viewer.py percorso/file.mp4")
        return
    
    media_path = sys.argv[1]
    
    if not os.path.exists(media_path):
        print(f"Errore: Il file {media_path} non esiste")
        return
    
    # Opzionalmente, puoi specificare il monitor come secondo argomento
    monitor_index = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    
    play_media(media_path, monitor_index)

if __name__ == "__main__":
    main() 