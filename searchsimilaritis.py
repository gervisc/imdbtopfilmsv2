import csv
from itertools import product

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from datetime import datetime
from DataModel import Base,FeaturesDef,levensteinresult
from OMDBapi import GetMovie
from sqlalchemy import and_
from difflib import SequenceMatcher
import multiprocessing
from joblib import Parallel, delayed
from tqdm import tqdm
import editdistance
import os


engine = create_engine('mysql://root:hu78to@127.0.0.1:3307/moviedborm?charset=utf8')



Base.metadata.create_all(engine)
session = Session(engine)
Feature = session.query(FeaturesDef).filter(FeaturesDef.ParentDescription =='Actors').all()
Feature2 = session.query(FeaturesDef).filter(FeaturesDef.ParentDescription =='Actors').all()


def levdist(k,Feature):
    for l in Feature:

        m = editdistance.distance(k.Description, l.Description)
        if 5 >= m > 0:
            return levensteinresult(featureobjectid1=k.ObjectId, score=m, featureobjectid2=l.ObjectId)


num_cores = multiprocessing.cpu_count()
inputs = tqdm(Feature)

processed_list = Parallel(n_jobs=100,prefer='threads')(delayed(levdist)(i,Feature2) for i in inputs)
for n in processed_list:
    if n is not None:
        session.add(n)


session.commit()