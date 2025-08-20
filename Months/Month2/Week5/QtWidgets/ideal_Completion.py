from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QSplitter, QVBoxLayout, QSpinBox, QLabel, QComboBox, QPushButton, QLineEdit
from PyQt5.QtCore import Qt
import numpy as np
from vispy import scene, app, visuals
from vispy.color import get_colormap

# Constants
WINDOW_POS = (100, 100)
WINDOW_SIZE = (1500, 900)
FOV = 45
CAMERA_DISTANCE = 20

class ObjectWidget(QtWidgets.QWidget):
    def __init__(self, parent=None, main_window=None):
        super().__init__(parent)
        self.main_window = main_window

        layout = QVBoxLayout()
        
        # Combo box for selecting colormaps
        self.combo = QComboBox()
        self.combo.addItems(['viridis', 'magma', 'inferno', 'plasma'])
        layout.addWidget(QLabel("Colormap:"))
        layout.addWidget(self.combo)
        
        # Spin boxes for grid points and limits
        self.grid_points = QSpinBox()
        self.grid_points.setRange(10, 200)
        self.grid_points.setValue(50)
        layout.addWidget(QLabel("Grid Points:"))
        layout.addWidget(self.grid_points)
        
        self.x_limits = QSpinBox()
        self.x_limits.setRange(1, 10)
        self.x_limits.setValue(5)
        layout.addWidget(QLabel("X Limits:"))
        layout.addWidget(self.x_limits)
        
        self.y_limits = QSpinBox()
        self.y_limits.setRange(1, 10)
        self.y_limits.setValue(5)
        layout.addWidget(QLabel("Y Limits:"))
        layout.addWidget(self.y_limits)

        # Function input
        self.function_input = QLineEdit("np.sin(X) + np.cos(Y)")
        layout.addWidget(QLabel("Function:"))
        layout.addWidget(self.function_input)

        # Add scaling speed and rule widgets
        self.scaling_speed_a = QComboBox()
        self.scaling_speed_a.addItems(['10 %', '50 %', '100 %'])
        self.scaling_rule_a = QComboBox()
        self.scaling_rule_a.addItems(['sin(t)', 'cos(t)', 'tan(t)', 'static'])

        self.scaling_speed_b = QComboBox()
        self.scaling_speed_b.addItems(['10 %', '50 %', '100 %'])
        self.scaling_rule_b = QComboBox()
        self.scaling_rule_b.addItems(['sin(t)', 'cos(t)', 'tan(t)', 'static'])

        self.scaling_speed_c = QComboBox()
        self.scaling_speed_c.addItems(['10 %', '50 %', '100 %'])
        self.scaling_rule_c = QComboBox()
        self.scaling_rule_c.addItems(['sin(t)', 'cos(t)', 'tan(t)', 'static'])

        layout.addWidget(QLabel("Scaling Speed A:"))
        layout.addWidget(self.scaling_speed_a)
        layout.addWidget(QLabel("Scaling Rule A:"))
        layout.addWidget(self.scaling_rule_a)

        layout.addWidget(QLabel("Scaling Speed B:"))
        layout.addWidget(self.scaling_speed_b)
        layout.addWidget(QLabel("Scaling Rule B:"))
        layout.addWidget(self.scaling_rule_b)

        layout.addWidget(QLabel("Scaling Speed C:"))
        layout.addWidget(self.scaling_speed_c)
        layout.addWidget(QLabel("Scaling Rule C:"))
        layout.addWidget(self.scaling_rule_c)

        # Update button
        self.update_button = QPushButton("Update Function")
        layout.addWidget(self.update_button)

        self.setLayout(layout)

class FunctionPlotter(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Function Plotter")
        self.setGeometry(WINDOW_POS[0], WINDOW_POS[1], WINDOW_SIZE[0], WINDOW_SIZE[1])

        splitter = QSplitter(Qt.Horizontal)
        self.setCentralWidget(splitter)

        self.props = ObjectWidget(self, main_window=self)
        splitter.addWidget(self.props)

        self.canvas = scene.SceneCanvas(keys='interactive', show=True)
        self.view = self.canvas.central_widget.add_view()
        self.view.camera = scene.TurntableCamera(fov=FOV, distance=CAMERA_DISTANCE)
        splitter.addWidget(self.canvas.native)

        self.initialize_parameters()
        self.setup_surface_plot()
        self.setup_timer()

        self.props.x_limits.valueChanged.connect(self.update_x_limits)
        self.props.y_limits.valueChanged.connect(self.update_y_limits)
        self.props.grid_points.valueChanged.connect(self.update_grid_points)
        self.props.update_button.clicked.connect(self.update_function)
        self.props.combo.currentIndexChanged.connect(self.update_colormap)

    def initialize_parameters(self):
        self.time = 0
        self.a = 1
        self.b = 1
        self.c = 0

        self.function_input = self.props.function_input.text()
        self.cm = get_colormap(self.props.combo.currentText())
        self.GRID_POINTS = self.props.grid_points.value()
        self.X_LIMITS = (self.props.x_limits.value() * -1, self.props.x_limits.value())
        self.Y_LIMITS = (self.props.y_limits.value() * -1, self.props.y_limits.value())

        self.X, self.Y, self.Z = self.create_function(self.a, self.b, self.c)

    def setup_surface_plot(self):
        self.surface = scene.visuals.SurfacePlot(x=self.X, y=self.Y, z=self.Z, shading='smooth')
        self.view.add(self.surface)

    def setup_timer(self):
        self.timer = app.Timer(connect=self.update, interval=0.1)
        self.timer.start()

    def create_function(self, a, b, c):
        x = np.linspace(*self.X_LIMITS, self.GRID_POINTS)
        y = np.linspace(*self.Y_LIMITS, self.GRID_POINTS)
        X, Y = np.meshgrid(x, y)

        context = {'X': X, 'Y': Y, 'a': a, 'b': b, 'c': c, 'np': np}
        Z = eval(self.function_input, context)
        return X, Y, Z

    def plot_function(self, X, Y, Z):
        norm_Z = (Z - Z.min()) / (Z.max() - Z.min())
        colors = self.cm.map(norm_Z)
        self.surface.set_data(z=Z, x=X, y=Y)
        self.surface.mesh_data.set_vertex_colors(colors)

    def update(self, event):
        try:
            self.time += 0.1

            speed_percent_a = int(self.props.scaling_speed_a.currentText().split()[0]) / 100
            speed_percent_b = int(self.props.scaling_speed_b.currentText().split()[0]) / 100
            speed_percent_c = int(self.props.scaling_speed_c.currentText().split()[0]) / 100

            self.a = self.get_scaled_value(self.props.scaling_rule_a.currentIndex(), speed_percent_a)
            self.b = self.get_scaled_value(self.props.scaling_rule_b.currentIndex(), speed_percent_b)
            self.c = self.get_scaled_value(self.props.scaling_rule_c.currentIndex(), speed_percent_c)

            self.X, self.Y, self.Z = self.create_function(self.a, self.b, self.c)
            self.plot_function(self.X, self.Y, self.Z)
        except Exception as e:
            print(f"Error during update: {e}")

    def get_scaled_value(self, rule_index, speed_percent):
        if rule_index == 0:  # sin(t)
            return np.sin(self.time * speed_percent)
        elif rule_index == 1:  # cos(t)
            return np.cos(self.time * speed_percent)
        elif rule_index == 2:  # tan(t)
            return np.tan(self.time * speed_percent)
        else:  # static
            return 1

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
        self.function_input = self.props.function_input.text()
        self.X, self.Y, self.Z = self.create_function(self.a, self.b, self.c)
        self.plot_function(self.X, self.Y, self.Z)

    def update_colormap(self):
        self.cm = get_colormap(self.props.combo.currentText())
        self.plot_function(self.X, self.Y, self.Z)

if __name__ == '__main__':
    appQt = QtWidgets.QApplication([])
    function_plotter = FunctionPlotter()
    function_plotter.show()
    appQt.exec_()