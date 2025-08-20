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

# Calculate positioning to have both rulers centered horizontally
# and stacked vertically with their centers aligned on the page
total_ruler_length_inch = 2 * half_ruler_length_inch
horizontal_offset = (page_width_inch - total_ruler_length_inch) / 2  # Center horizontally

# For vertical alignment, we want to stack the rulers with some space between them
# and have their centers aligned vertically on the page
spacing_between_rulers = 0.5  # inches
total_height_needed = 2 * ruler_width_inch + spacing_between_rulers
vertical_offset_first = (page_height_inch - total_height_needed) / 2  # Start of first ruler
vertical_offset_second = vertical_offset_first + ruler_width_inch + spacing_between_rulers  # Start of second ruler

# Set up a figure matching the dimensions of an 11x17 inch page
fig = plt.figure(figsize=(page_width_inch, page_height_inch))

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

# Add the first ruler (top)
# First half
ax1_top = fig.add_axes([horizontal_offset / page_width_inch, 
                        vertical_offset_first / page_height_inch, 
                        half_ruler_length_inch / page_width_inch, 
                        ruler_width_inch / page_height_inch])
render_ruler(ax1_top)

# Second half
ax2_top = fig.add_axes([(horizontal_offset + half_ruler_length_inch) / page_width_inch, 
                        vertical_offset_first / page_height_inch, 
                        half_ruler_length_inch / page_width_inch, 
                        ruler_width_inch / page_height_inch])
render_ruler(ax2_top, reverse=True)

# Add the second ruler (bottom)
# First half
ax1_bottom = fig.add_axes([horizontal_offset / page_width_inch, 
                          vertical_offset_second / page_height_inch, 
                          half_ruler_length_inch / page_width_inch, 
                          ruler_width_inch / page_height_inch])
render_ruler(ax1_bottom)

# Second half
ax2_bottom = fig.add_axes([(horizontal_offset + half_ruler_length_inch) / page_width_inch, 
                          vertical_offset_second / page_height_inch, 
                          half_ruler_length_inch / page_width_inch, 
                          ruler_width_inch / page_height_inch])
render_ruler(ax2_bottom, reverse=True)

plt.savefig("centered_rulers_11x17_landscape.pdf", format='pdf')
