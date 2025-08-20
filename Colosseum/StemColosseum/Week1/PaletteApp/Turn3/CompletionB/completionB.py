import os
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

# Directory of resources where plate images are stored
RESOURCES_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'resources')

class PaletteSelect(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        
        # Label for the dropdown
        self.palette_label = tk.Label(self, text="Select Well Plate Format:")
        self.palette_label.grid(row=0, column=0, padx=5, pady=5)
        
        # Dropdown menu for selecting well plate formats
        self.well_formats = ["96-well", "48-well", "24-well"]
        self.selected_format = tk.StringVar(value=self.well_formats[0])
        self.format_dropdown = ttk.OptionMenu(self, self.selected_format, self.well_formats[0], *self.well_formats, command=self.update_plate_image)
        self.format_dropdown.grid(row=0, column=1, padx=5, pady=5)

        # Placeholder for the well plate image
        self.image_label = tk.Label(self)
        self.image_label.grid(row=1, column=0, columnspan=2, padx=5, pady=10)
        
        # Update initial image display
        self.update_plate_image(self.selected_format.get())
        
    def update_plate_image(self, selected_format):
        """Updates the displayed image based on the selected well plate format."""
        image_path = os.path.join(RESOURCES_DIR, f'{selected_format.replace("-","_")}.png')
        
        if os.path.exists(image_path):
            well_image = Image.open(image_path)
            well_image = well_image.resize((400, 400), Image.ANTIALIAS)  # Adjust image size as needed
            self.plate_image = ImageTk.PhotoImage(well_image)
            self.image_label.config(image=self.plate_image)
        else:
            # If the image is not found, display a placeholder text
            self.image_label.config(text=f"No image found for {selected_format} format.", image='')

# Test the PaletteSelect frame independently
if __name__ == "__main__":
    root = tk.Tk()
    root.title("HTE Chemistry Palette Builder")
    palette_select_frame = PaletteSelect(root)
    palette_select_frame.pack(fill="both", expand=True)
    root.mainloop()
