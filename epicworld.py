from PyQt5.QtCore import pyqtSlot, Qt, QTimer, QRectF
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
        self.PBEFile= None;
        self.updateTimer = QTimer();
        self.updateTimer.setInterval(100);
        
        self.mainManager = MainManager(self.scene)
        self.listManager = BodyListManager(self.ui.bodyList)
        rect = self.mainManager.axes.childrenBoundingRect();
        # print(rect.x(), rect.y(), rect.width(), rect.height())
        self.ui.mainCanvas.setSceneRect(self.mainManager.axes.childrenBoundingRect())
        # self.ui.mainCanvas.setSceneRect(QRectF(-5000, -5000, 10000, 10000));
        self.connections();
        self.ui.mainCanvas.show();

    def connections(self):
        self.ui.actionImport_Bodies.triggered.connect(self.loadFromPBE);
        self.ui.actionLoad.triggered.connect(self.loadFile);
        self.mainManager.bodiesLoaded.connect(self.listManager.updateList);
        self.ui.actionSave.triggered.connect(self.save);
        self.scene.receivedBodyDrop.connect(self.mainManager.cloneBody);
        self.ui.actionScale.triggered.connect(self.scene.scaleStarted);
        self.ui.actionDelete_Body.triggered.connect(self.mainManager.deleteSelected)
        self.ui.actionUndo.triggered.connect(self.mainManager.undoStack.undo);
        self.ui.actionRedo.triggered.connect(self.mainManager.undoStack.redo);
        self.scene.mouseIsMovingItems.connect(self.mainManager.handleMoveCommand);
        self.scene.scalingStopped.connect(self.mainManager.handleScaleCommand);
        self.ui.actionSave_as.triggered.connect(self.saveAs);
        self.scene.itemChanging.connect(self.startStopUpdatingProperties);
        self.scene.selectionChanged.connect(self.enableDisableProperties);
        self.updateTimer.timeout.connect(self.updateItemProperties);
        self.ui.xEdit.textEdited.connect(self.itemUpdateX);
        self.ui.yEdit.textEdited.connect(self.itemUpdateY);
        self.ui.widthEdit.textEdited.connect(self.itemUpdateWidth);
        self.ui.idEdit.textEdited.connect(self.itemUpdateId);
        self.ui.actionRaise.triggered.connect(self.mainManager.raiseItems);
        self.ui.actionLower.triggered.connect(self.mainManager.lowerItems);
        self.ui.actionDuplicate.triggered.connect(self.mainManager.duplicateItems);

    def theOnlySelectedItem(self):
        if not self.scene.onlyOneItemSelected():
             return None;
        return self.scene.selectedItems()[0];

    def itemUpdateX(self, newVal):
        print(newVal);
        item = self.theOnlySelectedItem();
        if not item: return;
        try:
            x = int(newVal);
        except ValueError:
            return;
        item.setPosXByMeter(x)

    def itemUpdateY(self, newVal):
        item = self.theOnlySelectedItem();
        if not item: return;
        try:
            y = int(newVal);
        except ValueError:
            return;
        item.setPosYByMeter(y);

    def itemUpdateWidth(self, newVal):
        item = self.theOnlySelectedItem();
        if not item: return;
        try:
            width = int(newVal);
            item.setScale(item.scale()*width/item.getMeterWidth());
        except ValueError:
            return;

    def itemUpdateId(self, newId):
        item = self.theOnlySelectedItem();
        if not item: return;
        item.setId(newId)

    def updateItemProperties(self):
        item = self.theOnlySelectedItem();
        if not item: return;
        self.ui.xEdit.setText(str(item.meterPos().x()));
        self.ui.yEdit.setText(str(item.meterPos().y()));
        self.ui.widthEdit.setText(str(item.getMeterWidth()));
        self.ui.idEdit.setText(item.itemId);

    def enableDisableProperties(self):
        if self.scene.onlyOneItemSelected():
            self.ui.propertiesDock.setEnabled(True);
            self.updateItemProperties();
            return;
        self.ui.propertiesDock.setEnabled(False);

    def startStopUpdatingProperties(self, changing):
        if (not changing) or (not self.scene.onlyOneItemSelected()):
            self.updateTimer.stop();
            return;
        if changing:
            self.updateItemProperties();
            self.updateTimer.start();

    def saveAs(self):
        if not self.file:
            self.save();
        else:
            dialog = QFileDialog();
            #dialog.setFileMode(QFileDialog.AnyFile);
            dialog.setAcceptMode(QFileDialog.AcceptSave);
            if (dialog.exec()):
                self.file = (dialog.selectedFiles())[0];
                self.mainManager.save(self.file);

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

    def loadFromPBE(self):
        if not self.PBEFile:
            oFile = QFileDialog.getOpenFileName();
            if not oFile[0]:
                return
            else:
                self.PBEFile = oFile[0]
        self.mainManager.loadFromPBE(self.PBEFile);

    def loadFile(self):
        oFile = QFileDialog.getOpenFileName();
        if not oFile[0]:
            return
        else:
            self.file = oFile[0]
        self.mainManager.loadFile(self.file);

if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    gui = MainWindow()
    gui.show()
    sys.exit(app.exec_())
