from PyQt5 import QtCore, QtGui, QtWidgets
from monitor_manager import get_cameras, MVideoStreamMonitor
from screeninfo import get_monitors
import os
import json
import mss
import cv2
import numpy as np

# --- Utility per scrivere il file di configurazione ---
def write_json_file(filepath, data):
    with open(filepath, "w") as f:
        json.dump(data, f)

# --- Configurazione iniziale ---
CONFIG_FILENAME = "monitor_manager_config.txt"
APP_DATA_PATH = os.getenv("APPDATA")
CONFIG_FILEPATH = os.path.join(APP_DATA_PATH, CONFIG_FILENAME)

if not os.path.isfile(CONFIG_FILEPATH):
    config = {"defaultMonitor": 0, "defaultSource": 0}
    write_json_file(CONFIG_FILEPATH, config)
else:
    with open(CONFIG_FILEPATH, "r") as f:
        try:
            config = json.load(f)
        except json.JSONDecodeError:
            config = {"defaultMonitor": 0, "defaultSource": 0}
            write_json_file(CONFIG_FILEPATH, config)

# --- Thread per la cattura dello schermo ---
class MonitorPreviewThread(QtCore.QThread):
    frame_captured = QtCore.pyqtSignal(QtGui.QImage)

    def __init__(self, top, left, width, height):
        super().__init__()
        self.top = top
        self.left = left
        self.width = width
        self.height = height
        self.active = False

    def run(self):
        self.active = True
        with mss.mss() as sct:
            monitor = {"top": self.top, "left": self.left, "width": self.width, "height": self.height}
            while self.active:
                img = np.array(sct.grab(monitor))
                img = cv2.cvtColor(img, cv2.COLOR_BGRA2RGB)
                h, w, ch = img.shape
                bytes_per_line = ch * w
                qimg = QtGui.QImage(img.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
                self.frame_captured.emit(qimg)
                QtCore.QThread.msleep(30)  # ~30 fps

    def stop(self):
        self.active = False
        self.quit()
        self.wait()

# --- Thread per lo streaming della camera ---
class CameraStreamThread(QtCore.QThread):
    def __init__(self, video_stream_monitor):
        super().__init__()
        self.video_stream_monitor = video_stream_monitor

    def run(self):
        try:
            self.video_stream_monitor.streamCamera()
        except Exception:
            pass

# --- MainWindow UI ---
class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        # --- Recupera info su camere e monitor ---
        self.cameras = get_cameras()
        self.monitors = get_monitors()
        with open(CONFIG_FILEPATH, "r") as f:
            self.config = json.load(f)

        MainWindow.setObjectName("Monitor Manager")
        MainWindow.resize(318, 279)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        # --- Layout form ---
        self.formLayoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.formLayoutWidget.setGeometry(QtCore.QRect(10, 20, 301, 181))
        self.formLayoutWidget.setObjectName("formLayoutWidget")
        self.inputForm = QtWidgets.QFormLayout(self.formLayoutWidget)
        self.inputForm.setContentsMargins(0, 0, 0, 0)
        self.inputForm.setObjectName("inputForm")

        # --- Selettore monitor ---
        self.monitorLabel = QtWidgets.QLabel(self.formLayoutWidget)
        self.monitorLabel.setObjectName("monitorLabel")
        self.inputForm.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.monitorLabel)
        self.monitorSelector = QtWidgets.QComboBox(self.formLayoutWidget)
        self.monitorSelector.setObjectName("monitorSelector")
        self.inputForm.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.monitorSelector)
        for _ in self.monitors:
            self.monitorSelector.addItem("")

        # --- Selettore sorgente video ---
        self.sourceLabel = QtWidgets.QLabel(self.formLayoutWidget)
        self.sourceLabel.setObjectName("sourceLabel")
        self.inputForm.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.sourceLabel)
        self.sourceSelector = QtWidgets.QComboBox(self.formLayoutWidget)
        self.sourceSelector.setObjectName("sourceSelector")
        self.inputForm.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.sourceSelector)
        for _ in self.cameras:
            self.sourceSelector.addItem("")

        # --- Checkbox salva configurazione ---
        self.saveConfigCheckbox = QtWidgets.QCheckBox(self.formLayoutWidget)
        self.saveConfigCheckbox.setObjectName("saveConfigCheckbox")
        self.inputForm.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.saveConfigCheckbox)

        # --- Pulsanti ---
        self.refreshBtn = QtWidgets.QPushButton(self.centralwidget)
        self.refreshBtn.setGeometry(QtCore.QRect(10, 210, 101, 23))
        self.refreshBtn.setObjectName("refreshBtn")
        self.refreshBtn.clicked.connect(self.updateSelectors)

        self.streamBtn = QtWidgets.QPushButton(self.centralwidget)
        self.streamBtn.setGeometry(QtCore.QRect(120, 210, 187, 23))
        self.streamBtn.setObjectName("streamBtn")
        self.streamBtn.clicked.connect(self.startStream)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 318, 21))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _tr = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_tr("MainWindow", "Monitor Manager"))
        self.monitorLabel.setText(_tr("MainWindow", "Monitor:"))
        for idx, monitor in enumerate(self.monitors):
            self.monitorSelector.setItemText(idx, _tr("MainWindow", monitor.name))
        self.monitorSelector.setCurrentIndex(self.config["defaultMonitor"])
        self.sourceLabel.setText(_tr("MainWindow", "Sorgente Video Input:"))
        for idx, camera in enumerate(self.cameras):
            self.sourceSelector.setItemText(idx, _tr("MainWindow", f"{idx}: {camera}"))
        self.sourceSelector.setCurrentIndex(self.config["defaultSource"])
        self.saveConfigCheckbox.setText(_tr("MainWindow", "Salva questa configurazione"))
        self.refreshBtn.setText(_tr("MainWindow", "Aggiorna"))
        self.streamBtn.setText(_tr("MainWindow", "Mostra Streaming"))

    def startStream(self):
        monitor_idx = int(self.monitorSelector.currentIndex())
        monitor = self.monitors[monitor_idx]
        self.videoStream = MVideoStreamMonitor(
            monitor_index=monitor_idx,
            monitor_x=monitor.x,
            monitor_y=monitor.y,
            monitor_width=monitor.width,
            monitor_height=monitor.height,
            monitor_name=monitor.name,
            camera_index=int(self.sourceSelector.currentIndex())
        )
        # Thread preview monitor
        self.monitorThread = MonitorPreviewThread(
            top=monitor.y,
            left=monitor.x,
            width=monitor.width,
            height=monitor.height
        )
        self.monitorThread.frame_captured.connect(self.showMonitorPreview)
        # Thread streaming camera
        self.cameraThread = CameraStreamThread(self.videoStream)

        self.streamBtn.setEnabled(True)
        self.streamBtn.setText("Ferma")
        self.streamBtn.clicked.disconnect(self.startStream)
        self.streamBtn.clicked.connect(self.stopStream)

        try:
            self.cameraThread.start()
            self.monitorThread.start()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self.centralwidget, "Errore", f"Errore: {e}")

        self.refreshBtn.setEnabled(True)
        if self.saveConfigCheckbox.isChecked():
            self.saveConfig()

    def stopStream(self):
        try:
            # Ferma lo streaming della camera
            if hasattr(self, 'videoStream'):
                self.videoStream.stopStreaming()
            
            # Ferma il thread del monitor
            if hasattr(self, 'monitorThread'):
                self.monitorThread.stop()
                try:
                    self.monitorThread.frame_captured.disconnect(self.showMonitorPreview)
                except Exception:
                    pass
            
            # Ferma il thread della camera
            if hasattr(self, 'cameraThread'):
                self.cameraThread.quit()
                self.cameraThread.wait()
            
            # Ripristina il pulsante
            self.streamBtn.setText("Mostra Streaming")
            self.streamBtn.clicked.disconnect(self.stopStream)
            self.streamBtn.clicked.connect(self.startStream)
            
        except Exception as e:
            QtWidgets.QMessageBox.critical(self.centralwidget, "Errore", f"Errore: {e}")

    def updateSelectors(self):
        self.cameras = get_cameras()
        self.monitors = get_monitors()
        self.monitorSelector.clear()
        for idx, monitor in enumerate(self.monitors):
            self.monitorSelector.addItem("")
            self.monitorSelector.setItemText(idx, monitor.name)
        self.monitorSelector.setCurrentIndex(self.config["defaultMonitor"])
        self.sourceSelector.clear()
        for idx, camera in enumerate(self.cameras):
            self.sourceSelector.addItem("")
            self.sourceSelector.setItemText(idx, f"{idx}: {camera}")
        self.sourceSelector.setCurrentIndex(self.config["defaultSource"])

    def saveConfig(self):
        self.config["defaultMonitor"] = self.monitorSelector.currentIndex()
        self.config["defaultSource"] = self.sourceSelector.currentIndex()
        write_json_file(CONFIG_FILEPATH, self.config)

    def showMonitorPreview(self, qimg):
        if not hasattr(self, 'previewWindow'):
            self.previewWindow = QtWidgets.QWidget()
            self.previewWindow.setWindowTitle("Anteprima Monitor")
            self.previewLabel = QtWidgets.QLabel(self.previewWindow)
            self.previewLabel.setGeometry(0, 0, 400, 300)
            self.previewWindow.resize(400, 300)
            self.previewWindow.closeEvent = self._onPreviewWindowClose
        pixmap = QtGui.QPixmap.fromImage(qimg).scaled(
            self.previewLabel.size(), QtCore.Qt.KeepAspectRatio)
        self.previewLabel.setPixmap(pixmap)
        self.previewWindow.show()

    def _onPreviewWindowClose(self, event):
        if hasattr(self, 'monitorThread'):
            self.monitorThread.stop()
            try:
                self.monitorThread.frame_captured.disconnect(self.showMonitorPreview)
            except Exception:
                pass
        event.accept()
        if hasattr(self, 'previewWindow'):
            del self.previewWindow
        if hasattr(self, 'previewLabel'):
            del self.previewLabel

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
