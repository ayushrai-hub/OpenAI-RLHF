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

########################################################################
# Here we want to stack the two rulers one above the other, with their 
# centers aligned vertically. Hence:
# - horizontally, they will be centered on the page 
# - vertically, we compute total vertical space for 2 rulers and center them
########################################################################

# Total vertical height needed: 2 x ruler_width
total_rulers_height = 2 * ruler_width_inch

# Calculate horizontal offset to center them (since they share a single length).
horizontal_offset = (page_width_inch - half_ruler_length_inch) / 2

# Calculate vertical offset to center both stacked (they have a combined height).
vertical_offset = (page_height_inch - total_rulers_height) / 2

# Set up a figure matching the dimensions of an 11x17 inch page
fig = plt.figure(figsize=(page_width_inch, page_height_inch))

def render_ruler(ax, reverse=False):
    """
    Draws a half-bench rule on the given Axes object.
    If reverse=True, increments are labeled from right to left.
    """
    ax.set_xlim(0, half_ruler_length_inch)
    ax.set_ylim(0, ruler_width_inch)
    ax.axis('off')
    
    # Border around each half-ruler
    ax.add_patch(plt.Rectangle((0, 0), 
                               half_ruler_length_inch, 
                               ruler_width_inch, 
                               fill=None, 
                               edgecolor='black', 
                               linewidth=1))
    
    # Draw increments
    for i in range(number_increments + 1):
        x = i * (half_ruler_length_inch / number_increments)
        if i % 10 == 0:   # major increments with labels
            line_height = ruler_width_inch * 0.5
            label_text = str(i if not reverse else 180 - i)
            ax.text(x, line_height + 0.1, label_text, 
                    ha='center', va='bottom', fontsize=5)
        else:             # minor increments
            line_height = ruler_width_inch * 0.3
        ax.plot([x, x], [0, line_height], 'k')

# 1st ruler (top)
# left/bottom/width/height
ax1 = fig.add_axes([
    horizontal_offset / page_width_inch, 
    (vertical_offset + ruler_width_inch) / page_height_inch, 
    half_ruler_length_inch / page_width_inch, 
    ruler_width_inch / page_height_inch
])
render_ruler(ax1, reverse=False)

# 2nd ruler (bottom, reversed increments)
ax2 = fig.add_axes([
    horizontal_offset / page_width_inch,
    vertical_offset / page_height_inch, 
    half_ruler_length_inch / page_width_inch, 
    ruler_width_inch / page_height_inch
])
render_ruler(ax2, reverse=True)

plt.savefig("C:/Users/r.jones/OneDrive - GearTech/MeasuringTemplates/centered_rulers_11x17_vertical_stack.pdf", format='pdf')
plt.close()
