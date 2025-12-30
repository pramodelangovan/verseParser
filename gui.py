import chardet
import json
import os
import sys

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication, QCheckBox, QFileDialog, QHBoxLayout, QLabel, QLineEdit,
    QMainWindow, QMessageBox, QPushButton, QVBoxLayout, QWidget
)


def detect_encoding(file_path):
    """Detect the encoding of a file"""
    try:
        with open(file_path, 'rb') as f:
            result = chardet.detect(f.read())
            return result['encoding']
    except Exception as e:
        print(f"Error detecting encoding: {e}")
    return "utf-8"


class VerseParserGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.input_folder = ""
        self.output_folder = ""
        self.metadata_flag = True
        self.versename_flag = True
        self.init_ui()

    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("Verse Parser")
        self.setGeometry(100, 100, 600, 100)

        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Create main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(15, 15, 15, 15)

        # Input folder selection
        input_layout = QHBoxLayout()
        input_label = QLabel("Input Folder:")
        input_label.setFixedWidth(100)
        self.input_path_field = QLineEdit()
        self.input_path_field.setReadOnly(True)
        input_browse_btn = QPushButton("Browse")
        input_browse_btn.clicked.connect(self.select_input_folder)
        input_layout.addWidget(input_label)
        input_layout.addWidget(self.input_path_field)
        input_layout.addWidget(input_browse_btn)

        # Output folder selection
        output_layout = QHBoxLayout()
        output_label = QLabel("Output Folder:")
        output_label.setFixedWidth(100)
        self.output_path_field = QLineEdit()
        self.output_path_field.setReadOnly(True)
        output_browse_btn = QPushButton("Browse")
        output_browse_btn.clicked.connect(self.select_output_folder)
        output_layout.addWidget(output_label)
        output_layout.addWidget(self.output_path_field)
        output_layout.addWidget(output_browse_btn)

        # Checkboxes for options
        options_layout = QHBoxLayout()
        self.metadata_checkbox = QCheckBox("Include Metadata")
        self.metadata_checkbox.setChecked(True)
        self.metadata_checkbox.stateChanged.connect(self.update_metadata_flag)
        self.versename_checkbox = QCheckBox("Include Verse Names")
        self.versename_checkbox.setChecked(True)
        self.versename_checkbox.stateChanged.connect(self.update_versename_flag)
        options_layout.addWidget(self.metadata_checkbox)
        options_layout.addWidget(self.versename_checkbox)
        options_layout.addStretch()

        # Buttons layout
        button_layout = QHBoxLayout()
        generate_btn = QPushButton("Generate")
        generate_btn.setFixedWidth(100)
        generate_btn.clicked.connect(self.process_files)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setFixedWidth(100)
        cancel_btn.clicked.connect(self.close)
        button_layout.addStretch()
        button_layout.addWidget(generate_btn)
        button_layout.addWidget(cancel_btn)

        # Add all layouts to main layout
        main_layout.addLayout(input_layout)
        main_layout.addLayout(output_layout)
        main_layout.addLayout(options_layout)
        main_layout.addStretch()
        main_layout.addLayout(button_layout)

    def select_input_folder(self):
        """Open dialog to select input folder"""
        folder = QFileDialog.getExistingDirectory(self, "Select Input Folder")
        if folder:
            self.input_folder = folder
            self.input_path_field.setText(folder)

    def select_output_folder(self):
        """Open dialog to select output folder"""
        folder = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if folder:
            self.output_folder = folder
            self.output_path_field.setText(folder)

    def update_metadata_flag(self, state):
        """Update metadata flag based on checkbox state"""
        self.metadata_flag = state == Qt.CheckState.Checked.value

    def update_versename_flag(self, state):
        """Update versename flag based on checkbox state"""
        self.versename_flag = state == Qt.CheckState.Checked.value

    def process_content(self, content):
        """Process JSON content and return formatted text"""
        data = json.load(content)
        out = ''
        if self.metadata_flag:
            out += "\n".join([f"{prop}: {self.str_to_list(value).strip()}"
                            for prop, value in data["properties"].items()])
            out += '\n\n'
        for lines in data['lyrics']['verse']:
            if self.versename_flag:
                out += f"Verse: {lines['name']}\n"
            for line in lines['lines']:
                out += f"{line}\n"
            out += "\n"
        return out

    def str_to_list(self, value):
        """Convert list to comma-separated string if needed"""
        return value if isinstance(value, str) else ", ".join(value)

    def process_files(self):
        """Process files from input folder to output folder"""
        # Validation
        if not self.input_folder:
            QMessageBox.warning(self, "Error", "Please select an input folder.")
            return
        if not self.output_folder:
            QMessageBox.warning(self, "Error", "Please select an output folder.")
            return
        if not os.path.isdir(self.input_folder):
            QMessageBox.warning(self, "Error", f"{self.input_folder} is not a valid directory.")
            return

        try:
            # Create output folder if it doesn't exist
            if not os.path.exists(self.output_folder):
                os.makedirs(self.output_folder)

            # Process all files
            file_count = 0
            for root, dirs, files in os.walk(self.input_folder):
                # Replicate directory structure in output folder
                relative_path = os.path.relpath(root, self.input_folder)
                target_dir = os.path.join(self.output_folder, relative_path)
                os.makedirs(target_dir, exist_ok=True)

                for file in files:
                    input_file_path = os.path.join(root, file)
                    # Replace file extension with .txt
                    output_file_name = os.path.splitext(file)[0] + ".txt"
                    output_file_path = os.path.join(target_dir, output_file_name)

                    # Detect encoding
                    encoding = detect_encoding(input_file_path)

                    with open(input_file_path, 'r', encoding=encoding) as infile:
                        processed_content = self.process_content(infile)
                        with open(output_file_path, 'w', encoding=encoding) as outfile:
                            outfile.write(processed_content)

                    file_count += 1

            QMessageBox.information(self, "Success",
                                  f"Successfully processed {file_count} file(s).\n"
                                  f"Output saved to: {self.output_folder}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")


def main():
    app = QApplication(sys.argv)
    window = VerseParserGUI()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
