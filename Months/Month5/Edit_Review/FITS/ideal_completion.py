# ideal_completion.py

import sys
import os
import logging
from datetime import datetime
from astropy.io import fits
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QFileDialog, QMessageBox, QProgressBar, QMainWindow, QRadioButton, QButtonGroup
)
from PyQt6.QtGui import QIcon
import qdarkstyle
from threading import Thread

logging.basicConfig(
    filename="fits_manager.log",
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
# Create the application object
app = QWidget.QApplication(sys.argv)

# Apply QDarkStyle
app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())

# Create and show the main window
main_window = QtWidgets.QMainWindow()
main_window.show()

# Run the application
sys.exit(app.exec_())

class FitsManagerAndChangerApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("FITS File Manager & Changer")
        self.setWindowIcon(QIcon("example.ico"))
        self.setGeometry(100, 100, 500, 400)

        details = QLabel("""
            <ul>
                <li>Alters: 'SITELAT', 'SITELONG' keys</li>
                <li>Deletes: 'XPIXELSZ', 'YPIXELSZ', 'CDELTM1', 'CDELTM2' keys</li>
                <li>Rename files in batches for PixInsight</li>
                <li>Naming pattern: [OBJID]_CAT_[DATE]_[EAST/WEST]_index for lights, FLAT_CAT_[DATE]FILTER_[INDEX] for flats</li>
            </ul>
        """, self)

        details.setWordWrap(True)

        # Radio buttons for file type selection
        self.radio_flats = QRadioButton("Flats")
        self.radio_lights = QRadioButton("Lights")
        self.radio_lights.setChecked(True)  
        self.radio_group = QButtonGroup(self)
        self.radio_group.addButton(self.radio_flats)
        self.radio_group.addButton(self.radio_lights)

        self.object_id_label = QLabel("Define Object ID:", self)
        self.object_id_input = QLineEdit(self)

        self.filter_name_label = QLabel("Define Filter Name:", self)
        self.filter_name_input = QLineEdit(self)

        self.date_label = QLabel("Define Date (DDMMYYYY):", self)
        self.date_input = QLineEdit(self)

        self.label = QLabel("Choose a directory to load FITS files:", self)
        self.button_choose = QPushButton("Choose Directory", self)
        self.button_choose.clicked.connect(self.choose_folder)

        self.button_process = QPushButton("Process and Rename Files", self)
        self.button_process.clicked.connect(self.start_processing)
        self.button_process.setEnabled(False)

        self.progress_bar = QProgressBar(self)
        self.progress_bar.setMinimum(0)
        self.progress_bar.setValue(0)

        layout = QVBoxLayout()
        layout.addWidget(details)
        layout.addWidget(QLabel("Select file type:"))
        layout.addWidget(self.radio_flats)
        layout.addWidget(self.radio_lights)
        layout.addWidget(self.object_id_label)
        layout.addWidget(self.object_id_input)
        layout.addWidget(self.filter_name_label)
        layout.addWidget(self.filter_name_input)
        layout.addWidget(self.date_label)
        layout.addWidget(self.date_input)
        layout.addWidget(self.label)
        layout.addWidget(self.button_choose)
        layout.addWidget(self.button_process)
        layout.addWidget(self.progress_bar)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.folder = ""

    def choose_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Choose Directory")
        if folder:
            self.folder = folder
            fits_files = [f for f in os.listdir(self.folder) if f.lower().endswith('.fits')]
            self.label.setText(f"Selected Folder: {folder} ({len(fits_files)} FITS files found)")
            self.button_process.setEnabled(True if fits_files else False)
            self.auto_fill_from_fits()

    def auto_fill_from_fits(self):
        fits_files = [f for f in os.listdir(self.folder) if f.lower().endswith('.fits')]
        if not fits_files:
            QMessageBox.warning(self, "File Error", "No FITS files located in the chosen folder.")
            return

        first_fits = os.path.join(self.folder, fits_files[0])
        try:
            with fits.open(first_fits) as hdul:
                header = hdul[0].header
                date_obs = header.get("DATE-OBS")
                if date_obs:
                    self.date_input.setText(self.format_date_from_obs(date_obs))

                filter_name = header.get("FILTERS", "").strip()
                if filter_name:
                    self.filter_name_input.setText(filter_name)

        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not read FITS file for auto-fill: {str(e)}")
            logging.error(f"Auto-fill error: {e}")

    def format_date_from_obs(self, date_obs):
        try:
            date_part = date_obs.split('T')[0]
            date_obj = datetime.strptime(date_part, "%Y-%m-%d")
            return date_obj.strftime("%d%m%Y")
        except Exception as e:
            logging.error(f"Error formatting date: {e}")
            return ""

    def start_processing(self):
        thread = Thread(target=self.process_fits, daemon=True)
        thread.start()

    def process_fits(self):
        obj_id = self.object_id_input.text().strip()
        filter_name = self.filter_name_input.text().strip()
        date = self.date_input.text().strip()

        if not (obj_id and filter_name and date):
            QMessageBox.warning(self, "Input Error", "Complete all input areas.")
            return

        if len(date) != 8 or not date.isdigit():
            QMessageBox.warning(self, "Date Error", "Enter a valid date in DDMMYYYY format.")
            return

        if not self.folder:
            return

        fits_files = [f for f in os.listdir(self.folder) if f.endswith('.fits')]
        self.progress_bar.setMaximum(len(fits_files))

        for i, fits_file in enumerate(fits_files):
            file_path = os.path.join(self.folder, fits_file)
            try:
                with fits.open(file_path, mode='update') as hdul:
                    header = hdul[0].header

                    if 'SITELAT' in header:
                        header['SITELAT'] = self.modify_format(header['SITELAT'])
                    if 'SITELONG' in header:
                        header['SITELONG'] = self.modify_format(header['SITELONG'])

                    for key in ['XPIXELSZ', 'YPIXELSZ', 'CDELTM1', 'CDELTM2']:
                        if key in header:
                            del header[key]

                    new_name = self.generate_filename(i, header, obj_id, filter_name, date)
                    hdul.flush()

                new_file_path = os.path.join(self.folder, new_name)
                if os.path.exists(new_file_path):
                    new_file_path = os.path.join(self.folder, f"{new_name}_{i+1}")

                os.rename(file_path, new_file_path)
                self.progress_bar.setValue(i + 1)

            except Exception as e:
                QMessageBox.warning(self, "Processing Error", f"Error processing {fits_file}: {str(e)}")
                logging.error(f"Error processing file {file_path}: {e}")

    def generate_filename(self, index, header, obj_id, filter_name, date):
        if self.radio_flats.isChecked():
            return f"FLAT_CAT_{date}_FILTER_{filter_name}_{index+1:04d}.fits"
        else:
            pierside = header.get("PIERSIDE", "").strip()
            side = "EAST" if pierside.upper() == "WEST" else "WEST" if pierside.upper() == "EAST" else "UNKNOWN"
            return f"{obj_id}_CAT_{date}_FILTER_{filter_name}_{side}_{index+1:04d}.fits"

    def modify_format(self, value):
        if isinstance(value, str):
            parts = value.split(':')
            if len(parts) >= 3:
                return ':'.join(parts[:3])
        return value

if __name__ == "__main__":
    app = QApplication(sys.argv)
    qdarkstyle.setusep_theme()
    window = FitsManagerAndChangerApp()
    window.show()
    sys.exit(app.exec())