import unittest

from Service.importWatchListScraper import importWatchListScraper
from repository.MovieRepository import MovieCreate
from repository.repositorymovie import RepositoryMovie


class MyTestCase(unittest.TestCase):
    def test_import_list(self):
        # Mock IMDB_ID and logger for the test

        IMDB_ID = "51273819"  # Example IMDB ID for Inception
        logger = None  # Replace with a real logger if needed
        # Call the importList function
        importWatchListScraper(IMDB_ID,logger)

if __name__ == '__main__':
    unittest.main()