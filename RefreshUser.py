from sqlalchemy import create_engine, sql
from DataModel import Base, Expected, Expected_Serie
from sqlalchemy.orm import Session
import os
import csv

from IMDBUserImportCSV import importratings,importList,callStoredProcedure
from Analysis import analysisNeural


IMDB_ID ="51273819"

print("1: importeren ratings")
importratings("gvisscher@gmail.com", "plakkaas10",IMDB_ID)
print("2: importen watchlist")
importList('ls058067398',False,IMDB_ID,"watchlist")
print("3: bijwerken clusters")
callStoredProcedure("updateclusters")
print("4: aanmaken features")
callStoredProcedure("SPUpdateFeatures")

engine = create_engine('mysql://root:hu78to@127.0.0.1:3307/moviedborm?charset=utf8')
Base.metadata.create_all(engine)
session = Session(engine)
username = 'CSVImport'+IMDB_ID

print("5: neural network regressie")
analysisNeural(username,2,session,0.000)

delimiter_type=';'
outfile = open(os.path.join('C:/Users/Gerbrand/Dropbox/excels','filmlijst.csv'),'w', newline='')
outcsv = csv.writer(outfile,delimiter =';')

print("6: top 1000 films weg schrijven")
records = session.query(Expected).all()
outcsv.writerow([column.name for column in Expected.__mapper__.columns])
[outcsv.writerow([getattr(curr,column.name) for column in Expected.__mapper__.columns]) for curr in records]
outfile.close()
outfile = open(os.path.join('C:/Users/Gerbrand/Dropbox/excels','serielijst.csv'),'w', newline='')
outcsv = csv.writer(outfile,delimiter =';')

print("7: top 1000 series wegschrijven")
records = session.query(Expected_Serie).all()
outcsv.writerow([column.name for column in Expected_Serie.__mapper__.columns])
[outcsv.writerow([getattr(curr,column.name) for column in Expected_Serie.__mapper__.columns]) for curr in records]
outfile.close()
session.close()

