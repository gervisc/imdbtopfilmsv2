from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.orm import contains_eager

from sqlalchemy import and_,or_


from DataModel import Base,User, Movie,Rating,MovieFeatures,FeaturesCoeffs,FeaturesDef

import numpy as np
import scipy
from scipy import sparse
from scipy.sparse import linalg,csr_matrix

from keras.models import Sequential
from keras.layers import Dense
from keras import initializers
from keras.callbacks import EarlyStopping
from keras import activations

import tensorflow as tf
print(tf.version)
print(dir(tf.feature_column))
from numpy.random import seed
from tensorflow_core.python.framework.random_seed import set_seed



def analysisNeural(username,neuronslayer1,f1,f2):
    np.random.seed(1)
    set_seed(2)
    engine = create_engine('mysql://root:hu78to@127.0.0.1:3307/moviedborm?charset=utf8')
    Base.metadata.create_all(engine)
    session = Session(engine)

    actorcoefs,  featurs, othercoefs = GetData(session, username)

    # reduce features
    maxn = max( actorcoefs + othercoefs)
    featurs = ReduceOnOcurences(actorcoefs, featurs, maxn, othercoefs,f1,f2)

    factorsGDB,factorsGM,  featursM, n, ratingsM = GetAandBone(featurs, maxn)
    print(ratingsM)

    c = scipy.sparse.linalg.lsqr(featursM, ratingsM)
    c = c[0]
    # reduce matrix dimensionality

    MR = reducecombine(actorcoefs, c,  factorsGM, featurs, n, othercoefs)
    featursMR = featursM.dot(MR)
    model = Sequential()
    model.add(Dense(neuronslayer1, kernel_initializer=initializers.glorot_uniform(seed=12), activation='relu', input_dim=featursMR.shape[1]))
    model.add(Dense(1, activation='linear'))
    model.compile(loss='mean_squared_error', optimizer='adam', metrics=['accuracy'])
    es = EarlyStopping(monitor='loss', mode='min', verbose=1, patience=3, min_delta=1e-4)
    model.fit(featursMR, ratingsM, epochs=1000, callbacks=[es])
    w=model.get_weights()

    userdb = session.query(User).filter(User.UserName == username).first()
    session.query(FeaturesCoeffs).filter(FeaturesCoeffs.UserObjectId == userdb.ObjectId).delete()
    #print(w[0].shape[0])

    k=0
    for lay in model.layers:
        w=lay.get_weights()
        print(lay.name)
        if k== 0:
            w0  = MR.dot(w[0])
            for i in range(0, w0.shape[0]):
                for j in range(0, w0.shape[1]):
                    session.add(
                            FeaturesCoeffs(FeatureObjectId=factorsGDB[i], Value=w0[i, j], User=userdb, Layer=0,
                                           ColumnId=j, Bias=0))
        else:
            WriteCoefficients(session, userdb, w[0],k)

        WriteBias(session,userdb,w[1],k)
        k+=1


    session.commit()
    session.close()


def WriteCoefficients(session, userdb, w,layer):
    for i in range(0, w.shape[0]):
        for j in range(0,w.shape[1]):
            session.add(FeaturesCoeffs(FeatureObjectId=i, Value=w[i,j], User=userdb, Layer=layer, ColumnId=j,Bias=0))

def WriteBias(session, userdb, w,layer):
    for i in range(0, w.shape[0]):
        session.add(FeaturesCoeffs(FeatureObjectId=0, Value=w[i], User=userdb, Layer=layer, ColumnId=i,Bias=1))

def analysisLinear(username):
    engine = create_engine('mysql://root:hu78to@127.0.0.1:3307/moviedborm?charset=utf8')
    Base.metadata.create_all(engine)
    session = Session(engine)

    actorcoefs, featurs, othercoefs = GetData(session, username)

    # reduce features
    maxn = max( actorcoefs + othercoefs)
    featurs = ReduceOnOcurences(actorcoefs,  featurs, maxn, othercoefs)

    factorsGDB, factorsGM, featursM, n, ratingsM = GetAandBone(featurs, maxn)

    c = scipy.sparse.linalg.lsqr(featursM, ratingsM)
    c = c[0]
    # reduce matrix dimensionality

    MR = reducecombine(actorcoefs, c,   factorsGM, featurs, n, othercoefs)
    featursMR = featursM.dot(MR)


    cr=scipy.sparse.linalg.lsqr(featursMR,ratingsM)

    c=MR.dot(cr[0])

    userdb = session.query(User).filter(User.UserName == username).first()
    session.query(FeaturesCoeffs).filter(FeaturesCoeffs.UserObjectId == userdb.ObjectId).delete()
    k=0
    for ceff in c:
        session.add(FeaturesCoeffs(FeatureObjectId=factorsGDB[k],Value=ceff,User=userdb,Layer=0,Bias=0,ColumnId =0))
        k+=1



    session.commit()






def reducecombine(actorcoefs, c,  factorsGM, featurs, n, othercoefs):
    fns = list(set(node.FeatureObjectId for node in featurs))

    avgactors = 0
    for i in set(actorcoefs).intersection(fns):
        avgactors = avgactors + c[factorsGM[i]] / len(set(actorcoefs).intersection(fns))

    n2 = len(set(othercoefs).intersection(fns)) + 2
    coci=[]
    cori=[]
    cova=[]


    for v in actorcoefs:
        if c[factorsGM[v]] < avgactors and v in fns:
            cori.append(factorsGM[v])
            coci.append(0)
            cova.append(1)
        elif v in fns:
            cori.append(factorsGM[v])
            coci.append(1)
            cova.append(1)

    i = 2
    for v in othercoefs:
        if v in fns:
            cori.append(factorsGM[v])
            coci.append(i)
            cova.append(1)
            i += 1
    MR =csr_matrix((cova, (cori, coci)),shape=(n,n2))
    return MR


def GetAandBone(featurs, maxn):
    n = len(set((node.FeatureObjectId for node in featurs)))
    m = len(set(node.MovieObjectId for node in featurs))
    # featursM = np.zeros((m, n))
    ratingsM = np.zeros(m, dtype=float)
    j = -1
    kitem = 0
    # getfactor FeaturesM
    factorsGM = [-1] * (maxn + 1)
    # get factor features
    factorsGDB = []
    cori = []
    coci = []
    cova = []
    i = 0
    for f in featurs:

        if kitem != f.MovieObjectId:
            j += 1
            kitem = f.MovieObjectId
            ratingsM[j] = min(max(f.Movie.ratings[0].Rating, 5),9)

        if factorsGM[f.FeatureObjectId] == -1:
            factorsGDB.append(f.FeatureObjectId)
            factorsGM[f.FeatureObjectId] = i
            cori.append(j)
            coci.append(i)
            cova.append(f.Factor)
            i += 1
        else:
            cori.append(j)
            coci.append(factorsGM[f.FeatureObjectId])
            cova.append(f.Factor)
    featursM = csr_matrix((cova, (cori, coci)),shape=(m,n))
    return factorsGDB,factorsGM, featursM, n, ratingsM


def ReduceOnOcurences(actorcoefs,  featurs, maxn, othercoefs,f1, f2):
    m3 = []
    m3i = [0] * (maxn + 1)
    for f in featurs:
        m3i[f.FeatureObjectId] += 1
    for k in actorcoefs         :
        if m3i[k] < f1:
            m3.append(k)
    for k in othercoefs:
        if m3i[k] < f2:
            m3.append(k)
    f2 = []
    for f in featurs:
        if f.FeatureObjectId not in m3:
            f2.append(f)
    featurs = f2
    return featurs


def GetData(session, username):
    featurs = session.query(MovieFeatures).join(MovieFeatures.Movie).join(Rating, Movie.ratings).join(
        Rating.User).join(MovieFeatures.FeaturesDef).filter(and_(and_(User.UserName == username,FeaturesDef.ParentDescription != 'Countries') ,FeaturesDef.ParentDescription != 'Directors')). \
        options(contains_eager(MovieFeatures.Movie).contains_eager(Movie.ratings, alias=Rating)).order_by(
        MovieFeatures.MovieObjectId).all()

    actorcoefs = session.query(FeaturesDef.ObjectId).filter(FeaturesDef.ParentDescription == 'actors').all()

    othercoefs = session.query(FeaturesDef.ObjectId).filter(or_(
        or_(or_(or_(or_(FeaturesDef.ParentDescription == 'genres', FeaturesDef.ParentDescription == 'titletype'),
             FeaturesDef.ParentDescription == 'misc'),FeaturesDef.ParentDescription == 'years'),FeaturesDef.ParentDescription == 'CountryCluster'),FeaturesDef.ParentDescription== 'DirectorCluster')).all()

    actorcoefs = [value for value, in actorcoefs]

    othercoefs = [value for value, in othercoefs]
    return actorcoefs,  featurs, othercoefs



