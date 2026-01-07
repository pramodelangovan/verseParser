"""
Base Lyrics Scraper Interface

This module defines the abstract base class for all lyrics scrapers.
Each scraper implementation should inherit from this class and implement
the required methods.
"""

from abc import ABC, abstractmethod
from pathlib import Path
import os
import json


class LyricsScraper(ABC):
    """Abstract base class for lyrics scrapers"""

    def __init__(self, output_dir="./output/"):
        """Initialize the scraper

        Args:
            output_dir: Directory to save downloaded lyrics
        """
        self.output_dir = output_dir
        self.check_folder(output_dir)

    @property
    @abstractmethod
    def name(self):
        """Return the name of the scraper source"""
        pass

    @property
    @abstractmethod
    def description(self):
        """Return a description of what this scraper does"""
        pass

    @abstractmethod
    def scrape(self, artist_name, **kwargs):
        """Scrape lyrics for the given artist

        Args:
            artist_name: Name of the artist to scrape
            **kwargs: Additional arguments specific to the scraper

        Returns:
            dict: Scraping result with keys:
                - success: bool - Whether scraping was successful
                - message: str - Status message
                - files_count: int - Number of files downloaded
        """
        pass

    @staticmethod
    def check_folder(path):
        """Create a folder if it doesn't exist"""
        folder = Path(path)
        folder.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def check_file(file_path):
        """Generate a unique file path by appending a counter if file exists"""
        path = Path(file_path)

        if not path.exists():
            return str(path)

        stem = path.stem
        suffix = path.suffix
        parent = path.parent

        counter = 1
        while True:
            new_name = f"{stem}_{counter}{suffix}"
            new_path = parent / new_name
            if not new_path.exists():
                return str(new_path)
            counter += 1

    def write_to_output(self, contents, file_name, album="", artist_name=""):
        """Write lyrics content to a file in the output directory

        Args:
            contents: The lyrics content to write
            file_name: Name of the file (without extension)
            album: Album name (optional, used for subfolder)
        """
        album = album if album else ""
        folder_path = os.path.join(self.output_dir, artist_name)
        self.check_folder(folder_path)
        folder_path = os.path.join(folder_path, album)
        self.check_folder(folder_path)
        file_path = os.path.join(folder_path, f"{file_name}.txt")
        file_path = self.check_file(file_path)
        print(f"Writing to {file_path}")
        with open(file_path, 'w+', encoding='utf-8') as out_file:
            out_file.write(contents)

    def get_cache_dir(self):
        """Get the cache directory for artist data

        Returns:
            str: Path to cache directory
        """
        cache_dir = os.path.join(str(Path.home()), ".cache", "verseparser")
        os.makedirs(cache_dir, exist_ok=True)
        return cache_dir

    def get_cache_file(self):
        """Get the cache file path for this scraper's artists

        Returns:
            str: Path to cache file
        """
        cache_dir = self.get_cache_dir()
        return os.path.join(cache_dir, f"{self.name}_artists.json")

    def load_artists_from_cache(self):
        """Load artists from cache file if it exists

        Returns:
            list: List of artists or None if cache doesn't exist/is invalid
        """
        cache_file = self.get_cache_file()
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, list) and len(data) > 0:
                        return data
            except Exception:
                pass
        return None

    def save_artists_to_cache(self, artists_data):
        """Save artists to cache file

        Args:
            artists_data: List of artist data to cache
        """
        cache_file = self.get_cache_file()
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(artists_data, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def clear_cache(self):
        """Clear the artists cache file"""
        cache_file = self.get_cache_file()
        if os.path.exists(cache_file):
            try:
                os.remove(cache_file)
            except Exception:
                pass