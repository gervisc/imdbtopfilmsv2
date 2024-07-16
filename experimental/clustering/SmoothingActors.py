

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from repository.DataModel import Base, FeaturesDef,HighScores, Actor,ActorSmoothing,CorrelationActor
from scipy.sparse import csr_matrix
import numpy


class featureUsers:
  def __init__(self, descr, usr,movie):
    self.description = descr
    self.userobjectid = usr
    self.movieobjectid = movie

def init():
    engine = create_engine('mysql://root:hu78to@127.0.0.1:3307/moviedborm?charset=utf8')
    Base.metadata.create_all(engine)
    session = Session(engine)
    return session

def GetUserStats(session,features):
    ActorUser =        session.query(HighScores).join(Actor, HighScores.actors).all()
    usersDict = []
    userscount = {}
    moviecount = {}
    movieitems = {}
    for v in ActorUser:
        userscount[v.UserObjectId] = 1 if v.UserObjectId not in userscount else userscount[v.UserObjectId]+1

        for k in v.Movie.actors:
            #s = unicodedata.normalize('NFKD',k.Description).encode('ASCII','ignore')
            moviecount[k.Description] = 1 if k.Description not in moviecount else moviecount[k.Description] + 1
            if v.Movie.ObjectId not in movieitems:
                movieitems[v.Movie.ObjectId] = 1
            else:
                movieitems[v.Movie.ObjectId] += 1

            usersDict.append(featureUsers(k.Description, v.UserObjectId,v.Movie.ObjectId))


    cori = []
    coci = []
    cova = []


    avgmoviecount = sum(moviecount.values())/float(len(moviecount))
    for v in usersDict:
        codi = next(filter(lambda x: x.Description == v.description,features),None)
        if codi is not None:
            cori.append(codi)
            coci.append(v.userobjectid)
            cova.append(numpy.sqrt(1 / userscount[v.userobjectid] / movieitems[v.movieobjectid])/moviecount[v.description]*avgmoviecount)
        else:
            logger.info (v.description)
    FeaturesM = csr_matrix((cova, (cori, coci)), shape=(max(cori) + 1, max(coci) + 1),dtype='d')
    K = FeaturesM.dot(FeaturesM.transpose())
    return K,max(cori)

def GetDirectorStats(session,features):
    ActorSmooth =        session.query(ActorSmoothing).all()
    userscount = {}
    moviecount = {}
    movieitems = {}

    cori = []
    coci = []
    cova = []



    for v in ActorSmooth:
        cod1i = next(filter(lambda x: x.Description == v.act1,features),None)
        cod2i = next(filter(lambda x: x.Description == v.act2,features),None)
        if cod1i is not None and cod2i is not None:
            cori.append(cod1i)
            coci.append(cod2i)
            cova.append(numpy.sqrt(v.n))
            cori.append(cod2i)
            coci.append(cod1i)
            cova.append(numpy.sqrt(v.n))
    FeaturesM = csr_matrix((cova, (cori, coci)), shape=(max(cori) + 1, max(coci) + 1),dtype='d')

    return FeaturesM,max(cori)

#arbritary factor
gainuser = 1000

session = init()

logger.info("1 features ophalen")

features =   session.query(FeaturesDef).all()
logger.info("2 user")
#K, nrows = GetUserStats(session,features)
logger.info("3 director")
M , nrows = GetDirectorStats(session,features)
logger.info("4 addition")

logger.info("5 tocoo")
N=M.tocoo()
del M
logger.info("6 storing")
for i in range(0, len(N.data)):
    session.add(CorrelationActor(featureobjectid1=N.row[i],featureobjectid2=N.col[i],value=N.data[i]))

session.commit()
session.close()








