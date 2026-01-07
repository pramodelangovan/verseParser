"""
Master Lyrics Scraper

High-level interface for scraping lyrics from various sources.
This is what the GUI will interact with.
"""

from scraper_factory import ScraperFactory


class MasterScraper:
    """Master interface for scraping lyrics from different sources"""

    def __init__(self, output_dir="./output/"):
        """Initialize the master scraper

        Args:
            output_dir: Directory to save downloaded lyrics
        """
        self.output_dir = output_dir

    @staticmethod
    def get_available_sources():
        """Get list of available sources

        Returns:
            list: List of source names
        """
        return ScraperFactory.get_available_sources()

    @staticmethod
    def get_sources_info():
        """Get detailed information about all sources

        Returns:
            dict: Dictionary with source information
        """
        return ScraperFactory.get_scrapers_info()

    def scrape(self, source, artist_name, **kwargs):
        """Scrape lyrics from a specific source

        Args:
            source: Source name (e.g., "thegodsmusic")
            artist_name: Name of the artist to scrape
            **kwargs: Additional source-specific arguments

        Returns:
            dict: Result with keys:
                - success: bool
                - message: str
                - files_count: int
        """
        try:
            # Get the scraper for this source
            scraper = ScraperFactory.get_scraper(source, output_dir=self.output_dir)

            # Perform the scraping
            result = scraper.scrape(artist_name, **kwargs)

            return result

        except Exception as e:
            return {
                "success": False,
                "message": f"Error: {str(e)}",
                "files_count": 0
            }
