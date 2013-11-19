import json
import math
import os
from PyQt5.QtWidgets import QFileDialog, QGraphicsRectItem, QGraphicsPolygonItem, QGraphicsEllipseItem, \
QGraphicsLineItem, QGraphicsPixmapItem, QGraphicsItemGroup, QGraphicsItem, QAbstractItemView
from PyQt5.QtGui import QPen, QVector2D, QPolygonF, QBrush, QPixmap, QColor
from PyQt5.QtCore import Qt, QPointF, QRectF, pyqtSignal, QObject
from subclasses import BodyListModel

class BodyItem(QGraphicsRectItem):
	def __init__(self, margin):
		super(BodyItem, self).__init__(0, 0, 0, 0);
		self.margin = margin;
		pen = QPen(Qt.SolidLine);
		pen.setColor(QColor(230, 230, 230))
		pen.setWidth(0);
		self.setPen(pen);
		self.setFlags(QGraphicsItem.ItemIsSelectable | QGraphicsItem.ItemIsMovable);

	def updateBorder(self):
		margin = self.margin / self.scale();
		rect = self.childrenBoundingRect()
		self.setRect(QRectF(rect.x()-margin, rect.y()-margin, rect.width()+2*margin, rect.height()+2*margin));


class MainManager(QObject):
	DEFAULT_BODY_SIZE = 50;
	TRANSCOORD_X = 30;
	TRANSCOORD_Y = -30;

	bodiesLoaded = pyqtSignal(dict);

	def __init__(self, renderScene):
		super(MainManager, self).__init__();
		self.renderScene = renderScene;
		self.noPen = QPen(Qt.NoPen);
		self.bodies = {};
	
	def loadBodies(self):
		# file = QFileDialog.getOpenFileName();
		file = ('/home/phaikawl/Dev/Epic World/pobjects.json', 0);
		with open(file[0], "r") as f:
			baseDir = os.path.dirname(file[0]);
			data = json.load(f);
			for body in data["rigidBodies"]:
				self.loadBody(body, baseDir);
			self.bodiesLoaded.emit(self.bodies);


	def trans(self, vertexDef):
		return QPointF(vertexDef["x"]*self.TRANSCOORD_X, vertexDef["y"]*self.TRANSCOORD_Y)

	def loadBody(self, bodyDef, baseDir):
		bodyConf = {};
		if (bodyDef["imagePath"]):
			bodyConf["image"] = os.path.join(baseDir, bodyDef["imagePath"])
		else:
			bodyConf["image"] = None;
		bodyConf["shapes"] = [];
		for shape in bodyDef["shapes"]:
			bodyConf["shapes"].append(	{
									"type": shape["type"],
									"vertices": [self.trans(vertex) for vertex in shape["vertices"]]
								}
							);
		self.bodies[bodyDef["name"]] = bodyConf;

	def cloneBody(self, name, dropPos):
		bodyDef = self.bodies[name];
		body = BodyItem(2);
		body.setPos(dropPos);
		group = QGraphicsItemGroup(body);
		self.renderScene.addItem(body);

		for shape in bodyDef["shapes"]:
			vertices = shape["vertices"];
			if shape["type"] == "POLYGON":
				newItem = QGraphicsPolygonItem(QPolygonF(vertices));
			if shape["type"] == "CIRCLE":
				p1, p2 = vertices
				radius = math.hypot(p2.x()-p1.x(), p2.y()-p1.y());
				newItem = QGraphicsEllipseItem(p1.x()-radius, p1.y()-radius, radius*2, radius*2);
			pen = QPen();
			pen.setWidth(0);			
			newItem.setPen(pen);
			newItem.setParentItem(group);
		bounding = group.childrenBoundingRect();
		imagePath = None;
		if (bodyDef["image"]):
			imagePath = bodyDef["image"];
			pm = QGraphicsPixmapItem(QPixmap(imagePath).scaledToWidth(self.DEFAULT_BODY_SIZE), body);
			pm.setFlags(QGraphicsItem.ItemStacksBehindParent);
			pm.setOffset(0, -pm.boundingRect().height());
			group.setScale(self.DEFAULT_BODY_SIZE/self.TRANSCOORD_X);
		else:
			group.setScale(self.DEFAULT_BODY_SIZE/bounding.width());
		body.updateBorder();


class BodyListManager(QObject):
	def __init__(self, listWidget):
		self.listWidget = listWidget;
		self.listWidget.setDragDropMode(QAbstractItemView.DragOnly);
		self.listModel = BodyListModel();
		self.listWidget.setModel(self.listModel)

	def updateList(self, bodies):
		self.listModel.setStringList(list(bodies.keys()))


