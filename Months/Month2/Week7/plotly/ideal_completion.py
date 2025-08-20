import numpy as np
import plotly.graph_objects as go

def create_surface_plot(x_range=(-5, 5), y_range=(-5, 5), num_points=50):
    """
    Create a 3D surface plot using Plotly.
    
    Args:
    x_range (tuple): Range for x-axis (default: (-5, 5))
    y_range (tuple): Range for y-axis (default: (-5, 5))
    num_points (int): Number of points to generate for each axis (default: 50)
    
    Returns:
    plotly.graph_objects.Figure: The created figure object
    """
    # Generate sample data
    x = np.linspace(x_range[0], x_range[1], num_points)
    y = np.linspace(y_range[0], y_range[1], num_points)
    X, Y = np.meshgrid(x, y)
    Z = np.sin(np.sqrt(X**2 + Y**2))  # Z as a function of X and Y

    # Create a 3D surface plot using Plotly Graph Objects
    fig = go.Figure(data=[go.Surface(z=Z, x=x, y=y)])

    # Update the layout
    fig.update_layout(
        title='3D Surface Plot with Plotly',
        scene=dict(
            xaxis_title='X Axis',
            yaxis_title='Y Axis',
            zaxis_title='Z Axis'
        )
    )

    return fig

# Example usage
if __name__ == "__main__":
    fig = create_surface_plot()
    fig.show()