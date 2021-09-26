from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium.common.exceptions import *
from selenium.webdriver.firefox.options import Options
import os
import csv
import time
from DataModel import Base, User, Movie, Rating, ParentRating, CustomList, FeaturesDef, Director
from OMDBapi import GetMovie, GetDirectors, updateMovie
from sqlalchemy import and_,text
from sqlalchemy import update
import numpy as np


# Netflix renders quickly enough, but finishes very slowly
DRIVER_TIMEOUT = 6

ENGINE_ADDRESS= 'mysql://root:hu78to@127.0.0.1:3307/moviedborm'


def isfloat(string):
    try:
        float(string)
        return True
    except ValueError:
        return False

def login_to_imdb(driver: webdriver.Firefox, username: str, password: str):
    # As stated on global value, IMDB does something weird in login flow, so we need the 'pre-login' visit
    driver.get('https://www.imdb.com/registration/signin')
    login_button_elem = driver.find_element_by_partial_link_text('Sign in with IMDb')
    login_button_elem.click()

    time.sleep(2)
    user_elem = driver.find_element_by_id('ap_email')
    user_elem.send_keys(username)
    time.sleep(1.5)
    pass_elem = driver.find_element_by_id('ap_password')
    pass_elem.send_keys(password)
    time.sleep(1.5)
    submit = driver.find_element_by_id('signInSubmit')
    driver.find_element_by_id('signInSubmit').send_keys(u'\ue007')
    time.sleep(2)

def get_driver(headful: bool = False) -> webdriver.Firefox:
    options = Options()
    if not headful:
        options.headless = True
    profile = FirefoxProfile()
    profile.set_preference("browser.download.folderList", 2)
    profile.set_preference("browser.download.manager.showWhenStarting", False)
    profile.set_preference("browser.download.dir", os.getcwd())
    profile.set_preference("browser.helperApps.neverAsk.saveToDisk", 'text/csv')
    driver = webdriver.Firefox(firefox_options=options, firefox_profile=profile)
    driver.set_page_load_timeout(DRIVER_TIMEOUT)
    return driver

def remove_history_file(filename):
    os.remove(filename)

def fetch_history(filename,url,driver: webdriver.Firefox):
    if os.path.exists(filename):
        remove_history_file(filename)
    history_url = url
    # Download finishes quick, but somehow we never register an 'end',
    # so just set timeout and continue if file is there
    driver.set_page_load_timeout(DRIVER_TIMEOUT)
    try:
        driver.get(history_url)
    except TimeoutException:
        print("time out")
        if not os.path.exists(filename):
            raise


def getUser(session,IMDB_ID):

    username = 'CSVImport' + IMDB_ID
    ruser = session.query(User).filter(User.UserName == username).first()
    if ruser == None:
        ruser = User(UserName=username, CreatedAt=datetime.now(), UpdateAt=datetime.now())
        session.add(ruser)
    return ruser

def importratings(email,password,IMDB_ID):
    #lees csv in
    engine = create_engine(ENGINE_ADDRESS)

    Base.metadata.create_all(engine)
    session = Session(engine)
    driver = get_driver()

    login_to_imdb(driver, email ,password)
    url = 'https://imdb.com/user/ur{}/ratings/export'.format(IMDB_ID)

    fetch_history('ratings.csv', url, driver)

    with open('ratings.csv','r') as f:
        movies = list(csv.reader(f,delimiter= ','))
        movies.pop(0)
        ruser = getUser(session,IMDB_ID)
        currentratings= session.query(Rating).filter(Rating.UserObjectId == ruser.ObjectId).all()
        refreshed =0
        for m in movies:
            ImdbID = m[0][2:len(m[0])]
            numvotes = m[10]
            imdbrating = m[6]
            directors = m[12]
            rmovie = session.query(Movie).filter(Movie.ObjectId == ImdbID).first()
            if rmovie is not None and refreshed == 0 and rmovie.UpdateAt <   datetime.strptime("2021-09-16",'%Y-%m-%d'):
                rmovie =updateMovie(rmovie,ImdbID,session)
                refreshed = 1
            if  rmovie == None:
               print("nieuwe film")
               try:
                    #omdb api
                    rmovie = GetMovie(ImdbID,session)
               except:
                    print(f"mislukt {ImdbID}")
            if rmovie is None:
                    print(f"niet gevonden {id}", ImdbID)


            if rmovie != None:
                #if session.query(Director).filter(Director.MovieObjectId == ImdbID).count()==0:
                #    ndirectors = GetDirectors(ImdbID, rmovie, directors, session)
                #    for a in ndirectors:
                #        session.add(a)
                if numvotes.isdigit():
                    rmovie.NumVotes = numvotes
                if isfloat(imdbrating):
                    rmovie.IMDBRating  =imdbrating

                session.flush()
                session.commit()

            #wijzigen of nieuwe beoordeling aanmaken
            if rmovie != None:
                rrating = session.query(Rating).filter(and_(Rating.MovieObjectId == rmovie.ObjectId , Rating.UserObjectId == ruser.ObjectId)).first()
            if rrating == None:
                rrating = Rating(Rating=float(m[1]), User=ruser, Movie=rmovie,UpdatedAt=datetime.strptime(m[2],'%Y-%m-%d'),CreatedAt =datetime.strptime(m[2],'%Y-%m-%d'))
                session.add(rrating)
            else:
                currentratings.remove(rrating)
                rrating.Rating = float(m[1])
                rrating.UpdatedAt=datetime.strptime(m[2],'%Y-%m-%d')
            session.flush()
            session.commit()

        for i in currentratings:
            session.query(Rating).filter(and_(Rating.UserObjectId==i.UserObjectId,Rating.MovieObjectId== i.MovieObjectId)).delete()
            print(f"verwijderd {i.MovieObjectId}")
        session.commit()
    session.close()

def getList(listname,listdescription):
    url = 'https://www.imdb.com/list/{}/export'.format(listname)
    driver = get_driver()
    fetch_history(listdescription + '.csv', url, driver)

def importList(listname,save: bool,IMDB_ID,listdescription):
    engine = create_engine(ENGINE_ADDRESS)
    Base.metadata.create_all(engine)
    session = Session(engine)

    ruser = getUser(session, IMDB_ID)
    if save == True and ruser != None:
        session.query(CustomList).filter(and_(CustomList.User == ruser, CustomList.ObjectId == listname)).delete()

    with open(listdescription+'.csv','r') as f:
        movies = list(csv.reader(f,delimiter= ','))
        #remove title row
        movies.pop(0)
        refreshed = 0
        for m in movies:
            ImdbID = m[1][2:len(m[1])]
            numvotes = m[12]
            imdbrating = m[8]
            directors = m[14]
            rmovie = session.query(Movie).filter(Movie.ObjectId == ImdbID).first()
            if rmovie is not None and refreshed == 0 and rmovie.UpdateAt <  datetime.strptime("2021-09-16",'%Y-%m-%d'):
                rmovie =updateMovie(rmovie,ImdbID,session)
                refreshed = 1
            if rmovie == None:
                #try:
                rmovie = GetMovie(ImdbID,session)
                #except:
                #   print(f"mislukt {ImdbID}")
                if rmovie is None:
                    print(f"niet gevonden {id}", ImdbID)

            if rmovie != None:
               # if session.query(Director).filter(Director.MovieObjectId == ImdbID).count()==0:
               #     ndirectors = GetDirectors(ImdbID, rmovie, directors, session)
               #     for a in ndirectors:
               #         session.add(a)
                if numvotes.isdigit():
                    rmovie.NumVotes = numvotes
                if isfloat(imdbrating):
                    rmovie.IMDBRating  =imdbrating
                session.flush()
                session.commit()


            if save == True and rmovie != None and ruser != None:
                session.add(CustomList(UpdatedAt=datetime.now(),ObjectId=listname, Description=listdescription, User=ruser, Movie=rmovie))
            session.commit();

    session.commit()
    session.close()

def callStoredProcedure(sp):
    engine = create_engine(ENGINE_ADDRESS)
    connection = engine.raw_connection()
    cursor = connection.cursor()
    cursor.callproc(sp)
    results = list(cursor.fetchall())
    cursor.close()
    connection.commit()




