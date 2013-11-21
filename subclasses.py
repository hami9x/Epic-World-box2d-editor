from PyQt5.QtWidgets import QGraphicsScene
from PyQt5.QtCore import QStringListModel, QMimeData, pyqtSignal, QPointF
import math

NORMAL = 0;
SCALING = 1;

def pointDistance(p1, p2):
    return math.hypot(p2.x()-p1.x(), p2.y()-p1.y())

class MainAreaGraphicsScene(QGraphicsScene):
    receivedBodyDrop = pyqtSignal(str, QPointF);

    wantsToStopScaling = pyqtSignal(bool);

    def __init__(self, parent, view):
        super(MainAreaGraphicsScene, self).__init__(parent);
        self.view = view;
        self.state = NORMAL

    def scaleModeToggled(self, checked):
        self.state = SCALING if checked else NORMAL;
        self.view.setMouseTracking(checked);
        self.origDist = -1;

    def dragMoveEvent(self, event):
        event.accept();

    def dragEnterEvent(self, event):
        event.acceptProposedAction();

    def dropEvent(self, event):
        #print("Yay!");
        #print(event.mimeData().text());
        self.receivedBodyDrop.emit(event.mimeData().text(), event.scenePos());

    def mousePressEvent(self, mouseEvent):
        if self.state == SCALING:
            mouseEvent.accept();
            self.wantsToStopScaling.emit(True);
            return
        super(MainAreaGraphicsScene, self).mousePressEvent(mouseEvent)

    def mouseMoveEvent(self, mouseEvent):
        if self.state == SCALING:
            screenRoot = QPointF(0, 0)
            if self.origDist == -1:
                origMousePos = mouseEvent.screenPos();
                self.origDist = pointDistance(origMousePos, screenRoot);
                self.origScale = [item.scale() for item in self.selectedItems()];                
            dist = pointDistance(mouseEvent.screenPos(), screenRoot);
            #print(dist);
            threshold = (dist - self.origDist) / self.origDist *3;
            for idx, item in enumerate(self.selectedItems()):
                item.setScale(self.origScale[idx]*(1+threshold))
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