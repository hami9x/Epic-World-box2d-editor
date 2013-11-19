from PyQt5.QtCore import pyqtSlot, Qt
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QGraphicsView
from PyQt5.QtGui import QPainter

from ui_epicworld import Ui_MainWindow
from manager import MainManager, BodyListManager
from subclasses import MainAreaGraphicsScene


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.scene = MainAreaGraphicsScene(self.ui.centralwidget);
        self.ui.mainCanvas.setScene(self.scene);
        self.ui.mainCanvas.setDragMode(QGraphicsView.RubberBandDrag);
        self.ui.mainCanvas.setAcceptDrops(True);
        self.ui.mainCanvas.setRenderHint(QPainter.Antialiasing);
        self.ui.mainCanvas.setSceneRect(0, 0, 1000, 500)
        self.mainManager = MainManager(self.scene)
        self.listManager = BodyListManager(self.ui.bodyList)
        self.connections();
        self.ui.mainCanvas.show();

    def connections(self):
        self.ui.actionImport_Bodies.triggered.connect(self.mainManager.loadBodies);
        self.mainManager.bodiesLoaded.connect(self.listManager.updateList);
        self.scene.receivedBodyDrop.connect(self.mainManager.cloneBody);

if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    gui = MainWindow()
    gui.show()
    sys.exit(app.exec_())
