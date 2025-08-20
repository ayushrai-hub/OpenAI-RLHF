from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QSplitter, QVBoxLayout, QSpinBox, QLabel, QComboBox, QPushButton, QLineEdit, QGridLayout
from PyQt5.QtCore import Qt
import numpy as np
from vispy import scene, app, visuals
from vispy.color import get_colormap

def plot_function(self, X, Y, Z):
    """Update the surface plot with new data."""
    # Map the Z-values to colors using the colormap
    self.cm = get_colormap(self.props.combo.currentText())
    norm_Z = (Z - Z.min()) / (Z.max() - Z.min())
    colors = self.cm.map(norm_Z)
    
    # Ensure that the color array matches the shape of Z
    if colors.shape[0] != Z.shape[0] or colors.shape[1] != Z.shape[1]:
        colors = colors[:Z.shape[0], :Z.shape[1]]

    self.surface.set_data(z=Z, x=X, y=Y, colors=colors)

def update_function(self):
    self.X, self.Y, self.Z = self.create_function(self.a, self.b, self.c)
    self.plot_function(self.X, self.Y, self.Z)

class FunctionPlotter(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        # Set up the main window
        self.setWindowTitle("Function Plotter")
        self.setGeometry(WINDOW_POS[0], WINDOW_POS[1], WINDOW_SIZE[0], WINDOW_SIZE[1])

        # Setup splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        self.setCentralWidget(splitter)

        # Setup object widget
        self.props = ObjectWidget(self, main_window=self)
        splitter.addWidget(self.props)

        # Setup canvas
        self.canvas = scene.SceneCanvas(keys='interactive', show=True)
        self.view = self.canvas.central_widget.add_view()
        self.view.camera = 'turntable'
        self.view.camera.fov = FOV
        self.view.camera.distance = CAMERA_DISTANCE

        # Add the canvas to the splitter
        splitter.addWidget(self.canvas.native)

        # Initialize the function plotter
        self.initialize_parameters()
        self.setup_surface_plot()
        self.setup_timer()

        # Connect spinbox signals to update methods
        self.props.x_limits.valueChanged.connect(self.update_x_limits)
        self.props.y_limits.valueChanged.connect(self.update_y_limits)
        self.props.grid_points.valueChanged.connect(self.update_grid_points)

    def initialize_parameters(self):
        """Initialize plot parameters and time."""
        self.time = 0
        self.a = 1
        self.b = 1
        self.c = 0

        # Add the actual function structure, that will later come from the input line
        self.function_input = self.props.function_input.text()

        # Add a color map
        self.cm = get_colormap(self.props.combo.currentText())

        # Add the grid points from the spin box
        self.GRID_POINTS = self.props.grid_points.value()

        # Add the x and y limits from the spin boxes
        self.X_LIMITS = (self.props.x_limits.value() * -1, self.props.x_limits.value())
        self.Y_LIMITS = (self.props.y_limits.value() * -1, self.props.y_limits.value())

        # Calculate the function for the first time
        self.X, self.Y, self.Z = self.create_function(self.a, self.b, self.c)

    def setup_surface_plot(self):
        """Setup the surface plot."""
        self.surface = visuals.SurfacePlot(x=self.X, y=self.Y, z=self.Z, shading='smooth')
        self.view.add(self.surface)

    def setup_timer(self):
        """Setup the timer for updating the plot."""
        self.timer = app.Timer(connect=self.update, interval='auto')
        self.timer.start()

    def create_function(self, a, b, c):
        """Generate data for the 3D function."""
        x = np.linspace(*self.X_LIMITS, self.GRID_POINTS)
        y = np.linspace(*self.Y_LIMITS, self.GRID_POINTS)
        X, Y = np.meshgrid(x, y)

        # Pull the function from the input line
        context = {'X': X, 'Y': Y, 'a': a, 'b': b, 'c': c, 'np': np}
        Z = eval(self.function_input, context)
        return X, Y, Z

    def plot_function(self, X, Y, Z):
        """Update the surface plot with new data."""
        # Map the Z-values to colors using the colormap
        self.cm = get_colormap(self.props.combo.currentText())
        norm_Z = (Z - Z.min()) / (Z.max() - Z.min())
        colors = self.cm.map(norm_Z)
        
        # Ensure that the color array matches the shape of Z
        if colors.shape[0] != Z.shape[0] or colors.shape[1] != Z.shape[1]:
            colors = colors[:Z.shape[0], :Z.shape[1]]

        self.surface.set_data(z=Z, x=X, y=Y, colors=colors)

    def update(self, event):
        """Update the function coefficients and replot."""
        try:
            self.time += event.dt

            speed_percent_a = int(self.props.scaling_speed_a.currentText().split()[-2]) / 100
            speed_percent_b = int(self.props.scaling_speed_b.currentText().split()[-2]) / 100
            speed_percent_c = int(self.props.scaling_speed_c.currentText().split()[-2]) / 100

            # Dynamic scaling of the parameters a, b, c with the selected rule and speed
            if self.props.scaling_rule_a.currentIndex() == 0:  # a = sin(t)
                self.a = np.sin(self.time * speed_percent_a)
            elif self.props.scaling_rule_a.currentIndex() == 1:  # a = cos(t)
                self.a = np.cos(self.time * speed_percent_a)
            elif self.props.scaling_rule_a.currentIndex() == 2:  # a = tan(t)
                self.a = np.tan(self.time * speed_percent_a)
            else:  # a = 1; static
                self.a = 1

            if self.props.scaling_rule_b.currentIndex() == 0:  # b = sin(t)
                self.b = np.sin(self.time * speed_percent_b)
            elif self.props.scaling_rule_b.currentIndex() == 1:  # b = cos(t)
                self.b = np.cos(self.time * speed_percent_b)
            elif self.props.scaling_rule_b.currentIndex() == 2:  # b = tan(t)
                self.b = np.tan(self.time * speed_percent_b)
            else:  # b = 1; static
                self.b = 1

            if self.props.scaling_rule_c.currentIndex() == 0:  # c = sin(t)
                self.c = np.sin(self.time * speed_percent_c)
            elif self.props.scaling_rule_c.currentIndex() == 1:  # c = cos(t)
                self.c = np.cos(self.time * speed_percent_c)
            elif self.props.scaling_rule_c.currentIndex() == 2:  # c = tan(t)
                self.c = np.tan(self.time * speed_percent_c)
            else:  # c = 1; static
                self.c = 1

            # Update the function with the new parameters
            self.X, self.Y, self.Z = self.create_function(self.a, self.b, self.c)
            self.plot_function(self.X, self.Y, self.Z)
        except Exception as e:
            print(f"Error during update: {e}")

    def update_x_limits(self):
        self.X_LIMITS = (self.props.x_limits.value() * -1, self.props.x_limits.value())
        self.update_function()

    def update_y_limits(self):
        self.Y_LIMITS = (self.props.y_limits.value() * -1, self.props.y_limits.value())
        self.update_function()

    def update_grid_points(self):
        self.GRID_POINTS = self.props.grid_points.value()
        self.update_function()

    def update_function(self):
        self.X, self.Y, self.Z = self.create_function(self.a, self.b, self.c)
        self.plot_function(self.X, self.Y, self.Z)

    def change_color(self):
        """Change the color of the surface plot to a random color."""
        random_color = (np.random.rand(), np.random.rand(), np.random.rand(), 1)
        self.surface.color = random_color