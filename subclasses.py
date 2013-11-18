from PyQt5.QtWidgets import QGraphicsScene
from PyQt5.QtCore import QStringListModel, QMimeData, pyqtSignal, QPointF

class MainAreaGraphicsScene(QGraphicsScene):
    receivedBodyDrop = pyqtSignal(str, QPointF);

    def __init__(self, parent):
        super(MainAreaGraphicsScene, self).__init__(parent);

    def dragMoveEvent(self, event):
        event.accept();

    def dragEnterEvent(self, event):
        event.acceptProposedAction();

    def dropEvent(self, event):
        #print("Yay!");
        #print(event.mimeData().text());
        self.receivedBodyDrop.emit(event.mimeData().text(), event.scenePos());

class BodyListModel(QStringListModel):
    def mimeData(self, indexes):
        if len(indexes) > 1:
            raise Exception("Something wrong? Only 1 item is allowed to drag");
        data = QMimeData();
        data.setText(indexes[0].data());
        return data;