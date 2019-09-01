import csv
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from datetime import datetime
from DataModel import Base,User, Movie,Rating,ParentRating
from OMDBapi import GetMovie

engine = create_engine('mysql://root:hu78to@127.0.0.1:3306/moviedborm?charset=utf8')



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
                    print(imdbId)
                    break
        if imdbId != 0:
            rmovie = session.query(Movie).filter(Movie.ObjectId == imdbId).first()
            if  rmovie == None :
                rmovie = GetMovie(imdbId)
                if rmovie != None:
                    rprating = session.query(ParentRating).filter(ParentRating.ObjectId == rmovie.ParentRating).first()
                    if rprating == None:
                        session.add(ParentRating(ObjectId=rmovie.ParentRating))
                    session.add(rmovie)
                    session.flush()
                    print(rmovie.Title)
                    session.commit()
                    ruser = session.query(User).filter(User.UserName == 'MovieLens'+m[0]).first()
                    if ruser == None:
                        ruser = User(UserName = 'MovieLens'+m[0],CreatedAt=datetime.now(), UpdateAt=datetime.now() )
                        session.add(ruser)
                    rrating = session.query(Rating).filter(Rating.MovieObjectId == rmovie.ObjectId and Rating.UserObjectId == User.ObjectId).first()
                    if rrating == None:
                        rrating =Rating(Rating=float(m[2])*2,User=ruser, Movie=rmovie )
                        session.add(rrating)
                    session.flush()

            if insertmoviescount > 2 and rmovie == None:
                print( insertmoviescount)

                session.commit()
                break
session.close()









