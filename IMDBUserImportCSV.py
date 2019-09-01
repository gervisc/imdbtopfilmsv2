from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium.common.exceptions import *
from selenium.webdriver.firefox.options import Options
import os
import csv
from DataModel import Base,User, Movie,Rating,ParentRating
from OMDBapi import GetMovie

# Netflix renders quickly enough, but finishes very slowly
DRIVER_TIMEOUT = 15
IMDB_ID ="51273819"

engine = create_engine('mysql://root:hu78to@127.0.0.1:3306/moviedborm')

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
    user_elem = driver.find_element_by_id('ap_email')
    user_elem.send_keys(username)
    pass_elem = driver.find_element_by_id('ap_password')
    pass_elem.send_keys(password)
    submit = driver.find_element_by_id('signInSubmit')
    submit.click()

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
    print('Removing ratings file')
    os.remove(filename)

def fetch_history(filename,url,driver: webdriver.Firefox):
    if os.path.exists(filename):
        remove_history_file(filename)
    history_url = url
    print(history_url)
    # Download finishes quick, but somehow we never register an 'end',
    # so just set timeout and continue if file is there
    driver.set_page_load_timeout(5)
    try:
        driver.get(history_url)
    except TimeoutException:
        if not os.path.exists(filename):
            raise
    driver.set_page_load_timeout(DRIVER_TIMEOUT)

Base.metadata.create_all(engine)
session = Session(engine)

IMovies = []
#lees csv in


driver = get_driver()
login_to_imdb(driver, "gvisscher@gmail.com", "plakkaas10")
url = 'https://imdb.com/user/ur{}/ratings/export'.format(IMDB_ID)
fetch_history('ratings.csv', url, driver)
with open('ratings.csv','r') as f:
    movies = list(csv.reader(f,delimiter= ','))
    movies.pop(0)
    for m in movies:
        ImdbID = m[0][2:len(m[0])]
        rmovie = session.query(Movie).filter(Movie.ObjectId == ImdbID).first()
        if  rmovie == None:
            rmovie = GetMovie(ImdbID)
            if rmovie != None:
                rprating = session.query(ParentRating).filter(ParentRating.ObjectId == rmovie.ParentRating).first()
                if rprating == None:
                    session.add(ParentRating(ObjectId=rmovie.ParentRating))
                session.add(rmovie)
                session.flush()
                print(rmovie.Title)
                session.commit()
                username = 'CSVImport' + IMDB_ID
                ruser = session.query(User).filter(User.UserName == username).first()
                if ruser == None:
                    ruser = User(UserName=username , CreatedAt=datetime.now(), UpdateAt=datetime.now())
                    session.add(ruser)
                rrating = session.query(Rating).filter(
                    Rating.MovieObjectId == rmovie.ObjectId and Rating.UserObjectId == User.ObjectId).first()
                if rrating == None:
                    rrating = Rating(Rating=float(m[1]), User=ruser, Movie=rmovie)
                    session.add(rrating)
                session.flush()


url = 'https://www.imdb.com/list/ls058067398/export'
fetch_history('watchlist.csv', url, driver)
with open('watchlist.csv','r') as f:
    movies = list(csv.reader(f,delimiter= ','))
    #remove title row
    movies.pop(0)
    for m in movies:
        ImdbID = m[1][2:len(m[1])]
        rmovie = session.query(Movie).filter(Movie.ObjectId == ImdbID).first()
        if rmovie == None:
            rmovie = GetMovie(ImdbID)
            if rmovie != None:
                rprating = session.query(ParentRating).filter(ParentRating.ObjectId == rmovie.ParentRating).first()
                if rprating == None:
                    session.add(ParentRating(ObjectId=rmovie.ParentRating))
                session.add(rmovie)
                session.flush()
                print(rmovie.Title)
                session.commit()




session.close()







#     for n, movie in enumerate(movies):
#         k = 0
#         for om in omdbmovies:
#             if om[positionkey] == movie[positionkey]:
#                 movies[n] = om
#                 k = 1
#         if k == 1:
#             continue
#         resp = omdbget(movie[positionkey])
#         item = resp.json()
#         if item["Response"] == "True":
#             country = item["Country"]
#             actors = item["Actors"]
#             rated = item["Rated"]
#             wins = 0
#             nominations = 0
#             # awards
#             awards = item["Awards"]
#             winindex = awards.find("win")
#             if (winindex > 0):
#                 if (awards[max(winindex - 5, 0)] == " "):
#                     wins = int(awards[max(winindex - 4, 0):winindex])
#                 else:
#                     wins = int(awards[max(winindex - 3, 0):winindex])
#             nominationindex = awards.find("nomination")
#             if (nominationindex > 0):
#                 if (awards[max(nominationindex - 5, 0)] == " ") and (awards[max(nominationindex - 3, 0)] != " "):
#                     nominations = int(awards[max(nominationindex - 4, 0):nominationindex])
#                 else:
#                     nominations = int(awards[max(nominationindex - 3, 0):nominationindex])
#
#             movie.append(country)
#             movie.append(actors)
#             movie.append(rated.lower())
#             movie.append(wins)
#             movie.append(nominations)
#             movies[n] = movie
#             writer.writerow(movie)
#         else:
#             movie.append("Unknown")
#             movie.append("")
#             movie.append("Not Rated".lower())
#             movie.append(0)
#             movie.append(0)
#             movies[n] = movie
# return movies
