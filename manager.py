import json
import math
import os
from PyQt5.QtWidgets import QFileDialog, QGraphicsRectItem, QGraphicsPolygonItem, QGraphicsEllipseItem, \
QGraphicsLineItem, QGraphicsPixmapItem, QGraphicsItemGroup, QGraphicsItem
from PyQt5.QtGui import QPen, QVector2D, QPolygonF, QBrush, QPixmap
from PyQt5.QtCore import Qt, QPointF, QRectF

class BodyItem(QGraphicsRectItem):
	def __init__(self, margin):
		super(BodyItem, self).__init__(0, 0, 0, 0);
		self.margin = margin;
		pen = QPen(Qt.DashLine);
		pen.setWidth(0);
		self.setPen(pen);

	def updateBorder(self):
		margin = self.margin / self.scale();
		rect = self.childrenBoundingRect()
		self.setRect(QRectF(rect.x()-margin, rect.y()-margin, rect.width()+2*margin, rect.height()+2*margin));


class Manager(object):
	DEFAULT_BODY_SIZE = 300;

	def __init__(self, renderScene):
		self.renderScene = renderScene;
		self.noPen = QPen(Qt.NoPen);

	
	def loadBodies(self):
		# file = QFileDialog.getOpenFileName();
		file = ('/home/phaikawl/Dev/Epic World/pobjects.json', 0);
		with open(file[0], "r") as f:
			baseDir = os.path.dirname(file[0]);
			data = json.load(f);
			for body in data["rigidBodies"]:
				self.createBody(body, baseDir);
	
	def createBody(self, bodyDef, baseDir):
		body = BodyItem(2);
		group = QGraphicsItemGroup(body);
		self.renderScene.addItem(body);

		for shape in bodyDef["shapes"]:
			if shape["type"] == "POLYGON":
				vertices = [QPointF(vertex["x"], -vertex["y"]) for vertex in shape["vertices"]]
				newItem = QGraphicsPolygonItem(QPolygonF(vertices));
			if shape["type"] == "CIRCLE":
				vertices = shape["vertices"];
				p1 = QVector2D(vertices[0]["x"], -vertices[0]["y"]);
				p2 = QVector2D(vertices[1]["x"], -vertices[1]["y"]);
				radius = math.hypot(p2.x()-p1.x(), p2.y()-p1.y());
				newItem = QGraphicsEllipseItem(p1.x()-radius, p1.y()-radius, radius*2, radius*2);
			pen = QPen();
			pen.setWidth(0);			
			newItem.setPen(pen);
			newItem.setParentItem(group);
		bounding = group.childrenBoundingRect();
		imagePath = None;
		if (bodyDef["imagePath"]):
			imagePath = os.path.join(baseDir, bodyDef["imagePath"]);
			pm = QGraphicsPixmapItem(QPixmap(imagePath).scaledToWidth(self.DEFAULT_BODY_SIZE), body);
			pm.setFlags(QGraphicsItem.ItemStacksBehindParent);
			pm.setOffset(0, -pm.boundingRect().height());
			group.setScale(self.DEFAULT_BODY_SIZE);
		else:
			group.setScale(self.DEFAULT_BODY_SIZE/bounding.width());
		body.updateBorder();





