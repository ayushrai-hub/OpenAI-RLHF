import matplotlib.pyplot as plt

# Ruler details
half_ruler_length_mm = 565.5 / 2  # Half of the ruler's length in mm
ruler_width_mm = 20               # The ruler's width in mm
number_increments = 180           # Number of increments for half a ruler

# Convert mm to inches (1 inch = 25.4 mm)
half_ruler_length_inch = half_ruler_length_mm / 25.4
ruler_width_inch = ruler_width_mm / 25.4

# Page dimensions in inches (landscape 11x17)
page_width_inch = 17
page_height_inch = 11

# Since the rulers are to be one above the other, we now have:
# - Each ruler has a width of `half_ruler_length_inch` (x-dimension)
# - Each ruler has a height of `ruler_width_inch` (y-dimension)
#
# To center them horizontally, calculate the horizontal offset so that each ruler's
# width is centered on the page.
horizontal_offset = (page_width_inch - half_ruler_length_inch) / 2

# Vertically, we have two rulers (stacked) with a combined height of:
total_ruler_height = 2 * ruler_width_inch
# The vertical offset to center both rulers on the page is then:
vertical_offset = (page_height_inch - total_ruler_height) / 2

# Set up a figure matching the dimensions of an 11x17 inch page
fig = plt.figure(figsize=(page_width_inch, page_height_inch))

# Function for drawing each ruler
def render_ruler(ax, reverse=False):
    ax.set_xlim(0, half_ruler_length_inch)
    ax.set_ylim(0, ruler_width_inch)
    ax.axis('off')
    
    # Draw border around the ruler
    ax.add_patch(plt.Rectangle((0, 0),
                               half_ruler_length_inch,
                               ruler_width_inch,
                               fill=None,
                               edgecolor='black',
                               linewidth=1))
    
    # Draw increments and labels
    for i in range(number_increments + 1):
        x = i * (half_ruler_length_inch / number_increments)
        if i % 10 == 0:  # Every 10th increment gets a longer tick and a label
            line_height = ruler_width_inch * 0.5
            label = str(i) if not reverse else str(180 - i)
            ax.text(x, line_height + 0.1, label, ha='center', va='bottom', fontsize=5)
        else:
            line_height = ruler_width_inch * 0.3
        ax.plot([x, x], [0, line_height], 'k')

# Create the first (bottom) ruler
ax1 = fig.add_axes([
    horizontal_offset / page_width_inch,                # x-position
    vertical_offset / page_height_inch,                   # y-position (bottom ruler)
    half_ruler_length_inch / page_width_inch,             # width
    ruler_width_inch / page_height_inch                 # height
])
render_ruler(ax1)

# Create the second (top) ruler; note its bottom edge starts one ruler height above
ax2 = fig.add_axes([
    horizontal_offset / page_width_inch,                 # x-position remains the same to center it horizontally
    (vertical_offset + ruler_width_inch) / page_height_inch,  # y-position for the top ruler
    half_ruler_length_inch / page_width_inch,              # width
    ruler_width_inch / page_height_inch                  # height
])
# Invert numbering on the top ruler, if desired
render_ruler(ax2, reverse=True)

plt.savefig("centered_rulers_11x17_landscape.pdf", format='pdf')
