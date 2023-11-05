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
imbdids =[38426,	46866,	70419,	81454,	87690,	154827,	250305,	282674,	290538,	1307059,	1522863,	2077826,	3060338,	3300942,	6734480,	7920210,	14687104,	26443044,	116536,	13398086,	26345808,	226836,	26415809,	12545598,	14456690,	112865,	15742538,	21213266,	185048,	2207519,	113968,	15205370,	116949,	119264,	1570594,	84594,	110625,	38137,	5149620,	13845016,	13978188,	15535192,	101930,	13845002,	12490488,	11379620,	1099932,	10149938,	9308406,	309521,	9134096,	259981,	10504898,	15567198,	14793714,	9071368,	7570060,	12798078,	288403,	120848,	7933442,	8908368,	8221738,	8844204,	23450,	6318714,	18440,	874289,	11423420,	13817770,	12117860,	12182440,	7128732,	318069,	11905922,	8810204,	10300570,	9649436,	9196192]

for ImdbID in imbdids:


    rmovie = session.query(Movie).filter(Movie.ObjectId == ImdbID).first()

    rmovie =updateMovie(rmovie,str(ImdbID),session)





    session.flush()
    session.commit()
    print("next")