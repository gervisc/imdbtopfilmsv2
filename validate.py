from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.orm import contains_eager

from sqlalchemy import and_
from DataModel import Base

import numpy as np
import scipy
from scipy import sparse
from scipy.sparse import linalg,csr_matrix

from keras.models import Sequential
from keras.layers import Dense
from keras import initializers
from keras.callbacks import EarlyStopping
from keras import activations

import tensorflow
from numpy.random import seed
from IMDBUserImportCSV import importratings,importList,callStoredProcedure
from Analysis import analysisLinear,analysisNeural
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium.common.exceptions import *
from selenium.webdriver.firefox.options import Options
import os
import csv
from DataModel import Base,User, Movie,Rating,ParentRating,CustomList,ValResult,ValSet
from OMDBapi import GetMovie
from sqlalchemy import and_,text
from sqlalchemy import update

# Netflix renders quickly enough, but finishes very slowly
from Spectralclustering import GetLaplacianCountries


def validateCountry(sp):
    n=1
    f1=8
    f2=1
    callStoredProcedure(sp)
    analysisNeural('Test11357', n, f1, f2)
    analysisNeural('Test4119', n, f1, f2)
    analysisNeural('Test45011', n, f1, f2)

    engine = create_engine(ENGINE_ADDRESS)
    Base.metadata.create_all(engine)
    session = Session(engine)
    vals = session.query(ValSet).all()
    for v in vals:
        session.add(
        ValResult(UserObjectId=v.userobjectid, Score=v.score, CreatedAt=datetime.now(), Layer0Neurons=n, F1=f1, F2=f2, Description = '{}'.format(sp)))
        print(f"user={v.userobjectid} score ={v.score}  cluster = {sp}")
    session.commit()
    session.close()

def validate():
    for i in range(1, 3):
        for j in range(1, 10):
            for k in range(1, 10):
                analysisNeural('Test11357', i, j, k)
                analysisNeural('Test4119', i, j, k)
                analysisNeural('Test45011', i, j, k)

                engine = create_engine(ENGINE_ADDRESS)
                Base.metadata.create_all(engine)
                session = Session(engine)
                vals = session.query(ValSet).all()
                for v in vals:
                    session.add(
                        ValResult(UserObjectId=v.userobjectid, Score=v.score, CreatedAt=datetime.now(), Layer0Neurons=i,
                                  F1=j, F2=k))
                    print(f"user={v.userobjectid} score ={v.score}  layerneurons ={i} F1 = {j} F2 = {k}")
                session.commit()
DRIVER_TIMEOUT = 15

ENGINE_ADDRESS= 'mysql://root:hu78to@127.0.0.1:3307/moviedborm'


validateCountry("Valyear8SPFeaturesDefWithTruncate")
validateCountry("Valyear7SPFeaturesDefWithTruncate")
validateCountry("Valyear6SPFeaturesDefWithTruncate")



