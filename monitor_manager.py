import win32api, win32con # type: ignore
import ctypes
from ctypes import wintypes

import cv2
import os, dotenv

from multiprocessing import Process

import keyboard
import argparse
import sys

from cv2_enumerate_cameras import enumerate_cameras

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

def get_cameras():
    i = 0
    cameras = []
    for camera_info in enumerate_cameras():
        print(f'{camera_info.index}: {camera_info.name}')
        cameras.append({"index": i, "name": camera_info.name})
        i+=1
    return cameras

class MMonitor:
    def __init__(self, monitor_index, monitor_x, monitor_y, monitor_name):
        self.monitor_index = monitor_index

        self.monitor_x = monitor_x
        self.monitor_y = monitor_y
        self.monitor_name = monitor_name
        

        # Debug
        print(f"Monitor selezionato: {self.monitor_name}")
        print(f"Posizione: x={self.monitor_x}, y={self.monitor_y}")

class MVideoStreamMonitor(MMonitor):
    def __init__(self, monitor_index, monitor_x, monitor_y, monitor_name, camera_index):
        super().__init__(monitor_index, monitor_x, monitor_y, monitor_name)
        self.camera_index = camera_index
        self.is_streaming = None
        self.error = False
    
    def streamCamera_proc(self):
        # Apre la fotocamera virtuale (solitamente è l'indice 1 o 2)
        self.cap = cv2.VideoCapture(self.camera_index)
        
        if not self.cap.isOpened():
            print("Errore: Impossibile aprire la sorgente video")
            self.error = True
            return
        
        # Crea la finestra
        cv2.namedWindow('Video Streaming', cv2.WINDOW_NORMAL)
        
        # Imposta la posizione della finestra sul secondo monitor
        cv2.moveWindow('Video Streaming', self.monitor_x, self.monitor_y)
        
        # Imposta la finestra a schermo intero
        cv2.setWindowProperty('Video Streaming', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

        self.is_streaming = True
        while self.is_streaming:
            # Legge un frame dalla fotocamera
            ret, frame = self.cap.read()
            
            if not ret:
                print("Errore: Impossibile leggere il frame")
                self.is_streaming = False
                break
            
            # Mostra il frame
            cv2.imshow('Video Streaming', frame)
            
            # Se viene premuto 'q', esce dal ciclo
            if cv2.waitKey(1) & 0xFF == ord('q'):
                self.is_streaming = False
                break

        # Rilascia le risorse
        self.cap.release()
        cv2.destroyAllWindows()
    
    def streamCamera(self):
        # self.stream = Process(target=self.streamCamera_proc)
        # self.stream.start()
        self.streamCamera_proc()

    def stopStreaming(self):
        # if self.stream.is_alive():
        #     self.stream.terminate()
        if self.is_streaming:
            self.is_streaming = False

# def list_devices():
#     print("\nMonitor disponibili:")
#     monitors = get_monitor_info()
#     for i, monitor in enumerate(monitors):
#         print(f"Monitor {i}: {monitor['Device']}")
    
#     print("\nTelecamere disponibili:")
#     cameras = get_cameras()
#     for camera in cameras:
#         print(f"Camera {camera}")

def main():
    parser = argparse.ArgumentParser(description='Monitor Manager CLI')
    parser.add_argument('--list', '-l', action='store_true', 
                       help='Lista tutti i monitor e le telecamere disponibili')
    parser.add_argument('--monitor', '-m', type=int,
                       help='Indice del monitor da utilizzare')
    parser.add_argument('--camera', '-c', type=int,
                       help='Indice della telecamera da utilizzare')
    
    args = parser.parse_args()

    if args.list:
        list_devices()
        return

    if args.monitor is None or args.camera is None:
        print("Errore: Devi specificare sia il monitor che la telecamera")
        print("Uso: python monitor_manager.py -m MONITOR_INDEX -c CAMERA_INDEX")
        print("     python monitor_manager.py --list  (per vedere i dispositivi disponibili)")
        return

    try:
        monitor = MVideoStreamMonitor(args.monitor, args.camera)
        print(f"Avvio streaming da Camera {args.camera} su Monitor {args.monitor}")
        print("Premi 'ESC' per uscire...")
        monitor.streamCamera()
        keyboard.wait("esc")
        monitor.stopStreaming()
    except Exception as e:
        print(f"Errore durante l'esecuzione: {str(e)}")

if __name__ == "__main__":
    main()