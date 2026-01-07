"""
Verse Parser GUI

GUI application for processing JSON verse files to text format using PyQt6.
Loads UI from ui_main.ui XML file.
Also provides lyrics download functionality through scraper integration.
"""

import os
import sys
import json
from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QFileDialog, QMainWindow, QMessageBox, QDialog, QLabel, QVBoxLayout
from PyQt6 import uic

from parser import process_files
from scraper_master import MasterScraper


class VerseParserGUI(QMainWindow):
    """Main GUI window for the Verse Parser application"""

    def __init__(self):
        super().__init__()
        self.input_folder = ""
        self.output_folder = ""
        self.metadata_flag = True
        self.versename_flag = True
        self.lyrics_destination = ""
        self.current_artists_cache = None
        self.master_scraper = None

        # Load UI from .ui file
        ui_path = Path(__file__).parent / "ui_main.ui"
        uic.loadUi(ui_path, self)

        # Connect signals to slots
        self.connect_signals()

        # Initialize scraper with output folder
        self.initialize_scraper()

    def connect_signals(self):
        """Connect all UI signals to their corresponding slots"""
        # Tab 1: Verse Parser
        self.inputBrowseBtn.clicked.connect(self.select_input_folder)
        self.outputBrowseBtn.clicked.connect(self.select_output_folder)
        self.metadataCheckbox.stateChanged.connect(self.update_metadata_flag)
        self.versenameCheckbox.stateChanged.connect(self.update_versename_flag)
        self.generateBtn.clicked.connect(self.process_files)
        self.cancelBtn.clicked.connect(self.close)

        # Tab 2: Lyrics Download
        self.sourceComboBox.currentTextChanged.connect(self.on_source_changed)
        self.refreshArtistsBtn.clicked.connect(self.refresh_artists)
        self.destinationBrowseBtn.clicked.connect(self.select_lyrics_destination)
        self.downloadLyricsBtn.clicked.connect(self.download_lyrics)
        self.cancelLyricsBtn.clicked.connect(self.close)

    def select_input_folder(self):
        """Open dialog to select input folder"""
        folder = QFileDialog.getExistingDirectory(self, "Select Input Folder")
        if folder:
            self.input_folder = folder
            self.inputPathField.setText(folder)

    def select_output_folder(self):
        """Open dialog to select output folder"""
        folder = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if folder:
            self.output_folder = folder
            self.outputPathField.setText(folder)

    def update_metadata_flag(self, state):
        """Update metadata flag based on checkbox state"""
        self.metadata_flag = state == Qt.CheckState.Checked.value

    def update_versename_flag(self, state):
        """Update versename flag based on checkbox state"""
        self.versename_flag = state == Qt.CheckState.Checked.value

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

            # Process files using the parser module
            file_count = process_files(
                self.input_folder,
                self.output_folder,
                self.metadata_flag,
                self.versename_flag
            )

            QMessageBox.information(self, "Success",
                                  f"Successfully processed {file_count} file(s).\n"
                                  f"Output saved to: {self.output_folder}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")


    # ============ Lyrics Download Tab Methods ============

    def initialize_scraper(self):
        """Initialize the master scraper and populate sources"""
        try:
            lyrics_dir = os.path.join(str(Path.home()), "Downloads", "LyricsDownload")
            self.master_scraper = MasterScraper(output_dir=lyrics_dir)
            self.lyrics_destination = lyrics_dir
            self.destinationPathField.setText(lyrics_dir)

            # Populate source dropdown
            sources = self.master_scraper.get_available_sources()
            self.sourceComboBox.addItems(sources)

            self.log_console(f"Initialized scraper with {len(sources)} source(s)")
            self.log_console(f"Default destination: {lyrics_dir}")

            # Try to load cached artists for first source if cache exists
            if sources:
                from scraper_factory import ScraperFactory
                scraper = ScraperFactory.get_scraper(sources[0], output_dir=lyrics_dir)
                # Only load from cache if it exists, don't download
                cached_artists = scraper.load_artists_from_cache()
                if cached_artists:
                    artists = [artist.get('artist', '') for artist in cached_artists]
                    self.artistComboBox.addItems(sorted(artists))
                    self.log_console(f"Loaded {len(artists)} cached artists for {sources[0]}")
                else:
                    self.log_console(f"No cached artists for {sources[0]}. Click Refresh to download.")
        except Exception as e:
            self.log_console(f"Error initializing scraper: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to initialize scraper: {str(e)}")

    def log_console(self, message):
        """Log a message to the console output"""
        current_text = self.consoleOutput.toPlainText()
        new_text = f"{current_text}\n{message}" if current_text else message
        self.consoleOutput.setPlainText(new_text)
        # Scroll to bottom
        self.consoleOutput.verticalScrollBar().setValue(
            self.consoleOutput.verticalScrollBar().maximum()
        )

    def on_source_changed(self, source_name):
        """Handle source dropdown change"""
        if not source_name:
            return
        self.log_console(f"Selected source: {source_name}")
        # Only load cached artists if they exist, don't download
        from scraper_factory import ScraperFactory
        scraper = ScraperFactory.get_scraper(source_name, output_dir=self.lyrics_destination)
        cached_artists = scraper.load_artists_from_cache()
        if cached_artists:
            self.artistComboBox.clear()
            artists = [artist.get('artist', '') for artist in cached_artists]
            self.artistComboBox.addItems(sorted(artists))
            self.log_console(f"Loaded {len(artists)} cached artists")
        else:
            # Clear artist combobox when no cache available
            self.artistComboBox.clear()
            self.current_artists_cache = None
            self.log_console("No cached artists. Click Refresh to download artists.")

    def get_artists_cache_file(self):
        """Get the path to the artists cache file for current source"""
        source = self.sourceComboBox.currentText()
        if not source:
            return None
        cache_dir = os.path.join(str(Path.home()), ".cache", "verseparser")
        os.makedirs(cache_dir, exist_ok=True)
        return os.path.join(cache_dir, f"{source}_artists.json")

    def load_artists_from_cache(self):
        """Load artists from cache file if it exists"""
        cache_file = self.get_artists_cache_file()
        if cache_file and os.path.exists(cache_file):
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, list) and len(data) > 0:
                        artists = [artist.get('artist', '') if isinstance(artist, dict) else str(artist) for artist in data]
                        self.current_artists_cache = data
                        self.log_console(f"Loaded {len(artists)} artists from cache")
                        return artists
            except Exception as e:
                self.log_console(f"Error loading cache: {str(e)}")
        return None

    def save_artists_to_cache(self, artists_data):
        """Save artists to cache file"""
        cache_file = self.get_artists_cache_file()
        if cache_file:
            try:
                with open(cache_file, 'w', encoding='utf-8') as f:
                    json.dump(artists_data, f, ensure_ascii=False, indent=2)
                self.log_console(f"Cached {len(artists_data)} artists")
            except Exception as e:
                self.log_console(f"Error saving cache: {str(e)}")

    def refresh_artists(self):
        """Refresh the artist list from the selected source"""
        source = self.sourceComboBox.currentText()
        if not source:
            QMessageBox.warning(self, "Error", "Please select a source first.")
            return

        self.log_console(f"Refreshing artists for {source}...")
        self.refreshArtistsBtn.setEnabled(False)

        # Delete existing cache file
        cache_file = self.get_artists_cache_file()
        if cache_file and os.path.exists(cache_file):
            try:
                os.remove(cache_file)
                self.log_console("Deleted existing cache file")
            except Exception as e:
                self.log_console(f"Warning: Could not delete cache file: {str(e)}")

        # Create undismissable dialog with just text
        dialog = QDialog(self)
        dialog.setWindowModality(Qt.WindowModality.ApplicationModal)
        dialog.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.CustomizeWindowHint)
        dialog.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)

        layout = QVBoxLayout(dialog)
        label = QLabel("Fetching artists...")
        layout.addWidget(label)
        dialog.setLayout(layout)
        dialog.show()

        # Process events to show the dialog
        QApplication.processEvents()

        try:
            from scraper_factory import ScraperFactory

            scraper = ScraperFactory.get_scraper(source, output_dir=self.lyrics_destination)

            # Get artists with force refresh (will clear cache and download fresh)
            if hasattr(scraper, 'get_artists'):
                self.log_console("Downloading artists list (this may take a moment)...")
                try:
                    # Get fresh artists - scraper handles caching internally
                    artists_data = scraper.get_artists(force_refresh=True)

                    if artists_data:
                        # Populate combobox
                        self.current_artists_cache = artists_data
                        artists = [artist.get('artist', '') for artist in artists_data]
                        self.artistComboBox.clear()
                        self.artistComboBox.addItems(sorted(artists))
                        self.log_console(f"Successfully loaded {len(artists)} artists")
                    else:
                        self.log_console("No artists found")
                except Exception as e:
                    self.log_console(f"Error downloading artists: {str(e)}")
            else:
                self.log_console("Note: This source does not support artist listing")
        except Exception as e:
            self.log_console(f"Error refreshing artists: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to refresh artists: {str(e)}")
        finally:
            dialog.close()
            self.refreshArtistsBtn.setEnabled(True)

    def select_lyrics_destination(self):
        """Open dialog to select lyrics destination folder"""
        folder = QFileDialog.getExistingDirectory(self, "Select Lyrics Destination Folder")
        if folder:
            self.lyrics_destination = folder
            self.destinationPathField.setText(folder)
            self.log_console(f"Destination folder set to: {folder}")

    def download_lyrics(self):
        """Download lyrics for selected artist from selected source"""
        # Validation
        source = self.sourceComboBox.currentText()
        if not source:
            QMessageBox.warning(self, "Error", "Please select a source.")
            return

        artist = self.artistComboBox.currentText()
        if not artist:
            QMessageBox.warning(self, "Error", "Please select an artist.")
            return

        if not self.lyrics_destination:
            QMessageBox.warning(self, "Error", "Please select a destination folder.")
            return

        # Disable button during download
        self.downloadLyricsBtn.setEnabled(False)

        # Create undismissable download dialog
        dialog = QDialog(self)
        dialog.setWindowModality(Qt.WindowModality.ApplicationModal)
        dialog.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.CustomizeWindowHint)
        dialog.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)

        layout = QVBoxLayout(dialog)
        label = QLabel("Downloading lyrics...")
        layout.addWidget(label)
        dialog.setLayout(layout)
        dialog.show()

        # Process events to show the dialog
        QApplication.processEvents()

        try:
            self.log_console(f"\n{'='*60}")
            self.log_console(f"Starting download: {artist} from {source}")
            self.log_console(f"Destination: {self.lyrics_destination}")
            self.log_console(f"{'='*60}")

            # Create a new scraper with the selected destination
            master = MasterScraper(output_dir=self.lyrics_destination)

            # Perform the scraping
            result = master.scrape(source, artist)

            # Log results
            self.log_console(f"\nResult: {result['message']}")
            self.log_console(f"Files downloaded: {result['files_count']}")

            if result['success']:
                self.log_console(f"{'='*60}")
                self.log_console("Download completed successfully!")
                self.log_console(f"{'='*60}\n")
                QMessageBox.information(
                    self,
                    "Success",
                    f"Downloaded {result['files_count']} file(s).\n"
                    f"Saved to: {self.lyrics_destination}"
                )
            else:
                self.log_console(f"{'='*60}")
                self.log_console("Download failed!")
                self.log_console(f"{'='*60}\n")
                QMessageBox.warning(self, "Warning", result['message'])

        except Exception as e:
            error_msg = f"Error during download: {str(e)}"
            self.log_console(error_msg)
            self.log_console(f"{'='*60}\n")
            QMessageBox.critical(self, "Error", error_msg)
        finally:
            dialog.close()
            self.downloadLyricsBtn.setEnabled(True)


def main():
    """Launch the GUI application"""
    app = QApplication(sys.argv)
    window = VerseParserGUI()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()