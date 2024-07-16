import traceback

from IMDBSCRAPE.ScrapeService import getrelatedItems, importList, getStdInfo
from repository.MovieRepository import MovieExist, MovieCreate
from repository.repositorymovie import RepositoryMovie


def importWatchListScraper(IMDBuser_ID,logger):
    movies = importList(IMDBuser_ID, logger)
    for m in movies:
        try:
            movieexists = MovieExist(m.movie_id)
            if(not movieexists):
                relatedlist, genres, countries, titletype, contentrating = getrelatedItems(m.movie_id, logger)
                numberslist, avg, std, countryCodes, countryVotes, countryStd = getStdInfo(m.movie_id, logger)
                example_movie = RepositoryMovie(
                    id=m.movie_id,
                    title_type=titletype,
                    content_rating=contentrating,
                    countries=countries,
                    genres=genres,
                    related_movies=relatedlist,
                    name=m.movie_name,
                    year=m.year,
                    votes=m.num_ratings,
                    runtime=0,
                    actors=m.stars,
                    rating_distribution=numberslist,
                    arithmetic_value=avg,
                    std=std,
                    country_std=countryStd,
                    country_votes=countryVotes,
                    country_codes=countryCodes,
                    imdb_rating=m.rating_value,
                    directors=m.director,
                )
                MovieCreate(example_movie, logger)
        except Exception as e:
            print(f"failed to interpret movie {m.movie_id} {e}")
            traceback.print_exc()