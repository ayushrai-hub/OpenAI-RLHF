from PyQt5.QtWidgets import QApplication, QMainWindow, QGraphicsScene, QGraphicsLineItem, QGraphicsView, QGraphicsItem, QGraphicsRectItem, QMenu
from PyQt5.QtCore import Qt, QPointF, QLineF, QPoint
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

        self.view.setRenderHint(QPainter.Antialiasing)
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
            self.addNode(pos.x(), pos.y())

    def addNode(self, x: float, y: float) -> 'Node':
        node = Node(x, y)
        self.scene.addItem(node)
        return node

    def addConnection(self, source_node: 'Node', target_node: 'Node') -> 'Connection':
        connection = Connection(source_node, target_node)
        self.scene.addItem(connection)
        return connection

class Node(QGraphicsRectItem):
    def __init__(self, x: float, y: float, width: float = 100, height: float = 50):
        super().__init__(0, 0, width, height)
        self.setPos(x, y)
        self.setFlags(QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemIsSelectable)
        self.setBrush(Qt.lightGray)

    def pos(self) -> QPointF:
        return super().pos()

    def setPos(self, x: float, y: float):
        super().setPos(x, y)

class Connection(QGraphicsLineItem):
    def __init__(self, source_node: 'Node', target_node: 'Node'):
        super().__init__()
        self.source_node = source_node
        self.target_node = target_node
        self.update_position()

    def update_position(self):
        line = QLineF(self.source_node.pos(), self.target_node.pos())
        self.setLine(line)

    def line(self) -> QLineF:
        return super().line()
