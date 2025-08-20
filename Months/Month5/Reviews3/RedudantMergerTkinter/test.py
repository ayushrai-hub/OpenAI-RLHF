import unittest
import tkinter as tk
from tkinter import Canvas
from io import StringIO
import sys
from ideal_completion import main, ConnectorNode, testcallback  


class TestConnectorNode(unittest.TestCase):
    def setUp(self):
        """Set up the Tkinter environment and the ConnectorNode."""
        self.root = tk.Tk()
        self.canvas = Canvas(self.root, width=400, height=400)
        self.canvas.pack()

        # Initialize the ConnectorNode directly
        self.node = ConnectorNode(self.canvas, node_type="input", width=10, height=10, x=50, y=50)

    def tearDown(self):
        """Destroy the Tkinter root after each test to clean up."""
        self.root.destroy()

    def test_node_initialization(self):
        """Test if the node is initialized correctly.
        This test ensures that the node's properties (e.g., node_type, x, y, color) 
        are set properly during initialization, which is crucial for correct behavior.
        """
        self.assertEqual(self.node.node_type, "input")
        self.assertEqual(self.node.x, 50)
        self.assertEqual(self.node.y, 50)
        self.assertEqual(self.node.color, "purple")

    def test_make_draggable(self):
        """Test if the node can be dragged by checking the event bindings.
        Ensures that drag events are properly bound to the node, as dragging 
        is a core feature of interaction with ConnectorNode.
        """
        self.node.make_draggable()

        # Check if the drag-related events are bound to the node using tag_bind
        press_bindings = self.canvas.tag_bind(self.node.node_id, '<ButtonPress-1>')
        self.assertIsNotNone(press_bindings)

    def test_set_onclick_default(self):
        """Test if the default click handler is set correctly.
        Verifies that the node responds correctly to the default click callback 
        when no custom callback is provided, important for basic interaction.
        """
        click_event = tk.Event()
        click_event.x = 50
        click_event.y = 50

        # Capture print output to verify the default callback is triggered
        captured_output = StringIO()
        sys.stdout = captured_output  # Redirect stdout
        self.node.set_onclick()
        self.node._custom_callback(click_event)  # Call the default click callback

        sys.stdout = sys.__stdout__  # Reset redirect
        self.assertIn("input node clicked", captured_output.getvalue())

    def test_set_onclick_custom(self):
        """Test if a custom click callback can be set and triggered.
        Ensures that the node can accept a user-defined callback function, 
        which is essential for customizing node behavior.
        """
        click_event = tk.Event()
        click_event.x = 50
        click_event.y = 50

        # Capture print output to verify the custom callback is triggered
        captured_output = StringIO()
        sys.stdout = captured_output  # Redirect stdout
        self.node.set_onclick(callback=testcallback)
        self.node._custom_callback(click_event)  # Call the custom callback

        sys.stdout = sys.__stdout__  # Reset redirect
        self.assertIn("Test callback triggered.", captured_output.getvalue())

    def test_start_drag_or_click(self):
        """Test if dragging starts correctly.
        Ensures that the node correctly registers the start of a drag operation 
        and stores the initial drag position, which is key to smooth dragging functionality.
        """
        event = tk.Event()
        event.x, event.y = 50, 50
        # Simulate starting a drag or click
        self.node.start_drag_or_click(event)
        # Check that the drag data and start position are initialized correctly
        self.assertEqual(self.node.drag_start_position, (50, 50))

    def test_do_drag(self):
        """Test if the node is dragged when movement exceeds the drag threshold.
        Verifies that the node switches to 'drag mode' when sufficient movement 
        occurs, ensuring proper handling of dragging actions.
        """
        self.node.make_draggable()
        # Simulate starting the drag
        start_event = tk.Event()
        start_event.x, start_event.y = 50, 50
        self.node.start_drag_or_click(start_event)
        # Simulate dragging beyond the threshold
        drag_event = tk.Event()
        drag_event.x, drag_event.y = 100, 100
        self.node.do_drag(drag_event)
        # Ensure dragging has started
        self.assertTrue(self.node.is_dragging)

    def test_end_drag_or_click(self):
        """Test if the drag or click is ended correctly.
        Ensures that the node correctly ends the drag operation, including resetting 
        necessary variables and triggering any necessary callbacks.
        """
        self.node.make_draggable()

        # Simulate a drag
        start_event = tk.Event()
        start_event.x, start_event.y = 50, 50
        self.node.start_drag_or_click(start_event)

        # Simulate dragging
        drag_event = tk.Event()
        drag_event.x, drag_event.y = 100, 100
        self.node.do_drag(drag_event)

        # Simulate releasing the drag
        end_event = tk.Event()
        end_event.x, end_event.y = 100, 100  # Add the missing x and y attributes

        # Capture the print output to verify if drag end behavior is correctly triggered
        captured_output = StringIO()
        sys.stdout = captured_output  # Redirect stdout

        self.node.end_drag_or_click(end_event)

        sys.stdout = sys.__stdout__  # Reset redirect
        self.assertIn("Drag ended.", captured_output.getvalue())

    def test_main_and_drag(self):
        """Test the integration of dragging in the main application loop.
        Verifies that dragging works in a real use case within the `main` function 
        setup, testing end-to-end interaction within the full application.
        """
        # Create the window and set up the canvas and node
        root, canvas, node = main(start_mainloop=False)

        # Ensure the window is rendered before performing actions
        root.update_idletasks()

        # Simulate a mouse press to start dragging the node at (50, 50)
        canvas.event_generate("<ButtonPress-1>", x=50, y=50)

        # Simulate dragging the node to a new position (e.g., (100, 100))
        canvas.event_generate("<B1-Motion>", x=100, y=100)

        # Simulate releasing the mouse button to stop dragging
        canvas.event_generate("<ButtonRelease-1>", x=100, y=100)

        # Give Tkinter time to process the events
        root.update()

        # Verify that the node has been moved by checking its new coordinates
        coords = canvas.coords(node.node_id)
        self.assertNotEqual(coords, [])  # Ensure the node exists
        self.assertEqual(coords, [95.0, 95.0, 105.0, 105.0])  # Check if node was moved

        # Close the window after the test
        root.after(100, root.quit)  # Schedule window to close after 100ms
        root.update()
        root.destroy()  # Clean up and destroy the window

    def test_main_and_click(self):
        """Test the click functionality in the main application loop.
        Ensures that custom click events are properly registered and triggered 
        within the `main` function setup, confirming interaction correctness.
        """
        # Create the window and set up the canvas and node
        root, canvas, node = main(start_mainloop=False)

        # Ensure the window is rendered before performing actions
        root.update_idletasks()

        # Set a flag to check if the click event works correctly
        self.click_flag = False

        # Define a custom callback to test the click functionality
        def on_node_click(event):
            self.click_flag = True

        # Attach the custom click callback to the node
        node.set_onclick(callback=on_node_click)

        # Simulate a click on the node at the coordinates where it is located (50, 50)
        canvas.event_generate("<Button-1>", x=50, y=50)

        # Give Tkinter time to process the events
        root.update()

        # Verify that the click callback was triggered
        self.assertTrue(self.click_flag, "The click callback was not triggered.")

        # Close the window after the test
        root.after(100, root.quit)  # Schedule window to close after 100ms
        root.update()
        root.destroy()  # Clean up and destroy the window

if __name__ == "__main__":
    unittest.main(verbosity=2)