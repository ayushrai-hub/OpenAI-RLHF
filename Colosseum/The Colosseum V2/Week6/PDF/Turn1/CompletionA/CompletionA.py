import matplotlib.pyplot as plt

# Ruler details
half_ruler_length_mm = 565.5 / 2  # Half ruler length in mm
ruler_width_mm = 20               # Ruler width in mm
number_increments = 180           # increments per half ruler

# Convert mm to inches (1 inch = 25.4 mm)
half_ruler_length_inch = half_ruler_length_mm / 25.4
ruler_width_inch = ruler_width_mm / 25.4
total_ruler_length_inch = half_ruler_length_inch * 2

# Page dimensions in inches (landscape)
page_width_inch = 17
page_height_inch = 11

# Calculate positions to center rulers horizontally and vertically stacked
horizontal_offset = (page_width_inch - total_ruler_length_inch) / 2
vertical_spacing = 0.5  # inch gap between the two stacked rulers

total_rulers_height = 2 * ruler_width_inch + vertical_spacing
vertical_offset = (page_height_inch - total_rulers_height) / 2

# Set up figure
fig = plt.figure(figsize=(page_width_inch, page_height_inch))

# Render ruler function
def render_ruler(ax, reverse=False):
    ax.set_xlim(0, half_ruler_length_inch)
    ax.set_ylim(0, ruler_width_inch)
    ax.axis('off')

    # Border
    ax.add_patch(plt.Rectangle((0, 0), half_ruler_length_inch, ruler_width_inch, fill=None, edgecolor='black', linewidth=1))

    # Draw increments
    for i in range(number_increments + 1):
        x = i * (half_ruler_length_inch / number_increments)
        if i % 10 == 0:
            line_height = ruler_width_inch * 0.5
            label = str(i) if not reverse else str(180 - i)
            ax.text(x, line_height + 0.05, label, ha='center', va='bottom', fontsize=5)
        else:
            line_height = ruler_width_inch * 0.3
        ax.plot([x, x], [0, line_height], 'k')

# Top ruler
ax1 = fig.add_axes([
    horizontal_offset / page_width_inch,
    (vertical_offset + ruler_width_inch + vertical_spacing) / page_height_inch,
    half_ruler_length_inch / page_width_inch,
    ruler_width_inch / page_height_inch
])
render_ruler(ax1, reverse=False)

# Second half of the top ruler
ax1b = fig.add_axes([
    (horizontal_offset + half_ruler_length_inch) / page_width_inch,
    (vertical_offset + ruler_width_inch + vertical_spacing) / page_height_inch,
    half_ruler_length_inch / page_width_inch,
    ruler_width_inch / page_height_inch
])
render_ruler(ax1b, reverse=True)

# Bottom ruler
ax2 = fig.add_axes([
    horizontal_offset / page_width_inch,
    vertical_offset / page_height_inch,
    half_ruler_length_inch / page_width_inch,
    ruler_width_inch / page_height_inch
])
render_ruler(ax2, reverse=False)

# Second half of the bottom ruler
ax2b = fig.add_axes([
    (horizontal_offset + half_ruler_length_inch) / page_width_inch,
    vertical_offset / page_height_inch,
    half_ruler_length_inch / page_width_inch,
    ruler_width_inch / page_height_inch
])
render_ruler(ax2b, reverse=True)

# Save figure
plt.savefig("vertical.pdf", format='pdf', bbox_inches='tight')
