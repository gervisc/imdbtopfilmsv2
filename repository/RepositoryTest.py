import unittest

from repository.MovieRepository import MovieCreate
from repository.repositorymovie import RepositoryMovie


class MyTestCase(unittest.TestCase):
    def test_import_list(self):
        # Mock IMDB_ID and logger for the test

        logger = None  # Replace with a real logger if needed
        example_movie = RepositoryMovie(
            id=5,
            title_type="Feature",
            content_rating="PG-13",
            countries=["USA"],
            genres=["Drama", "Action"],
            related_movies=[2, 3, 4],
            name="Example Movie",
            year=2023,
            votes=1000,
            runtime=120,
            actors=["Actor 1", "Actor 3"],
            rating_distribution=[100, 200, 300, 400, 500, 600, 700, 800, 900, 1000],
            arithmetic_value=60,
            std=5.0,
            country_std=2.0,
            country_votes=[5028.0, 1058.0, 594.0, 453.0, 3],
            country_codes=['US', 'GB', 'CA', 'AU', 'NL'],
            imdb_rating=7.5,
            directors= ["d 1", "d 2"],
        )
        # Call the importList function
        MovieCreate(example_movie,logger)

if __name__ == '__main__':
    unittest.main()
