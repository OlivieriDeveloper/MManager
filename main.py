from PyQt5 import QtCore, QtGui, QtWidgets
from monitor_manager import get_cameras, MVideoStreamMonitor
from screeninfo import get_monitors
import os, json

def writeJSONFile(filepath, dict):
    with open(filepath, "w") as f:
        f.write(json.dumps(dict))
        f.close()
    
CONFIG_FILENAME = "config.txt"
if not os.path.isfile(CONFIG_FILENAME):
    config = {
        "defaultMonitor": 0,
        "defaultSource": 0,
    }
    writeJSONFile(CONFIG_FILENAME, config)
else:
    with open(CONFIG_FILENAME, "r") as f:
        try:
            config = json.load(f)  # Carica il contenuto del file JSON
        except json.JSONDecodeError:
            print("Errore: Il file di configurazione è vuoto o non valido. Utilizzo valori predefiniti.")
            config = {
                "defaultMonitor": 0,
                "defaultSource": 0,
            }
            writeJSONFile(CONFIG_FILENAME, config)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):

        # Retrieve Informations
        self.cameras = get_cameras()
        self.monitors = get_monitors()
        with open(CONFIG_FILENAME, "r") as f:
            self.config = json.load(f)

        MainWindow.setObjectName("Monitor Manager")
        MainWindow.resize(318, 279)
        
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        
        self.formLayoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.formLayoutWidget.setGeometry(QtCore.QRect(10, 20, 301, 181))
        self.formLayoutWidget.setObjectName("formLayoutWidget")

        self.InputForm = QtWidgets.QFormLayout(self.formLayoutWidget)
        self.InputForm.setContentsMargins(0, 0, 0, 0)
        self.InputForm.setObjectName("InputForm")
        
        self.MonitorLabel = QtWidgets.QLabel(self.formLayoutWidget)
        self.MonitorLabel.setObjectName("MonitorLabel")
        self.InputForm.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.MonitorLabel)
        
        self.MonitorSelector = QtWidgets.QComboBox(self.formLayoutWidget)
        self.MonitorSelector.setObjectName("MonitorSelector")
        self.InputForm.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.MonitorSelector)

        for _ in self.monitors:
            self.MonitorSelector.addItem("")
        
        self.SourceLabel = QtWidgets.QLabel(self.formLayoutWidget)
        self.SourceLabel.setObjectName("SourceLabel")
        self.InputForm.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.SourceLabel)
        
        self.SourceSelector = QtWidgets.QComboBox(self.formLayoutWidget)
        self.SourceSelector.setObjectName("SourceSelector")
        self.InputForm.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.SourceSelector)

        for _ in self.cameras:
            self.SourceSelector.addItem("")
        
        self.SaveConfig = QtWidgets.QCheckBox(self.formLayoutWidget)
        self.SaveConfig.setObjectName("SaveConfigCheckbox")
        self.InputForm.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.SaveConfig)
        
        
        self.RefreshBtn = QtWidgets.QPushButton(self.centralwidget)
        self.RefreshBtn.setGeometry(QtCore.QRect(10, 210, 101, 23))
        self.RefreshBtn.setObjectName("RefreshBtn")
        self.RefreshBtn.clicked.connect(self.updateSelectors)
        
        self.StreamBtn = QtWidgets.QPushButton(self.centralwidget)
        self.StreamBtn.setGeometry(QtCore.QRect(120, 210, 187, 23))
        self.StreamBtn.setObjectName("StreamBtn")
        self.StreamBtn.clicked.connect(self.startStream)
        
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
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Monitor Manager"))

        self.MonitorLabel.setText(_translate("MainWindow", "Monitor:"))

        for index, monitor in enumerate(self.monitors):
            self.MonitorSelector.setItemText(index, _translate("MainWindow", monitor.name))
        self.MonitorSelector.setCurrentIndex(self.config["defaultMonitor"])
        
        self.SourceLabel.setText(_translate("MainWindow", "Sorgente Video Input:"))

        print("CAMERAS: ", self.cameras)
        for index, camera in enumerate(self.cameras):
            self.SourceSelector.setItemText(index, _translate("MainWindow", f"{index}: {camera}"))
        self.SourceSelector.setCurrentIndex(self.config["defaultSource"])

        self.SaveConfig.setText(_translate("MainWindow", "Salva questa configurazione"))
        
        self.RefreshBtn.setText(_translate("MainWindow", "Aggiorna"))
        self.StreamBtn.setText(_translate("MainWindow", "Mostra Streaming"))
    
    def startStream(self):
        mon_index = int(self.MonitorSelector.currentIndex())
        self.m = MVideoStreamMonitor(monitor_index=mon_index, 
                                     monitor_x=self.monitors[mon_index].x, 
                                     monitor_y=self.monitors[mon_index].y,
                                     monitor_width=self.monitors[mon_index].width, 
                                     monitor_height=self.monitors[mon_index].height,
                                     monitor_name=self.monitors[mon_index].name, 
                                     camera_index=int(self.SourceSelector.currentIndex()))
        self.StreamBtn.setEnabled(True)

        self.StreamBtn.setText("Ferma")
        self.StreamBtn.clicked.disconnect(self.startStream)
        self.StreamBtn.clicked.connect(self.stopStream)
        
        try:
            self.m.streamCamera()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Errore", f"Errore: {e}")

        self.StreamBtn.setText("Mostra Streaming")
        self.StreamBtn.clicked.disconnect(self.stopStream)
        self.StreamBtn.clicked.connect(self.startStream)
        
        self.RefreshBtn.setEnabled(True)
        
        if self.SaveConfig.isChecked():
            try:
                self.saveConfig()
            except:
                QtWidgets.QMessageBox.warning(self, "Errore", "Errore: Impossibile salvare il file di configurazione")
    
    def stopStream(self):
        self.m.stopStreaming()
    
    def updateSelectors(self):
        self.cameras = get_cameras()
        self.monitors = get_monitors()

        self.MonitorSelector.clear()
        for index, monitor in enumerate(self.monitors):
            self.MonitorSelector.addItem("")
            self.MonitorSelector.setItemText(index, monitor.name)
        self.MonitorSelector.setCurrentIndex(self.config["defaultMonitor"])
        
        self.SourceSelector.clear()
        print("CAMERAS: ", self.cameras)
        for index, camera in enumerate(self.cameras):
            self.SourceSelector.addItem("")
            self.SourceSelector.setItemText(index, f"{index}: {camera}")
        self.SourceSelector.setCurrentIndex(self.config["defaultSource"])
    
    def saveConfig(self):
        self.config["defaultMonitor"] = self.MonitorSelector.currentIndex()
        self.config["defaultSource"] = self.SourceSelector.currentIndex()
        writeJSONFile(CONFIG_FILENAME, self.config)

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
