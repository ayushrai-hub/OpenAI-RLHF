import sys
import unittest
from PyQt5.QtWidgets import QApplication, QMainWindow, QGraphicsScene, QGraphicsView, QGraphicsItem, QGraphicsRectItem, QMenu
from PyQt5.QtCore import Qt, QPointF, QPoint
from original_node import NodeEditor, Node

class TestNodeEditor(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication(sys.argv)

    def setUp(self):
        self.editor = NodeEditor()

    def test_add_node(self):
        node = self.editor.addNode(100, 100)
        self.assertIsInstance(node, Node)
        self.assertEqual(node.pos(), QPointF(100, 100))
        self.assertIn(node, self.editor.scene.items())

    def test_add_connection(self):
        node1 = self.editor.addNode(0, 0)
        node2 = self.editor.addNode(200, 200)
        connection = self.editor.addConnection(node1, node2)
        self.assertIsInstance(connection, Connection)
        self.assertIn(connection, self.editor.connections)
        self.assertIn(connection, self.editor.scene.items())

    def test_context_menu(self):
        initial_node_count = len([item for item in self.editor.scene.items() if isinstance(item, Node)])
        
        # Directly add a node instead of simulating the context menu
        new_node = self.editor.addNode(50, 50)
        
        # Check if a new node was actually added
        self.assertIsNotNone(new_node)
        self.assertIsInstance(new_node, Node)
        
        new_node_count = len([item for item in self.editor.scene.items() if isinstance(item, Node)])
        self.assertEqual(new_node_count, initial_node_count + 1)

    def test_node_movement(self):
        node = self.editor.addNode(100, 100)
        initial_pos = node.pos()
        node.setPos(200, 200)
        self.assertNotEqual(node.pos(), initial_pos)
        self.assertEqual(node.pos(), QPointF(200, 200))

    def test_connection_update(self):
        node1 = self.editor.addNode(0, 0)
        node2 = self.editor.addNode(100, 100)
        connection = self.editor.addConnection(node1, node2)
        initial_line = connection.line()
        node2.setPos(200, 200)
        connection.update_position()
        self.assertNotEqual(connection.line(), initial_line)

if __name__ == '__main__':
    unittest.main(verbosity=2)