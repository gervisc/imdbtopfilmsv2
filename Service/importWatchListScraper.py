import time
import traceback


from IMDBSCRAPE.ScrapeService import importList, getmovie
from repository.MovieRepository import MovieExist, MovieCreate, MovieUpdate, GetMoviesToUpdate, GetRatedMoviesToUpdate, \
    GetRecentMoviesToUpdate


def importWatchListScraper(IMDBuser_ID,logger):
    url = f"https://www.imdb.com/user/ur{IMDBuser_ID}/watchlist/?sort=date_added%2Cdesc"
    movies = importList(url, logger)
    for m in movies:
        try:

            movieexists = MovieExist(m)
            if(not movieexists):
                if (logger is not None):
                    logger.info(f"create movie {m}")
                else:
                    print(f"movie {m}")
                createMovie( m,logger)
        except Exception as e:
            print(f"failed to interpret movie {m} {e}")
            traceback.print_exc()


def createMovie(m,logger):
    example_movie = getmovie(m, logger)
    MovieCreate(example_movie, logger)
    time.sleep(1)


def update(imbdid,logger):
    try:
        example_movie = getmovie(imbdid, logger)
        MovieUpdate(example_movie, logger)
    except Exception as e:
        print(f"failed to interpret movie {imbdid} {e}")
        traceback.print_exc()

def UpdateMyMovies(logger):
    ids =GetMoviesToUpdate(25)
    for id in ids:
        if (logger is not None):
            logger.info(f"update movie {id}")
        else:
            print(f"movie {id}")
        update(id,logger)
    ids = GetRecentMoviesToUpdate(3)
    for id in ids:
        if (logger is not None):
            logger.info(f"update rated movie {id}")
        else:
            print(f"movie {id}")
        update(id, logger)
    ids = GetRatedMoviesToUpdate()
    for id in ids:
        if (logger is not None):
            logger.info(f"update rated movie {id}")
        else:
            print(f"movie {id}")
        update(id,logger)

