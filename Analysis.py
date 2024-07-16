from numpy import double
from sqlalchemy.orm import contains_eager

from sqlalchemy import and_

from repository.DataModel import User, Movie, Rating, MovieFeatures, FeaturesCoeffs, FeaturesDef, Constant

import numpy as np
from scipy.sparse import csr_matrix

from keras.models import Sequential
from keras.layers import Dense
from keras import initializers,regularizers
from keras.callbacks import EarlyStopping

import tensorflow as tf


def analysisNeural(username,neuronslayer1,logger,session,l2=0,leakyalpha=0.01,sseed=800):
    np.random.seed(199)
    tf.random.set_seed(88)
    tf.keras.backend.set_floatx('float64')
    leaky =session.query(Constant).filter(Constant.Description == "LeakyAlpha").first()
    leaky.Value = leakyalpha
    session.commit()

    featurs,coeffs = GetData(session, username)

    # reduce features
    maxn = max( coeffs)
    factorsGDB,factorsGM,  featursM, n, ratingsM = GetAandBone(featurs, maxn)


    featursMR = featursM#._mul_sparse_matrix(MR)
    featursMR.sort_indices()
    model = Sequential()
    model.add(Dense(neuronslayer1,kernel_regularizer= regularizers.L1L2(l1=l2, l2=l2) ,  kernel_initializer=initializers.HeUniform(seed=sseed),
                    activation=tf.keras.layers.LeakyReLU(alpha=leakyalpha), input_dim=featursMR.shape[1]))

    model.add(Dense(1, activation='linear'))
    model.compile(loss='mean_squared_error', optimizer='Adam', metrics=['accuracy'])
    es = EarlyStopping(monitor='loss', mode='min', verbose=1, patience=25, min_delta=1e-5,restore_best_weights=True)
    model.fit(featursMR, ratingsM, epochs=20000, callbacks=[es],batch_size= len(ratingsM))


    userdb = session.query(User).filter(User.UserName == username).first()
    session.query(FeaturesCoeffs).filter(FeaturesCoeffs.UserObjectId == userdb.ObjectId).delete()

    session.flush()
    session.commit()
    k=0
    for lay in model.layers:
        w=lay.get_weights()
        logger.info(lay.name)
        if k== 0:
            w0  =w[0]# MR._mul_sparse_matrix(w[0])
            for i in range(0, w0.shape[0]):
                for j in range(0, w0.shape[1]):
                    session.add(
                            FeaturesCoeffs(FeatureObjectId=factorsGDB[i], Value=w0[i, j], User=userdb, Layer=0,
                                           ColumnId=j, Bias=0))
        else:
            WriteCoefficients(session, userdb, w[0],k)

        WriteBias(session,userdb,w[1],k)
        k+=1

    session.flush()
    session.commit()



def WriteCoefficients(session, userdb, w,layer):
    for i in range(0, w.shape[0]):
        for j in range(0,w.shape[1]):
            session.add(FeaturesCoeffs(FeatureObjectId=i, Value=w[i,j], User=userdb, Layer=layer, ColumnId=j,Bias=0))

def WriteBias(session, userdb, w,layer):
    for i in range(0, w.shape[0]):
        session.add(FeaturesCoeffs(FeatureObjectId=0, Value=w[i], User=userdb, Layer=layer, ColumnId=i,Bias=1))







def GetAandBone(featurs, maxn):
    n = len(set((node.FeatureObjectId for node in featurs)))
    m = len(set(node.MovieObjectId for node in featurs))
    # featursM = np.zeros((m, n))
    ratingsM = np.zeros(m, dtype=double)
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



