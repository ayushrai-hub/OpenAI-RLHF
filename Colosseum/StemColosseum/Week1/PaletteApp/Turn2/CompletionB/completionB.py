import tkinter as tk
from tkinter import ttk

class PaletteApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("HTE Chemistry Palette Builder")
        self.geometry("800x600")

        # Variable to store the selected palette size
        self.palette_size = tk.StringVar()
        self.palette_size.set("96 Wells")

        # Create the dropdown menu
        self.create_dropdown()

        # Canvas to display the wells
        self.canvas = tk.Canvas(self, width=760, height=500, bg='white')
        self.canvas.pack(pady=20)

        # Draw the initial palette
        self.draw_palette()

    def create_dropdown(self):
        frame = tk.Frame(self)
        frame.pack(pady=10)

        label = tk.Label(frame, text="Select Palette Size:")
        label.pack(side=tk.LEFT, padx=5)

        options = ["96 Wells", "48 Wells", "24 Wells"]
        dropdown = ttk.OptionMenu(
            frame, self.palette_size, options[0], *options, command=self.on_palette_change
        )
        dropdown.pack(side=tk.LEFT)

    def on_palette_change(self, *args):
        # Redraw the palette when the selection changes
        self.draw_palette()

    def draw_palette(self):
        # Clear the canvas
        self.canvas.delete("all")

        size = self.palette_size.get()
        if size == "96 Wells":
            rows, cols = 8, 12
        elif size == "48 Wells":
            rows, cols = 6, 8
        elif size == "24 Wells":
            rows, cols = 4, 6

        # Calculate cell size
        cell_width = self.canvas.winfo_width() / cols
        cell_height = self.canvas.winfo_height() / rows

        # Draw the wells
        for row in range(rows):
            for col in range(cols):
                x0 = col * cell_width + 5
                y0 = row * cell_height + 5
                x1 = x0 + cell_width - 10
                y1 = y0 + cell_height - 10

                self.canvas.create_oval(
                    x0, y0, x1, y1, fill='lightblue', outline='black'
                )

if __name__ == "__main__":
    app = PaletteApp()
    app.mainloop()
