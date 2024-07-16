import unicodedata

from repository.DataModel import Country,Actor,Director, Genre
import requests

from datetime import datetime
import os
import time
from repository.DataModel import Movie, ParentRating, FeaturesDef,MovieCountry

from sqlalchemy import and_

from scrapedeviation import getStdInfo


def isfloat(string):
    try:
        float(string)
        return True
    except ValueError:
        return False

def GetMovie(imdbId,session,logger):
    resp = requests.get("http://www.omdbapi.com/?apikey=ad9a897d&i=tt"+imdbId)
    logger.info("http://www.omdbapi.com/?apikey=ad9a897d&i=tt"+imdbId)

    item = resp.json()
    nactors = []
    ndirectors= []
    rmovie = None
    actors = session.query(FeaturesDef).filter(FeaturesDef.ParentDescription == 'Actors').all()

    if item["Response"] == "True":
        rmovie = Movie(ObjectId=imdbId, CreatedAt=datetime.now(), UpdateAt=datetime.now())

        for c in item["Country"].split(', '):
            ccountry = GetCountry(c, session)
            rmovie.MovieCountrys.append(MovieCountry(CountryObjectId = ccountry.ObjectId))
        for row in item["Actors"].split(', '):
            row = unicodedata.normalize('NFKD', row).encode("ascii", "ignore").decode("ascii", "ignore").lower()
            nactor = None

            if next((x for x in rmovie.actors if x.Description.lower() == row), None) == None:
                for f in actors:
                    if f.Description.lower() == row:
                        nactor =  Actor(MovieObjectId = imdbId, FeatureObjectId = f.ObjectId)
                        break
                    if f.Description.lower().replace(" ","").replace("-","").replace(".","")== row.replace(" ","").replace("-","").replace(".",""):
                        nactor =  Actor(MovieObjectId = imdbId, FeatureObjectId = f.ObjectId)
                        f.Description = row.lower()
                        break
                if nactor is None:
                    session.add(FeaturesDef(Description = row.lower(), ParentDescription = 'Actors', Active =0))
                    fid = session.query(FeaturesDef).filter(and_(FeaturesDef.ParentDescription == 'Actors',
                                                                             FeaturesDef.Description == row)).first().ObjectId
                    logger.info(fid)
                    nactor =   Actor(MovieObjectId = imdbId, FeatureObjectId = fid)
                nactors.append(nactor)


        #ndirectors = GetDirectors( imdbId, rmovie, item["Director"], session)

        rmovie.Title = item["Title"]
        rmovie.Year =  item["Year"][0:4]

        rmovie.ParentRating = item["Rated"]
        rmovie.TitleType = item["Type"]
        rmovie.IMDBRating =  7.4 # item["ImdbRating"]
        rmovie.IMDBRatingArithmeticMean = 7.4
        rmovie.Std = 1.67
        rmovie.ratingCountryStd=0
        rmovie.NumVotes =  0# [item["ImdbVotes"]
        rmovie.Runtime =item["Runtime"][0:len(item["Runtime"])-4] if item["Runtime"][0:len(item["Runtime"])-4].isnumeric() else 0# item["Runtime"]
        rprating = session.query(ParentRating).filter(ParentRating.ObjectId == rmovie.ParentRating).first()
        if rprating is None:
            session.add(ParentRating(ObjectId=rmovie.ParentRating))
        session.add(rmovie)
        for a in nactors:
            session.add(a)
        session.flush()
    session.commit()
    return rmovie


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


def updateMovie(rmovie,imdbId,session,logger):
    omdbky  = os.environ.get("OMDBAPIKEY")
    resp = requests.get("http://www.omdbapi.com/?apikey="+omdbky+"&i=tt"+imdbId)
    logger.info("http://www.omdbapi.com/?apikey="+omdbky+"&i=tt"+imdbId)

    item = resp.json()
    nactors = []

    actors = session.query(FeaturesDef).filter(FeaturesDef.ParentDescription == 'Actors').all()

    if item["Response"] == "True":
        session.query(MovieCountry).filter(MovieCountry.MovieObjectId == imdbId).delete()
        for c in item["Country"].split(', '):
            ccountry = GetCountry(c, session)
            rmovie.MovieCountrys.append(MovieCountry(CountryObjectId=ccountry.ObjectId))
        for row in item["Actors"].split(', '):
            row = unicodedata.normalize('NFKD', row).encode("ascii", "ignore").decode("ascii", "ignore").lower()
            nactor = None


            for f in actors:
                if f.Description.lower() == row:
                    nactor =  Actor(MovieObjectId = imdbId, FeatureObjectId = f.ObjectId)
                    break
                if f.Description.lower().replace("-"," ")== row.replace("-"," "):
                    nactor =  Actor(MovieObjectId = imdbId, FeatureObjectId = f.ObjectId)
                    f.Description = row.lower()
                    break
            if nactor is None:
                session.add(FeaturesDef(Description = row.lower(), ParentDescription = 'Actors', Active =0))
                fid = session.query(FeaturesDef).filter(and_(FeaturesDef.ParentDescription == 'Actors',
                                                                         FeaturesDef.Description == row)).first().ObjectId
                logger.info(fid)
                nactor =   Actor(MovieObjectId = imdbId, FeatureObjectId = fid)
            nactors.append(nactor)

        session.query(Genre).filter(Genre.MovieObjectId == imdbId).delete()
        for row in item["Genre"].split(', '):
            rmovie.genres.append(Genre(Description =row))
        rmovie.Title = item["Title"]
        rmovie.Year =  item["Year"][0:4]

        rmovie.ParentRating = item["Rated"]
        rmovie.TitleType = item["Type"]
        rmovie.UpdateAt=datetime.now()
        rmovie.Runtime =item["Runtime"][0:len(item["Runtime"])-4] if item["Runtime"][0:len(item["Runtime"])-4].isnumeric() else 0# item["Runtime"]
        rprating = session.query(ParentRating).filter(ParentRating.ObjectId == rmovie.ParentRating).first()
        if rprating is None:
            session.add(ParentRating(ObjectId=rmovie.ParentRating))
        session.query(Actor).filter(Actor.MovieObjectId == imdbId).delete()
        for a in nactors:
            session.add(a)
        session.flush()
        # add std info
    if (rmovie.NumVotes > 1):
        numberslist, arithmeticvalue, std,countrycodes ,countryvotes,countryStd= getStdInfo(imdbId,logger)
        if(rmovie.NumVotes > 1 and numberslist is not None):
            rmovie.NumVotes1 = numberslist[0]
            rmovie.NumVotes2 = numberslist[1]
            rmovie.NumVotes3 = numberslist[2]
            rmovie.NumVotes4 = numberslist[3]
            rmovie.NumVotes5 = numberslist[4]
            rmovie.NumVotes6 = numberslist[5]
            rmovie.NumVotes7 = numberslist[6]
            rmovie.NumVotes8 = numberslist[7]
            rmovie.NumVotes9 = numberslist[8]
            rmovie.NumVotes10 = numberslist[9]
            rmovie.IMDBRatingArithmeticMean = arithmeticvalue
            rmovie.Std = std
        rmovie.ratingCountryStd = countryStd
        totalcountryvotes = 0
        for vote in countryvotes:
            totalcountryvotes = totalcountryvotes + vote
        l = 0
        for vote in countryvotes:
            code = session.query(FeaturesDef).filter(and_(FeaturesDef.Description == countrycodes[l],
                                                          FeaturesDef.ParentDescription == "countrycodevote")).first()
            if (code is None):
                code = FeaturesDef(Description=countrycodes[l], ParentDescription="countrycodevote", Active=0)
                session.add(code)
                session.flush()
                session.commit()
            if (l == 0):
                rmovie.ratingCountry1Votes = vote / totalcountryvotes
                rmovie.ratingCountry1 = code.ObjectId
            if (l == 1):
                rmovie.ratingCountry2Votes = vote / totalcountryvotes
                rmovie.ratingCountry2 = code.ObjectId
            if (l == 2):
                rmovie.ratingCountry3Votes = vote / totalcountryvotes
                rmovie.ratingCountry3 = code.ObjectId
            if (l == 3):
                rmovie.ratingCountry4Votes = vote / totalcountryvotes
                rmovie.ratingCountry4 = code.ObjectId
            if (l == 4):
                rmovie.ratingCountry5Votes = vote / totalcountryvotes
                rmovie.ratingCountry5 = code.ObjectId
            l = l + 1
    time.sleep(0.5)
    rmovie.UpdateAt = datetime.now()
    session.commit()
    return rmovie

def GetDirectors(imdbId, rmovie, directorCSV, session,logger):
    ndirectors = []
    for row in directorCSV.split(', '):
        directors = session.query(FeaturesDef).filter(FeaturesDef.ParentDescription == 'Directors').all()

        row = unicodedata.normalize('NFKD', row).encode('ASCII', 'ignore').decode("ascii", "ignore").lower()
        ndirector = None
        if next((x for x in rmovie.directors if x.Description == row), None) == None:
            for f in directors:
                if f.Description.lower() == row:
                    ndirector = Director(MovieObjectId=imdbId, FeatureObjectId=f.ObjectId)
                    break
                if f.Description.lower().replace(" ","").replace("-","").replace(".","") == row.replace(" ","").replace("-","").replace(".",""):
                    ndirector = Director(MovieObjectId=imdbId, FeatureObjectId=f.ObjectId)
                    f.Description = row.lower()
                    break
            if ndirector is None:
                session.add(FeaturesDef(Description=row.lower(), ParentDescription='Directors', Active=0))
                fid = session.query(FeaturesDef).filter(and_(FeaturesDef.ParentDescription == 'Directors',
                                                             FeaturesDef.Description == row)).first().ObjectId
                logger.info(fid)
                ndirector = Director(MovieObjectId=imdbId, FeatureObjectId=fid)

                session.flush()
                session.commit()
            ndirectors.append(ndirector)
    return ndirectors