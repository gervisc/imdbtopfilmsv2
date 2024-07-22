import unittest

from Service.importWatchListScraper import importWatchListScraper, update, createMovie


class MyTestCase(unittest.TestCase):
    @unittest.skip("Skipping this test method")
    def test_import_list(self):
        # Mock IMDB_ID and logger for the test

        IMDB_ID = "51273819"  # Example IMDB ID for Inception
        logger = None  # Replace with a real logger if needed
        # Call the importList function
        importWatchListScraper(IMDB_ID,logger)

    @unittest.skip("Skipping this test method")
    def test_updateMovies(self):
        # Mock IMDB_ID and logger for the test
        imbdids = [26753003	,
27788968	,
22408160	,
13433802	,
23731242	,
17677860	,
1188927	,
1560220	,
3469050	,
1319900	,
1800864	,
15560314	,
22048412	,
18162096	,
20114686	,
25434854	,
1896747	,
6263850	,
1262426	,
14824600	]


        logger = None  # Replace with a real logger if needed
        # Call the importList function
        for m in imbdids:
            update( m, logger)

    def test_createMovies(self):
        # Mock IMDB_ID and logger for the test
        imbdids = [
                   253963,
                   201368]

        logger = None  # Replace with a real logger if needed
        # Call the importList function
        for m in imbdids:
            createMovie(m, logger)

if __name__ == '__main__':
    unittest.main()