import csv
import mysql.connector
from sqlalchemy import create_engine
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import exists
from datetime import datetime
from InsertFunctions import GetWins
from InsertFunctions import GetNominations
import json
import requests
from DataModel import Base,User,Country,Actor,Director, Movie,Genre,Rating

from sqlalchemy.orm import sessionmaker

engine = create_engine('mysql://root:hu78to@127.0.0.1:3306/moviedborm')

def isfloat(string):
    try:
        float(string)
        return True
    except ValueError:
        return False

Base.metadata.create_all(engine)
session = Session(engine)

IMovies = []
#lees csv in
with open('storage/ratings movielens.csv','r') as f:
    ratings = csv.reader(f,delimiter= ',')
    insertmoviescount = 0

    #remove title row

    for m in ratings:
        insertmoviescount = 1 +insertmoviescount
        imdbId = 0
        with open('storage/links.csv', 'r') as f:
            links = csv.reader(f, delimiter=',')
            # remove title row


            for l in links:
                if m[1]== l[0]:
                    imdbId = l[1]
                    break
        if imdbId != 0:
            rmovie = session.query(Movie).filter(Movie.ObjectId == imdbId).first()
            if  rmovie == None:
                resp = requests.get("http://www.omdbapi.com/?apikey=ad9a897d&i=tt"+imdbId)
                item = resp.json()
                if item["Response"] == "True":
                    rmovie = Movie(ObjectId=imdbId, CreatedAt=datetime.now(), UpdateAt=datetime.now())
                    for c in item["Country"].split(', '):
                        rmovie.countrys.append(Country(Description =c))
                    for a in item["Actors"].split(', '):
                        rmovie.actors.append(Actor(Description  =a))
                    for row in item["Director"].split(', '):
                        rmovie.directors.append(Director(Description =row))
                    for row in item["Genre"].split(', '):
                        rmovie.genres.append(Genre(Description =row))
                    rmovie.Title = item["Title"]
                    rmovie.Year =  item["Year"]
                    rmovie.ParentRating = item["Rated"]
                    rmovie.TitleType = item["Type"]
                    rmovie.IMDBRating = item["imdbRating"] if isfloat( item["imdbRating"]) else 7.8 # item["ImdbRating"]
                    rmovie.NumVotes = item["imdbVotes"].replace(',','') if item["imdbVotes"].replace(',','').isnumeric() else 0# [item["ImdbVotes"]
                    rmovie.Runtime =item["Runtime"][0:len(item["Runtime"])-4] if item["Runtime"][0:len(item["Runtime"])-4].isnumeric() else 0# item["Runtime"]
                    session.add(rmovie)
                    session.flush()

            if rmovie != None:
                ruser = session.query(User).filter(User.UserName == 'MovieLens'+m[0]).first()
                if ruser == None:
                    ruser = User(UserName = 'MovieLens'+m[0],CreatedAt=datetime.now(), UpdateAt=datetime.now() )
                    session.add(ruser)
                rrating = session.query(Rating).filter(Rating.MovieObjectId == rmovie.ObjectId and Rating.UserObjectId == User.ObjectId).first()
                if rrating == None:
                    rrating =Rating(Rating=float(m[2])*2,User=ruser, Movie=rmovie )
                    session.add(rrating)
                session.flush()
        if insertmoviescount % 2000 == 0:
            print( insertmoviescount)

            session.commit()
            break
session.close()









