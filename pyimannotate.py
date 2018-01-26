from functools import partial
from base64 import b64encode, b64decode
import json
import re
import pandas as pd
import os
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

# def newIcon(icon):
#     return QIcon(':/' + icon)

# def newButton(text, icon=None, slot=None):
#     b = QPushButton(text)
#     if icon is not None:
#         b.setIcon(newIcon(icon))
#     if slot is not None:
#         b.clicked.connect(slot)
#     return b


class ToolButton(QToolButton):
    """ToolBar companion class which ensures all buttons have the same size."""
    minSize = (100, 100)
    def minimumSizeHint(self):
        ms = super(ToolButton, self).minimumSizeHint()
        w1, h1 = ms.width(), ms.height()
        w2, h2 = self.minSize
        ToolButton.minSize = max(w1, w2), max(h1, h2)
        return QSize(*ToolButton.minSize)

def process(filename, default=None):
    try:
        with open(filename, 'rb') as f:
            return f.read()
    except:
        return default

def newAction(parent, text, slot=None, shortcut=None, icon=None,
        tip=None, checkable=False, enabled=True):
    """Create a new action and assign callbacks, shortcuts, etc."""
    a = QAction(text, parent)
    # if icon is not None:
    #     a.setIcon(newIcon(icon))
    if shortcut is not None:
        if isinstance(shortcut, (list, tuple)):
            a.setShortcuts(shortcut)
        else:
            a.setShortcut(shortcut)
    if tip is not None:
        a.setToolTip(tip)
        a.setStatusTip(tip)
    if slot is not None:
        a.triggered.connect(slot)
    if checkable:
        a.setCheckable(True)
    a.setEnabled(enabled)
    return a


def distance(delta):
    return (delta.x()**2 + delta.y()**2)


class Annotationscene(object):
    def __init__(self, filename=None):
        self.polygons = None
        self.imagePath = None
        self.imageData = None
        self.filename=None
        self.fillColor=None
        self.lineColor=None
        self.imsizes=None
        self.object_types=None
    
    def shapes_to_pandas(self):
        imsize, objects, types = self.imsizes, self.shapes, self.object_types
        df=pd.DataFrame(columns=['width', 'height', 'Object', 'X', 'Y'])
        for i, obj in enumerate(objects):
            X, Y=list(zip(*obj))
            df=df.append(pd.DataFrame({'width': imsize[0], 'height': imsize[1], 'Object': i+1, 'Type': types[i], 'X': X, 'Y': Y}), ignore_index=True)
        return df

    def save(self):

        self.imData = b64encode(self.imageData).decode('utf-8')
        self.shapes=[[(point.x(), point.y()) for point in poly] for poly in self.polygons]
        self.shapes_to_pandas().to_csv(re.search(re.compile('(.+?)(\.[^.]*$|$)'), self.filename).group(1)+'.csv', sep=',')

        try:
            with open(self.filename, 'w') as f:

                json.dump({
                    'objects': self.shapes,
                    'type': self.object_types,
                    'width/height': self.imsizes,
                    'lineColor': self.lineColor,
                    'fillColor': self.fillColor,
                    'imagePath': self.imagePath,
                    'imageData': self.imData},
                    f, ensure_ascii=True, indent=2)
        except:
            pass

 

class Shape(QGraphicsItem):

    line_color = QColor(0, 6, 255)
    select_line_color = QColor(255, 255, 255)
    vertex_fill_color = QColor(0, 255, 0, 255)
    hvertex_fill_color = QColor(255, 0, 0)
    point_size = 2
    hsize = 4.0

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
        # xs=[point.x() for point in self.points]
        # ys=[point.y() for point in self.points]
        # return QRectF(min(xs), min(ys), max(xs) - min(xs), max(ys) - min(ys))
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
    NAVIGATION, DRAWING, MOVING = 0, 1, 2
    POLYDRAWING, POLYREADY = 0, 1
    epsilon=100.0
    def __init__(self, parent=None):
        super(SubQGraphicsScene, self).__init__(parent)
        self.mode=self.NAVIGATION
        self.QGitem=None
        self.polys=[]
        self._cursor = CURSOR_DEFAULT
        self.line=None
        self.lineColor=QColor(3,252,66)
        self.shapeColor=QColor(0, 6, 255)
        self.selectedVertex=None
        self.selectedShape=None
        self.polystatus=self.POLYDRAWING
        self.objtypes=[]

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
        # if event.key() == Qt.Key_E:
        #     self.mode=self.DRAWING
        #     self.overrideCursor(CURSOR_DRAW)
        #     print('Drawing')
        # if event.key() == Qt.Key_N:
        #     self.mode=self.NAVIGATION
        #     self.overrideCursor(CURSOR_GRAB)
        #     print('Navigating')
        # if event.key() == Qt.Key_M:
        #     self.mode=self.MOVING
        #     print('Moving')
        if event.key() == Qt.Key_Delete:
            self.deleteSelected()
        # if event.key() == Qt.Key_C:
        #     self.triggerClosure()
            

    def triggerClosure(self):
    	self.finalisepoly(premature=True)

    def mousePressEvent(self, event):
        '''Draw or move vertices/shapes'''
        pos = event.scenePos()

        if self.drawing() & (event.button() == Qt.LeftButton):
            self.overrideCursor(CURSOR_DRAW)
            #update the tail of the pointing line
            if self.line and self.polygon_not_finished():
                self.line.points[0]=pos
                self.line.setPos(pos)
            #initialize a pointing line for a new polygon
            elif self.line==None or self.polygonfinished():
                self.line=Shape()
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
                self.QGitem=Shape()

                self.addItem(self.QGitem)
                self.QGitem.setPos(pos)
                self.QGitem.addPoint(pos)
                self.QGitem.setZValue(len(self.polys)+1)
            self.update()

        elif self.moving() & (event.button() == Qt.LeftButton):
            #self.overrideCursor(CURSOR_GRAB)
            self.selectShapebyPoint(pos)
            self.prevPoint=pos
            event.accept()
            self.update()

        elif self.navigating():
            #self.overrideCursor(CURSOR_GRAB)
            self.update()
        #event.accept()

    def mouseMoveEvent(self, event):
        '''Track the movement of the cursor and update selections/drawings'''
        pos = event.scenePos()

        if self.drawing():
            self.overrideCursor(CURSOR_DRAW)

            if self.QGitem:

                if len(self.QGitem.points)==1:  #initialize the pointing line collapsed to a point
                    self.line.points=[self.QGitem.points[0], self.QGitem.points[0]]
                colorLine = self.lineColor
                colorShape=self.shapeColor
                #attract cursor to the polygons start point if close
                if len(self.QGitem) > 1 and self.closeEnough(pos, self.QGitem[0]):
                    pos = self.QGitem[0]
                    colorLine = self.QGitem.line_color
                    self.overrideCursor(CURSOR_POINT)
                    self.QGitem.highlightVertex(0)

                if len(self.line.points)==2: #update the pointing line
                   self.line.points[1]=pos
                else: #load the pointing line (if another shape was just created)
                   self.line.addPoint(pos)

                self.QGitem.line_color = colorShape
                self.line.line_color = colorLine
                self.update()
            return

        #moving shapes/vertices
        if self.moving and Qt.LeftButton & event.buttons():
            #self.overrideCursor(CURSOR_GRAB)
            if self.vertexSelected():
                self.moveVertex(pos)
                self.update()
            elif self.selectedShape and self.prevPoint:
                self.overrideCursor(CURSOR_MOVE)
                self.moveShape(self.selectedShape, pos)
                self.update()
            return


        #update selections/highlights based on cursor location

        #check if any vertex is epsilon close to the cursor position and find the corresponding shape
        id_point=[[i for i, y in enumerate(poly.points) if distance(pos-y)<=self.epsilon] for poly in self.polys]
        id_shape=[i for i, y in enumerate(id_point) if y != []]

        itemUnderMouse=self.itemAt(pos, QTransform())
        
        #if shape/vertix combination found, highlight vertex and shape
        if id_shape != []:
            self.selectedVertex=id_point[id_shape[0]][0]
            self.selectShape(self.items()[:-1][::-1][id_shape[0]])
            self.selectedShape.highlightVertex(self.selectedVertex)
            self.overrideCursor(CURSOR_POINT)
            self.update()
            return
        elif itemUnderMouse in self.items()[:-1]: #if the cursor is inside of a shape, highlight it
            self.selectedVertex = None
            self.selectShape(itemUnderMouse)
            self.selectedShape.hIndex=None
            self.overrideCursor(CURSOR_GRAB)
            self.update()
            return
        else:#nothing found: no shape under the cursor, no vertices in vicinity, clear all
            self.clearShapeSelections()
            self.selectedVertex = None
            self.update()
            return

        event.accept()

    def mouseReleaseEvent(self,event):
        if event.button() == Qt.LeftButton and self.selectedShape:
            self.overrideCursor(CURSOR_GRAB)
            self.update()
        event.accept()

    def closeEnough(self, p1, p2):
        return distance(p1 - p2) < self.epsilon

    def finalisepoly(self, premature=False):
        if self.QGitem:
            if premature:
                if len(self.QGitem.points)==1:
                    self.objtypes.append('Point')
                else:
                    self.objtypes.append('Line')
            else:
                self.objtypes.append('Polygon')
            if self.line:
                self.removeItem(self.line)
                self.line.popPoint()
            self.polys.append(self.QGitem)
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
            self.selectedShape = None
            print('Shape deleted')
            self.update()
            return

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
    epsilon=121.0
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


        action = partial(newAction, self)
        quit = action('&Quit', self.close, 'Ctrl+Q', 'quit', 'Quit application')
        openshort = action('&Open', self.handleOpen,'Ctrl+O', 'open', 'Open image')
        save = action('&Save', self.saver,
           'Ctrl+S', 'save', 'Save labels to file', enabled=True)
        linecolorselect = action('&Select line color', self.setLineColor, 'Ctrl+G')
        shapecolorselect = action('&Select shape color', self.setShapeColor, 'Ctrl+H')
        setEditing = action('&Drawing Mode', self.setEditing, 'E', 'Drawing', 'Enable drawing mode')
        setMoving = action('&Moving Mode', self.setMoving, 'M', 'Moving', 'Enable moving mode')
        setNavigating = action('&Navigation Mode', self.setNavigating, 'N', 'Navigating', 'Enable navigation mode')
        setClosed = action('&Annotation complete', self.setClosure, 'C', 'Closing shape', 'Complete current annotation')

     
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('File')
        self.actions_to_menus(fileMenu, [openshort, save, setEditing, setMoving, setNavigating, setClosed, linecolorselect, shapecolorselect, quit])
        
        self.toolbar=QToolBar()
        self.toolbar.clear()
        [self.addbutton(self.toolbar, action) for action in [openshort, save, setEditing, setMoving, setNavigating, setClosed, linecolorselect, shapecolorselect, quit]]
        self.addToolBar(Qt.LeftToolBarArea, self.toolbar)

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
        return

    def setMoving(self):
        self.viewer.scene.mode=self.viewer.scene.MOVING
        return

    def setNavigating(self):
        self.viewer.scene.mode=self.viewer.scene.NAVIGATION
        return

    def imagenameDoubleClicked(self, item=None):
    	return self.handleOpen(self.currentPath+item.text())

    def saver(self):
        dialogue=QFileDialog()
        dialogue.setNameFilter("*.json")
        dialogue.setDefaultSuffix('json')
        dialogue.selectFile(self.imname)
        dialogue.exec()
        savepath=dialogue.selectedFiles()
        if savepath:
            return self.saveFile(filename=savepath[0], polygons=self.viewer.scene.polys, object_types=self.viewer.scene.objtypes)
   
    def selectColor(self):
        dialogue=QColorDialog()
        dialogue.exec()
        color=dialogue.selectedColor()
        return color

    def setLineColor(self):
        self.viewer.scene.lineColor=self.selectColor()

    def setShapeColor(self):
        self.viewer.scene.shapeColor=self.selectColor()

    def actions_to_menus(self,menu,actions):
        for x in actions:
            menu.addAction(x)
        return

    def imageIdentifier(self, path):
        exts=['png', 'jpeg', 'tif', 'tiff', 'bmp', 'json', 'jpg']
        files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f)) and f.split(".")[-1] in exts]
        return files

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
            imagePath=path
            path_decomposed=re.search(re.compile('^(.+\/)*(.+)\.(.+)$'), imagePath)
            self.imname=path_decomposed.group(2)
            self.currentPath=path_decomposed.group(1)
            self.populateImageList()

            if path.endswith('.json'):
                self.loadjson(path)
            else:
                self.imageData = process(path, None)

            image = QImage.fromData(self.imageData)
            self.imsizes=(image.size().width(), image.size().height())
            self.viewer.setPhoto(QPixmap.fromImage(image))

            self.loadShapes(self.shapestoload, self.object_types)
            self.annotationscene.imagePath=self.imagePath
            self.annotationscene.imageData=self.imageData
            self.annotationscene.imsizes=self.imsizes
            print('LOADED')

    def loadjson(self, filename):
        try:
            with open(filename, 'rb') as f:
                data = json.load(f)
                self.imagePath = data['imagePath']
                self.imageData = b64decode(data['imageData'])
                self.lineColor = data['lineColor']
                self.fillColor = data['fillColor']
                self.shapestoload = data['objects']
                self.object_types= data['types']

        except:
            pass

    def resetState(self):
        if self.imageData:
            self.imageData=None
            self.shapestoload=None
            self.object_types=None
            [self.viewer.scene.removeItem(item) for item in self.viewer.scene.items()[:-1]]
            self.viewer.scene.polys=[]
            self.viewer.scene.update()
            self.viewer.viewport().update()
            return

    def loadShapes(self, polygons, types):
        if self.shapestoload:
            for ps in range(len(polygons)):
                polygon=Shape()
                polygon.points=[QPointF(p[0], p[1]) for p in polygons[ps]]
                polygon.closed=True
                self.viewer.scene.polys.append(polygon)
                self.viewer.scene.objtypes.append(types[ps])
                self.viewer.scene.addItem(polygon)

    def saveFile(self, filename, polygons, object_types):
        self.annotationscene.polygons=polygons
        self.annotationscene.filename=filename
        self.annotationscene.object_types=object_types
        self.annotationscene.save()
        self.populateImageList()
        print('SAVED')


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
