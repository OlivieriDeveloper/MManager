from PyQt5 import QtCore, QtGui, QtWidgets
from monitor_manager import get_cameras, MVideoStreamMonitor
from screeninfo import get_monitors


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):

        # Retrieve Informations
        self.cameras = get_cameras()
        self.cameras.pop(0)
        self.monitors = get_monitors()

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

        for monitor in self.monitors:
            self.MonitorSelector.addItem("")
        
        self.SourceLabel = QtWidgets.QLabel(self.formLayoutWidget)
        self.SourceLabel.setObjectName("SourceLabel")
        self.InputForm.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.SourceLabel)
        
        self.SourceSelector = QtWidgets.QComboBox(self.formLayoutWidget)
        self.SourceSelector.setObjectName("SourceSelector")
        for camera in self.cameras:
            self.SourceSelector.addItem("")
        self.InputForm.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.SourceSelector)
        
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

        for index, monitor in enumerate(self.monitors,start=0):
            self.MonitorSelector.setItemText(index, _translate("MainWindow", monitor.name))
        
        self.SourceLabel.setText(_translate("MainWindow", "Sorgente Video Input:"))

        for index, camera in enumerate(self.cameras):
            self.SourceSelector.setItemText(index, _translate("MainWindow", str(camera["index"])+" "+str(camera["name"])))
        
        self.RefreshBtn.setText(_translate("MainWindow", "Aggiorna"))
        self.StreamBtn.setText(_translate("MainWindow", "Mostra Streaming"))
    
    def startStream(self):
        mon_index = int(self.MonitorSelector.currentIndex())
        self.m = MVideoStreamMonitor(monitor_index=mon_index, monitor_x=self.monitors[mon_index].x, monitor_y=self.monitors[mon_index].y, monitor_name=self.monitors[mon_index].name, camera_index=int(self.SourceSelector.currentIndex()))
        self.StreamBtn.setText("Ferma")
        self.StreamBtn.clicked.disconnect(self.startStream)
        self.StreamBtn.clicked.connect(self.stopStream)
        self.m.streamCamera()
        self.StreamBtn.setText("Mostra Streaming")
        self.StreamBtn.clicked.disconnect(self.stopStream)
        self.StreamBtn.clicked.connect(self.startStream)
    
    def stopStream(self):
        self.m.stopStreaming()
    
    def updateSelectors(self):
        self.cameras = get_cameras()
        self.cameras.pop(0)
        self.monitors = get_monitors()

        self.MonitorSelector.clear()
        for index, monitor in enumerate(self.monitors):
            self.MonitorSelector.addItem("")
            self.MonitorSelector.setItemText(index, monitor.name)
        
        self.SourceSelector.clear()
        for index, camera in enumerate(self.cameras):
            self.SourceSelector.addItem("")
            self.SourceSelector.setItemText(index, str(camera["index"])+" "+str(camera["name"]))

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
