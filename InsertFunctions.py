import csv
import mysql.connector
from sqlalchemy import create_engine
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import exists
import json
import requests



def InsertDBObject(description,session,DBclass):
    (ret,), = Session.query(exists().where(DBclass.Description == description))
    if ret:
        newTitleType = DBclass(Description=description)
        session.add(newTitleType)
        session.flush()
    return



def InsertGenre(description,Base,session):
    Genre = Base.classes.genre
    (ret,), = Session.query(exists().where(Genre.Description == description))
    if ret:
        newGenre = Genre(Description=description)
        session.add(newGenre)
        session.flush()
    return


def GetWins(awards):
    winindex = awards.find("win")
    if (winindex > 0):
        if (awards[max(winindex - 5, 0)] == " "):
            wins = int(awards[max(winindex - 4, 0):winindex])
        else:
            wins = int(awards[max(winindex - 3, 0):winindex])
    return wins

def GetNominations(awards):
    nominationindex = awards.find("nomination")
    if (nominationindex > 0):
        if (awards[max(nominationindex - 5, 0)] == " ") and (awards[max(nominationindex - 3, 0)] != " "):
            nominations = int(awards[max(nominationindex - 4, 0):nominationindex])
        else:
            nominations = int(awards[max(nominationindex - 3, 0):nominationindex])
    return nominations