from sqlalchemy import create_engine,cast, Integer
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
from keras import initializers,regularizers
from keras.callbacks import EarlyStopping
from keras import activations
from sqlalchemy import func

import tensorflow as tf
print(tf.version)
print(dir(tf.feature_column))
from numpy.random import seed




def analysisNeural(username,neuronslayer1,session,l2=0,sseed=12):
    np.random.seed(2)
    tf.random.set_seed(3)


    featurs,coeffs = GetData(session, username)

    # reduce features
    maxn = max( coeffs)
    factorsGDB,factorsGM,  featursM, n, ratingsM = GetAandBone(featurs, maxn)

    # reduce matrix dimensionality
    MR = reducecombine(factorsGM, featurs, n, coeffs)
    featursMR = featursM.dot(MR)
    featursMR.sort_indices()
    model = Sequential()
    model.add(Dense(neuronslayer1,kernel_regularizer=regularizers.l2(l2) ,  kernel_initializer=initializers.glorot_uniform(seed=sseed), activation='relu', input_dim=featursMR.shape[1]))
    model.add(Dense(1, activation='linear'))
    model.compile(loss='mean_squared_error', optimizer='adam', metrics=['accuracy'])
    es = EarlyStopping(monitor='loss', mode='min', verbose=1, patience=3, min_delta=1e-4)
    model.fit(featursMR, ratingsM, epochs=1000, callbacks=[es])


    userdb = session.query(User).filter(User.UserName == username).first()
    session.query(FeaturesCoeffs).filter(FeaturesCoeffs.UserObjectId == userdb.ObjectId).delete()


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



def WriteCoefficients(session, userdb, w,layer):
    for i in range(0, w.shape[0]):
        for j in range(0,w.shape[1]):
            session.add(FeaturesCoeffs(FeatureObjectId=i, Value=w[i,j], User=userdb, Layer=layer, ColumnId=j,Bias=0))

def WriteBias(session, userdb, w,layer):
    for i in range(0, w.shape[0]):
        session.add(FeaturesCoeffs(FeatureObjectId=0, Value=w[i], User=userdb, Layer=layer, ColumnId=i,Bias=1))







def reducecombine(factorsGM, featurs, n, othercoefs):
    fns = list(set(node.FeatureObjectId for node in featurs))
    n2 = len(set(othercoefs).intersection(fns))
    coci=[]
    cori=[]
    cova=[]
    i = 0
    for v in othercoefs:
        if v in fns:
            cori.append(factorsGM[v])
            coci.append(i)
            cova.append(1)
            i += 1
    print(f"n {n}")
    print(f"n2 {n2}")
    print(f"coci {max(coci)}")
    print(f"cori {max(cori)}")


    MR =csr_matrix((cova, (cori, coci)),shape=(n2,max(coci)+1))

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





def GetData(session, username):
    featurs = session.query(MovieFeatures).join(MovieFeatures.Movie).join(Rating, Movie.ratings).join(
        Rating.User).join(MovieFeatures.FeaturesDef).filter(and_(User.UserName == username,FeaturesDef.Active == 1 )). \
        options(contains_eager(MovieFeatures.Movie).contains_eager(Movie.ratings, alias=Rating)).order_by(
        MovieFeatures.MovieObjectId).all()
    othercoefs = [value.FeatureObjectId for value in featurs]
    return featurs, othercoefs



