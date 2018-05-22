from functools import partial
from base64 import b64encode, b64decode
import json
import re
import pandas as pd
import os
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *


class LineWidthDialog(QDialog):
    '''A window with a slider to set line width of annotations
    '''
    def __init__(self, allshapes=None, scene=None, parent=None):
        super(LineWidthDialog, self).__init__(parent)
        self.setWindowTitle("Line width editor")
        self.scene=scene
        self.allshapes=allshapes
        self.lwidth=allshapes[0].point_size
        
        self.form=QGridLayout(self)
        
        self.form.addWidget(QLabel("Please set line width"), 0, 0)

        self.slider=QSlider(Qt.Horizontal)
        self.slider.setTickPosition(QSlider.TicksBothSides)
 
        self.slider.setMinimum(0)
        self.slider.setMaximum(10)
        self.slider.setValue(self.lwidth)
        self.form.addWidget(self.slider, 1, 0)
        self.buttonBox=QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, Qt.Horizontal)

        self.form.addWidget(self.buttonBox,2,0)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        self.accepted.connect(self.extractInputs)
        
    def extractInputs(self):   
        self.size = self.slider.value()
        if self.size != self.lwidth:
            self.scene.point_size=self.size
            for shape in self.allshapes:
                shape.point_size=self.size
        
class EpsilonSliderDialog(QDialog):
    '''A window with a slider to set attraction epsilon, i.e. pull the cursor
    to the first point of the shape if epsilon close
    '''
    def __init__(self, scene=None, parent=None):
        super(EpsilonSliderDialog, self).__init__(parent)
        self.setWindowTitle("Attraction epsilon editor")
        self.scene=scene
        
        self.epsilon=self.scene.epsilon
        
        self.form=QGridLayout(self)
        
        self.form.addWidget(QLabel("Please set epsilon"), 0, 0)

        self.slider=QSlider(Qt.Horizontal)
        self.slider.setTickPosition(QSlider.TicksBothSides)
 
        self.slider.setMinimum(0)
        self.slider.setMaximum(2*self.epsilon)
        self.slider.setValue(self.epsilon)
        self.form.addWidget(self.slider, 1, 0)
        self.buttonBox=QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, Qt.Horizontal)

        self.form.addWidget(self.buttonBox,2,0)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        self.accepted.connect(self.extractInputs)
        
    def extractInputs(self):   
        self.newepsilon = self.slider.value()
        if self.newepsilon != self.epsilon:
            self.scene.epsilon=self.newepsilon
       
        


class PropertiesWindow(QDialog):
    '''A window that pops up on right click (see mousepressevent in qscene).
    Lets the user reassign an annotated ("closed") shape to a different label class.
    '''
    def __init__(self, shape=None, all_labels=[None], parent=None):
        super(PropertiesWindow, self).__init__(parent)
        self.shape=shape
        self.points = self.shape.points
        self.objtype=self.shape.objtype
        self.label=self.shape.label
        self.all_labels=all_labels
        self.setWindowTitle("Properties editor")
        self.label_names=[label.name for label in all_labels if label is not None]

        self.form=QGridLayout(self)
        
        self.form.addWidget(QLabel("Object properties"), 0, 0)

        self.qbox=QComboBox(self)
        self.qbox.addItem(self.label)
        [self.qbox.addItem(label) for label in self.label_names if label != self.label]
        

        self.form.addWidget(QLabel("Type:"), 1, 0)
        self.form.addWidget(QLabel(self.objtype),1,1)
        self.form.addWidget(QLabel("Label:"), 2, 0)
        self.form.addWidget(self.qbox, 2, 1)
                
        
        self.buttonBox=QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, Qt.Horizontal)
        self.form.addWidget(self.buttonBox,3,0)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        self.accepted.connect(self.extractInputs)

        
    def extractInputs(self):
        oldlabel=self.shape.label
        newlabel=self.qbox.currentText()
        if oldlabel != newlabel:
            if oldlabel in self.label_names:
                self.all_labels[self.label_names.index(oldlabel)].untieShape(self.shape)
                newlabelclass=self.all_labels[self.label_names.index(newlabel)]
                newlabelclass.assignObject(self.shape)
        return
    


    
    
class LabelDialog(QDialog):
    '''Label editor form. Given # of new classes to initiate (nlabels) pops up
    a form with a line editor to name a class and a button to set label color.
    If nlabel=0, the form features only already initialized labels for editing.
    '''
    def __init__(self, nlabels=1, prelabels=None, parent=None):
        super(LabelDialog, self).__init__(parent)
        self.names=[]
        self.colors=[None for i in range(nlabels)]
        self.prelabels=prelabels
        self.setWindowTitle("Initialize labels")
        self.lineedits=[]
        
        
        self.form=QGridLayout(self)  
        self.form.addWidget(QLabel("Please give description of labels below:"), 0, 0)
        self.buttonBox=QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, Qt.Horizontal)
        
        if prelabels is not None:
            self.prenames=[label.name for label in prelabels]
            self.precolors=[label.fillColor for label in prelabels]
            nprelabels=len(prelabels)
            self.colors=self.colors+nprelabels*[None]
            [self.addLabelInfo(index, prelabdata=[self.prenames[index], self.precolors[index]]) for index in range(nprelabels)]
            [self.addLabelInfo(index) for index in range(nprelabels,nprelabels+nlabels)]
            self.form.addWidget(self.buttonBox,2*(nprelabels+nlabels)+1,0)
        else:
            [self.addLabelInfo(index) for index in range(nlabels)]
            self.form.addWidget(self.buttonBox,2*nlabels+1,0)

        
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        self.accepted.connect(self.extractInputs)
        self.rejected.connect(self.clearInputs)

    def extractInputs(self):
        self.names=[lineedit.text() for lineedit in self.lineedits]
        return
    
    def clearInputs(self):
        self.names=[]
        self.colors=[None for i in range(len(self.colors))]
        if self.prelabels is not None:
            self.names=self.prenames
            self.colors=self.precolors
        return
    
    def addLabelInfo(self, labelindex, prelabdata=2*[None]):
        lineEdit=QLineEdit(self)
        button = QPushButton('Select color', self)
        labelname=QLabel('Label {} name'.format(labelindex+1))
        labelcolor=QLabel('Label {} color'.format(labelindex+1))
        
        if prelabdata[0] is not None:
            lineEdit.setText("{}".format(prelabdata[0]))
            color=prelabdata[1]
            self.colors[labelindex]=color
            palette = button.palette()
            role = button.backgroundRole()
            palette.setColor(role, color)
            button.setPalette(palette)
            button.setAutoFillBackground(True)
        
        button.clicked.connect(lambda: self.selectColor(labelindex))
            
        self.lineedits.append(lineEdit)
        self.form.addWidget(labelname, 2*labelindex+1,0)
        self.form.addWidget(lineEdit,2*labelindex+1,1)
        self.form.addWidget(labelcolor, 2*labelindex+2,0)
        self.form.addWidget(button,2*labelindex+2,1)

        
    def selectColor(self, labelindex):
        dialogue=QColorDialog()
        dialogue.exec()
        color=dialogue.selectedColor()
        self.colors[labelindex]=color
        
        button = QPushButton('Select color', self)
        palette = button.palette()
        role = button.backgroundRole()
        palette.setColor(role, color)
        button.setPalette(palette)
        button.setAutoFillBackground(True)
        button.clicked.connect(lambda: self.selectColor(labelindex))
        self.form.addWidget(button,2*labelindex+2,1)
        return


class ToolButton(QToolButton):
    '''Overwrite QToolButton to ensure all buttons are of same size
    '''
    minSize = (80, 80)
    def minimumSizeHint(self):
        ms = super(ToolButton, self).minimumSizeHint()
        w1, h1 = ms.width(), ms.height()
        w2, h2 = self.minSize
        ToolButton.minSize = max(w1, w2), max(h1, h2)
        return QSize(*ToolButton.minSize)

def process(filename, default=None):
    '''Return bytes for an image given its path
    '''
    try:
        with open(filename, 'rb') as f:
            return f.read()
    except:
        return default

def newAction(parent, text, slot=None, shortcut=None, icon=None,
        tip=None, checkable=False, enabled=True):
    '''Initialize an action with flags as requested'''
    a = QAction(text, parent)

    if shortcut is not None:
        if isinstance(shortcut, (list, tuple)):
            a.setShortcuts(shortcut)
        else:
            a.setShortcut(shortcut)
    if tip is not None:
        a.setToolTip(tip)
    if slot is not None:
        a.triggered.connect(slot)
    if checkable:
        a.setCheckable(True)
    a.setEnabled(enabled)
    return a


def distance(delta):
    '''Squared euclidean distance as metric. Returns distance given an elementwise delta
    '''
    return (delta.x()**2 + delta.y()**2)

class LabelClass(object):
    '''Class to keep record of a label class characteristics with a method to
    assign shapes to it
    '''
    def __init__(self):
        self.polygons = []
        self.fillColor=None
        self.name=None

    def assignObject(self, obj):
        self.polygons.append(obj)
        obj.line_color=self.fillColor
        obj.label=self.name
        
    def untieShape(self, obj):
        self.polygons.pop(self.polygons.index(obj))


class Annotationscene(object):
    '''Class to store and save outputs as .csv and .json
    '''
    def __init__(self, filename=None):
        self.polygons = None
        self.imagePath = None
        self.imageData = None
        self.filename=None
        self.lineColor=None
        self.imsizes=None
        self.object_types=None
        self.labels=None
        self.savebytes=False
    
    def shapes_to_pandas(self):
        imsize, objects, types, labels = self.imsizes, self.shapes, self.object_types, self.labels
        df=pd.DataFrame(columns=['width', 'height', 'Object', 'X', 'Y'])
        for i, obj in enumerate(objects):
            X, Y=list(zip(*obj))
            df=df.append(pd.DataFrame({'width': imsize[0], 'height': imsize[1], 'Object': i+1, 'Type': types[i], 'Label': labels[i], 'X': X, 'Y': Y}), ignore_index=True)
        return df

    def save(self):

        self.imData = b64encode(self.imageData).decode('utf-8')
        self.shapes=[[(point.x(), point.y()) for point in poly] for poly in self.polygons]
        self.shapes_to_pandas().to_csv(re.search(re.compile('(.+?)(\.[^.]*$|$)'), self.filename).group(1)+'.csv', sep=',')
        if self.savebytes:
            try:
                with open(self.filename, 'w') as f:
    
                    json.dump({
                        'objects': self.shapes,
                        'type': self.object_types,
                        'label': self.labels,
                        'width/height': self.imsizes,
                        'lineColor': self.lineColor,
                        'imagePath': self.imagePath,
                        'imageData': self.imData},
                        f, ensure_ascii=True, indent=2)
            except:
                pass
        else:
            try:
                with open(self.filename, 'w') as f: 
                        json.dump({
                            'objects': self.shapes,
                            'type': self.object_types,
                            'label': self.labels,
                            'width/height': self.imsizes,
                            'lineColor': self.lineColor,
                            'imagePath': self.imagePath},
                            f, ensure_ascii=True, indent=2)
            except:
                pass

 

class Shape(QGraphicsItem):
    '''The main class controlling shape's points, its color, highlight behavior
    '''
    line_color = QColor(0, 6, 255)
    select_line_color = QColor(255, 255, 255)
    vertex_fill_color = QColor(0, 255, 0, 255)
    hvertex_fill_color = QColor(255, 0, 0)
    point_size = 1.5
    hsize = 3.0

    def __init__(self, line_color=None, point_size=None, parent=None):
        super(Shape, self).__init__(parent)
        self.points = []
        self.selected = False
        self.painter = QPainter()
        self.hIndex = None
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.closed = False
        self.points_adjusted=None
        self.objtype=None
        self.label=None
        
        if line_color is not None:
            self.line_color = line_color

        if point_size is not None:
            self.point_size = point_size

    def addPoint(self, point):
        self.setSelected(True)
        if self.points and point == self.points[0]:
            self.closed = True
        else:
            self.points.append(point)

    def popPoint(self):
        if self.points:
            return self.points.pop()
        return None

    def paint(self, painter, option, widget):

        if self.points:
            self.prepareGeometryChange()
            color = self.select_line_color if self.selected else self.line_color
            pen = QPen(color)
            pen.setWidth(self.point_size/2)
            painter.setPen(pen)
            path=self.shape()
            if self.closed == True:
                path.closeSubpath()
            painter.drawPath(path)
            vertex_path=QPainterPath()
            self.drawVertex(vertex_path, 0)
            [self.drawVertex(vertex_path, i) for i in range(len(self.points))]
            painter.drawPath(vertex_path)
            painter.fillPath(vertex_path, self.vertex_fill_color)


    def drawVertex(self, path, index):
        psize = self.point_size
        if index == self.hIndex:
            psize = self.hsize
        if self.hIndex is not None:
            self.vertex_fill_color = self.hvertex_fill_color
        else:
            self.vertex_fill_color = Shape.vertex_fill_color
        path.addEllipse(self.mapFromScene(self.points[index]), psize, psize)
 

    def shape(self):
        path = QPainterPath()
        polygon=self.mapFromScene(QPolygonF(self.points))
        path.addPolygon(polygon)
        return path

    def boundingRect(self):
        return self.shape().boundingRect()

    def moveBy(self, tomove, delta):
        if tomove=='all':
            tomove=slice(0,len(self.points))
        else:
            tomove=slice(tomove,tomove+1)
        self.points[tomove] = [point + delta for point in self.points[tomove]]

    def highlightVertex(self, index):
        self.hIndex = index

    def highlightClear(self):
        self.hIndex = None
        self.selected = False

    def __len__(self):
        return len(self.points)

    def __getitem__(self, index):
        return self.points[index]

    def __setitem__(self, index, value):
        self.points[index] = value


CURSOR_DEFAULT = Qt.ArrowCursor
CURSOR_POINT   = Qt.PointingHandCursor
CURSOR_DRAW    = Qt.CrossCursor
CURSOR_MOVE    = Qt.ClosedHandCursor
CURSOR_GRAB    = Qt.OpenHandCursor

class SubQGraphicsScene(QGraphicsScene):
    '''Overwrite QGraphicsScene to prescribe actions to mouse events, 
    collect annotated shapes and label classes, tracks which mode the program is in
    at any moment (drawing, navigating, moving)
    '''
    NAVIGATION, DRAWING, MOVING = 0, 1, 2
    POLYDRAWING, POLYREADY = 0, 1
    epsilon=30.0
    def __init__(self, parent=None):
        super(SubQGraphicsScene, self).__init__(parent)
        self.mode=self.NAVIGATION
        self.QGitem=None
        self.polys=[]
        self._cursor = CURSOR_DEFAULT
        self.overrideCursor(self._cursor)
        self.line=None
        self.lineColor=QColor(3,252,66)
        self.shapeColor=QColor(0, 6, 255)
        self.selectedVertex=None
        self.selectedShape=None
        self.polystatus=self.POLYDRAWING
        self.objtypes=[]
        self.labelclasses=[]
        self.labelmode=0 #the default class
        self.initializeClass('default', QColor(0, 6, 255)) #initialize default class
        self.point_size=1.5
        
    def drawing(self):
        return self.mode == self.DRAWING

    def navigating(self):
        return self.mode == self.NAVIGATION

    def moving(self):
        return self.mode == self.MOVING

    def polygon_not_finished(self):
        return self.polystatus == self.POLYDRAWING

    def polygonfinished(self):
        return self.polystatus == self.POLYREADY

    def vertexSelected(self):
        return self.selectedVertex is not None

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Delete:
            self.deleteSelected()

            
    def refreshShapestoLabels(self, labelclass):
        labelpolygons=labelclass.polygons
        labelclass.polygons=[]
        [labelclass.assignObject(shape) for shape in labelpolygons]
        return

    def initializeClasses(self, names, colors):
        for c, name in enumerate(names):
            if (c<len(self.labelclasses)):
                self.initializeClass(name, colors[c], labelclass=self.labelclasses[c])
                self.refreshShapestoLabels(labelclass=self.labelclasses[c])
            else:
                self.initializeClass(name, colors[c])

    def updateColor(self, color):
        self.shapeColor=color
        active_labelclass=self.labelclasses[self.labelmode]
        active_labelclass.fillColor=self.shapeColor
        self.refreshShapestoLabels(labelclass=active_labelclass)

        return

    def setLabelMode(self, classindex):
        labelclass=self.labelclasses[classindex]
        self.labelmode=classindex
        self.shapeColor=labelclass.fillColor
        return
        
        
    def initializeClass(self, name, color, labelclass=None):
        ind=None
        if labelclass is None:
            labelclass=LabelClass()
        else:
            ind=self.labelclasses.index(labelclass)
        labelclass.name=name
        labelclass.fillColor=color
        if ind is not None:
            self.labelclasses[ind]=labelclass
        else:
            self.labelclasses.append(labelclass)

    def triggerClosure(self):
        self.finalisepoly(premature=True)

    def mousePressEvent(self, event):
        '''Draw, move vertices/shapes, open properties window'''
        pos = event.scenePos()

        if (event.button() == Qt.RightButton):
            if self.selectedShape:
                all_labels=[None]
                if len(self.labelclasses) > 0:
                    all_labels=self.labelclasses
                propdialog=PropertiesWindow(shape=self.selectedShape, all_labels=all_labels)
                propdialog.move(event.screenPos())
                propdialog.exec()

        if self.drawing() & (event.button() == Qt.LeftButton):
            self.overrideCursor(CURSOR_DRAW)
            #update the tail of the pointing line
            if self.line and self.polygon_not_finished():
                self.line.points[0]=pos
                self.line.setPos(pos)
            #initialize a pointing line for a new polygon
            elif self.line==None or self.polygonfinished():
                self.line=Shape(point_size=self.point_size)
                self.addItem(self.line)
                self.line.setPos(pos)
                self.line.addPoint(pos)

            if self.QGitem:
                #attract the cursor to the start point of the polygon and close it
                if len(self.QGitem.points) > 1 and self.closeEnough(pos, self.QGitem.points[0]):

                    pos = self.QGitem.points[0]
                    self.overrideCursor(CURSOR_POINT)
                    self.QGitem.highlightVertex(0)

                self.QGitem.addPoint(pos)
                if (self.QGitem.points[0]==pos):
                    self.finalisepoly()


            else:
                self.polystatus=self.POLYDRAWING
                self.QGitem=Shape(point_size=self.point_size)

                self.addItem(self.QGitem)
                self.QGitem.setPos(pos)
                self.QGitem.addPoint(pos)
                self.QGitem.setZValue(len(self.polys)+1)
            self.update()
            event.accept()

        elif self.moving() & (event.button() == Qt.LeftButton):
            self.overrideCursor(CURSOR_GRAB)
            self.selectShapebyPoint(pos)
            self.prevPoint=pos
            event.accept()
            self.update()

        elif self.navigating():
            self.overrideCursor(CURSOR_GRAB)
            self.update()


    def mouseMoveEvent(self, event):
        '''Track the movement of the cursor and update selections/drawings'''
        pos = event.scenePos()

        if self.drawing():
            self.overrideCursor(CURSOR_DRAW)

            if self.QGitem:

                if len(self.QGitem.points)==1:  #initialize the pointing line collapsed to a point
                    self.line.points=[self.QGitem.points[0], self.QGitem.points[0]]
                colorLine = self.lineColor
                if len(self.QGitem) > 1 and self.closeEnough(pos, self.QGitem[0]):
                    pos = self.QGitem[0]
                    colorLine = self.QGitem.line_color
                    self.overrideCursor(CURSOR_POINT)
                    self.QGitem.highlightVertex(0)

                if len(self.line.points)==2: #update the pointing line
                   self.line.points[1]=pos
                else: #load the pointing line (if another shape was just created)
                   self.line.addPoint(pos)

                self.line.line_color = colorLine
                self.update()
            return

        #moving shapes/vertices
        if self.moving and Qt.LeftButton & event.buttons():
            self.overrideCursor(CURSOR_GRAB)
            if self.vertexSelected():
                self.moveVertex(pos)
                self.update()
            elif self.selectedShape and self.prevPoint:
                self.moveShape(self.selectedShape, pos)
                self.update()
            return


        #update selections/highlights based on cursor location

        #check if any vertex is epsilon close to the cursor position and find the corresponding shape
        id_point=[[i for i, y in enumerate(poly.points) if distance(pos-y)<=self.epsilon] for poly in self.polys]
        id_shape=[i for i, y in enumerate(id_point) if y != []]

        itemUnderMouse=self.itemAt(pos, QTransform())
        
        #if shape/vertex combination found, highlight vertex and shape
        if id_shape != []:
            self.selectedVertex=id_point[id_shape[0]][0]
            self.selectShape(self.items()[:-1][::-1][id_shape[0]])
            self.selectedShape.highlightVertex(self.selectedVertex)
            self.update()
            return
        elif itemUnderMouse in self.items()[:-1]: #if the cursor is inside of a shape, highlight it
            self.selectedVertex = None
            self.selectShape(itemUnderMouse)
            self.selectedShape.hIndex=None
            self.update()
            return
        else:#nothing found: no shape under the cursor, no vertices in vicinity, clear all
            self.clearShapeSelections()
            self.selectedVertex = None
            self.update()
            return

        event.accept()

    def mouseReleaseEvent(self,event):
        if self.navigating or (event.button() == Qt.LeftButton and self.selectedShape):
            self.overrideCursor(CURSOR_DEFAULT)
            self.update()
        event.accept()

    def closeEnough(self, p1, p2):
        return distance(p1 - p2) < self.epsilon

    def finalisepoly(self, premature=False):
        if self.QGitem:
            if premature:
                if len(self.QGitem.points)==1:
                    self.objtypes.append('Point')
                    self.QGitem.objtype='Point'
                else:
                    self.objtypes.append('Line')
                    self.QGitem.objtype='Line'
            else:
                self.objtypes.append('Polygon')
                self.QGitem.objtype='Polygon'
            if self.line:
                self.removeItem(self.line)
                self.line.popPoint()
            self.polys.append(self.QGitem)
            if self.labelmode is not None:
                labelobject=self.labelclasses[self.labelmode]
                labelobject.assignObject(self.QGitem)
                self.QGitem.label=labelobject.name
            self.QGitem = None
            self.polystatus=self.POLYREADY
            self.update()

    def overrideCursor(self, cursor):
        self._cursor = cursor
        QApplication.setOverrideCursor(cursor) 

    def deleteSelected(self):
        if self.selectedShape:
            shape = self.items()[:-1][::-1].index(self.selectedShape)
            self.polys.pop(shape)
            self.objtypes.pop(shape)
            self.removeItem(self.selectedShape)
            labelind=self.findShapeInLabel(self.selectedShape)
            if len(labelind) > 0:
                label, shapeind = labelind[0]
                self.labelclasses[label].polygons.pop(shapeind)
            self.selectedShape = None
            print('Shape deleted')
            self.update()
            return

    def findShapeInLabel(self, shape):
        if len(self.labelclasses) > 0:
            labelpolys=[l.polygons for l in self.labelclasses]
            return ([(i, label.index(shape)) for i, label in enumerate(labelpolys) if shape in label])
        else:
            return 2*[None]            



    def selectShape(self, shape):
        shape.selected = True
        self.selectedShape = shape
        self.update()

    def selectShapebyPoint(self, point):
        """Select the first shape created which contains this point."""
        if self.vertexSelected(): # A vertex is marked for selection.
            self.selectedShape.highlightVertex(self.selectedVertex)
            return

        itemUnderMouse=self.itemAt(point, QTransform())
        if itemUnderMouse in self.items()[:-1]:
            self.selectShape(itemUnderMouse)
            return

    def clearShapeSelections(self):
        if self.selectedShape:
            self.selectedShape.highlightClear()
            self.selectedShape = None
            self.update()

    def moveVertex(self, pos):
        self.selectedShape.moveBy(self.selectedVertex, pos - self.selectedShape[self.selectedVertex])


    def moveShape(self, shape, pos):
        delta = pos - self.prevPoint
        if delta:
            shape.moveBy('all', delta)
            self.prevPoint = pos
            self.update()
            return True
        return False


class QViewer(QGraphicsView):
    '''Initializes the scene, sets images, controls wheel event
    '''
    def __init__(self, parent=None):
        super(QViewer, self).__init__(parent)
        self.scene = SubQGraphicsScene()
        self.photo = QGraphicsPixmapItem()
        self.photo.setZValue(-1)
        self.scene.addItem(self.photo)
        self.setScene(self.scene)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setBackgroundBrush(QBrush(QColor(30, 30, 30)))
        self.setFrameShape(QFrame.NoFrame)
        self.pixmap = QPixmap()



    def setPhoto(self, pixmap=None):

        if pixmap and not pixmap.isNull():
            self.setDragMode(QGraphicsView.ScrollHandDrag)
            self.photo.setPixmap(pixmap)
            self.fitInView(self.sceneRect(), Qt.KeepAspectRatio)
            self.pixmap=pixmap
        else:
            self.setDragMode(QGraphicsView.NoDrag)
            self.photo.setPixmap(QPixmap())

    def wheelEvent(self, event):
        if not self.photo.pixmap().isNull():

            factor=1.1
            if event.angleDelta().y() > 0:
                QGraphicsView.scale(self,factor,factor)
            else:
                QGraphicsView.scale(self,1/factor,1/factor)


class MainWindow(QMainWindow):
    '''A window with 3 menu tabs, 2 list widgets on the right and a toolbar
    populated with buttons on the left. Initializes and defines actions, connects
    them to the scene
    '''
    def __init__(self):
        super(MainWindow, self).__init__()
        self.imageData = None
        self.imagePath = None
        self.imsizes = None
        self.viewer = QViewer(self)
        self.viewer.setViewportUpdateMode(QGraphicsView.BoundingRectViewportUpdate)
        self.setCentralWidget(self.viewer)
        self.annotationscene=Annotationscene()
        self.shapestoload=None
        self.imname=None
        self.imlist=[]
        self.currentPath=None
        self.object_types=None
        self.savebytes=False
        
        self.currentlabel=None
        self.modedict={0: 'navigation', 1: 'drawing', 2: 'moving'}
        
        self.labelnames=None
        self.labelcolors=None

        self.statusbar = self.statusBar()

        self.fileListWidget = QListWidget()
        self.fileListWidget.itemDoubleClicked.connect(self.imagenameDoubleClicked)
        filelistLayout = QVBoxLayout()
        filelistLayout.setContentsMargins(0, 0, 0, 0)
        filelistLayout.addWidget(self.fileListWidget)
        fileListContainer = QWidget()
        fileListContainer.setLayout(filelistLayout)
        self.filedock = QDockWidget(u'Image List', self)
        self.filedock.setObjectName(u'Images')
        self.filedock.setWidget(fileListContainer)
        self.addDockWidget(Qt.RightDockWidgetArea, self.filedock)
        
        self.labelListWidget = QListWidget()
        self.labelListWidget.itemDoubleClicked.connect(self.labelDoubleClicked)
        labellistLayout = QVBoxLayout()
        labellistLayout.setContentsMargins(0, 0, 0, 0)
        labellistLayout.addWidget(self.labelListWidget)
        labelListContainer = QWidget()
        labelListContainer.setLayout(labellistLayout)
        self.labeldock = QDockWidget(u'Label List', self)
        self.labeldock.setObjectName(u'Label')
        self.labeldock.setWidget(labelListContainer)
        self.addDockWidget(Qt.RightDockWidgetArea, self.labeldock)


        action = partial(newAction, self)
        quitaction = action('&Quit', self.close, 'Ctrl+Q', 'quit', 'Quit application')
        openshort = action('&Open', self.handleOpen,'Ctrl+O', 'open', 'Open image')
        save = action('&Save', self.saver,
           'Ctrl+S', 'save', 'Save labels to file', enabled=True)
        linecolorselect = action('&Select line color', self.setLineColor, 'Ctrl+G')
        shapecolorselect = action('&Select shape color', self.setShapeColor, 'Ctrl+H')
        setEditing = action('&Drawing Mode', self.setEditing, 'E', 'Drawing', 'Enable drawing mode')
        setMoving = action('&Moving Mode', self.setMoving, 'M', 'Moving', 'Enable moving mode')
        setNavigating = action('&Navigation Mode', self.setNavigating, 'N', 'Navigating', 'Enable navigation mode')
        setClosed = action('&Annotation complete', self.setClosure, 'C', 'Closing shape', 'Complete current annotation')
        initLabels = action('&Initialize labels', self.initLabels, 'I', 'Label classes initialized', 'Initialize label classes')
        setwidth = action('&Set line width', self.openLineWidthSlider, 'L', 'Line width set', 'Set line width')
        setepsilon = action('&Set attraction epsilon', self.openEpsilonSlider, '[', 'Epsilon set', 'Set epsilon')
        saveoriginal = QAction('&Save original image bytes', self, checkable=True, shortcut="]", triggered=self.checkaction)
        
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('File')
        editMenu = menubar.addMenu('Edit')
        modesMenu = menubar.addMenu('Modes')
        
        self.actions_to_menus(fileMenu, [openshort, save, saveoriginal, quitaction])
        self.actions_to_menus(editMenu, [initLabels, setwidth, setepsilon, linecolorselect, shapecolorselect])
        self.actions_to_menus(modesMenu, [setEditing, setMoving, setNavigating, setClosed])
        
        self.toolbar=QToolBar()
        self.toolbar.clear()
        [self.addbutton(self.toolbar, action) for action in [openshort, save, setEditing, setMoving, setNavigating, setClosed, initLabels, linecolorselect, shapecolorselect, quitaction]]
        self.addToolBar(Qt.LeftToolBarArea, self.toolbar)

    def checkaction(self, checked=False):
        if checked:
            self.savebytes=True
        else:
            self.savebytes=False

    def openLineWidthSlider(self):
        polys=self.viewer.scene.polys
        if len(polys) > 0:
            dialog=LineWidthDialog(allshapes=polys, scene=self.viewer.scene)
            dialog.exec()

    def openEpsilonSlider(self):
        dialog=EpsilonSliderDialog(scene=self.viewer.scene)
        dialog.exec()
            

    def labelDoubleClicked(self, item=None):
        index=self.labelListWidget.indexFromItem(item).row()
        self.viewer.scene.setLabelMode(index)
        self.currentlabel=item.text()
        self.statusbar.showMessage('{} | {} | {}'.format('LOADED: '+self.imname, 'MODE: '+self.modedict[self.viewer.scene.mode], 'LABEL: '+ item.text()))
        return

    def initLabels(self):
        text, okPressed = QInputDialog.getText(self, "Initialize labels", "How many NEW labels to create (type 0 to edit existing list)?", QLineEdit.Normal, "")
        if okPressed and text != '':
            dialog=LabelDialog(nlabels=int(text), prelabels=self.viewer.scene.labelclasses)
            dialog.exec()
            self.labelnames=dialog.names
            self.labelcolors=dialog.colors
            
            self.initlabclasses()
            self.populateLabelList()
            
        return


    def initlabclasses(self):
        self.viewer.scene.initializeClasses(self.labelnames,self.labelcolors)

    def addbutton(self, toolbar, action):
        btn = ToolButton()
        btn.setDefaultAction(action)
        btn.setToolButtonStyle(toolbar.toolButtonStyle())
        toolbar.addWidget(btn)
        toolbar.addSeparator()

    def setClosure(self):
        self.viewer.scene.triggerClosure()

    def setEditing(self):
        self.viewer.scene.mode=self.viewer.scene.DRAWING
        if self.currentlabel is not None:
            self.statusbar.showMessage('{} | {} | {}'.format('LOADED: '+self.imname, 'MODE: '+self.modedict[self.viewer.scene.mode], 'LABEL: '+ self.currentlabel))
        else:
            self.statusbar.showMessage('{} | {} | {}'.format('LOADED: '+self.imname, 'MODE: '+self.modedict[self.viewer.scene.mode], ''))
          
        return

    def setMoving(self):
        self.viewer.scene.mode=self.viewer.scene.MOVING
        if self.currentlabel is not None:
            self.statusbar.showMessage('{} | {} | {}'.format('LOADED:'+self.imname, 'MODE: '+self.modedict[self.viewer.scene.mode], 'LABEL: '+ self.currentlabel))
        else:
            self.statusbar.showMessage('{} | {} | {}'.format('LOADED:'+self.imname, 'MODE: '+self.modedict[self.viewer.scene.mode], ''))
          
        return

    def setNavigating(self):
        self.viewer.scene.mode=self.viewer.scene.NAVIGATION
        if self.currentlabel is not None:
            self.statusbar.showMessage('{} | {} | {}'.format('LOADED: '+self.imname, 'MODE: '+self.modedict[self.viewer.scene.mode], 'LABEL: '+ self.currentlabel))
        else:
            self.statusbar.showMessage('{} | {} | {}'.format('LOADED: '+self.imname, 'MODE: '+self.modedict[self.viewer.scene.mode], ''))
          
        return

    def imagenameDoubleClicked(self, item=None):
        return self.handleOpen(self.currentPath+item.text())

    def saver(self):
        dialogue=QFileDialog()
        dialogue.setLabelText(QFileDialog.Accept, "Save")
        dialogue.setNameFilter("*.json")
        dialogue.setDefaultSuffix('json')
        dialogue.selectFile(self.imname)
        dialogue.exec()
        savepath=dialogue.selectedFiles()
        if savepath:
            return self.saveFile(filename=savepath[0], polygons=self.viewer.scene.polys, object_types=self.viewer.scene.objtypes,
                                 labels=self.labelAssigner(), colors=[shape.line_color.name() for shape in self.viewer.scene.polys])
   
    def labelAssigner(self):
        if len(self.viewer.scene.labelclasses) > 0:
            shapetolabel=[]
            for shape in self.viewer.scene.polys:
                l=self.viewer.scene.findShapeInLabel(shape)
                if len(l)>0:
                    shapetolabel.append(self.viewer.scene.labelclasses[l[0][0]].name)
                else:
                    shapetolabel.append(None)
            
        else:
            shapetolabel=len(self.viewer.scene.polys)*[None]
        return shapetolabel
        
        
    def selectColor(self):
        dialogue=QColorDialog()
        dialogue.exec()
        color=dialogue.selectedColor()
        return color

    def setLineColor(self):
        self.viewer.scene.lineColor=self.selectColor()

    def setShapeColor(self):
        self.viewer.scene.updateColor(self.selectColor())
        self.populateLabelList()

    def actions_to_menus(self,menu,actions):
        for x in actions:
            menu.addAction(x)
        return

    def imageIdentifier(self, path):
        exts=['png', 'jpeg', 'tif', 'tiff', 'bmp', 'json', 'jpg']
        files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f)) and f.split(".")[-1] in exts]
        return files

    def populateLabelList(self):
        labellist = [label.name for label in self.viewer.scene.labelclasses]
        colors=[label.fillColor for label in self.viewer.scene.labelclasses]
           
        self.labelListWidget.clear()
        [self.labelListWidget.addItem(label) for label in labellist]
        [self.labelListWidget.item(i).setForeground(colors[i]) for i in range(len(colors))]
        return
    

    def populateImageList(self):
        self.imlist = self.imageIdentifier(self.currentPath)
        self.fileListWidget.clear()
        [self.fileListWidget.addItem(im) for im in self.imlist]
        return

    def handleOpen(self, path=None):
        self.resetState()
        if not path:
            path = QFileDialog.getOpenFileName(
                self, 'Choose Image')[0]
        
        if path:
            self.imagePath=path
            path_decomposed=re.search(re.compile('^(.+\/)*(.+)\.(.+)$'), self.imagePath)
            self.imname=path_decomposed.group(2)
            self.currentPath=path_decomposed.group(1)
            self.populateImageList()
            
            if path.endswith('.json'):
                self.loadjson(path, jsonfile=True)
            else:
                self.imageData = process(path, None)
                dialog=QMessageBox.question(self, "Label file?", 'Do you have a label file for this image?', QMessageBox.Yes|QMessageBox.No)
                if dialog == QMessageBox.Yes:
                    labelfilepath = QFileDialog.getOpenFileName(self,
   "Select label file", path, "Label Files (*.json)")[0]
                    self.loadjson(labelfilepath)
            
            image = QImage.fromData(self.imageData)
            self.imsizes=(image.size().width(), image.size().height())
            self.viewer.setPhoto(QPixmap.fromImage(image))

            self.loadShapes(self.shapestoload, self.object_types)
            self.populateLabelList()
            self.annotationscene.imagePath=self.imagePath
            self.annotationscene.imageData=self.imageData
            self.annotationscene.imsizes=self.imsizes

            if self.currentlabel is not None:
                self.statusbar.showMessage('{} | {} | {}'.format('LOADED: '+self.imname, 'MODE: '+self.modedict[self.viewer.scene.mode], 'LABEL: '+ self.currentlabel))
            else:
                self.statusbar.showMessage('{} | {} | {}'.format('LOADED: '+self.imname, 'MODE: '+self.modedict[self.viewer.scene.mode], ''))

    def loadjson(self, filename, jsonfile=False):
        try:
            with open(filename, 'rb') as f:
                
                data = json.load(f)
                self.lineColor = data['lineColor']
                self.shapestoload = data['objects']
                self.object_types = data['type']
                self.labels = data['label']
                self.imagePath = data['imagePath']
                
                if jsonfile:
                    if 'imageData' in data:
                        print('HERE')
                        self.imageData = b64decode(data['imageData'])
                    else:
                        self.imageData=process(self.imagePath, None)
        except:
            pass

    def resetState(self):
        if self.imageData:
            self.imageData=None
            self.shapestoload=None
            self.object_types=None
            [self.viewer.scene.removeItem(item) for item in self.viewer.scene.items()[:-1]]
            self.viewer.scene.polys=[]
            for labelclass in self.viewer.scene.labelclasses:
                labelclass.polygons=[]
            self.viewer.scene.update()
            self.viewer.viewport().update()
            return

    def loadShapes(self, polygons, types):
        if self.shapestoload:
            
            if isinstance(self.lineColor[0],str):
                self.lineColor=[QColor(color) for color in self.lineColor]
            self.viewer.scene.labelclasses=[]
            labellist=list(zip(self.labels, self.lineColor))
            labellistuniques=[]
            [labellistuniques.append(x) for x in labellist if x not in labellistuniques]
            labellistuniques=list(zip(*labellistuniques))
            self.labelnames,self.labelcolors = list(labellistuniques[0]),list(labellistuniques[1])
            self.initlabclasses()
            labeldict={self.labelnames[c]: label for c,label in enumerate(self.viewer.scene.labelclasses)}
            
            for ps in range(len(polygons)):
                polygon=Shape()
                polygon.points=[QPointF(p[0], p[1]) for p in polygons[ps]]
                polygon.closed=True
                self.viewer.scene.polys.append(polygon)
                self.viewer.scene.objtypes.append(types[ps])
                self.viewer.scene.addItem(polygon)
                labeldict[self.labels[ps]].assignObject(polygon)


    def saveFile(self, filename, polygons, object_types, labels, colors):
        self.annotationscene.polygons=polygons
        self.annotationscene.filename=filename
        self.annotationscene.lineColor=colors
        self.annotationscene.object_types=object_types
        self.annotationscene.labels=labels
        self.annotationscene.savebytes=self.savebytes
        self.annotationscene.save()
        self.populateImageList()
        if self.currentlabel is not None:
            self.statusbar.showMessage('{} | {} | {}'.format('SAVED: '+self.imname, 'MODE: '+self.modedict[self.viewer.scene.mode], 'LABEL: '+ self.currentlabel))
        else:
            self.statusbar.showMessage('{} | {} | {}'.format('SAVED: '+self.imname, 'MODE: '+self.modedict[self.viewer.scene.mode], ''))


if __name__ == '__main__':

    import sys
    app = QApplication(sys.argv)
    app.setStyleSheet("QToolButton { background-color: gray; }\n"
              "QToolButton:pressed { background-color: green; }\n"
              "QToolButton:hover { color: white }\n");
    window = MainWindow()
    window.setWindowTitle('pyimannotate')
    #window.setWindowState(Qt.WindowFullScreen)
    screenGeometry = QApplication.desktop().screenGeometry()
    x = screenGeometry.width()
    y = screenGeometry.height()
    window.setGeometry(QRect(x/10, y/10, x/1.2, y/1.2))
    window.show()
    sys.exit(app.exec_())
