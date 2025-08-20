#ideal_completion.py
import tkinter as tk
from tkinter import Canvas

class ConnectorNode(Canvas):
    """Class representing a draggable and clickable node on the canvas."""

    def __init__(self, parent, node_type="input", x=50, y=50, width=10, height=10, color="purple", *args, **kwargs):
        """Initialize the node with type, position, and appearance."""
        super().__init__(parent, width=width, height=height, *args, **kwargs)

        self.node_type = node_type
        self.canvas = parent
        self.x = x
        self.y = y
        self.color = color
        self.is_dragging = False  # Track if dragging
        self.drag_threshold = 5  # Distance threshold to distinguish drag from click

        # Create the node (a circle) on the canvas
        self.node_id = self.canvas.create_oval(x - 5, y - 5, x + 5, y + 5, fill=self.color, outline='black', tags="node")
        self.drag_start_position = None
        self._custom_callback = self.on_click  # Default callback

    def make_draggable(self):
        """Enable dragging for the node by binding mouse events."""
        self.canvas.tag_bind(self.node_id, "<ButtonPress-1>", self.start_drag_or_click)
        self.canvas.tag_bind(self.node_id, "<B1-Motion>", self.do_drag)
        self.canvas.tag_bind(self.node_id, "<ButtonRelease-1>", self.end_drag_or_click)

    def set_onclick(self, callback=None):
        """Set a custom callback for click events."""
        self._custom_callback = callback if callback else self.on_click

        # Unbind any previous <Button-1> events
        self.canvas.tag_unbind(self.node_id, "<Button-1>") 

        def wrapped_callback(event):
            self._custom_callback(event)

        # Bind the new click event
        self.canvas.tag_bind(self.node_id, "<Button-1>", wrapped_callback)

    def start_drag_or_click(self, event):
        """Track the start of a drag or click event."""
        self.is_dragging = False
        self.drag_start_position = (event.x, event.y)
        self.canvas._drag_data = {"x": self.canvas.canvasx(event.x), "y": self.canvas.canvasy(event.y)}

    def do_drag(self, event):
        """Move the node if the user is dragging."""
        delta_x = self.canvas.canvasx(event.x) - self.canvas._drag_data["x"]
        delta_y = self.canvas.canvasy(event.y) - self.canvas._drag_data["y"]

        if abs(delta_x) > self.drag_threshold or abs(delta_y) > self.drag_threshold:
            self.is_dragging = True

        if self.is_dragging:
            self.canvas.move(self.node_id, delta_x, delta_y)
            self.canvas._drag_data = {"x": self.canvas.canvasx(event.x), "y": self.canvas.canvasy(event.y)}

    def end_drag_or_click(self, event):
        """Determine whether the event was a drag or a click."""
        if self.is_dragging:
            print("Drag ended.")
        else:
            self._custom_callback(event)
        self.is_dragging = False
    def on_click(self, event):
        """Default click handler for the node."""
        print(f"{self.node_type} node clicked at {event.x}, {event.y}")
        

def testcallback(event):
    """Test callback for node click."""
    print("Test callback triggered.")

def main(start_mainloop=True):
    """Create the Tkinter canvas and initialize the node.
    
    Args:
        start_mainloop (bool): Whether to start the Tkinter mainloop (default is True).
    """
    root = tk.Tk()
    canvas = Canvas(root, width=400, height=400)
    canvas.pack()

    # Initialize the node
    node = ConnectorNode(canvas, node_type="input", width=10, height=10, x=50, y=50)
    
    # Set custom click callback
    node.set_onclick(callback=testcallback)
    
    # Enable dragging functionality
    node.make_draggable()
    
    if start_mainloop:
        root.mainloop()
    
    return root, canvas, node


if __name__ == "__main__":
    main()