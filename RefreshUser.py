import datetime

from sqlalchemy import create_engine

from Service.importWatchListScraper import importWatchListScraper, UpdateMyMovies
from repository.DataModel import Expected, Expected_Serie, RatedLastYear
from sqlalchemy.orm import Session
import os
import csv
import logging
from IMDBUserImportCSV import importratings, importList, callStoredProcedure, getList, get_driver
from Analysis import analysisNeural
import dropbox

from repository.MovieRepository import GetIsRunning, SetIsRunning

logger = logging.getLogger()

# Set the log level for the logger
logger.setLevel(logging.DEBUG)

# Create a formatter for the log messages
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Create a file handler
current_date = datetime.datetime.now().strftime('%Y-%m-%d')
log_filename = f'log_{current_date}.log'
file_handler = logging.FileHandler(log_filename)
file_handler.setLevel(logging.DEBUG)  # Set the log level for the file handler
file_handler.setFormatter(formatter)  # Apply the formatter to the file handler

# Create a console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)  # Set the log level for the console handler
console_handler.setFormatter(formatter)  # Apply the formatter to the console handler

# Add both handlers to the logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)
try:
    if(GetIsRunning()):
        logger.info("already running")
        exit(1)
    SetIsRunning(True)
    cstring = os.environ.get("MOVIEDB")
    engine = create_engine(cstring)
    #driver = get_driver()

    #Base.metadata.create_all(engine)
    session = Session(engine)
    skip = False

    userimdb ="51273819"
    if not skip:
        #userimdb = os.environ.get("USERIMDB")
        #passwordimdb = os.environ.get("PASSWORDIMDB")
        #logger.info("1: importeren ratings")
        #importratings(userimdb, passwordimdb,IMDB_ID,logger,driver)
        #logger.info("2a: ophalen list")
        #getList('ls058067398',"WATCHLIST",logger,driver)
        #logger.info("2: importen watchlist")
        importWatchListScraper(userimdb, logger)
        UpdateMyMovies(logger)



        #importList('ls058067398',False,IMDB_ID,"WATCHLIST",logger)
        # # # # ##
        logger.info("4: aanmaken features")
        callStoredProcedure("SPUpdateFeatures")
        logger.info("4a: countries")
        callStoredProcedure("updatecountry")
        logger.info("4b: updateactorfeatures")
        callStoredProcedure("updateactorfeatures")
        logger.info("4c: updatedirectorfeatures")
        callStoredProcedure("updatedirectorfeatures")
        #  #
    #driver.quit()
    username = 'CSVImport'+userimdb
        # # #

        # #
    logger.info("5: neural network regressie")
    analysisNeural(username,3,logger,session,0.01,0.0001)
    delimiter_type=';'
    dropboxkey = os.environ.get("DROPBOXKEY")
    dropboxappkey = os.environ.get("DROPBOXAPPKEY")
    dropboxsecretkey = os.environ.get("DROPBOXAPPSECRET")
    dropboxrefreshtoken = os.environ.get("DROPBOXREFRESHTOKEN")
    dbx = dropbox.Dropbox(  app_key = dropboxappkey,  app_secret = dropboxsecretkey, oauth2_refresh_token=dropboxrefreshtoken )



    logger.info("6: top 1000 films weg schrijven")
    outfile = open(os.path.join('/home/gerbrand/Downloads','filmlijst.csv'),'w', newline='')
    outcsv = csv.writer(outfile,delimiter =';')
    #
    #
    records = session.query(Expected).all()
    outcsv.writerow([column.name for column in Expected.__mapper__.columns])
    [outcsv.writerow([getattr(curr,column.name) for column in Expected.__mapper__.columns]) for curr in records]
    outfile.close()
    with open(os.path.join('/home/gerbrand/Downloads','filmlijst.csv'), 'rb') as f:
        dbx.files_upload(f.read(), '/filmlijst.csv', mode=dropbox.files.WriteMode('overwrite'))

    logger.info("7: top 1000 series wegschrijven")
    outfile = open(os.path.join('/home/gerbrand/Downloads','serielijst.csv'),'w', newline='')
    outcsv = csv.writer(outfile,delimiter =';')

    records = session.query(Expected_Serie).all()
    outcsv.writerow([column.name for column in Expected_Serie.__mapper__.columns])
    [outcsv.writerow([getattr(curr,column.name) for column in Expected_Serie.__mapper__.columns]) for curr in records]
    outfile.close()
    with open(os.path.join('/home/gerbrand/Downloads','serielijst.csv'), 'rb') as f:
        dbx.files_upload(f.read(), '/serielijst.csv', mode=dropbox.files.WriteMode('overwrite'))

    logger.info("8: last year rated wegschrijven")
    outfile = open(os.path.join('/home/gerbrand/Downloads','ratedlastyear.csv'),'w', newline='')
    outcsv = csv.writer(outfile,delimiter =';')


    records = session.query(RatedLastYear).all()
    outcsv.writerow([column.name for column in RatedLastYear.__mapper__.columns])
    [outcsv.writerow([getattr(curr,column.name) for column in RatedLastYear.__mapper__.columns]) for curr in records]
    outfile.close()
    with open(os.path.join('/home/gerbrand/Downloads','ratedlastyear.csv'), 'rb') as f:
        dbx.files_upload(f.read(), '/ratedlastyear.csv', mode=dropbox.files.WriteMode('overwrite'))
    session.close()
    SetIsRunning(False)
except Exception as e:
    logger.exception("Exception occurred")
    SetIsRunning(False)



