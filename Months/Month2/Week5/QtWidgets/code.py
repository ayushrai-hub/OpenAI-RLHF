import numpy as np
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QSplitter, QVBoxLayout, QSpinBox, QLabel, QComboBox, QPushButton, QLineEdit
from PyQt5.QtCore import Qt
from vispy import scene, app
from vispy.color import get_colormap

class FunctionPlotter(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Function Plotter")
        self.setGeometry(100, 100, 1500, 900)

        self.splitter = QSplitter(Qt.Horizontal)
        self.setCentralWidget(self.splitter)

        self.props = ObjectWidget(self, main_window=self)
        self.splitter.addWidget(self.props)

        self.canvas = scene.SceneCanvas(keys='interactive', show=True)
        self.view = self.canvas.central_widget.add_view()
        self.view.camera = scene.TurntableCamera(fov=45, distance=20)
        self.splitter.addWidget(self.canvas.native)

        self._initialize_parameters()
        self._setup_surface_plot()
        self._setup_timer()
        self._connect_signals()

    def _initialize_parameters(self):
        self.time = 0
        self.a = self.b = 1
        self.c = 0
        self._function_input = self.props.function_input.text()
        self._cm = get_colormap(self.props.combo.currentText())
        self._grid_points = self.props.grid_points.value()
        self._x_limits = (-self.props.x_limits.value(), self.props.x_limits.value())
        self._y_limits = (-self.props.y_limits.value(), self.props.y_limits.value())
        self.X, self.Y, self.Z = self._create_function(self.a, self.b, self.c)

    def _setup_surface_plot(self):
        self.surface = scene.visuals.SurfacePlot(x=self.X, y=self.Y, z=self.Z, shading='smooth')
        self.view.add(self.surface)

    def _setup_timer(self):
        self.timer = app.Timer(connect=self.update, interval=0.1)
        self.timer.start()

    def _connect_signals(self):
        self.props.x_limits.valueChanged.connect(self.update_x_limits)
        self.props.y_limits.valueChanged.connect(self.update_y_limits)
        self.props.grid_points.valueChanged.connect(self.update_grid_points)
        self.props.update_button.clicked.connect(self.update_function)
        self.props.combo.currentIndexChanged.connect(self.update_colormap)

    def _create_function(self, a: float, b: float, c: float):
        x = np.linspace(*self._x_limits, self._grid_points)
        y = np.linspace(*self._y_limits, self._grid_points)
        X, Y = np.meshgrid(x, y)
        context = {'X': X, 'Y': Y, 'a': a, 'b': b, 'c': c, 'np': np}
        try:
            Z = eval(self._function_input, context)
        except Exception as e:
            print(f"Error evaluating function: {e}")
            Z = np.zeros_like(X)
        return X, Y, Z

    def _plot_function(self, X, Y, Z):
        norm_Z = (Z - Z.min()) / (Z.max() - Z.min())
        colors = self._cm.map(norm_Z)
        self.surface.set_data(z=Z, x=X, y=Y)
        self.surface.mesh_data.set_vertex_colors(colors)

    def update(self, event):
        try:
            self.time += 0.1
            self.a = self._get_scaled_value(self.props.scaling_rule_a.currentIndex(), 
                                            int(self.props.scaling_speed_a.currentText().split()[0]) / 100)
            self.b = self._get_scaled_value(self.props.scaling_rule_b.currentIndex(), 
                                            int(self.props.scaling_speed_b.currentText().split()[0]) / 100)
            self.c = self._get_scaled_value(self.props.scaling_rule_c.currentIndex(), 
                                            int(self.props.scaling_speed_c.currentText().split()[0]) / 100)
            self.X, self.Y, self.Z = self._create_function(self.a, self.b, self.c)
            self._plot_function(self.X, self.Y, self.Z)
        except Exception as e:
            print(f"Error during update: {e}")

    @staticmethod
    def _get_scaled_value(rule_index: int, speed_percent: float) -> float:
        if rule_index == 0:  # sin(t)
            return np.sin(self.time * speed_percent)
        elif rule_index == 1:  # cos(t)
            return np.cos(self.time * speed_percent)
        elif rule_index == 2:  # tan(t)
            return np.tan(self.time * speed_percent)
        else:  # static
            return 1

    def update_x_limits(self):
        self._x_limits = (-self.props.x_limits.value(), self.props.x_limits.value())
        self.update_function()

    def update_y_limits(self):
        self._y_limits = (-self.props.y_limits.value(), self.props.y_limits.value())
        self.update_function()

    def update_grid_points(self):
        self._grid_points = self.props.grid_points.value()
        self.update_function()

    def update_function(self):
        self._function_input = self.props.function_input.text()
        self.X, self.Y, self.Z = self._create_function(self.a, self.b, self.c)
        self._plot_function(self.X, self.Y, self.Z)

    def update_colormap(self):
        self._cm = get_colormap(self.props.combo.currentText())
        self._plot_function(self.X, self.Y, self.Z)