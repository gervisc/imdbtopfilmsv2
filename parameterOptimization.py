import os

import numpy as np
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sklearn.model_selection import GridSearchCV
from scikeras.wrappers import KerasRegressor, KerasClassifier
from sklearn.model_selection import LeaveOneOut
from scipy.sparse import linalg,csr_matrix

from keras.models import Sequential
from keras.layers import Dense,LeakyReLU
from keras import initializers,regularizers
from keras.callbacks import EarlyStopping
import tensorflow as tf

from Analysis import GetData, GetAandBone

cstring = os.environ.get("MOVIEDB")
engine = create_engine(cstring)
session = Session(engine)
IMDB_ID = "51273819"
username = 'CSVImport' + IMDB_ID
featurs,coeffs = GetData(session, username)

# reduce features
maxn = max( coeffs)
factorsGDB,factorsGM,  featursM, n, ratingsM = GetAandBone(featurs, maxn)
featursMR = featursM#._mul_sparse_matrix(MR)
featursMR.sort_indices()
input_dim=featursMR.shape[1]
print(input_dim)
np.random.seed(199)
tf.random.set_seed(88)
tf.keras.backend.set_floatx('float64')
def create_model(l1_reg, l2_reg, num_layers=1, nodes_per_layer=16,leaky_relu=0.0001):
    sseed=800
    optimizer = 'adam'
    modelk = Sequential()
    modelk.add(Dense(nodes_per_layer, kernel_regularizer=regularizers.L1L2(l1=l1_reg, l2=l2_reg), input_dim=3381, activation=tf.keras.layers.LeakyReLU(alpha=leaky_relu), kernel_initializer=initializers.HeUniform(seed=sseed)))


    for _ in range(num_layers-1):
        modelk.add(Dense(nodes_per_layer, kernel_regularizer=regularizers.L1L2(l1=l1_reg, l2=l2_reg), input_dim=3381, activation=tf.keras.layers.LeakyReLU(alpha=leaky_relu), kernel_initializer=initializers.HeUniform(seed=sseed)))
    modelk.add(Dense(1, activation='linear'))
    modelk.compile(loss='mean_squared_error', optimizer='Adam', metrics=['accuracy'])
    modelk.compile(loss='mean_squared_error', optimizer=optimizer)
    return modelk


param_grid = {
    'model__l1_reg': [0.005, 0.01, 0.02, 0.03, 0.04, 0.05],
    'model__l2_reg': [0.005, 0.01, 0.02, 0.03, 0.04, 0.05],
    'model__num_layers': [1, 2],  # Number of hidden layers
    'model__nodes_per_layer': [2,3,4],# Nodes per hidden layer
    'model__leaky_relu' : [0.0001,0.001,0.0005,0.0002]
}

es = EarlyStopping(monitor='loss', mode='min', verbose=0, patience=2, min_delta=1e-4,restore_best_weights=True)
model = KerasClassifier(build_fn=create_model, verbose=0 ,epochs=20000, callbacks=[es],batch_size= -1)
grid_search = GridSearchCV(estimator=model, param_grid=param_grid, cv=10, n_jobs=-1)
grid_result = grid_search.fit(featursMR, ratingsM)
# summarize results
print("Best: %f using %s" % (grid_result.best_score_, grid_result.best_params_))
means = grid_result.cv_results_['mean_test_score']
stds = grid_result.cv_results_['std_test_score']
params = grid_result.cv_results_['params']
for mean, stdev, param in zip(means, stds, params):
    print("%f (%f) with: %r" % (mean, stdev, param))

