from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QGraphicsScene

from ui_epicworld import Ui_MainWindow
from manager import Manager


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.scene = QGraphicsScene(self.ui.centralwidget);
        self.ui.mainCanvas.setScene(self.scene);
        self.manager = Manager(self.scene)
        self.connections();
        self.ui.mainCanvas.show();


    def connections(self):
    	self.ui.actionImport_Bodies.triggered.connect(self.manager.loadBodies)

if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    gui = MainWindow()
    gui.show()
    sys.exit(app.exec_())
