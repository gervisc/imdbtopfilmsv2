

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from repository.DataModel import Base, FeaturesDef, DirectorCluster,DensityDirectorCluster
import math
from experimental.clustering.Spectralclustering import GetLaplacianDirectors
from datetime import datetime

def init():
    engine = create_engine('mysql://root:hu78to@127.0.0.1:3307/moviedborm?charset=utf8')
    Base.metadata.create_all(engine)
    session = Session(engine)
    return session

def splice(k,n,session):
    logger.info('feature delete {}'.format(datetime.now().time()))
    session.query(FeaturesDef).delete('fetch')
    session.commit()
    logger.info('laplacian {}'.format(datetime.now().time()))
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
            logger.info('cluster{}'.format(k))
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
logger.info('cluster delete {}'.format(datetime.now().time()))
session.query(DirectorCluster).delete('fetch')
while kn > ko:
    logger.info('cluster delete {}'.format(datetime.now().time()))
    session.query(DirectorCluster).filter(DirectorCluster.Cluster == 'restgroep').delete('fetch')
    session.commit()
    ko=kn
    logger.info('splice {}'.format(datetime.now().time()))
    kn= splice(kn,2,session)
















