import os
import unicodedata
from datetime import datetime

from sqlalchemy import create_engine, and_
from sqlalchemy.orm import Session

from repository.DataModel import Movie, ParentRating, FeaturesDef, Country, MovieCountry, Genre, MovieRelated, Actor, \
    Director
from Domain.utils import isfloat
from repository.repositorymovie import RepositoryMovie

ENGINE_ADDRESS = os.environ.get("MOVIEDB")

def MovieExist(movie_id):
    engine = create_engine(ENGINE_ADDRESS)
    session = Session(engine)
    rmovie = session.query(Movie).filter(Movie.ObjectId == movie_id).first()
    return True if rmovie is not None else False

def GetCountry(c, session):
    fcountry = session.query(FeaturesDef).filter(
        FeaturesDef.Description == c and FeaturesDef.ParentDescription == "countries").first()
    ccountry = session.query(Country).filter(Country.Description == c).first()
    if (fcountry is None):
        fcountry = FeaturesDef(Description=c.lower(), ParentDescription="countries", Active=0)
        session.add(fcountry)
        session.flush()
        session.commit()
    if (ccountry is None):
        ccountry = Country(Description=c.lower(), FeatureObjectId=fcountry.ObjectId)
        session.add(ccountry)
        session.flush()
        session.commit()
    return ccountry

def MovieCreate(movie : RepositoryMovie, logger):
    engine = create_engine(ENGINE_ADDRESS)
    session = Session(engine)
    rmovie = Movie(ObjectId=movie.id, CreatedAt=datetime.now(),TitleType = movie.title_type,Title = movie.name,UpdateAt = datetime.now(),Year = movie.year, IMDBRatingArithmeticMean = movie.arithmetic_value,   Std = movie.std, ratingCountryStd = movie.country_std)
    rmovie.ParentRating = movie.content_rating
    rprating = session.query(ParentRating).filter(ParentRating.ObjectId == rmovie.ParentRating).first()
    if rprating is None:
        session.add(ParentRating(ObjectId=rmovie.ParentRating))

    for c in movie.countries:
        ccountry = GetCountry(c, session)
        rmovie.MovieCountrys.append(MovieCountry(CountryObjectId=ccountry.ObjectId))

    for genre in movie.genres:
        rmovie.genres.append(Genre(Description=genre))

    for relatedid in movie.related_movies:
        rmovie.RelatedMovies.append(MovieRelated(movieobjectid2=int(relatedid)))

    rmovie.NumVotes = movie.votes if isfloat(movie.votes) else 0
    rmovie.IMDBRating = movie.imdb_rating if isfloat(movie.imdb_rating)  else   7.4
    rmovie.Runtime = movie.runtime  if isfloat(movie.runtime)  else    0

    session.add(rmovie)

    nactors=[]
    actors = session.query(FeaturesDef).filter(FeaturesDef.ParentDescription == 'Actors').all()
    actors_dict1 = {f.Description.lower(): f for f in actors}
    actors_dict2 = {f.Description.lower().replace(" ", "").replace("-", "").replace(".", "") : f for f in actors}
    for row in movie.actors:
        row = unicodedata.normalize('NFKD', row).encode("ascii", "ignore").decode("ascii", "ignore").lower()
        rowalt = row.replace(" ", "").replace("-", "").replace(".", "")
        nactor = None
        if row in actors_dict1:
            nactor = Actor(MovieObjectId=movie.id, FeatureObjectId=actors_dict1[row].ObjectId)
        elif rowalt in actors_dict2:
            nactor = Actor(MovieObjectId=movie.id, FeatureObjectId=actors_dict2[rowalt].ObjectId)

        if nactor is None:
            session.add(FeaturesDef(Description=row.lower(), ParentDescription='Actors', Active=0))
            fid = session.query(FeaturesDef).filter(and_(FeaturesDef.ParentDescription == 'Actors', FeaturesDef.Description == row)).first().ObjectId
            if(logger is not None):
                logger.info(fid)
            nactor = Actor(MovieObjectId=movie.id, FeatureObjectId=fid)
        nactors.append(nactor)
    for a in nactors:
        session.add(a)

    ndirectors = []
    directors = session.query(FeaturesDef).filter(FeaturesDef.ParentDescription == 'Directors').all()
    directors_dict1 = {f.Description.lower(): f for f in directors}
    directors_dict2 = {f.Description.lower().replace(" ", "").replace("-", "").replace(".", ""): f for f in directors}
    for row in movie.directors:
        row = unicodedata.normalize('NFKD', row).encode("ascii", "ignore").decode("ascii", "ignore").lower()
        rowalt = row.replace(" ", "").replace("-", "").replace(".", "")
        ndirector = None
        if row in directors_dict1:
            ndirector = Director(MovieObjectId=movie.id, FeatureObjectId=directors_dict1[row].ObjectId)
        elif rowalt in directors_dict2:
            ndirector = Director(MovieObjectId=movie.id, FeatureObjectId=directors_dict2[rowalt].ObjectId)

        if ndirector is None:
            session.add(FeaturesDef(Description=row.lower(), ParentDescription='directors', Active=0))
            fid = session.query(FeaturesDef).filter(
                and_(FeaturesDef.ParentDescription == 'directors', FeaturesDef.Description == row)).first().ObjectId
            if (logger is not None):
                logger.info(fid)
            ndirector = Director(MovieObjectId=movie.id, FeatureObjectId=fid)
        ndirectors.append(ndirector)
    for a in ndirectors:
        session.add(a)

    if (movie.rating_distribution != None):
        rmovie.NumVotes1 = movie.rating_distribution[0]
        rmovie.NumVotes2 = movie.rating_distribution[1]
        rmovie.NumVotes3 = movie.rating_distribution[2]
        rmovie.NumVotes4 = movie.rating_distribution[3]
        rmovie.NumVotes5 = movie.rating_distribution[4]
        rmovie.NumVotes6 = movie.rating_distribution[5]
        rmovie.NumVotes7 = movie.rating_distribution[6]
        rmovie.NumVotes8 = movie.rating_distribution[7]
        rmovie.NumVotes9 = movie.rating_distribution[8]
        rmovie.NumVotes10 = movie.rating_distribution[9]


    totalcountryvotes = 0
    for vote in movie.country_votes:
        totalcountryvotes += vote
    l = 0
    for vote in movie.country_votes:
        code = session.query(FeaturesDef).filter(and_(FeaturesDef.Description == movie.country_codes[l], FeaturesDef.ParentDescription == "countrycodevote")).first()
        fid = code.ObjectId
        if (code is None):
            code = FeaturesDef(Description=movie.country_codes[l], ParentDescription="countrycodevote", Active=0)
            fid = session.query(FeaturesDef).filter(
                and_(FeaturesDef.ParentDescription == 'countrycodevote', FeaturesDef.Description == movie.country_codes[l])).first().ObjectId
            session.add(code)
        if (l == 0):
            rmovie.ratingCountry1Votes = vote / totalcountryvotes
            rmovie.ratingCountry1 = fid
        elif (l == 1):
            rmovie.ratingCountry2Votes = vote / totalcountryvotes
            rmovie.ratingCountry2 = fid
        elif (l == 2):
            rmovie.ratingCountry3Votes = vote / totalcountryvotes
            rmovie.ratingCountry3 = fid
        elif (l == 3):
            rmovie.ratingCountry4Votes = vote / totalcountryvotes
            rmovie.ratingCountry4 = fid
        elif (l == 4):
            rmovie.ratingCountry5Votes = vote / totalcountryvotes
            rmovie.ratingCountry5 = fid
        l = l + 1

    session.flush()
    session.commit()
    session.close()
