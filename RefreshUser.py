from sqlalchemy import create_engine, sql
from DataModel import Base, Expected, Expected_Serie
from sqlalchemy.orm import Session
import os
import csv

from IMDBUserImportCSV import importratings,importList,callStoredProcedure
from Analysis import analysisNeural
from Spectralclustering import GetLaplacianCountries,GetLaplacianDirectors,GetLaplacianActors

IMDB_ID ="51273819"
importratings("gvisscher@gmail.com", "plakkaas10",IMDB_ID)
importList('ls058067398',False,IMDB_ID,"watchlist")

#importList('ls095479606',True,IMDB_ID,"filmhuisfilms gouda")
#importList('ls093865788',True,IMDB_ID,"netflix series")

#callStoredProcedure("SPFeaturesDefWithTruncate")
#callStoredProcedure("SP_CountryFeatures")

callStoredProcedure("SPUpdateFeatures")

username = 'CSVImport'+IMDB_ID
analysisNeural(username,2,0.000)

delimiter_type=';'
engine = create_engine('mysql://root:hu78to@127.0.0.1:3307/moviedborm?charset=utf8')
Base.metadata.create_all(engine)
session = Session(engine)
outfile = open(os.path.join('C:/Users/Gerbrand/Dropbox/excels','filmlijst.csv'),'w', newline='')
outcsv = csv.writer(outfile,delimiter =';')
records = session.query(Expected).all()
outcsv.writerow([column.name for column in Expected.__mapper__.columns])
[outcsv.writerow([getattr(curr,column.name) for column in Expected.__mapper__.columns]) for curr in records]
outfile.close()
outfile = open(os.path.join('C:/Users/Gerbrand/Dropbox/excels','serielijst.csv'),'w', newline='')
outcsv = csv.writer(outfile,delimiter =';')
records = session.query(Expected_Serie).all()
outcsv.writerow([column.name for column in Expected_Serie.__mapper__.columns])
[outcsv.writerow([getattr(curr,column.name) for column in Expected_Serie.__mapper__.columns]) for curr in records]
outfile.close()
session.close()

