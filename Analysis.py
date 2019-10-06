from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.orm import contains_eager

from sqlalchemy import and_
from DataModel import Base,User, Movie,Rating,MovieFeatures,FeaturesCoeffs,FeaturesDef

import numpy as np
import scipy
from scipy import sparse
from scipy.sparse import linalg

def analysis(username):

    engine = create_engine('mysql://root:hu78to@127.0.0.1:3307/moviedborm?charset=utf8')
    Base.metadata.create_all(engine)
    session = Session(engine)



    featurs = session.query(MovieFeatures).join(MovieFeatures.Movie).join(Rating,Movie.ratings).join(Rating.User).filter(User.UserName==username).\
            options(contains_eager(MovieFeatures.Movie).contains_eager(Movie.ratings,alias=Rating)).order_by(MovieFeatures.MovieObjectId).all()
    directorcoefs =session.query(FeaturesDef.ObjectId).filter(FeaturesDef.ParentDescription == 'directors').all()
    actorcoefs =session.query(FeaturesDef.ObjectId).filter(FeaturesDef.ParentDescription == 'actors').all()
    countrycoefs =session.query(FeaturesDef.ObjectId).filter(FeaturesDef.ParentDescription == 'countries').all()
    othercoefs = session.query(FeaturesDef.ObjectId).filter(and_(and_(FeaturesDef.ParentDescription != 'countries',FeaturesDef.ParentDescription != 'actors'),FeaturesDef.ParentDescription != 'directors')).all()

    directorcoefs = [value for value, in directorcoefs]

    actorcoefs = [value for value, in actorcoefs]

    countrycoefs = [value for value, in countrycoefs]

    othercoefs = [value for value, in othercoefs]



    maxn = max(directorcoefs+actorcoefs+countrycoefs+othercoefs)


    m3 = []
    m3i=[0]*(maxn+1)
    for f in featurs:
        m3i[f.FeatureObjectId]+=1

    for k in actorcoefs+countrycoefs+directorcoefs:
        if m3i[k] < 3:
            m3.append(k)

    for k in othercoefs:
        if m3i[k] < 6:
            m3.append(k)
    f2 =[]
    for f in featurs:
        if f.FeatureObjectId not in m3:
            f2.append(f)
    featurs= f2


    n= len(set((node.FeatureObjectId for node in featurs)))

    m = len(set(node.MovieObjectId for node in featurs))

    featursM = np.zeros((m,n))
    ratingsM = np.zeros(m,dtype=float)
    j=-1

    kitem = 0
    #getfactor FeaturesM
    factorsGM= [-1]*(maxn+1)

    # get factor features
    factorsGDB = []
    i=0
    for f in featurs:

        if kitem != f.MovieObjectId:
            j += 1
            kitem = f.MovieObjectId
            ratingsM[j]=max(f.Movie.ratings[0].Rating,5)

        if factorsGM[f.FeatureObjectId] == -1:
            factorsGDB.append(f.FeatureObjectId)
            factorsGM[f.FeatureObjectId] = i
            featursM[j, i] = f.Factor
            i+=1
        else:
            featursM[j,factorsGM[f.FeatureObjectId]]=f.Factor







    c=scipy.sparse.linalg.lsqr(featursM,ratingsM)
    c = c[0]
    # reduce matrix dimensionality

    fns = list(set(node.FeatureObjectId for node in featurs))
    avgdirectors=0
    for i in set(directorcoefs).intersection(fns):
        avgdirectors = avgdirectors+c[factorsGM[i]]/len(set(directorcoefs).intersection(fns))


    avgactors=0
    for i in set(actorcoefs).intersection(fns):
        avgactors = avgactors+c[factorsGM[i]]/len(set(actorcoefs).intersection(fns))



    avgcountries=0
    for i in set(countrycoefs).intersection(fns):
        avgcountries = avgcountries+c[factorsGM[i]]/len(set(countrycoefs).intersection(fns))




    n2=len(set(othercoefs).intersection(fns)) + 6
    MR = np.zeros((n, n2))




    for v in directorcoefs:
        if c[factorsGM[v]] < avgdirectors and v in fns:
            MR[factorsGM[v],0]=1
        elif v in fns  :
            MR[factorsGM[v],1] = 1
    for v in actorcoefs:
        if c[factorsGM[v]] < avgactors and v in fns:
            MR[factorsGM[v],2] = 1
        elif v in fns:
            MR[factorsGM[v],3] = 1
    for v in countrycoefs:
        if c[factorsGM[v]] < avgcountries and v in fns:
            MR[factorsGM[v], 4] = 1
        elif v in fns:
            MR[factorsGM[v], 5] = 1
    i=6
    for v in othercoefs:
        if   v in fns:
            MR[factorsGM[v], i] = 1
            i+=1



    featursMR= featursM.dot(MR)


    cr=scipy.sparse.linalg.lsqr(featursMR,ratingsM)

    c=MR.dot(cr[0])

    userdb = session.query(User).filter(User.UserName == username).first()
    session.query(FeaturesCoeffs).filter(FeaturesCoeffs.UserObjectId == userdb.ObjectId).delete()
    k=0
    for ceff in c:
        session.add(FeaturesCoeffs(FeatureObjectId=factorsGDB[k],Value=ceff,User=userdb))
        k+=1



    session.commit()

