import unittest

from IMDBSCRAPE.ScrapeService import importList, getrelatedItems, getStdInfo


class MyTestCase(unittest.TestCase):

    @unittest.skip("Skipping this test method")
    def test_import_list(self):
        # Mock IMDB_ID and logger for the test
        IMDB_ID = "11514868"  # Example IMDB ID for Inception
        logger = None  # Replace with a real logger if needed
        url = f"https://www.imdb.com/user/ur{IMDB_ID}/ratings/"
        # Call the importList function
        movies = importList(url, logger)

        # Ensure that the list is not empty
        self.assertTrue(len(movies) > 0, "The returned movie list is empty")

        # Print the first movie info
        print(movies[0])


    def test_getrelatedItems(self):
        # Mock IMDB_ID and logger for the test
        IMDB_ID = "11514868"  # Example IMDB ID for Inception
        logger = None  # Replace with a real logger if needed

        # Call the importList function
        movie= getrelatedItems(IMDB_ID, logger)
        print(f"movie {movie}")


    @unittest.skip("Skipping this test method")
    def test_getStdInfo(self):
        # Mock IMDB_ID and logger for the test
        IMDB_ID = "1879032"  # Example IMDB ID for Inception
        logger = None  # Replace with a real logger if needed

        # Call the importList function
        numberslist, avg, std, countryCodes, countryVotes,countryStd,votes= getStdInfo(IMDB_ID, logger)
        print(f"numberslist {numberslist}")
        print(f"avg {avg}")
        print(f"std {std}")
        print(f"countryCodes {countryCodes}")
        print(f"countryVotes {countryVotes}")
        print(f"countryStd {countryStd}")


if __name__ == '__main__':
    unittest.main()
