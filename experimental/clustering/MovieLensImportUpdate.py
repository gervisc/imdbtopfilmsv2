import csv
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from repository.DataModel import Base,User, Movie,Rating
from sqlalchemy import and_
import datetime

engine = create_engine('mysql://root:hu78to@127.0.0.1:3307/moviedborm?charset=utf8')



Base.metadata.create_all(engine)
session = Session(engine)

IMovies = []
#lees csv in
with open('C:/Users/Gerbrand/OneDrive/PycharmProjects/imdbtopfilmsV2/storage/ratings movielens.csv','r') as f:
    ratings = csv.reader(f,delimiter= ',')
    insertmoviescount = 0

    #remove title row
    i =0
    for m in ratings:
        insertmoviescount = 1 +insertmoviescount
        imdbId = 0
        with open('C:/Users/Gerbrand/OneDrive/PycharmProjects/imdbtopfilmsV2/storage/links.csv', 'r') as f:
            links = csv.reader(f, delimiter=',')
            # remove title row


            for l in links:
                if m[1]== l[0]:
                    imdbId = l[1]
                    break
        if imdbId != 0:
            rmovie = session.query(Movie).filter(Movie.ObjectId == imdbId).first()
            if rmovie != None:
                ruser = session.query(User).filter(User.UserName == 'MovieLens'+m[0]).first()
                if ruser != None:
                    rrating = session.query(Rating).filter(and_(Rating.MovieObjectId == rmovie.ObjectId , Rating.UserObjectId == ruser.ObjectId)).first()
                    if rrating != None:
                        rrating.CreatedAt = datetime.datetime.fromtimestamp(int(m[3]))
                        rrating.UpdatedAt = datetime.datetime.now()
                        session.flush()
            i=i+1





session.commit()
session.close()









