import matplotlib.pyplot as plt

# Ruler details
half_ruler_length_mm = 565.5 / 2  # Half the full ruler's length in mm
ruler_width_mm = 20               # The ruler's width in mm
number_increments = 180           # Number of increments for each half

# Convert mm to inches (1 inch = 25.4 mm)
half_ruler_length_inch = half_ruler_length_mm / 25.4
ruler_width_inch = ruler_width_mm / 25.4

# Page dimensions in inches (11x17 inch page in landscape orientation)
page_width_inch = 17
page_height_inch = 11

# For a vertically stacked arrangement where each ruler has a width (x-dimension) equal to half_ruler_length_inch:
# 1. Center horizontally: the offset is (page_width - ruler_width) / 2.
horizontal_offset = (page_width_inch - half_ruler_length_inch) / 2

# 2. For vertical stacking, the total height is two rulers high.
total_rulers_height = 2 * ruler_width_inch
vertical_offset = (page_height_inch - total_rulers_height) / 2

# Set up the figure matching the page dimensions.
fig = plt.figure(figsize=(page_width_inch, page_height_inch))

def render_ruler(ax, reverse=False):
    """
    Draws a half-ruler on the given Axes.
    
    Parameters:
        ax: Matplotlib Axes to draw on.
        reverse: If True, it reverses the numbering (i.e. labels go from 180 to 0).
    """
    ax.set_xlim(0, half_ruler_length_inch)
    ax.set_ylim(0, ruler_width_inch)
    ax.axis('off')
    
    # Draw the border around the ruler area.
    ax.add_patch(plt.Rectangle((0, 0),
                               half_ruler_length_inch,
                               ruler_width_inch,
                               fill=None,
                               edgecolor='black',
                               linewidth=1))
    
    # Draw tick marks and labels.
    for i in range(number_increments + 1):
        x = i * (half_ruler_length_inch / number_increments)
        if i % 10 == 0:  # Major tick: add a label.
            line_height = ruler_width_inch * 0.5
            label = str(i) if not reverse else str(180 - i)
            ax.text(x, line_height + 0.1,
                    label,
                    ha='center', va='bottom', fontsize=5)
        else:
            line_height = ruler_width_inch * 0.3
        ax.plot([x, x], [0, line_height], 'k')

# Create the bottom ruler axes.
# Calculate normalized coordinates for the subplot:
#   Left: horizontal_offset normalized by page width.
#   Bottom: vertical_offset normalized by page height.
#   Width and height: ruler dimensions normalized by page dimensions.
ax_bottom = fig.add_axes([
    horizontal_offset / page_width_inch,
    vertical_offset / page_height_inch,
    half_ruler_length_inch / page_width_inch,
    ruler_width_inch / page_height_inch
])
# Render the bottom ruler normally.
render_ruler(ax_bottom, reverse=False)

# Create the top ruler axes.
# Its left coordinate is the same (horizontally centered).
# Its bottom coordinate is shifted upward by the height of one ruler.
ax_top = fig.add_axes([
    horizontal_offset / page_width_inch,
    (vertical_offset + ruler_width_inch) / page_height_inch,
    half_ruler_length_inch / page_width_inch,
    ruler_width_inch / page_height_inch
])
# Render the top ruler (you can choose to reverse it if desired).
render_ruler(ax_top, reverse=True)

plt.savefig("centered_rulers_stacked_vertically.pdf", format='pdf')
