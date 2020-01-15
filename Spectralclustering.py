
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.orm import contains_eager
from DataModel import Base,User, Movie,Rating,MovieFeatures,FeaturesCoeffs,FeaturesDef,HighScores,Country,Director,Actor,TopActor
from sqlalchemy import and_
from scipy import sparse
from scipy import sparse
import unicodedata
from scipy.sparse import linalg,csr_matrix,diags,csgraph
from scipy.sparse.linalg import eigsh
from sklearn.cluster import SpectralClustering
import sys
import matplotlib.pyplot as plt

from sklearn.cluster import KMeans
import numpy

numpy.set_printoptions(threshold=sys.maxsize)

def GetLaplacianCountries(n_clusters):
    session = init()
    CountryUser =  session.query(HighScores).join(HighScores.Movie).join(Country,Movie.countrys).options(contains_eager(HighScores.Movie).contains_eager(Movie.countrys,alias= Country)).all()

    usersDict = []
    for v in CountryUser:
        for k in v.Movie.countrys:
            usersDict.append(featureUsers(k.Description,v.UserObjectId))
    colors = Clustering(usersDict, n_clusters, session,'Country')
    return colors

def GetLaplacianActors(n_clusters):
    session = init()
    usersDict = GetUserDictActor(session)
    colors = Clustering(usersDict, n_clusters, session,'Actor')
    return colors


def GetUserDictActor(session):
    ActorUser = session.query(HighScores).join(HighScores.Movie).join(TopActor, Movie.topactors).options(
        contains_eager(HighScores.Movie).contains_eager(Movie.topactors, alias=TopActor)).all()
    usersDict = []
    for v in ActorUser:
        for k in v.Movie.topactors:
            s = unicodedata.normalize('NFKD',k.Description).encode('ASCII','ignore')
            usersDict.append(featureUsers(s.lower(), v.UserObjectId))
    return usersDict


def GetLaplacianDirectors(n_clusters):
    session = init()
    DirectorUser =  session.query(HighScores).join(HighScores.Movie).join(Director,Movie.directors).options(contains_eager(HighScores.Movie).contains_eager(Movie.directors,alias= Director)).all()
    usersDict = []
    for v in DirectorUser:
        for k in v.Movie.directors:
            usersDict.append(featureUsers(k.Description, v.UserObjectId))
    colors = Clustering(usersDict, n_clusters, session,'Director')
    return colors

def Clustering(usersDict, n_clusters, session, description):
    print(f"ophalen {description}]")
    print("aanmaken sparse matrix")
    clusterfeaturesM, countriesDict = sparselapl(usersDict)
    print("laplacian")
    print(f"clusterfeaturesM sparse {clusterfeaturesM.dtype}")
    LaPlacian = csgraph.laplacian(clusterfeaturesM.dot(clusterfeaturesM.transpose()),normed=True)
    print("correctie laplacian")
    print(f"LaPlacian sparse {LaPlacian.dtype}")


    print(f"LaPlacian sparse {LaPlacian.dtype}")
    vals, vecs = eigsh(LaPlacian,n_clusters+100,which='LM',sigma=0)
    #vals, vecs = numpy.linalg.eig(LaPlacian.todense())
    vecs = vecs[:, numpy.argsort(vals)].real
    kmeans = KMeans(n_clusters)
    kmeans.fit(vecs[:, 1:n_clusters+100])
    colors = kmeans.labels_
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
  def __init__(self, descr, usr):
    self.description = descr
    self.userobjectid = usr





def sparselapl(userDict):
    cori = []
    coci = []
    cova = []
    i = 0
    featuresDict = {}
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
            cova.append(1)
    FeaturesM = csr_matrix((cova, (cori, coci)), shape=(max(cori) + 1, max(coci) + 1),dtype='d')
    return FeaturesM,featuresDict

