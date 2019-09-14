from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium.common.exceptions import *
from selenium.webdriver.firefox.options import Options
import os
import csv
from DataModel import Base,User, Movie,Rating,ParentRating,UserFeatures,FeaturesCoeffs
from OMDBapi import GetMovie
from sqlalchemy import text
import numpy as np
import scipy
from scipy import sparse
from scipy.sparse import linalg

username = 'CSVImport51273819'
engine = create_engine('mysql://root:hu78to@127.0.0.1:3306/moviedborm?charset=utf8')
Base.metadata.create_all(engine)
session = Session(engine)

#r1 = session.execute(text("CAll features()"))
#print("r1")
#r2  = session.execute(text("CALL SPUserfeatures(:p1)"),{'p1' : username})
#print("r2")
featurs = session.query(UserFeatures).all()
print(len(featurs))
n= len(featurs[0].UserFeatures.split(', '))
featursM = np.zeros((len(featurs),n-2))
ratingsM = np.zeros(len(featurs),dtype=float)
j=0
for f in featurs:
    x=f.UserFeatures.split(', ')
    for i in range(1,n-1):
        featursM[j,i-1]=x[i]
    ratingsM[j]=x[n-1]
    j+=1

#remove empty columns
# ons = np.eye((n-2))
# print(ons.shape)
# ndel = 0 #number of columns deleted
# for i in range(0,n-2):
#     chk = 0 #column all zeross
#     for j in range(0,len(featurs)):
#         if featursM[j,i] != 0:
#             chk=1
#             break
#     if chk ==0:
#         print("ja")
#         ons = np.delete(ons,i-ndel,1)
#         ndel+=1
# print(featursM.shape)
# print(ons.shape)
#featursM= featursM.dot(ons)

c=scipy.sparse.linalg.lsqr(featursM,ratingsM)

userdb = session.query(User).filter(User.UserName == username).first()
session.query(FeaturesCoeffs).filter(FeaturesCoeffs.UserObjectId == userdb.ObjectId).delete()
k=1
for ceff in c[0]:
    session.add(FeaturesCoeffs(Col=k,Value=ceff,User=userdb))
    print(ceff)
    k+=1
session.commit()

