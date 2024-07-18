import time
import traceback


from IMDBSCRAPE.ScrapeService import getrelatedItems, importList, getStdInfo
from repository.MovieRepository import MovieExist, MovieCreate
from repository.repositorymovie import RepositoryMovie


def importWatchListScraper(IMDBuser_ID,logger):
    url = f"https://www.imdb.com/user/ur{IMDBuser_ID}/watchlist/?sort=date_added%2Cdesc"
    movies = importList(url, logger)
    for m in movies:
        try:
            movieexists = MovieExist(m)
            if(not movieexists):
                movie = getrelatedItems(m, logger)
                numberslist, avg, std, countryCodes, countryVotes, countryStd,votes = getStdInfo(m, logger)
                example_movie = RepositoryMovie(
                    id=m,
                    title_type=movie.titletype,
                    content_rating=movie.contentrating,
                    countries=movie.countries,
                    genres=movie.genres,
                    related_movies=movie.related_movies,
                    name=movie.movie_name,
                    year=movie.year,
                    votes=movie.num_ratings,
                    runtime=0,
                    actors=movie.stars,
                    rating_distribution=numberslist,
                    arithmetic_value=avg,
                    std=std,
                    country_std=countryStd,
                    country_votes=countryVotes,
                    country_codes=countryCodes,
                    imdb_rating=movie.rating_value,
                    directors=movie.director,
                )
                MovieCreate(example_movie, logger)
                time.sleep(1)
        except Exception as e:
            print(f"failed to interpret movie {m} {e}")
            traceback.print_exc()