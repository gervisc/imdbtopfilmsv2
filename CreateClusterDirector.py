

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.orm import contains_eager
from DataModel import Base,User, Movie,Rating,MovieFeatures,FeaturesCoeffs,FeaturesDef,HighScores,HighScoresActor,HighScoresDirector,Country,Director,Actor,TopActor,DirectorCluster,DensityDirectorCluster
from sqlalchemy import and_
import math
from scipy import sparse
from scipy import sparse
import unicodedata
from scipy.sparse import linalg,csr_matrix,diags,csgraph
from scipy.sparse.linalg import eigsh
from sklearn.cluster import SpectralClustering
import sys
import matplotlib.pyplot as plt
import networkx
from IMDBUserImportCSV import importratings,importList,callStoredProcedure
from Analysis import analysisNeural
from Spectralclustering import GetLaplacianCountries,GetLaplacianDirectors,GetLaplacianActors,GetLaplacianDirectorsMinimalCut
from datetime import datetime

def init():
    engine = create_engine('mysql://root:hu78to@127.0.0.1:3307/moviedborm?charset=utf8')
    Base.metadata.create_all(engine)
    session = Session(engine)
    return session

def splice(k,n,session):
    print('feature delete {}'.format(datetime.now().time()))
    session.query(FeaturesDef).delete('fetch')
    session.commit()
    print('laplacian {}'.format(datetime.now().time()))
    GetLaplacianDirectors(n,session)
    Clusters =session.query(DensityDirectorCluster).order_by(DensityDirectorCluster.aantal).all()
    for cl in Clusters:
        if cl.aantal is None or cl.aantal < 10:
            FClusters = session.query(FeaturesDef).filter(FeaturesDef.ParentDescription == cl.parentdescription).all()
            for j in FClusters:
                session.delete(j)
                session.add(DirectorCluster(Description=j.Description, Cluster='restgroep'))
        elif 10 <= cl.aantal <= 25:
            FClusters = session.query(FeaturesDef).filter(FeaturesDef.ParentDescription == cl.parentdescription).all()
            for j in FClusters:
                session.add(DirectorCluster(Description = j.Description, Cluster = 'DirectorCluster{}'.format(k)))
                session.delete(j)
            k = k+1
            print('cluster{}'.format(k))
            session.commit()
        elif cl.aantal > 25:
            splitgroep = session.query(FeaturesDef).filter(FeaturesDef.ParentDescription !=  cl.parentdescription ).filter(FeaturesDef.ParentDescription != 'DirectorCluster').filter(FeaturesDef.ParentDescription.contains('DirectorCluster')).all()
            for j in splitgroep:
                session.add(DirectorCluster(Description=j.Description, Cluster='restgroep'))
            session.commit()
            k=splice(k,math.ceil(cl.aantal/12),session)
            session.commit()
            break
    return k


session = init()
ko=-1
kn=0
n=2
print('cluster delete {}'.format(datetime.now().time()))
session.query(DirectorCluster).delete('fetch')
while kn > ko:
    print('cluster delete {}'.format(datetime.now().time()))
    session.query(DirectorCluster).filter(DirectorCluster.Cluster == 'restgroep').delete('fetch')
    session.commit()
    ko=kn
    print('splice {}'.format(datetime.now().time()))
    kn= splice(kn,2,session)
















