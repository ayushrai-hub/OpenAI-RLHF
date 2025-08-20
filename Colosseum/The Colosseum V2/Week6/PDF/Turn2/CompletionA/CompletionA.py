import matplotlib.pyplot as plt

# Ruler details
half_ruler_length_mm = 565.5 / 2  # Half of the ruler's length in mm
ruler_width_mm = 20  # The ruler's width in mm
number_increments = 180  # Number of increments for half a ruler

# Convert mm to inches (1 inch = 25.4 mm)
half_ruler_length_inch = half_ruler_length_mm / 25.4
ruler_width_inch = ruler_width_mm / 25.4

# Page dimensions in inches (11x17 landscape)
page_width_inch = 17
page_height_inch = 11

# Set up a figure matching the dimensions of an 11x17 inch page
fig = plt.figure(figsize=(page_width_inch, page_height_inch))

def render_ruler(ax, reverse=False):
    ax.set_xlim(0, half_ruler_length_inch)
    ax.set_ylim(0, ruler_width_inch)
    ax.axis('off')
    
    # Add border around each ruler
    ax.add_patch(plt.Rectangle((0, 0), half_ruler_length_inch, ruler_width_inch, fill=None, edgecolor='black', linewidth=1))
    
    # Calculate and draw increments
    for i in range(number_increments + 1):
        x = i * (half_ruler_length_inch / number_increments)
        if i % 10 == 0:  # Every 10th increment
            line_height = ruler_width_inch * 0.5
            ax.text(x, line_height + 0.1, str(i) if not reverse else str(180-i), ha='center', va='bottom', fontsize=5)
        else:
            line_height = ruler_width_inch * 0.3
        ax.plot([x, x], [0, line_height], 'k')

# Calculate y-offset to center both rulers one above the other vertically
middle_y = page_height_inch / 2
vertical_offset_ruler = ruler_width_inch / 2

# Adding the rulers one above the other
ax1 = fig.add_axes([(page_width_inch - half_ruler_length_inch) / (2 * page_width_inch),  # Centered horizontally
                    (middle_y + vertical_offset_ruler) / page_height_inch,  # First stack offset vertical
                    half_ruler_length_inch / page_width_inch, 
                    ruler_width_inch / page_height_inch])
render_ruler(ax1)

ax2 = fig.add_axes([(page_width_inch - half_ruler_length_inch) / (2 * page_width_inch),  # Centered horizontally
                    (middle_y - (ruler_width_inch + vertical_offset_ruler)) / page_height_inch,  # Second ruler aligned
                    half_ruler_length_inch / page_width_inch,
                    ruler_width_inch / page_height_inch])
render_ruler(ax2, reverse=True)

plt.savefig("vertical_stacked_center_rulers.pdf", format='pdf')
