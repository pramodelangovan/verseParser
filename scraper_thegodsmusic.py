"""
The God's Music Lyrics Scraper

Scraper implementation for thegodsmusic.com
"""

import re
import requests
from bs4 import BeautifulSoup
from time import sleep

from scraper_base import LyricsScraper


class TheGodsMusícScraper(LyricsScraper):
    """Scraper for thegodsmusic.com"""

    MASTER_URL = "https://thegodsmusic.com/artist/"

    @property
    def name(self):
        return "The God's Music"

    @property
    def description(self):
        return "Scrapes lyrics from thegodsmusic.com"

    def __init__(self, output_dir="./output/"):
        """Initialize The God's Music scraper"""
        super().__init__(output_dir)
        self.artists = []

    def get_soup(self, url):
        """Fetch a URL and return a BeautifulSoup object"""
        sleep(1)
        print(f"Fetching {url}")
        res = requests.get(url)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, 'html5lib')
        return soup

    def get_pages(self, soup):
        """Extract the number of pages from pagination"""
        pagination = soup.find("div", class_="custom-pagination")
        if pagination:
            idx = int(pagination.find_all("li")[-2].text)
            return idx
        return 1

    def parse_artists_page(self, soup):
        """Extract artist URLs and names from a search results page"""
        entries = soup.find_all("div", class_="blog-entry clearfix")
        for entry in entries:
            link = entry.find("h3").find("a")
            if link:
                self.artists.append({
                    "url": link.get("href"),
                    "artist": link.text
                })

    def store_artists(self, url, get_idx=False):
        """Store artists from a page and optionally return the total page count"""
        idx = 0
        soup = self.get_soup(url)
        if get_idx:
            idx = self.get_pages(soup)
        self.parse_artists_page(soup)
        return idx

    def fetch_all_artists(self):
        """Fetch and cache all artists from the source

        Returns:
            list: List of artist dictionaries
        """
        # Reset artists list
        self.artists = []

        # Fetch all artists across all pages
        idx = self.store_artists(self.MASTER_URL, get_idx=True)
        for i in range(2, idx + 1):
            page_url = f"{self.MASTER_URL}page/{i}/"
            self.store_artists(page_url)

        return self.artists

    def get_artists(self, force_refresh=False):
        """Get artists with caching support

        Args:
            force_refresh: If True, bypass cache and download fresh artists

        Returns:
            list: List of artist dictionaries with 'artist' and 'url' keys
        """
        # Check cache first unless forced refresh
        if not force_refresh:
            cached_artists = self.load_artists_from_cache()
            if cached_artists:
                return cached_artists

        # If refresh requested, clear cache
        if force_refresh:
            self.clear_cache()

        # Fetch artists from source
        artists = self.fetch_all_artists()

        # Save to cache
        if artists:
            self.save_artists_to_cache(artists)

        return artists

    def get_songs_list(self, artist_url):
        """Get a list of song URLs for an artist"""
        song_url = []
        artist_soup = self.get_soup(artist_url)

        album_list = artist_soup.find('div', class_="full-artist-album-list").find_all('a')
        for al in album_list:
            song_soup = self.get_soup(al.get("href"))
            for song in song_soup.find_all('div', class_="list-line"):
                song_url.append(song.find('a').get('href'))

        lyrics_list_div = artist_soup.find_all("div", class_="lyric-line")
        if len(lyrics_list_div) > 1:
            song_list = lyrics_list_div[1].find_next_siblings()[0].find_all('li')
            for song in song_list:
                song_url.append(song.find('a').get('href'))

        return song_url

    def get_lyrics(self, song_url):
        """Scrape and save lyrics from a song page"""
        song_page_soup = self.get_soup(song_url)
        lyrics = song_page_soup.find('div', class_='lyric-text')

        if not lyrics:
            print(f"Could not find lyrics on {song_url}")
            return

        title = lyrics.find('h1').text
        album_artist_soup = song_page_soup.find('div', class_='single-lyrics-album')
        artist_name = album_artist_soup.find('h3').text.strip().replace('\n', ' ').replace('\r', '').replace('\t', ' ')
        artist_name = re.sub(' +', ' ', artist_name)
        album = album_artist_soup.find('h4').text.strip()

        lyrics_lines = lyrics.find_all('p')
        keywords = lyrics_lines[0].text if lyrics_lines else ""

        lyrics_text = ""
        for i in range(1, len(lyrics_lines) - 1):
            lyrics_text += f"{lyrics_lines[i].text.strip()}"
            lyrics_text += "\n\n"

        lyrics_content = f"""Title: {title}
Artist: {artist_name}
Album: {album}
Source: {song_url}

Keywords: {keywords}


{lyrics_text}
        """

        self.write_to_output(lyrics_content, title, album, artist_name)

    def scrape(self, artist_name, **kwargs):
        """Scrape lyrics for the given artist from The God's Music

        Args:
            artist_name: Name of the artist to scrape
            **kwargs: Additional arguments (unused)

        Returns:
            dict: Scraping result
        """
        try:
            print(f"Searching for artist: {artist_name}")

            # Get artists from cache if available, otherwise download
            artists_data = self.get_artists(force_refresh=False)
            self.artists = artists_data if artists_data else []

            print(f"Total artists available: {len(self.artists)}")

            # Find the target artist
            artist_url = None
            for art in self.artists:
                if artist_name.lower() in art["artist"].lower():
                    print(f"Found '{art['artist']}'")
                    artist_url = art["url"]
                    break

            if not artist_url:
                return {
                    "success": False,
                    "message": f"Artist '{artist_name}' not found!",
                    "files_count": 0
                }

            # Scrape and save all songs for the artist
            song_url_list = self.get_songs_list(artist_url)
            print(f"Total songs to scrape: {len(song_url_list)}")

            for i, song in enumerate(song_url_list, 1):
                print(f"Scraping song {i}/{len(song_url_list)}", end=" ")
                self.get_lyrics(song)

            return {
                "success": True,
                "message": f"Successfully downloaded {len(song_url_list)} songs lyrics for artist '{artist_name}'.",
                "files_count": f"{len(song_url_list)}"
            }

        except Exception as e:
            return {
                "success": False,
                "message": f"Error during scraping: {str(e)}",
                "files_count": 0
            }
