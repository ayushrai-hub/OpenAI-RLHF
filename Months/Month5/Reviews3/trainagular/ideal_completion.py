# ideal_completion.py

import tkinter as tk
from PIL import Image, ImageDraw, ImageTk, ImageFilter

# Custom colors based on NTU values
ntu_tints = {
    0: (225, 234, 242),
    100: (215, 219, 217),
    250: (198, 188, 163),
    500: (176, 153, 101),
    1000: (150, 120, 66),
    2000: (115, 91, 41),
    3000: (96, 72, 33)
}

def blend_color(color1, color2, factor):
    """Blends color1 and color2 by an amount given by factor (0 to 1)."""
    return tuple(int(c1 + (c2 - c1) * factor) for c1, c2 in zip(color1, color2))

def color_for_ntu(ntu):
    """Calculate the color for a particular NTU by interpolating between nearest values."""
    levels = sorted(ntu_tints.keys())
    for i in range(len(levels) - 1):
        if levels[i] <= ntu <= levels[i + 1]:
            factor = (ntu - levels[i]) / (levels[i + 1] - levels[i])
            return blend_color(ntu_tints[levels[i]], ntu_tints[levels[i + 1]], factor)
    if ntu <= levels[0]:
        return ntu_tints[levels[0]]
    else:
        return ntu_tints[levels[-1]]

def create_spectrum(draw, x_start, y_start, width, height, color_start, color_end, current_value):
    """Generates a vertical spectrum with a pointer and labels in the given area."""
    # Create the gradient spectrum
    for i in range(height):
        factor = 1 - (i / height)  # Invert to start with color_start at the top
        color = blend_color(color_start, color_end, factor)
        draw.line([(x_start, y_start + i), (x_start + width, y_start + i)], fill=color)

    # Add labels
    label_positions = [0, 500, 1000, 1500, 2000, 2500, 3000]
    for label in label_positions:
        y_label = y_start + height - (label / 3000) * height
        draw.text((x_start + width + 5, y_label - 10), str(label), fill="black")

    marker_x = x_start  
    marker_y = y_start + height - (current_value / 3000) * height
    triangle = [(marker_x + 10, marker_y - 5),  
                (marker_x, marker_y),           
                (marker_x + 10, marker_y + 5)]  
    draw.polygon(triangle, fill='black')
    return triangle  

def render_water(color, color_start, color_end, ntu_value):
    # Create a blank image with support for transparency (RGBA)
    width, height = 300, 300
    image = Image.new("RGBA", (width, height), (255, 255, 255, 0))
    draw = ImageDraw.Draw(image)

    # Generate the spectrum (gradient rectangle) on the right
    spectrum_width = 50
    spectrum_x_start = width - spectrum_width - 30  # Gap between glass and spectrum
    spectrum_y_start = 20  # Adjusted to move the color scale down
    create_spectrum(draw, spectrum_x_start, spectrum_y_start, spectrum_width, height - 40, color_start, color_end, ntu_value)

    # Add a light shadow beneath the glass
    shadow = Image.new("RGBA", image.size, (255, 255, 255, 0))
    shadow_draw = ImageDraw.Draw(shadow)
    shadow_draw.ellipse([(50, height - 70), (150, height)], fill=(0, 0, 0, 80))
    shadow = shadow.filter(ImageFilter.GaussianBlur(10))
    image.paste(shadow, mask=shadow)

    # Draw the glass (a vertical rectangle to represent a glass)
    draw.rectangle([50, 50, 150, 250], outline='black', width=2)
    draw.rectangle([50, 100, 150, 250], fill=color, outline='black')

    return image

class WaterGlassApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Glass of Water")

        # Set up a canvas for the glass drawing
        self.canvas = tk.Canvas(root, width=300, height=300, bg='white')
        self.canvas.pack()

        # Set up an empty image container on the canvas
        self.water_container = self.canvas.create_image(0, 0, anchor="nw")

        # Set up a vertical scale with NTU range from 0 to 3000
        self.scale = tk.Scale(root, from_=0, to=3000, orient="vertical", resolution=1, command=self.on_scale_change)
        self.scale.pack(side="left", fill="y", padx=20)

        # Set up a text box for entering NTU value
        self.ntu_entry = tk.Entry(root)
        self.ntu_entry.pack(side="left", padx=10)

        # Set up a button to update the water image based on the text box value
        self.update_button = tk.Button(root, text="Update NTU", command=self.update)
        self.update_button.pack(side="left", padx=10)

        # Start with the default water image
        self.update()

    def update(self):
        # Get the NTU value from the text box
        try:
            ntu_value = float(self.ntu_entry.get())
            if ntu_value < 0:
                ntu_value = 0
            elif ntu_value > 3000:
                ntu_value = 3000
        except ValueError:
            ntu_value = 0

        # Retrieve the color for the current NTU value
        color = color_for_ntu(ntu_value)
        color_start = color_for_ntu(0)
        color_end = color_for_ntu(3000)

        image = render_water(color, color_start, color_end, ntu_value)
        water_img = ImageTk.PhotoImage(image)
        self.canvas.itemconfig(self.water_container, image=water_img)
        self.canvas.image = water_img  # Save a reference to avoid being deleted

    def on_scale_change(self, val):
        # Change the NTU value according to the vertical scale
        ntu_value = self.scale.get()
        self.ntu_entry.delete(0, tk.END)
        self.ntu_entry.insert(0, str(ntu_value))
        self.update()

if __name__ == "__main__":
    root = tk.Tk()
    app = WaterGlassApp(root)
    root.mainloop()