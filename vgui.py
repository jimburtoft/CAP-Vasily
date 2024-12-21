import sys
import os
import xml.etree.ElementTree as ET
import PyQt5
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFileDialog, 
                             QLineEdit, QMessageBox, QGroupBox, QRadioButton, QScrollArea, QCheckBox, QInputDialog)
from PyQt5.QtGui import QPixmap, QDoubleValidator
from PyQt5.QtCore import Qt
import webview
import io

# Import the utility functions
from flightline_utils import add_endpoints, flip_rows, add_keyholes, output_points, fpl_export, resource_path

#To build:
# pyi-makespec --name="CAP Waldo Flightline Converter" --windowed --onefile --add-data="logo.png;." --add-data="flightline_utils.py;." vgui.py
# pyi-makespec --name="CAP Waldo Flightline Converter" --windowed --onefile --add-data="logo.png;." --add-data="flightline_utils.py;." --hidden-import PyQt5 --hidden-import PyQt5.QtCore --hidden-import PyQt5.QtGui --hidden-import PyQt5.QtWidgets vgui.py

# edit datas to have add         ('flightline_utils.py', '.'),  # Add this line
# pyinstaller "CAP Waldo Flightline Converter.spec"

class ConverterApp(QWidget):
    def __init__(self, is_web=False):
        super().__init__()
        self.is_web = is_web
        self.flightlines = []
        self.initUI()

    def initUI(self):
        self.setWindowTitle('CAP Waldo Flightline Converter')
        self.setMinimumSize(600, 450)

        main_layout = QVBoxLayout()

        # Scroll area for the main content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)

        # Logo
        logo_label = QLabel(self)
        logo_path = resource_path('logo.png')
        pixmap = QPixmap(logo_path)  # Replace with your actual logo file
        pixmap = pixmap.scaled(256, 256, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        logo_label.setPixmap(pixmap)
        logo_label.setAlignment(Qt.AlignCenter)
        scroll_layout.addWidget(logo_label)

        # Title
        title_label = QLabel('CAP Waldo Flightline Converter')
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 20px; font-weight: bold;")
        scroll_layout.addWidget(title_label)

        # Input file selection
        input_layout = QHBoxLayout()
        self.input_line = QLineEdit()
        self.input_line.setReadOnly(True)
        input_layout.addWidget(self.input_line)
        self.input_button = QPushButton('Choose File')
        self.input_button.clicked.connect(self.select_input_file if not self.is_web else self.web_select_input_file)
        input_layout.addWidget(self.input_button)
        scroll_layout.addLayout(input_layout)

        # Output file selection
        output_layout = QHBoxLayout()
        output_label = QLabel('Output path:')
        output_layout.addWidget(output_label)
        self.output_line = QLineEdit()
        self.output_line.setReadOnly(True)
        output_layout.addWidget(self.output_line)
        self.output_button = QPushButton('Choose File')
        self.output_button.clicked.connect(self.select_output_file if not self.is_web else self.web_set_output_file)
        output_layout.addWidget(self.output_button)
        scroll_layout.addLayout(output_layout)

        # Preprocess button
        self.preprocess_button = QPushButton('Preprocess')
        self.preprocess_button.clicked.connect(self.preprocess)
        scroll_layout.addWidget(self.preprocess_button)

        # Flightline selection group
        self.flightline_group = QGroupBox("Starting Corner Selection")
        self.flightline_group.setVisible(False)
        flightline_layout = QVBoxLayout()
        self.corner_radio_1 = QRadioButton("First corner")
        self.corner_radio_2 = QRadioButton("Second corner")
        self.corner_radio_1.setChecked(True)
        flightline_layout.addWidget(self.corner_radio_1)
        flightline_layout.addWidget(self.corner_radio_2)
        self.flightline_group.setLayout(flightline_layout)
        scroll_layout.addWidget(self.flightline_group)

        # Pattern selection group
        self.pattern_group = QGroupBox("Flight Pattern")
        self.pattern_group.setVisible(False)
        pattern_layout = QHBoxLayout()
        self.sawtooth_radio = QRadioButton("Sawtooth")
        self.unidirectional_radio = QRadioButton("Unidirectional")
        self.sawtooth_radio.setChecked(True)
        self.sawtooth_radio.toggled.connect(self.update_keyhole_availability)
        self.unidirectional_radio.toggled.connect(self.update_keyhole_availability)
        pattern_layout.addWidget(self.sawtooth_radio)
        pattern_layout.addWidget(self.unidirectional_radio)
        self.pattern_group.setLayout(pattern_layout)
        scroll_layout.addWidget(self.pattern_group)

        # Options group
        self.options_group = QGroupBox("Additional Options")
        self.options_group.setVisible(False)
        options_layout = QVBoxLayout()
        extension_layout = QHBoxLayout()
        self.extension_checkbox = QCheckBox("Extension points")
        self.extension_checkbox.setChecked(True)
        self.keyhole_checkbox = QCheckBox("Keyhole points")
        self.keyhole_checkbox.setChecked(False)
        extension_layout.addWidget(self.extension_checkbox)
        
        self.extension_value = QLineEdit()
        self.extension_value.setText("0.5")
        self.extension_value.setFixedWidth(60)
        self.extension_value.setValidator(QDoubleValidator(0.0, 100.0, 2))
        extension_layout.addWidget(self.extension_value)
        
        extension_label = QLabel("nautical miles")
        extension_layout.addWidget(extension_label)
        extension_layout.addStretch()
        options_layout.addLayout(extension_layout)
        options_layout.addWidget(self.keyhole_checkbox)
        self.options_group.setLayout(options_layout)
        scroll_layout.addWidget(self.options_group)

        # Export button
        self.export_button = QPushButton('Export')
        self.export_button.clicked.connect(self.export)
        self.export_button.setVisible(False)
        scroll_layout.addWidget(self.export_button)

        scroll.setWidget(scroll_content)
        main_layout.addWidget(scroll)

        self.setLayout(main_layout)

    def select_input_file(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Select KML File", "", "KML Files (*.kml)")
        if file_name:
            self.input_line.setText(file_name)
            self.update_output_path(file_name)

    def select_output_file(self):
        file_name, _ = QFileDialog.getSaveFileName(self, "Save FPL File", "", "FPL Files (*.fpl)")
        if file_name:
            self.output_line.setText(file_name)

    def web_select_input_file(self):
        file_content = webview.windows[0].create_file_dialog(webview.OPEN_DIALOG, allow_multiple=False, file_types=['KML Files (*.kml)'])
        if file_content:
            self.process_kml_content(file_content[0])

    def web_set_output_file(self):
        filename, ok = QInputDialog.getText(self, 'Set Output Filename', 'Enter filename (without extension):')
        if ok and filename:
            self.output_line.setText(filename + '.fpl')

    def update_output_path(self, input_path):
        dir_name = os.path.dirname(input_path)
        base_name = os.path.splitext(os.path.basename(input_path))[0]
        output_path = os.path.join(dir_name, f"{base_name}.fpl")
        self.output_line.setText(output_path)

    def preprocess(self):
        kml_file = self.input_line.text()
        if not kml_file:
            QMessageBox.warning(self, "Error", "Please select a KML file first.")
            return

        try:
            tree = ET.parse(kml_file)
            self.process_kml_tree(tree)
        except ET.ParseError:
            QMessageBox.warning(self, "Error", f"File {kml_file} is not a valid KML file. Please select a valid KML file.")

    def process_kml_content(self, content):
        try:
            tree = ET.fromstring(content)
            self.process_kml_tree(tree)
        except ET.ParseError:
            QMessageBox.warning(self, "Error", "Invalid KML file. Please select a valid KML file.")

    def process_kml_tree(self, tree):
        root = tree.getroot()
        self.flightlines = []

        for placemark in root.iter("{http://www.opengis.net/kml/2.2}Placemark"):
            name = placemark.find("{http://www.opengis.net/kml/2.2}name").text
            if name.startswith(" Flightline"):
                coordinates_tag = placemark.find("{http://www.opengis.net/kml/2.2}LineString/{http://www.opengis.net/kml/2.2}coordinates")
                if coordinates_tag is not None:
                    coordinates = self.extract_coordinates(coordinates_tag)
                    self.flightlines.append(coordinates)

        if self.flightlines:
            self.update_flightline_display()
            self.flightline_group.setVisible(True)
            self.pattern_group.setVisible(True)
            self.options_group.setVisible(True)
            self.export_button.setVisible(True)
            QMessageBox.information(self, "Preprocess Complete", f"Preprocessing complete. Found {len(self.flightlines)} flightlines.")
        else:
            QMessageBox.warning(self, "Error", "No flightlines found in the KML file.")

    def extract_coordinates(self, coordinates_tag):
        coordinates = coordinates_tag.text.strip().split()
        coordinates = [coord.split(',') for coord in coordinates]
        #remember, two coordinates per row and lat/long flipped in kml.  Returning 1,0 instead of 0,1 fixes that for everything
        return [(float(coord[1]), float(coord[0])) for coord in coordinates]

    def update_flightline_display(self):
        if self.flightlines:
            self.corner_radio_1.setText(f"First corner: {self.flightlines[0][0]}")
            self.corner_radio_2.setText(f"Second corner: {self.flightlines[0][1]}")

    def update_keyhole_availability(self):
        self.keyhole_checkbox.setEnabled(self.sawtooth_radio.isChecked())
        if self.unidirectional_radio.isChecked():
            self.keyhole_checkbox.setChecked(False)

    def export(self):
        if not self.flightlines:
            QMessageBox.warning(self, "Error", "No flightlines to export. Please preprocess a KML file first.")
            return

        corner_choice = 1 if self.corner_radio_1.isChecked() else 2
        flip = self.sawtooth_radio.isChecked()
        extension_points = self.extension_checkbox.isChecked()
        keyhole_points = self.keyhole_checkbox.isChecked()
        
        processed_flightlines = self.flightlines.copy()

        if extension_points:
            extension_distance = float(self.extension_value.text())
            processed_flightlines = add_endpoints(processed_flightlines, extension_distance)

        processed_flightlines = flip_rows(processed_flightlines, corner_choice, flip)

        if keyhole_points:
            processed_flightlines = add_keyholes(processed_flightlines)

        output_file = self.output_line.text()
        if not output_file:
            QMessageBox.warning(self, "Error", "No output file specified. Please choose an output file.")
            return

        flightlines_output = output_file[:-4] + " flightlines.txt"

        original_kml = self.input_line.text()
        prefix = os.path.basename(original_kml)[:1]

        try:
            if self.is_web:
                flightlines_content = io.StringIO()
                output_points(flightlines_content, processed_flightlines)
                flightlines_content.seek(0)

                fpl_content = io.StringIO()
                fpl_export(processed_flightlines, fpl_content, prefix)
                fpl_content.seek(0)

                webview.windows[0].evaluate_js(f"downloadFile('{os.path.basename(flightlines_output)}', '{flightlines_content.getvalue()}')")
                webview.windows[0].evaluate_js(f"downloadFile('{os.path.basename(output_file)}', '{fpl_content.getvalue()}')")
            else:
                output_points(flightlines_output, processed_flightlines)
                fpl_export(processed_flightlines, output_file, prefix)

            QMessageBox.information(self, "Export Complete", 
                                    f"Export completed successfully with the following settings:\n"
                                    f"Starting corner: {'First' if corner_choice == 1 else 'Second'}\n"
                                    f"Pattern: {'Sawtooth' if flip else 'Unidirectional'}\n"
                                    f"Extension points: {'Added' if extension_points else 'Not added'}\n"
                                    f"Keyhole points: {'Added' if keyhole_points else 'Not added'}\n"
                                    f"Flightlines output: {flightlines_output}\n"
                                    f"FPL output: {output_file}")
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"An error occurred while exporting:\n{str(e)}")

def run_app():
    app = QApplication(sys.argv)
    ex = ConverterApp(is_web=False)
    ex.show()
    sys.exit(app.exec_())

def run_web_app():
    def expose_file_dialog(window):
        window.expose(window.create_file_dialog)

    webview.create_window("CAP Waldo Flightline Converter", ConverterApp(is_web=True), js_api=expose_file_dialog)
    webview.start()

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--web':
        run_web_app()
    else:
        run_app()