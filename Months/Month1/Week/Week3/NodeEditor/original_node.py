import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QGraphicsScene, QGraphicsView, QGraphicsItem, QGraphicsRectItem, QMenu
from PyQt5.QtCore import Qt, QRectF, QPointF
from PyQt5.QtGui import QPainter

class NodeEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setGeometry(100, 100, 800, 600)
        self.setWindowTitle('Custom Node Editor')

        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene, self)
        self.setCentralWidget(self.view)

        self.view.setRenderHint(QPainter.Antialiasing)  # Correct attribute for antialiasing
        self.view.setDragMode(QGraphicsView.RubberBandDrag)

        self.scene.setSceneRect(-400, -300, 800, 600)

        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.contextMenuEvent)

        self.show()

    def contextMenuEvent(self, event):
        context_menu = QMenu(self)
        add_node_action = context_menu.addAction('Add Node')
        action = context_menu.exec_(self.mapToGlobal(event.pos()))

        if action == add_node_action:
            pos = self.view.mapToScene(event.pos())
            self.scene.addItem(Node(pos.x(), pos.y()))

class Node(QGraphicsRectItem):
    def __init__(self, x, y, width=100, height=50):
        super().__init__(0, 0, width, height)
        self.setPos(x, y)
        self.setFlags(QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemIsSelectable)
        self.setBrush(Qt.lightGray)

def main():
    app = QApplication(sys.argv)
    editor = NodeEditor()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
