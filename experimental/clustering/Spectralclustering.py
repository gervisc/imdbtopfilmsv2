
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.orm import contains_eager
from repository.DataModel import Base, Movie, FeaturesDef,HighScores,Country, TopActor,TopDirector
from scipy.sparse import csr_matrix
from sklearn.cluster import SpectralClustering
import sys
from datetime import datetime
import numpy

numpy.set_logger.infooptions(threshold=sys.maxsize)

def GetLaplacianCountries(n_clusters):
    session = init()
    CountryUser =  session.query(HighScores).join(HighScores.Movie).join(Country,Movie.countrys).options(contains_eager(HighScores.Movie).contains_eager(Movie.countrys,alias= Country)).all()
    userscount = {}
    movieitems = {}
    moviecount ={}
    usersDict = []
    for v in CountryUser:
        userscount[v.UserObjectId] = 1 if v.UserObjectId not in userscount  else userscount[v.UserObjectId]+1

        for k in v.Movie.countrys:
            moviecount[k.Description] = 1 if k.Description not in moviecount else moviecount[k.Description]+1
            movieitems[v.Movie.ObjectId] = 1 if v.Movie.ObjectId not in movieitems else movieitems[v.Movie.ObjectId]+ 1
            usersDict.append(featureUsers(k.Description,v.UserObjectId,v.Movie.ObjectId))
    colors = Clustering(usersDict,userscount,movieitems,moviecount, n_clusters, session,'Country')
    return colors

def GetLaplacianActors(n_clusters,session):

    usersDict,userscount,movieitems,moviecount = GetUserDictActor(session)
    colors = Clustering(usersDict,userscount,movieitems,moviecount, n_clusters, session,'Actor')
    return colors


def GetUserDictActor(session):
    ActorUser = \
        session.query(HighScores).join(TopActor, HighScores.topactors2). \
            options(contains_eager(HighScores.topactors2)).all()
    usersDict = []
    userscount = {}
    moviecount = {}
    movieitems = {}
    for v in ActorUser:
        userscount[v.UserObjectId] = 1 if v.UserObjectId not in userscount else userscount[v.UserObjectId]+1

        for k in v.Movie.topactors:
            #s = unicodedata.normalize('NFKD',k.Description).encode('ASCII','ignore')
            moviecount[k.Description] = 1 if k.Description not in moviecount else moviecount[k.Description] + 1
            if v.Movie.ObjectId not in movieitems:
                movieitems[v.Movie.ObjectId] = 1
            else:
                movieitems[v.Movie.ObjectId] += 1

            usersDict.append(featureUsers(k.Description, v.UserObjectId,v.Movie.ObjectId))
    return usersDict,userscount,movieitems,moviecount


def GetLaplacianDirectors(n_clusters,session):
    #session = init()
    logger.info('director set {}'.format(datetime.now().time()))
    DirectorUser =  \
        session.query(HighScores).join(TopDirector,HighScores.topdirectors2).\
        options(contains_eager(HighScores.topdirectors2)).all()
           # options(contains_eager(HighScoresDirector.Movie).contains_eager(Movie.directors,alias=Director))
    logger.info('verdicht director {}'.format(datetime.now().time()))
    usersDict = []
    userscount = {}
    movieitems = {}
    moviecount = {}
    for v in DirectorUser:
        if v.UserObjectId not in userscount:
            userscount[v.UserObjectId] = 1
        else:
            userscount[v.UserObjectId] +=1

        for k in v.Movie.topdirectors:
            moviecount[k.Description] = 1 if k.Description not in moviecount else moviecount[k.Description] + 1
            if v.Movie.ObjectId not in movieitems:
                movieitems[v.Movie.ObjectId] = 1
            else:
                movieitems[v.Movie.ObjectId] += 1
        for l in    v.Movie.topdirectors:
            usersDict.append(featureUsers(l.Description, v.UserObjectId,v.Movie.ObjectId))
    logger.info('clusteren {}'.format(datetime.now().time()))
    colors = Clustering(usersDict,userscount, movieitems,moviecount, n_clusters, session,'Director')
    return colors



def Clustering(usersDict, userscount, movieitems,moviecount, n_clusters, session, description):
    logger.info(f"ophalen {description}]")
    logger.info("aanmaken sparse matrix")
    clusterfeaturesM, countriesDict, nrows = sparselapl(usersDict, userscount, movieitems,moviecount)
    logger.info("laplacian")
    logger.info(f"clusterfeaturesM sparse {clusterfeaturesM.dtype}")
    #LaPlacian = csgraph.laplacian(clusterfeaturesM.dot(clusterfeaturesM.transpose()),normed=True)
    logger.info("correctie laplacian")


    #colors = KmeansAlgorithm(LaPlacian, n_clusters, nrows)

    Clustering =SpectralClustering(n_clusters=n_clusters, affinity="precomputed").fit(clusterfeaturesM.dot(clusterfeaturesM.transpose()))
    colors = Clustering.labels_

    for k, v in countriesDict.items():
        session.add(FeaturesDef(Description=k, ParentDescription="{}Cluster".format(description) + str(colors[v])))
    for i in range(0, n_clusters):
        session.add(FeaturesDef(Description="{}Cluster".format(description) + str(i), ParentDescription="{}Cluster".format(description)))
    #  plt.scatter(numpy.arange(len(vals)),vals)
    #plt.grid()
    #plt.show()
    session.commit()
    session.close()
    return colors





def init():
    engine = create_engine('mysql://root:hu78to@127.0.0.1:3307/moviedborm?charset=utf8')
    Base.metadata.create_all(engine)
    session = Session(engine)
    return session

class featureUsers:
  def __init__(self, descr, usr,movie):
    self.description = descr
    self.userobjectid = usr
    self.movieobjectid = movie





def sparselapl(userDict, userscount, movieitems,moviecount):
    cori = []
    coci = []
    cova = []
    i = 0
    featuresDict = {}
    avgmoviecount = sum(moviecount.values())/float(len(moviecount))
    for v in userDict:
        codi = None
        if v.description not in featuresDict and v.description.strip() != '':
            featuresDict[v.description] = i
            codi = i
            i += 1
        elif v.description.strip() != '':
            codi = featuresDict.get(v.description)
        if codi is not None:
            cori.append(codi)
            coci.append(v.userobjectid)
            cova.append(numpy.sqrt(1 / userscount[v.userobjectid] / movieitems[v.movieobjectid])/moviecount[v.description]*avgmoviecount)
    FeaturesM = csr_matrix((cova, (cori, coci)), shape=(max(cori) + 1, max(coci) + 1),dtype='d')
    return FeaturesM,featuresDict,max(cori)

