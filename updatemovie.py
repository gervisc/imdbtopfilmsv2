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
from DataModel import Base, User, Movie, Rating, ParentRating, CustomList, FeaturesDef, Director
from OMDBapi import GetMovie, GetDirectors, updateMovie
from sqlalchemy import and_,text
from scrapedeviation import getStdInfo
from sqlalchemy import update
import numpy as np


# Netflix renders quickly enough, but finishes very slowly
DRIVER_TIMEOUT = 30

ENGINE_ADDRESS= 'mysql://root:hu78to@127.0.0.1:3306/movies'
engine = create_engine(ENGINE_ADDRESS)

Base.metadata.create_all(engine)
session = Session(engine)
imbdids =[1795369]
for ImdbID in imbdids:


    rmovie = session.query(Movie).filter(Movie.ObjectId == ImdbID).first()

    rmovie =updateMovie(rmovie,str(ImdbID),session)





    session.flush()
    session.commit()
    print("next")