

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.orm import contains_eager
from DataModel import Base,User, Movie,Rating,MovieFeatures,FeaturesCoeffs,FeaturesDef,HighScores,Country,Director,Actor,TopActor,DensityActorCluster,ActorCluster
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
from Spectralclustering import GetLaplacianCountries,GetLaplacianDirectors,GetLaplacianActors


def init():
    engine = create_engine('mysql://root:hu78to@127.0.0.1:3307/moviedborm?charset=utf8')
    Base.metadata.create_all(engine)
    session = Session(engine)
    return session

def splice(k,n,session):

    session.query(FeaturesDef).delete('fetch')
    session.commit()
    GetLaplacianActors(n,session)
    Clusters =session.query(DensityActorCluster).order_by(DensityActorCluster.aantal).all()
    for cl in Clusters:
        if cl.aantal is None or cl.aantal < 10:
            FClusters = session.query(FeaturesDef).filter(FeaturesDef.ParentDescription == cl.parentdescription).all()
            for j in FClusters:
                session.delete(j)
                session.add(ActorCluster( Description=j.Description, Cluster='restgroep'))
                session.commit()
        elif 10 <= cl.aantal <= 25:
            FClusters = session.query(FeaturesDef).filter(FeaturesDef.ParentDescription == cl.parentdescription).all()
            for j in FClusters:
                session.add(ActorCluster(Description = j.Description, Cluster = 'ActorCluster{}'.format(k)))
                session.delete(j)
            k = k+1
            print('cluster{}'.format(k))
            session.commit()
        elif cl.aantal > 25:

            splitgroep = session.query(FeaturesDef).filter(FeaturesDef.ParentDescription !=  cl.parentdescription ).filter(FeaturesDef.ParentDescription != 'ActorCluster').filter(FeaturesDef.ParentDescription.contains('ActorCluster')).all()
            for j in splitgroep:
                session.add(ActorCluster( Description=j.Description, Cluster='restgroep'))
            session.commit()
            k=splice(k,math.ceil(cl.aantal/8),session)
            session.commit()
            break
    return k


session = init()
ko=-1
kn=0
n=2
#session.query(ActorCluster).delete('fetch')
while kn > ko:
    session.query(ActorCluster).filter(ActorCluster.Cluster == 'restgroep').delete('fetch')
    session.commit()
    ko=kn
    kn= splice(kn,2,session)
    print('blab')
















