import matplotlib.pyplot as plt

# Ruler details
half_ruler_length_mm = 565.5 / 2  # Half of the ruler's length in mm
ruler_width_mm = 20  # The ruler's width in mm
number_increments = 180  # Number of increments for half a ruler

# Convert mm to inches (1 inch = 25.4 mm)
half_ruler_length_inch = half_ruler_length_mm / 25.4
ruler_width_inch = ruler_width_mm / 25.4

# Page dimensions in inches
page_width_inch = 17
page_height_inch = 11

# Total ruler length (combining both halves)
total_ruler_length_inch = 2 * half_ruler_length_inch

# Calculate offsets for vertical stacking with centers aligned
# For horizontal centering, we want each ruler's center to align with page center
horizontal_offset = (page_width_inch - total_ruler_length_inch) / 2  # Left edge of first ruler

# For vertical stacking, calculate the appropriate spacing
# Total height taken by both rulers
total_rulers_height = 2 * ruler_width_inch
# Space between top of page and top of first ruler
vertical_offset_top = (page_height_inch - total_rulers_height) / 2
# Space between top of page and top of second ruler (positioned below the first)
vertical_offset_bottom = vertical_offset_top + ruler_width_inch

# Set up a figure matching the dimensions of an 11x17 inch page
fig = plt.figure(figsize=(page_width_inch, page_height_inch))
dpi_value = fig.dpi  # Get the DPI to position the rulers correctly

# Function for drawing each ruler
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

# Add the top ruler's left half
ax1 = fig.add_axes([horizontal_offset / page_width_inch, 
                    vertical_offset_top / page_height_inch, 
                    half_ruler_length_inch / page_width_inch, 
                    ruler_width_inch / page_height_inch])
render_ruler(ax1)

# Add the top ruler's right half
ax2 = fig.add_axes([(horizontal_offset + half_ruler_length_inch) / page_width_inch, 
                    vertical_offset_top / page_height_inch, 
                    half_ruler_length_inch / page_width_inch, 
                    ruler_width_inch / page_height_inch])
render_ruler(ax2, reverse=True)

# Add the bottom ruler's left half
ax3 = fig.add_axes([horizontal_offset / page_width_inch, 
                    vertical_offset_bottom / page_height_inch, 
                    half_ruler_length_inch / page_width_inch, 
                    ruler_width_inch / page_height_inch])
render_ruler(ax3)

# Add the bottom ruler's right half
ax4 = fig.add_axes([(horizontal_offset + half_ruler_length_inch) / page_width_inch, 
                    vertical_offset_bottom / page_height_inch, 
                    half_ruler_length_inch / page_width_inch, 
                    ruler_width_inch / page_height_inch])
render_ruler(ax4, reverse=True)

plt.savefig("stacked_centered_ruler_11x17_landscape.pdf", format='pdf')
