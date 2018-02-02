from functools import partial
import re
import os
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *


IMSIZE=(400,400)


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


CURSOR_DEFAULT = Qt.ArrowCursor
CURSOR_POINT   = Qt.PointingHandCursor
CURSOR_DRAW    = Qt.CrossCursor
CURSOR_MOVE    = Qt.ClosedHandCursor
CURSOR_GRAB    = Qt.OpenHandCursor

class SubQGraphicsScene(QGraphicsScene):
    NAVIGATION, SELECTING  = 0, 1
    def __init__(self, parent=None):
        super(SubQGraphicsScene, self).__init__(parent)
        self.mode=self.NAVIGATION
        self.image=QImage()
        self.imcropped=[]
        self._cursor = CURSOR_DEFAULT
        self.sizetocrop=IMSIZE
        self.path=None

    def selecting(self):
        return self.mode == self.SELECTING

    def navigating(self):
        return self.mode == self.NAVIGATION


    def keyPressEvent(self, event):
        if event.key() == Qt.Key_E:
            self.mode=self.SELECTING
            self.overrideCursor(CURSOR_DRAW)
            print('SELECTING')
        if event.key() == Qt.Key_N:
            self.mode=self.NAVIGATION
            self.overrideCursor(CURSOR_GRAB)
            print('Navigating')

            

    def mousePressEvent(self, event):
        '''Draw or move vertices/shapes'''
        pos = event.scenePos()

        if self.selecting() & (event.button() == Qt.LeftButton):
            self.overrideCursor(CURSOR_DRAW)
            rect_to_crop=QRect(pos.x()-self.sizetocrop[0]/2, pos.y()-self.sizetocrop[1]/2, self.sizetocrop[0], self.sizetocrop[1])
            cropped = self.image.copy(rect_to_crop)
            self.imcropped.append('CROPPED')
            cropped.save(self.path+'_'+str(len(self.imcropped))+'.tif')
 
            self.addRect(pos.x()-self.sizetocrop[0]/2, pos.y()-self.sizetocrop[1]/2, self.sizetocrop[0], self.sizetocrop[1])

            self.update()
            return

        elif self.navigating():
            self.overrideCursor(CURSOR_GRAB)
            self.update()
 

    def overrideCursor(self, cursor):
        self._cursor = cursor
        QApplication.setOverrideCursor(cursor) 

 
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

class ToolButton(QToolButton):
    """ToolBar companion class which ensures all buttons have the same size."""
    minSize = (100, 100)
    def minimumSizeHint(self):
        ms = super(ToolButton, self).minimumSizeHint()
        w1, h1 = ms.width(), ms.height()
        w2, h2 = self.minSize
        ToolButton.minSize = max(w1, w2), max(h1, h2)
        return QSize(*ToolButton.minSize)

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.imageData = None
        self.viewer = QViewer(self)
        self.viewer.setViewportUpdateMode(QGraphicsView.BoundingRectViewportUpdate)
        self.setCentralWidget(self.viewer)
        self.currentPath=None


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
        setselecting = action('&Selection Mode', self.setSelecting, 'E', 'Selecting', 'Enable selection mode')
        setNavigating = action('&Navigation Mode', self.setNavigating, 'N', 'Navigating', 'Enable navigation mode')

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('File')
        self.actions_to_menus(fileMenu, [openshort, setselecting, setNavigating, quit])


        self.toolbar=QToolBar()
        self.toolbar.clear()
        [self.addbutton(self.toolbar, action) for action in [openshort, setselecting, setNavigating, quit]]
        self.addToolBar(Qt.LeftToolBarArea, self.toolbar)

    def addbutton(self, toolbar, action):
        btn = ToolButton()
        btn.setDefaultAction(action)
        btn.setToolButtonStyle(toolbar.toolButtonStyle())
        toolbar.addWidget(btn)
        toolbar.addSeparator()
    
    def setSelecting(self):
        self.viewer.scene.mode=self.viewer.scene.SELECTING
        self.viewer.scene.overrideCursor(CURSOR_DRAW)
        return

    def setNavigating(self):
        self.viewer.scene.mode=self.viewer.scene.NAVIGATION
        self.viewer.scene.overrideCursor(CURSOR_GRAB)
        return

    def imagenameDoubleClicked(self, item=None):
        return self.handleOpen(self.currentPath+item.text())


    def imageIdentifier(self, path):
        exts=['png', 'jpeg', 'tif', 'tiff', 'bmp', 'json', 'jpg']
        files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f)) and f.split(".")[-1] in exts]
        return files

    def populateImageList(self):
        self.imlist = self.imageIdentifier(self.currentPath)
        self.fileListWidget.clear()
        [self.fileListWidget.addItem(im) for im in self.imlist]
        return

    def actions_to_menus(self,menu,actions):
        for x in actions:
            menu.addAction(x)
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

            self.viewer.scene.path=self.currentPath+self.imname
            self.imageData = process(path, None)

            image = QImage.fromData(self.imageData)
            self.viewer.scene.image=image
            self.imsizes=(image.size().width(), image.size().height())
            self.viewer.setPhoto(QPixmap.fromImage(image))

        print('LOADED')

    def resetState(self):
        if self.imageData:
            self.imageData=None
            self.viewer.scene.imcropped=[]
            [self.viewer.scene.removeItem(item) for item in self.viewer.scene.items()[:-1]]
            self.viewer.scene.update()
            self.viewer.viewport().update()
            return

if __name__ == '__main__':

    import sys
    app = QApplication(sys.argv)
    app.setStyleSheet("QToolButton { background-color: gray; }\n"
          "QToolButton:pressed { background-color: green; }\n"
          "QToolButton:hover { color: white }\n");
    window = MainWindow()
    #window.setWindowState(Qt.WindowFullScreen)
    screenGeometry = QApplication.desktop().screenGeometry()
    x = screenGeometry.width()
    y = screenGeometry.height()
    window.setGeometry(QRect(x/10, y/10, x/1.2, y/1.2))
    window.show()
    sys.exit(app.exec_())