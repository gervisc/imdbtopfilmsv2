from sqlalchemy import create_engine
from sqlalchemy.orm import Session
import os
from repository.DataModel import Movie
from OMDBapi import updateMovie
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