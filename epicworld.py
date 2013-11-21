from PyQt5.QtCore import pyqtSlot, Qt
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QGraphicsView, QFileDialog
from PyQt5.QtGui import QPainter

from ui_epicworld import Ui_MainWindow
from manager import MainManager, BodyListManager
from subclasses import MainAreaGraphicsScene


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.scene = MainAreaGraphicsScene(self.ui.centralwidget, self.ui.mainCanvas);
        self.ui.mainCanvas.setScene(self.scene);
        self.ui.mainCanvas.setDragMode(QGraphicsView.RubberBandDrag);
        self.ui.mainCanvas.setAcceptDrops(True);
        self.ui.mainCanvas.setRenderHint(QPainter.Antialiasing);
        self.file = None;
        
        self.mainManager = MainManager(self.scene)
        self.listManager = BodyListManager(self.ui.bodyList)
        rect = self.mainManager.axes.childrenBoundingRect();
        print(rect.x(), rect.y(), rect.width(), rect.height())
        self.ui.mainCanvas.setSceneRect(self.mainManager.axes.childrenBoundingRect())
        self.connections();
        self.ui.mainCanvas.show();

    def connections(self):
        self.ui.actionImport_Bodies.triggered.connect(self.mainManager.loadBodies);
        self.mainManager.bodiesLoaded.connect(self.listManager.updateList);
        self.ui.actionSave.triggered.connect(self.save);
        self.scene.receivedBodyDrop.connect(self.mainManager.cloneBody);

    def save(self):
        if not self.file:
            dialog = QFileDialog();
            #dialog.setFileMode(QFileDialog.AnyFile);
            dialog.setAcceptMode(QFileDialog.AcceptSave);
            if (dialog.exec()):
                self.file = (dialog.selectedFiles())[0];
            else:
                return;
        self.mainManager.save(self.file);

if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    gui = MainWindow()
    gui.show()
    sys.exit(app.exec_())
