import csv
from itertools import product

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from datetime import datetime
from DataModel import Base,FeaturesDef,Levensteinresult
from OMDBapi import GetMovie
from sqlalchemy import and_
from difflib import SequenceMatcher
import multiprocessing
from joblib import Parallel, delayed
from tqdm import tqdm

import os
from Levenshtein import distance


def levdist(word1,word2):
    m = distance(word1,word2, score_cutoff=4)
    if 3 >= m > 0:
        print(f"{word1} ,{word2}")
        return Levensteinresult(Name1=word1, Name2=word2, Score=m)



engine = create_engine('mysql://root:hu78to@127.0.0.1:3307/moviedborm?charset=utf8')



Base.metadata.create_all(engine)
session = Session(engine)
Feature = session.query(FeaturesDef.Description).filter(FeaturesDef.ParentDescription =='actors').all()
print("fetched")


l=0
for f in Feature:

    o=0
    for g in Feature:
        if (o>l):
            n =levdist(f._data[0],g._data[0])
            if n is not None:
                session.add(n)
                session.commit()
        o=o+1

    if(l%1000==0):
        print(l)
    l=l+1





#print("parallel")
#num_cores = multiprocessing.cpu_count()
#inputs = tqdm(wordcombos)

#processed_list = Parallel(n_jobs=10000,prefer='threads')(delayed(levdist)(i) for i in inputs)
#for n in processed_list:
#    if n is not None:
#        session.add(n)


#session.commit()