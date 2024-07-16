import unittest

from IMDBSCRAPE.ScrapeService import importList, getrelatedItems, getStdInfo


class MyTestCase(unittest.TestCase):
    @unittest.skip("Skipping this test method")
    def test_import_list(self):
        # Mock IMDB_ID and logger for the test
        IMDB_ID = "51273819"  # Example IMDB ID for Inception
        logger = None  # Replace with a real logger if needed

        # Call the importList function
        movies = importList(IMDB_ID, logger)

        # Ensure that the list is not empty
        self.assertTrue(len(movies) > 0, "The returned movie list is empty")

        # Print the first movie info
        print(movies[0])

    @unittest.skip("Skipping this test method")
    def test_getrelatedItems(self):
        # Mock IMDB_ID and logger for the test
        IMDB_ID = "21163478"  # Example IMDB ID for Inception
        logger = None  # Replace with a real logger if needed

        # Call the importList function
        relatedlist,genres,countries,titletype,contentrating = getrelatedItems(IMDB_ID, logger)
        print(f"relatedlist {relatedlist}")
        print(f"genres {genres}")
        print(f"countries {countries}")
        print(f"titletype {titletype}")
        print(f"contentrating {contentrating}")

    def test_getStdInfo(self):
        # Mock IMDB_ID and logger for the test
        IMDB_ID = "1879032"  # Example IMDB ID for Inception
        logger = None  # Replace with a real logger if needed

        # Call the importList function
        numberslist, avg, std, countryCodes, countryVotes,countryStd= getStdInfo(IMDB_ID, logger)
        print(f"numberslist {numberslist}")
        print(f"avg {avg}")
        print(f"std {std}")
        print(f"countryCodes {countryCodes}")
        print(f"countryVotes {countryVotes}")
        print(f"countryStd {countryStd}")


if __name__ == '__main__':
    unittest.main()
