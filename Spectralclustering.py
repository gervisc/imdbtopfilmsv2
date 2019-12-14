
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.orm import contains_eager
from DataModel import Base,User, Movie,Rating,MovieFeatures,FeaturesCoeffs,FeaturesDef,HighScores,Country
from sqlalchemy import and_
from scipy import sparse
from scipy import sparse
from scipy.sparse import linalg,csr_matrix,diags
from sklearn.cluster import SpectralClustering
import sys

from sklearn.cluster import KMeans
import numpy

numpy.set_printoptions(threshold=sys.maxsize)

def GetLaplacianCountries():
    engine = create_engine('mysql://root:hu78to@127.0.0.1:3307/moviedborm?charset=utf8')
    Base.metadata.create_all(engine)
    session = Session(engine)
    CountryUser =  session.query(HighScores).join(HighScores.Movie).join(Country,Movie.countrys).options(contains_eager(HighScores.Movie).contains_eager(Movie.countrys,alias= Country)).all()
    print("ophalen countries")
    #countriesDict = GetCountryDict(session,CountryUser)
    print("aanmaken sparse matrix")
    CountryUserM = sparselapl(CountryUser)
    print("laplacian")
    LaPlacian =CountryUserM.dot(CountryUserM.transpose()).multiply(-1)

    print("correctie laplaacian")
    diag = LaPlacian.diagonal()*-1
    LaPlacian.setdiag(diag)
    LaPlacian.eliminate_zeros()
    vals,vecs = numpy.linalg.eig(LaPlacian.todense())
    vecs=vecs[:,numpy.argsort(vals)]


    kmeans = KMeans(n_clusters=8)
    kmeans.fit(vecs[:,1:8])
    colors = kmeans.labels_
    OldRecords = session.query(FeaturesDef).filter(FeaturesDef.Description.startswith("CountryCluster"))
    session.query(FeaturesCoeffs).filter(FeaturesCoeffs.UserObjectId == userdb.ObjectId).delete()

    #print(LaPlacian.todense())
    #clustering = SpectralClustering(n_clusters=10,affinity='precomputed',assign_labels='discretize').fit_predict(LaPlacian)
    return colors


# def GetCountryDict(session,CountryUser):
#     #countries = session.query(FeaturesDef).filter(FeaturesDef.ParentDescription == 'countries').all()
#     print("vullen country dictionary")
#     countriesDict = {}
#     i=0
#     for c in countries:
#         if c.Description in [k.Description for k in [for l in ] [v.Movie for v in CountryUser]]:
#             countriesDict[c.Description] = i
#             print(F"land{c.Description} : {i}")
#             i+=1
#     return countriesDict


def sparselapl(CountryUser):
    cori = []
    coci = []
    cova = []
    i = 0
    countriesDict = {}
    for v in CountryUser:
        for k in v.Movie.countrys:
            codi = None
            if k.Description not in countriesDict and k.Description.strip() != '':
                countriesDict[k.Description] = i
                codi = i
                i += 1
            elif k.Description.strip() != '':
                codi = countriesDict.get(k.Description)
            if codi is not None:
                cori.append(codi)
                coci.append(v.UserObjectId)
                cova.append(1)
    CountryUserM = csr_matrix((cova, (cori, coci)), shape=(max(cori) + 1, max(coci) + 1))
    return CountryUserM,countriesDict
