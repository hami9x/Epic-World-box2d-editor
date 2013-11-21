import json
import math
import os
from PyQt5.QtWidgets import QFileDialog, QGraphicsRectItem, QGraphicsPolygonItem, QGraphicsEllipseItem, \
QGraphicsLineItem, QGraphicsPixmapItem, QGraphicsItemGroup, QGraphicsItem, QAbstractItemView
from PyQt5.QtGui import QPen, QVector2D, QPolygonF, QBrush, QPixmap, QColor
from PyQt5.QtCore import Qt, QPointF, QRectF, pyqtSignal, QObject
from subclasses import BodyListModel

class BodyItem(QGraphicsRectItem):
	def __init__(self, itemId, bodyspecName, margin):
		super(BodyItem, self).__init__(0, 0, 0, 0);
		self.itemId = itemId;
		self.bodyspecName = bodyspecName;
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

class GridItem(QGraphicsItemGroup):
	def __init__(self, origX, origY, perCell, n):
		super(GridItem, self).__init__();
		length = perCell*n/2;
		pen = QPen(Qt.DashLine);
		pen.setColor(QColor(230, 230, 230))
		pen.setWidth(0);
		x1, y1, x2, y2 = origX-length, origY-length, origX-length, origY+length
		for i in range(1, n):
			line = QGraphicsLineItem(x1, y1, x2, y2, self)
			line.setPen(pen)
			x1, y1, x2, y2 = x1+perCell, y1, x2+perCell, y2
		x1, y1, x2, y2 = origX-length, origY-length, origX+length, origY-length
		for i in range(1, n):
			line = QGraphicsLineItem(x1, y1, x2, y2, self)
			line.setPen(pen)
			x1, y1, x2, y2 = x1, y1+perCell, x2, y2+perCell

class MyJsonEncoder(json.JSONEncoder):
	def default(self, o):
		if isinstance(o, QPointF):
			return {"x": o.x(), "y": o.y()}
		return json.JSONEncoder.default(self, o)

class MainManager(QObject):
	DEFAULT_BODY_SIZE = 50;
	TRANSCOORD_X = 30;
	TRANSCOORD_Y = -30;
	AXIS_LEN = 250;
	UNITS_PER_METER = 30;

	bodiesLoaded = pyqtSignal(dict);

	def __init__(self, renderScene):
		super(MainManager, self).__init__();
		self.renderScene = renderScene;
		self.noPen = QPen(Qt.NoPen);
		self.bodies = {};
		self.bodyInstances = [];
		self.nameIndex = {};
		self.axes = QGraphicsItemGroup();
		renderScene.addItem(self.axes);
		xAxis = QGraphicsItemGroup(self.axes);
		s1, s2 = 10, 4
		x1, y1, x2, y2 = -self.AXIS_LEN, 0, self.AXIS_LEN, 0
		QGraphicsLineItem(x1, y1, x2, y2, xAxis);
		QGraphicsLineItem(x2-s1, y2-s2, x2, y2, xAxis);
		QGraphicsLineItem(x2-s1, y2+s2, x2, y2, xAxis);
		x1, y1, x2, y2 = 0, -self.AXIS_LEN, 0, self.AXIS_LEN
		yAxis = QGraphicsItemGroup(self.axes);
		QGraphicsLineItem(x1, y1, x2, y2, yAxis);
		QGraphicsLineItem(x2-s2, -(y2-s1), x2, -y2, yAxis);
		QGraphicsLineItem(x2+s2, -(y2-s1), x2, -y2, yAxis);
		grid = GridItem(0, 0, self.UNITS_PER_METER, 100);
		renderScene.addItem(grid);
		#print(rect.x(), rect.y(), rect.width(), rect.height())

	def loadFromPBE(self, PBEFile):
		with open(PBEFile, "r") as f:
			baseDir = os.path.dirname(PBEFile);
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

	def cloneBody(self, bodyspecName, dropPos, itemId=None):
		bodyDef = self.bodies[bodyspecName];
		if not itemId:
			if bodyspecName not in self.nameIndex:
				self.nameIndex[bodyspecName] = 0;
			self.nameIndex[bodyspecName] += 1;
			itemId = "{}{}".format(bodyspecName, self.nameIndex[bodyspecName]);
		body = BodyItem(itemId, bodyspecName, 2);
		self.bodyInstances.append(body);
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

	def save(self, file):
		with open(file, "w") as f:
			instancesDef = [];
			for inst in self.bodyInstances:
				pos = inst.scenePos();
				instancesDef.append({"id": inst.itemId, "bodyspec": inst.bodyspecName,
					"pos": {"x": pos.x()/self.UNITS_PER_METER, "y": pos.y()/self.UNITS_PER_METER}});
			output = {"spec": self.bodies, "instances": instancesDef};
			json.dump(output, f, cls=MyJsonEncoder);

	def loadFile(self, file):
		with open(file, "r") as f:
			data = json.load(f);			
			self.bodies = data["spec"];
			for name, body in self.bodies.items():
				shapes = [];
				for shape in body["shapes"]:
					shape["vertices"]=[QPointF(vertex["x"], vertex["y"]) for vertex in shape["vertices"]];
					shapes.append(shape);
				body["shapes"]=shapes;
				self.bodies[name] = body;

			for inst in data["instances"]:
				pos = inst["pos"];
				self.cloneBody(inst["bodyspec"], QPointF(pos["x"]*self.UNITS_PER_METER, pos["y"]*self.UNITS_PER_METER), inst["id"])
			self.bodiesLoaded.emit(self.bodies);
			


class BodyListManager(QObject):
	def __init__(self, listWidget):
		self.listWidget = listWidget;
		self.listWidget.setDragDropMode(QAbstractItemView.DragOnly);
		self.listModel = BodyListModel();
		self.listWidget.setModel(self.listModel)

	def updateList(self, bodies):
		self.listModel.setStringList(list(bodies.keys()))

