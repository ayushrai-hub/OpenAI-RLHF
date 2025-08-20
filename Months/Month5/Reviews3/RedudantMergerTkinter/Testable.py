import tkinter as tk
from tkinter import Canvas

class ConnectorNode(Canvas):
    def __init__(self, parent: tk.Widget, node_type: str = "input", x: int = 50, y: int = 50, 
                 width: int = 10, height: int = 10, color: str = "purple", *args, **kwargs) -> None:
        super().__init__(parent, width=width, height=height, *args, **kwargs)
        
        self.node_type = node_type
        self.canvas = parent
        self.x = x
        self.y = y
        self.color = color
        self.is_dragging = False
        self.drag_threshold = 5

        self.node_id = self.canvas.create_oval(x-5, y-5, x+5, y+5, fill=self.color, outline='black', tags="node")
        self._custom_callback = self.on_click
        
        self.make_draggable()
        self.set_onclick()

    def make_draggable(self) -> None:
        self.canvas.tag_bind(self.node_id, "<ButtonPress-1>", self.start_drag_or_click)
        self.canvas.tag_bind(self.node_id, "<B1-Motion>", self.do_drag)
        self.canvas.tag_bind(self.node_id, "<ButtonRelease-1>", self.end_drag_or_click)

    def set_onclick(self, callback: callable = None) -> None:
        self._custom_callback = callback if callback else self.on_click

        def wrapped_callback(event):
            self._custom_callback(event)

        self.canvas.tag_bind(self.node_id, "<Button-1>", wrapped_callback)

    def start_drag_or_click(self, event: tk.Event) -> None:
        self.is_dragging = False
        self.drag_start_position = (event.x, event.y)
        self.canvas._drag_data = {"x": self.canvas.canvasx(event.x), "y": self.canvas.canvasy(event.y)}

    def do_drag(self, event: tk.Event) -> None:
        delta_x = self.canvas.canvasx(event.x) - self.canvas._drag_data["x"]
        delta_y = self.canvas.canvasy(event.y) - self.canvas._drag_data["y"]

        if abs(delta_x) > self.drag_threshold or abs(delta_y) > self.drag_threshold:
            self.is_dragging = True

        if self.is_dragging:
            self.canvas.move(self.node_id, delta_x, delta_y)
            self.canvas._drag_data = {"x": self.canvas.canvasx(event.x), "y": self.canvas.canvasy(event.y)}

    def end_drag_or_click(self, event: tk.Event) -> None:
        if not self.is_dragging:
            self._custom_callback(event)
        self.is_dragging = False

    def on_click(self, event: tk.Event) -> None:
        print(f"Node {self.node_type} clicked at {event.x}, {event.y}")

def testcallback(event: tk.Event) -> None:
    print("Test callback executed.")

def main(start_mainloop: bool = True) -> tuple[tk.Tk, Canvas, ConnectorNode]:
    root = tk.Tk()
    
    canvas = Canvas(root, width=400, height=400)
    canvas.pack()

    node = ConnectorNode(canvas, node_type="input", width=10, height=10, x=50, y=50)

    node.set_onclick(callback=lambda event: print("Node Clicked!"))
    node.set_onclick(callback=testcallback)

    if start_mainloop:
        root.mainloop()

    return root, canvas, node
