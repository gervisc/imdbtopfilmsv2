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
import logging

# Netflix renders quickly enough, but finishes very slowly
cstring = os.environ.get("MOVIEDB")
engine = create_engine(cstring)
session = Session(engine)
logger = logging.getLogger()

# Set the log level for the logger
logger.setLevel(logging.DEBUG)
imbdids =["0048452"]
for ImdbID in imbdids:


    rmovie = session.query(Movie).filter(Movie.ObjectId == ImdbID).first()

    rmovie =updateMovie(rmovie,str(ImdbID),session,logger)





    session.flush()
    session.commit()
    print("next")