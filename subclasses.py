from PyQt5.QtWidgets import QGraphicsScene, QUndoCommand, QGraphicsItem
from PyQt5.QtCore import QStringListModel, QMimeData, pyqtSignal, QPointF, Qt
from PyQt5.QtGui import QTransform
import math

NORMAL = 0;
SCALING = 1;

def pointDistance(p1, p2):
    return math.hypot(p2.x()-p1.x(), p2.y()-p1.y())

class MainAreaGraphicsScene(QGraphicsScene):
    receivedBodyDrop = pyqtSignal(str, QPointF);
    scalingStopped = pyqtSignal(float);
    mouseClickEndedScaling = pyqtSignal(bool);
    mouseIsMovingItems = pyqtSignal(QPointF, QPointF)

    def __init__(self, parent, view):
        super(MainAreaGraphicsScene, self).__init__(parent);
        self.view = view;
        self.state = NORMAL

    def clearInstancesOf(self, cls):
        for item in self.items():
            if isinstance(item, cls):
                self.removeItem(item);

    def scaleModeToggled(self, checked):
        self.state = SCALING if checked else NORMAL;
        self.view.setMouseTracking(checked);
        self.origDist = -1;
        if not checked:
            self.scalingStopped.emit(self.scaleDelta);

    def dragMoveEvent(self, event):
        event.accept();

    def dragEnterEvent(self, event):
        event.acceptProposedAction();

    def dragLeaveEvent(self, event):
        event.acceptProposedAction();

    def dropEvent(self, event):
        #print("Yay!");
        #print(event.mimeData().text());
        self.receivedBodyDrop.emit(event.mimeData().text(), event.scenePos());

    def mousePressEvent(self, mouseEvent):
        if self.state == SCALING:
            mouseEvent.accept();
            return;
        self.origMousePos = mouseEvent.scenePos();
        super(MainAreaGraphicsScene, self).mousePressEvent(mouseEvent)

    def mouseMoveEvent(self, mouseEvent):
        if self.state == SCALING and (Qt.LeftButton == mouseEvent.buttons()):
            screenRoot = QPointF(0, 0)
            if self.origDist == -1:
                origMousePos = mouseEvent.screenPos();
                self.origDist = pointDistance(origMousePos, screenRoot);
                self.origScale = [item.scale() for item in self.selectedItems()];                
            dist = pointDistance(mouseEvent.screenPos(), screenRoot);
            #print(dist);
            threshold = (dist - self.origDist) / self.origDist * 10;
            if threshold<-1: threshold = -0.9999
            items = self.selectedItems();
            for idx, item in enumerate(items):
                item.setScale(self.origScale[idx]*(1+threshold))
            self.scaleDelta = (1+threshold);
        super(MainAreaGraphicsScene, self).mouseMoveEvent(mouseEvent)

    def mouseReleaseEvent(self, mouseEvent):
        if self.state == SCALING:
            # self.scalingStopped.emit(self.scaleDelta);
            self.mouseClickEndedScaling.emit(False);
            return
        if self.state == NORMAL:
            pos = mouseEvent.scenePos();
            item = self.itemAt(pos, QTransform());
            if item and QGraphicsItem.ItemIsMovable | item.flags():
                oPos = self.origMousePos;
                if (oPos.x()!=pos.x() or oPos.y()!=pos.y()):
                    self.mouseIsMovingItems.emit(self.origMousePos, pos)
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


class MoveCommand(QUndoCommand):
    def __init__(self, items, pos1, pos2):
        super(MoveCommand, self).__init__();
        self.items = items;
        self.deltaX = pos2.x() - pos1.x();
        self.deltaY = pos2.y() - pos1.y();

    def undo(self):
        for item in self.items:
            pos = item.pos();
            item.setPos(pos.x()-self.deltaX, pos.y()-self.deltaY);

    def redo(self):
        for item in self.items:
            pos = item.pos();
            item.setPos(pos.x()+self.deltaX, pos.y()+self.deltaY);

class ScaleCommand(QUndoCommand):
    def __init__(self, items, scaleDelta):
        super(ScaleCommand, self).__init__();
        self.items = items;
        self.scaleDelta = scaleDelta;

    def undo(self):
        for item in self.items:
            item.setScale(item.scale()/self.scaleDelta)
    def redo(self):
        for item in self.items:
            item.setScale(item.scale()*self.scaleDelta)

class DeleteCommand(QUndoCommand):
    def __init__(self, items):
        super(DeleteCommand, self).__init__();
        self.items = items;

    def undo(self):
        for item in self.items:
            item.setDeleted(False);

    def redo(self):
        for item in self.items:
            item.setDeleted(True);