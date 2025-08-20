
import pandas as pd
import numpy as np
import plotly.graph_objects as go

def create_surface_plot(x_range=(-5, 5), y_range=(-5, 5), num_points=50) -> go.Figure:
    # Generate sample data
    x = np.linspace(x_range[0], x_range[1], num_points)
    y = np.linspace(y_range[0], y_range[1], num_points)
    X, Y = np.meshgrid(x, y)
    Z = np.sin(np.sqrt(X**2 + Y**2))

    # Create a DataFrame from the grid data
    df = pd.DataFrame({'X': X.ravel(), 'Y': Y.ravel(), 'Z': Z.ravel()})

    # Create a 3D surface plot using Plotly
    fig = go.Figure(data=[go.Surface(z=Z, x=X[0], y=Y[:, 0])])
    fig.update_layout(title='3D Surface Plot with Plotly', autosize=True)

    return fig
