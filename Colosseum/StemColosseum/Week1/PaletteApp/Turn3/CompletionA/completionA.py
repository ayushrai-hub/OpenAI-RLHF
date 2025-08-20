import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

class WellPlateSelectorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Well Palette Selector")
        self.root.geometry("500x400")

        well_options = ["96-well", "48-well", "24-well"]

        # Current well type
        self.current_well_type = tk.StringVar()
        self.current_well_type.set(well_options[0])  # Default selection is "96-well"

        # Droplist to select well type
        self.dropdown_menu_label = tk.Label(self.root, text="Select Well Palette Format:")
        self.dropdown_menu_label.pack(pady=10)

        self.dropdown = ttk.Combobox(self.root, values=well_options, textvariable=self.current_well_type, state="readonly")
        self.dropdown.pack(pady=10)
        self.dropdown.bind("<<ComboboxSelected>>", self.update_displayed_well_image)

        # Frame to hold the well image
        self.image_frame = tk.Frame(self.root)
        self.image_frame.pack(pady=20)

        # Load and display the default image (96-well)
        self.image_label = tk.Label(self.image_frame)
        self.image_label.pack()

        # Load well palette images
        self.palette_images = {
            "96-well": ImageTk.PhotoImage(Image.open("resources/96-well.png").resize((300, 300))),
            "48-well": ImageTk.PhotoImage(Image.open("resources/48-well.png").resize((300, 300))),
            "24-well": ImageTk.PhotoImage(Image.open("resources/24-well.png").resize((300, 300)))
        }

        # Display the default image
        self.update_displayed_well_image()

    def update_displayed_well_image(self, event=None):
        selected_well_type = self.current_well_type.get()
        self.image_label.config(image=self.palette_images[selected_well_type])

if __name__ == "__main__":
    root = tk.Tk()
    app = WellPlateSelectorApp(root)
    root.mainloop()
