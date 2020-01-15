from DataModel import Country,Actor,Director, Movie,Genre
from datetime import datetime
import requests

def isfloat(string):
    try:
        float(string)
        return True
    except ValueError:
        return False

def GetMovie(imdbId):
    resp = requests.get("http://www.omdbapi.com/?apikey=ad9a897d&i=tt"+imdbId)
    print("http://www.omdbapi.com/?apikey=ad9a897d&i=tt"+imdbId)
    print(resp)
    item = resp.json()
    if item["Response"] == "True":
        rmovie = Movie(ObjectId=imdbId, CreatedAt=datetime.now(), UpdateAt=datetime.now())
        for c in item["Country"].split(', '):
            rmovie.countrys.append(Country(Description =c))
        for row in item["Actors"].split(', '):
            if next((x for x in rmovie.actors if x.Description.lower() == row.lower()), None) == None:
                rmovie.actors.append(Actor(Description =row))
        for row in item["Director"].split(', '):
            if next((x for x in rmovie.directors if x.Description == row), None) == None:
                rmovie.directors.append(Director(Description =row))
        for row in item["Genre"].split(', '):
            rmovie.genres.append(Genre(Description =row))
        rmovie.Title = item["Title"]
        rmovie.Year =  item["Year"][0:4]

        rmovie.ParentRating = item["Rated"]
        rmovie.TitleType = item["Type"]
        rmovie.IMDBRating = item["imdbRating"] if isfloat( item["imdbRating"]) else 7.8 # item["ImdbRating"]
        rmovie.NumVotes = item["imdbVotes"].replace(',','') if item["imdbVotes"].replace(',','').isnumeric() else 0# [item["ImdbVotes"]
        rmovie.Runtime =item["Runtime"][0:len(item["Runtime"])-4] if item["Runtime"][0:len(item["Runtime"])-4].isnumeric() else 0# item["Runtime"]
        return rmovie