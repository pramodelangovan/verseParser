"""
Scraper Factory

This module manages all available lyrics scrapers and provides
a central way to access them.
"""

from scraper_thegodsmusic import TheGodsMusícScraper


class ScraperFactory:
    """Factory for managing lyrics scrapers"""

    _scrapers = {
        "thegodsmusic": TheGodsMusícScraper,
    }

    @classmethod
    def get_scraper(cls, source_name, **kwargs):
        """Get a scraper instance by source name

        Args:
            source_name: Name of the scraper source
            **kwargs: Arguments to pass to the scraper constructor

        Returns:
            LyricsScraper: Instance of the requested scraper

        Raises:
            ValueError: If source not found
        """
        source_key = source_name.lower()
        if source_key not in cls._scrapers:
            raise ValueError(f"Unknown scraper source: {source_name}")

        scraper_class = cls._scrapers[source_key]
        return scraper_class(**kwargs)

    @classmethod
    def get_available_sources(cls):
        """Get list of available scraper sources

        Returns:
            list: List of available source names
        """
        return list(cls._scrapers.keys())

    @classmethod
    def get_scrapers_info(cls):
        """Get information about all available scrapers

        Returns:
            dict: Dictionary with source names as keys and info dicts as values
        """
        info = {}
        for source_name in cls._scrapers.keys():
            try:
                scraper = cls.get_scraper(source_name)
                info[source_name] = {
                    "name": scraper.name,
                    "description": scraper.description
                }
            except Exception as e:
                info[source_name] = {
                    "name": source_name,
                    "description": f"Error loading: {str(e)}"
                }
        return info

    @classmethod
    def register_scraper(cls, source_key, scraper_class):
        """Register a new scraper

        Args:
            source_key: Unique key for the scraper (lowercase)
            scraper_class: Class that inherits from LyricsScraper
        """
        cls._scrapers[source_key.lower()] = scraper_class
