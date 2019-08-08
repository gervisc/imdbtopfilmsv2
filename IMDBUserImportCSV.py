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
from DataModel import Base,User,Country,Actor,Director, Movie,Genre

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
with open('storage/ratings.csv','r') as f:
    movies = list(csv.reader(f,delimiter= ','))
    #remove title row
    movies.pop(0)
    for m in movies:

        rmovie = session.query(Movie).filter(Movie.ObjectId == m[0][2:len(m[0])]).first()
        if  rmovie == None:
            resp = requests.get("http://www.omdbapi.com/?apikey=ad9a897d&i="+m[0])
            item = resp.json()
            if item["Response"] == "True":
                iMovie = Movie(ObjectId=m[0][2:len(m[0])], CreatedAt=datetime.now(), UpdateAt=datetime.now())
                for c in item["Country"].split(', '):
                    iMovie.countrys.append(Country(Description =c))
                for a in item["Actors"].split(', '):
                    iMovie.actors.append(Actor(Description  =a))
                for row in m[12].split(', '):
                    iMovie.directors.append(Director(Description =row))
                for row in m[9].split(', '):
                    iMovie.genres.append(Genre(Description =row))
                iMovie.Title = m[3]#item["Title"]
                iMovie.Year = m[8] # item["Year"]
                iMovie.ParentRating = item["Rated"]
                iMovie.TitleType = m[5] #item["Type"]
                iMovie.IMDBRating =m[6] if isfloat(m[6]) else 7.8 # item["ImdbRating"]
                iMovie.NumVotes = m[10] if m[10].isnumeric() else 0# [item["ImdbVotes"]
                iMovie.Runtime =m[7] if m[7].isnumeric() else 0# item["Runtime"]
                session.add(iMovie)
                session.flush()
        else:
            rmovie.Title = m[3]  # item["Title"]
            rmovie.Year = m[8]  # item["Year"]
            rmovie.TitleType = m[5]  # item["Type"]
            rmovie.IMDBRating =m[6] if isfloat(m[6]) else 7.8  # item["ImdbRating"]
            rmovie.NumVotes = m[10] if m[10].isnumeric() else 0  # [item["ImdbVotes"]
            rmovie.Runtime = m[7] if m[7].isnumeric() else 0  # item["Runtime"]
            rmovie.UpdateAt = datetime.now()
            session.flush()
    session.commit()


with open('storage/watchlist.csv','r') as f:
    movies = list(csv.reader(f,delimiter= ','))
    #remove title row
    movies.pop(0)
    for m in movies:

        rmovie = session.query(Movie).filter(Movie.ObjectId == m[1][2:len(m[1])]).first()
        if  rmovie == None:
            resp = requests.get("http://www.omdbapi.com/?apikey=ad9a897d&i="+m[1])
            item = resp.json()
            if item["Response"] == "True":
                iMovie = Movie(ObjectId=m[1][2:len(m[1])], CreatedAt=datetime.now(), UpdateAt=datetime.now())
                for c in item["Country"].split(', '):
                    iMovie.countrys.append(Country(Description =c))
                for a in item["Actors"].split(', '):
                    iMovie.actors.append(Actor(Description  =a))
                for row in m[14].split(', '):
                    iMovie.directors.append(Director(Description =row))
                for row in m[11].split(', '):
                    iMovie.genres.append(Genre(Description =row))
                iMovie.Title = m[5]#item["Title"]
                iMovie.Year = m[10] # item["Year"]
                iMovie.ParentRating = item["Rated"]
                iMovie.TitleType = m[7] #item["Type"]
                iMovie.IMDBRating =m[8] if isfloat(m[8]) else 7.8# item["ImdbRating"]

                iMovie.NumVotes = m[12] if m[12].isnumeric() else 0# [item["ImdbVotes"]
                iMovie.Runtime =m[9] if m[9].isnumeric() else 0# item["Runtime"]
                session.add(iMovie)
                session.flush()
        else:
            rmovie.Title = m[5]  # item["Title"]
            rmovie.Year = m[10]  # item["Year"]
            rmovie.TitleType = m[7]  # item["Type"]
            rmovie.IMDBRating=m[8] if isfloat(m[8]) else 7.8 # item["ImdbRating"]
            rmovie.NumVotes = m[12] if m[12].isnumeric() else 0  # [item["ImdbVotes"]
            rmovie.Runtime = m[9] if m[9].isnumeric() else 0  # item["Runtime"]
            rmovie.UpdateAt = datetime.now()
            session.flush()
    session.commit()



session.close()







#     for n, movie in enumerate(movies):
#         k = 0
#         for om in omdbmovies:
#             if om[positionkey] == movie[positionkey]:
#                 movies[n] = om
#                 k = 1
#         if k == 1:
#             continue
#         resp = omdbget(movie[positionkey])
#         item = resp.json()
#         if item["Response"] == "True":
#             country = item["Country"]
#             actors = item["Actors"]
#             rated = item["Rated"]
#             wins = 0
#             nominations = 0
#             # awards
#             awards = item["Awards"]
#             winindex = awards.find("win")
#             if (winindex > 0):
#                 if (awards[max(winindex - 5, 0)] == " "):
#                     wins = int(awards[max(winindex - 4, 0):winindex])
#                 else:
#                     wins = int(awards[max(winindex - 3, 0):winindex])
#             nominationindex = awards.find("nomination")
#             if (nominationindex > 0):
#                 if (awards[max(nominationindex - 5, 0)] == " ") and (awards[max(nominationindex - 3, 0)] != " "):
#                     nominations = int(awards[max(nominationindex - 4, 0):nominationindex])
#                 else:
#                     nominations = int(awards[max(nominationindex - 3, 0):nominationindex])
#
#             movie.append(country)
#             movie.append(actors)
#             movie.append(rated.lower())
#             movie.append(wins)
#             movie.append(nominations)
#             movies[n] = movie
#             writer.writerow(movie)
#         else:
#             movie.append("Unknown")
#             movie.append("")
#             movie.append("Not Rated".lower())
#             movie.append(0)
#             movie.append(0)
#             movies[n] = movie
# return movies
