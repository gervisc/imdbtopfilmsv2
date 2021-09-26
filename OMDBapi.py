import unicodedata

from DataModel import Country,Actor,Director, Movie,Genre
from datetime import datetime
import requests

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium.common.exceptions import *
from selenium.webdriver.firefox.options import Options
import os
import csv
import time
from DataModel import Base,User, Movie,Rating,ParentRating,CustomList,FeaturesDef

from sqlalchemy import and_,text
from sqlalchemy import update

def isfloat(string):
    try:
        float(string)
        return True
    except ValueError:
        return False

def GetMovie(imdbId,session):
    resp = requests.get("http://www.omdbapi.com/?apikey=ad9a897d&i=tt"+imdbId)
    print("http://www.omdbapi.com/?apikey=ad9a897d&i=tt"+imdbId)
    print(resp)
    item = resp.json()
    nactors = []
    ndirectors= []
    rmovie = None
    actors = session.query(FeaturesDef).filter(FeaturesDef.ParentDescription == 'Actors').all()

    if item["Response"] == "True":
        rmovie = Movie(ObjectId=imdbId, CreatedAt=datetime.now(), UpdateAt=datetime.now())

        for c in item["Country"].split(', '):
            rmovie.countrys.append(Country(Description =c))
        for row in item["Actors"].split(', '):
            row = unicodedata.normalize('NFKD', row).encode("ascii", "ignore").decode("ascii", "ignore").lower()
            nactor = None

            if next((x for x in rmovie.actors if x.Description.lower() == row), None) == None:
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
                    print(fid)
                    nactor =   Actor(MovieObjectId = imdbId, FeatureObjectId = fid)
                nactors.append(nactor)


        #ndirectors = GetDirectors( imdbId, rmovie, item["Director"], session)
        for row in item["Genre"].split(', '):
            rmovie.genres.append(Genre(Description =row))
        rmovie.Title = item["Title"]
        rmovie.Year =  item["Year"][0:4]

        rmovie.ParentRating = item["Rated"]
        rmovie.TitleType = item["Type"]
        rmovie.IMDBRating =  7.8 # item["ImdbRating"]
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

def updateMovie(rmovie,imdbId,session):
    resp = requests.get("http://www.omdbapi.com/?apikey=ad9a897d&i=tt"+imdbId)
    print("http://www.omdbapi.com/?apikey=ad9a897d&i=tt"+imdbId)
    print(resp)
    item = resp.json()
    nactors = []

    actors = session.query(FeaturesDef).filter(FeaturesDef.ParentDescription == 'Actors').all()

    if item["Response"] == "True":
        session.query(Country).filter(Country.MovieObjectId == imdbId).delete()
        for c in item["Country"].split(', '):
            rmovie.countrys.append(Country(Description =c))
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
                print(fid)
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
    session.commit()
    return rmovie

def GetDirectors(imdbId, rmovie, directorCSV, session):
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
                if f.Description.lower().replace("-", " ") == row.replace("-", " "):
                    ndirector = Director(MovieObjectId=imdbId, FeatureObjectId=f.ObjectId)
                    f.Description = row.lower()
                    break
            if ndirector is None:
                session.add(FeaturesDef(Description=row.lower(), ParentDescription='Directors', Active=0))
                fid = session.query(FeaturesDef).filter(and_(FeaturesDef.ParentDescription == 'Directors',
                                                             FeaturesDef.Description == row)).first().ObjectId
                print(fid)
                ndirector = Director(MovieObjectId=imdbId, FeatureObjectId=fid)

                session.flush()
                session.commit()
            ndirectors.append(ndirector)
    return ndirectors