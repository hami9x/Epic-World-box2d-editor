from PyQt5.QtWidgets import QGraphicsScene
from PyQt5.QtCore import QStringListModel, QMimeData, pyqtSignal, QPointF

class MainAreaGraphicsScene(QGraphicsScene):
    receivedBodyDrop = pyqtSignal(str, QPointF);

    def __init__(self, parent, view):
        super(MainAreaGraphicsScene, self).__init__(parent);
        self.view = view;

    def dragMoveEvent(self, event):
        event.accept();

    def dragEnterEvent(self, event):
        event.acceptProposedAction();

    def dropEvent(self, event):
        #print("Yay!");
        #print(event.mimeData().text());
        self.receivedBodyDrop.emit(event.mimeData().text(), event.scenePos());

    def mousePressEvent(self, mouseEvent):
        super(MainAreaGraphicsScene, self).mousePressEvent(mouseEvent)

    def mouseMoveEvent(self, mouseEvent):
        super(MainAreaGraphicsScene, self).mouseMoveEvent(mouseEvent)

    def mouseReleaseEvent(self, mouseEvent): 
        super(MainAreaGraphicsScene, self).mouseReleaseEvent(mouseEvent)

    def wheelEvent(self, event):
        event.accept();
        sx = 1 + event.delta()/(180*8);
        self.view.centerOn(event.scenePos());
        self.view.scale(sx, sx);

class BodyListModel(QStringListModel):
    def mimeData(self, indexes):
        if len(indexes) > 1:
            raise Exception("Something wrong? Only 1 item is allowed to drag");
        data = QMimeData();
        data.setText(indexes[0].data());
        return data;