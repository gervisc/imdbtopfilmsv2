from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from datetime import datetime
import os
import csv
import time
from DataModel import Base, User, Movie, Rating, CustomList, Director, MovieRelated, Genre
from OMDBapi import GetMovie, GetDirectors, updateMovie
from sqlalchemy import and_
from scrapedeviation import getStdInfo,getrelatedItems
from selenium import webdriver
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium.common.exceptions import *
from undetected_chromedriver import  ChromeOptions
from selenium.webdriver import DesiredCapabilities
import undetected_chromedriver as uc

# Netflix renders quickly enough, but finishes very slowly
DRIVER_TIMEOUT = 45

ENGINE_ADDRESS= cstring = os.environ.get("MOVIEDB")


def isfloat(string):
    try:
        float(string)
        return True
    except ValueError:
        return False

def login_to_imdb(driver: webdriver.Firefox, username: str, password: str, logger):
    # As stated on global value, IMDB does something weird in login flow, so we need the 'pre-login' visit
    driver.get('https://www.imdb.com/registration/signin')
    login_button_elem = driver.find_element("link text",'Sign in with IMDb')
    login_button_elem.click()

    time.sleep(2)
    try:
        user_elem = driver.find_element('id','ap_email')
        user_elem.send_keys(username)
        time.sleep(1.5)
        pass_elem = driver.find_element('id','ap_password')
        pass_elem.send_keys(password)
        time.sleep(2)
        submit = driver.find_element('id','signInSubmit')
        driver.find_element('id','signInSubmit').send_keys(u'\ue007')
        time.sleep(30)
        content = driver.page_source

    except NoSuchElementException:
        logger.info("no ap_email")
    except Exception:
        raise

def get_driver(headful: bool = False) -> webdriver.chrome:
    # options = Options()
    #
    #
    # profile = FirefoxProfile("/home/gerbrand/.mozilla/firefox/18k4mtnf.default-esr")
    # profile.set_preference("browser.download.folderList", 2)
    # profile.set_preference("browser.download.manager.showWhenStarting", False)
    # profile.set_preference("browser.download.dir", os.getcwd())
    # profile.set_preference("browser.helperApps.neverAsk.saveToDisk", 'text/csv')
    # profile.set_preference("dom.webdriver.enabled", False)
    # profile.set_preference('useAutomationExtension', False)
    # profile.set_preference('devtools.jsonview.enabled', False)
    # desired = DesiredCapabilities.FIREFOX
    # profile.update_preferences()
    # Create ChromeOptions object
    chrome_options = ChromeOptions()

    # Add the --disable-features=UseANGLE flag
    chrome_options.add_argument('--disable-features=UseANGLE')

    # Use undetected_chromedriver.v2 to create the webdriver

    PROFILE = "/home/gerbrand/.config/google-chrome"
    driver = uc.Chrome(user_data_dir=PROFILE,headless=False,use_subprocess=False,Options=chrome_options)

    #driver = webdriver.Firefox(options=options, firefox_profile=profile, desired_capabilities=desired)
    #driver.set_page_load_timeout(DRIVER_TIMEOUT)
    #driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    return driver

def remove_history_file(filename):
    os.remove(filename)

def fetch_history(filename,url,driver: webdriver.Firefox,logger):
    if os.path.exists(filename):
        remove_history_file(filename)
    history_url = url
    # Download finishes quick, but somehow we never register an 'end',
    # so just set timeout and continue if file is there
    driver.set_page_load_timeout(DRIVER_TIMEOUT)
    try:
        driver.get(history_url)
        content = driver.page_source
    except TimeoutException:
        logger.info("time out")
        if not os.path.exists(filename):
            raise
    except Exception:
        raise
    time.sleep(3)

def getUser(session,IMDB_ID):

    username = 'CSVImport' + IMDB_ID
    ruser = session.query(User).filter(User.UserName == username).first()
    if ruser == None:
        ruser = User(UserName=username, CreatedAt=datetime.now(), UpdateAt=datetime.now())
        session.add(ruser)
    return ruser

def importratings(email,password,IMDB_ID,logger,driver):
    #lees csv in
    engine = create_engine(ENGINE_ADDRESS)

    #Base.metadata.create_all(engine)
    session = Session(engine)


    #login_to_imdb(driver, email ,password)
    url = 'https://www.imdb.com/user/ur{}/ratings/export'.format(IMDB_ID)
    logger.info(url)
    fetch_history('/home/gerbrand/Downloads/ratings.csv', url, driver,logger)

    with open('/home/gerbrand/Downloads/ratings.csv','r') as f:
        movies = list(csv.reader(f,delimiter= ','))
        movies.pop(0)
        ruser = getUser(session,IMDB_ID)
        currentratings= session.query(Rating).filter(Rating.UserObjectId == ruser.ObjectId).all()
        refreshed =0
        for m in movies:
            ImdbID = m[0][2:len(m[0])]
            numvotes = m[10]
            imdbrating = m[6]
            genres = m[9].split(', ') if m[9] else []
            directors = m[12]
            rmovie = session.query(Movie).filter(Movie.ObjectId == ImdbID).first()
            if rmovie is not None and refreshed == 0 and rmovie.UpdateAt <   datetime.strptime("2021-09-16",'%Y-%m-%d'):
                rmovie =updateMovie(rmovie,ImdbID,session,logger)
                refreshed = 1
            if  rmovie == None:
               logger.info("nieuwe film")
               try:
                    #omdb api
                    rmovie = GetMovie(ImdbID,session,logger)

               except Exception as e:
                    logger.exception(f"mislukt {ImdbID}")
            if rmovie is None:
                    logger.info(f"niet gevonden {id}", ImdbID)


            if rmovie != None:
                if not session.query(Genre).filter(Genre.MovieObjectId == ImdbID).count() == len(genres):
                    session.query(Genre).filter(Genre.MovieObjectId == ImdbID).delete()
                    for genre in genres:
                        rmovie.genres.append(Genre(Description=genre))
                    rmovie.UpdateAt = datetime.now()
                if session.query(Director).filter(Director.MovieObjectId == ImdbID).count()==0:
                    ndirectors = GetDirectors(ImdbID, rmovie, directors, session,logger)
                    for a in ndirectors:
                        session.add(a)
                if numvotes.isdigit():
                    rmovie.NumVotes = numvotes
                if isfloat(imdbrating):
                    rmovie.IMDBRating  =imdbrating
                if(session.query(MovieRelated).filter(MovieRelated.movieobjectid1==ImdbID).count()==0):
                    relatedIds = getrelatedItems(ImdbID,logger)
                    for id in relatedIds:
                        rmovie.RelatedMovies.append(MovieRelated(movieobjectid2=int(id)))
                    logger.info("added "+str(len(relatedIds)) +" relatedids")
                session.flush()
                session.commit()

            #add std info
            if(rmovie.NumVotes1 is None and rmovie.NumVotes > 1 ):
                numberslist, arithmeticvalue, std = getStdInfo(ImdbID,logger)
                if (numberslist is not None):
                    logger.info("get table std")
                    rmovie.NumVotes1 = numberslist[0]
                    rmovie.NumVotes2 = numberslist[1]
                    rmovie.NumVotes3 = numberslist[2]
                    rmovie.NumVotes4 = numberslist[3]
                    rmovie.NumVotes5 = numberslist[4]
                    rmovie.NumVotes6 = numberslist[5]
                    rmovie.NumVotes7 = numberslist[6]
                    rmovie.NumVotes8 = numberslist[7]
                    rmovie.NumVotes9 = numberslist[8]
                    rmovie.NumVotes10 = numberslist[9]
                    rmovie.IMDBRatingArithmeticMean = arithmeticvalue
                    rmovie.Std= std
                    time.sleep(0.5)
                    rmovie.UpdateAt = datetime.now()



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
            logger.info(f"verwijderd {i.MovieObjectId}")
        session.commit()
    session.close()

def getList(listname,listdescription,logger,driver):
    url = 'https://www.imdb.com/list/{}/export'.format(listname)
    fetch_history('/home/gerbrand/Downloads/' +listdescription + '.csv', url, driver,logger)

def importList(listname,save: bool,IMDB_ID,listdescription,logger):
    engine = create_engine(ENGINE_ADDRESS)
    #Base.metadata.create_all(engine)
    session = Session(engine)

    ruser = getUser(session, IMDB_ID)
    if save == True and ruser != None:
        session.query(CustomList).filter(and_(CustomList.User == ruser, CustomList.ObjectId == listname)).delete()

    with open('/home/gerbrand/Downloads/' +listdescription+'.csv','r',encoding="utf8") as f:
        movies = list(csv.reader(f,delimiter= ','))
        #remove title row
        movies.pop(0)
        refreshed =0
        stdrefreshed =0
        for m in movies:
            ImdbID = m[1][2:len(m[1])]
            numvotes = m[12]
            imdbrating = m[8]
            directors = m[14]
            genres = m[11].split(', ') if m[11] else []
            rmovie = session.query(Movie).filter(Movie.ObjectId == ImdbID).first()
            if rmovie is not None and refreshed == 0 and rmovie.UpdateAt <  datetime.strptime("2021-09-16",'%Y-%m-%d'):
                rmovie =updateMovie(rmovie,ImdbID,session,logger)
                refreshed = 1
            if rmovie == None:
                try:
                    rmovie = GetMovie(ImdbID,session,logger)
                except Exception as e:
                    logger.info(e)
                    logger.exception(f"mislukt {ImdbID}")
                if rmovie is None:
                    logger.info(f"niet gevonden {ImdbID}")

            if rmovie != None:
                if not session.query(Genre).filter(Genre.MovieObjectId == ImdbID).count() == len(genres):
                    session.query(Genre).filter(Genre.MovieObjectId == ImdbID).delete()
                    for genre in genres:
                        rmovie.genres.append(Genre(Description=genre))
                    rmovie.UpdateAt = datetime.now()
                if session.query(Director).filter(Director.MovieObjectId == ImdbID).count()==0:
                    ndirectors = GetDirectors(ImdbID, rmovie, directors, session,logger)
                    for a in ndirectors:
                        session.add(a)
                if numvotes.isdigit():
                    rmovie.NumVotes = numvotes
                if isfloat(imdbrating):
                    rmovie.IMDBRating  =imdbrating
                session.flush()
                session.commit()

            #add std info
            if(rmovie!= None and rmovie.NumVotes1 is None and rmovie.NumVotes > 1 and stdrefreshed < 200 ):
                numberslist, arithmeticvalue, std = getStdInfo(ImdbID,logger)
                if(numberslist!=None):
                    rmovie.NumVotes1 = numberslist[0]
                    rmovie.NumVotes2 = numberslist[1]
                    rmovie.NumVotes3 = numberslist[2]
                    rmovie.NumVotes4 = numberslist[3]
                    rmovie.NumVotes5 = numberslist[4]
                    rmovie.NumVotes6 = numberslist[5]
                    rmovie.NumVotes7 = numberslist[6]
                    rmovie.NumVotes8 = numberslist[7]
                    rmovie.NumVotes9 = numberslist[8]
                    rmovie.NumVotes10 = numberslist[9]
                    rmovie.IMDBRatingArithmeticMean = arithmeticvalue
                    rmovie.Std= std
                    time.sleep(0.5)
                    rmovie.UpdateAt = datetime.now()
                    stdrefreshed = stdrefreshed+1




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
    #results = list(cursor.fetchall())
    cursor.close()
    connection.commit()




