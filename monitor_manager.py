from screeninfo import get_monitors
import cv2
from cv2_enumerate_cameras import enumerate_cameras
import keyboard
import argparse
from pygrabber.dshow_graph import FilterGraph
import mss, numpy


def get_cameras():
    graph = FilterGraph()
    devices = graph.get_input_devices()
    for idx, name in enumerate(devices):
        print(f"{idx}: {name}")
    return devices

class MMonitor:
    def __init__(self, monitor_index, monitor_x, monitor_y, monitor_name, monitor_width, monitor_height):
        self.monitor_index = monitor_index
        self.monitor_x = monitor_x
        self.monitor_y = monitor_y
        self.monitor_name = monitor_name
        self.monitor_width = monitor_width
        self.monitor_height = monitor_height
        print(f"Monitor selezionato: {self.monitor_name} - Posizione: x={self.monitor_x}, y={self.monitor_y} - Risoluzione {self.monitor_width}x{self.monitor_height}")

class MVideoStreamMonitor(MMonitor):
    def __init__(self, monitor_index, monitor_x, monitor_y, monitor_name, monitor_width, monitor_height, camera_index):
        super().__init__(monitor_index, monitor_x, monitor_y, monitor_name, monitor_width, monitor_height)
        self.camera_index = camera_index
        self.is_streaming = None
        self.error = False
    
    def streamCamera_proc(self):
        self.is_streaming = None
        # Apre la fotocamera virtuale (solitamente è l'indice 1 o 2)
        self.cap = cv2.VideoCapture(self.camera_index)
        
        if not self.cap.isOpened():
            print("Errore: Impossibile aprire la sorgente video")
            self.error = True
            return
        
        # Crea la finestra
        self.setup_window()

        self.is_streaming = True
        self.stream_video()
    
    def setup_window(self):
        cv2.namedWindow('Video Streaming', cv2.WINDOW_NORMAL)
        cv2.moveWindow('Video Streaming', self.monitor_x, self.monitor_y)
        cv2.setWindowProperty('Video Streaming', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

        # Imposta la risoluzione in base alle dimensioni del monitor
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.monitor_width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.monitor_height)

    def stream_video(self):
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

        self.cleanup()

    def cleanup(self):
        # Rilascia le risorse
        self.cap.release()
        cv2.destroyAllWindows()
    
    def streamCamera(self):
        self.streamCamera_proc()

    def stopStreaming(self):
        if self.is_streaming:
            self.is_streaming = False


def list_devices():
    print("\nMonitor disponibili:")
    monitors = get_monitors()
    for i, monitor in enumerate(monitors):
        print(f"Monitor {i}: {monitor.name} - Risoluzione: {monitor.width}x{monitor.height}")
    
    print("\nTelecamere disponibili:")
    cameras = get_cameras()
    for camera in cameras:
        print(f"Camera {camera}")

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
        monitors = get_monitors()
        selected_monitor = monitors[args.monitor]
        monitor = MVideoStreamMonitor(args.monitor, selected_monitor.x, selected_monitor.y, selected_monitor.name, selected_monitor.width, selected_monitor.height, args.camera)
        print(f"Avvio streaming da Camera {args.camera} su Monitor {args.monitor}")
        print("Premi 'ESC' per uscire...")
        monitor.streamCamera()
        keyboard.wait("esc")
        monitor.stopStreaming()
    except Exception as e:
        print(f"Errore durante l'esecuzione: {str(e)}")

if __name__ == "__main__":
    main()