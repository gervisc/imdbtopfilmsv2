import unicodedata
from datetime import datetime

from bs4 import BeautifulSoup
import requests
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from DataModel import Base, User, Movie, Rating, CustomList, Director, MovieRelated, Genre, FeaturesDef, ParentRating, \
    MovieCountry, Actor
from OMDBapi import GetMovie, GetDirectors, updateMovie, GetCountry
import os

from scrapedeviation import getrelatedItems

ENGINE_ADDRESS=  os.environ.get("MOVIEDB")

def isfloat(string):
    try:
        float(string)
        return True
    except ValueError:
        return False

def importList(IMDB_ID,logger):
    engine = create_engine(ENGINE_ADDRESS)

    session = Session(engine)
    url = f"https://www.imdb.com/user/ur{IMDB_ID}/watchlist/?sort=date_added%2Cdesc"
    headers = {
        "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.82 Safari/537.36',
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'lxml')

    list_items = soup.find_all('li', class_='ipc-metadata-list-summary-item')

    for li in list_items:
        movie_url = li.find('a', class_='ipc-lockup-overlay ipc-focusable')['href']
        movie_id = movie_url.split('/')[2][2:]

        movie_name = li.find('h3', class_='ipc-title__text').get_text().split('. ', 1)[1]
        yearitem = li.find('span', class_='sc-b189961a-8 kLaxqf dli-title-metadata-item')
        if (yearitem is None):
            print(f"{movie_name} is without year")
            continue
        year = yearitem.get_text()
        rating_element = li.find('span',
                                 class_='ipc-rating-star ipc-rating-star--base ipc-rating-star--imdb ratingGroup--imdb-rating')
        rating = rating_element.get_text().strip()
        num_ratings = rating_element.find('span', class_='ipc-rating-star--voteCount').get_text().strip().strip(
            '()')
        rating_value = rating.split('\xa0')[0]  # 5.7 part

        # Extract the director
        director = ''
        directoritem = li.find('a', class_='ipc-link ipc-link--base dli-director-item')
        if (directoritem is not None):
            director = directoritem.get_text()

        # Extract the stars
        stars = [a.get_text() for a in li.find_all('a', class_='ipc-link ipc-link--base dli-cast-item')]

        # Store the extracted information in a dictionary
        movie_info = {
            'Movie ID': movie_id,
            'Movie Name': movie_name,
            'Year': year,
            'Number of Ratings': num_ratings,
            'Rating': rating_value,
            'Director': director,
            'Stars': stars
        }

        rmovie = session.query(Movie).filter(Movie.ObjectId == movie_id).first()
        if rmovie is None:
            try:
                rmovie = Movie(ObjectId=movie_id, CreatedAt=datetime.now())
                relatedlist, genres, countries,titletype,contentrating= getrelatedItems(movie_id, logger)
                rmovie.TitleType= titletype
                rmovie.ParentRating=contentrating
                rprating = session.query(ParentRating).filter(ParentRating.ObjectId == rmovie.ParentRating).first()
                if rprating is None:
                    session.add(ParentRating(ObjectId=rmovie.ParentRating))
                for c in countries:
                    ccountry = GetCountry(c, session)
                    rmovie.MovieCountrys.append(MovieCountry(CountryObjectId=ccountry.ObjectId))
                for genre in genres:
                    rmovie.genres.append(Genre(Description=genre))
                for relatedid in relatedlist:
                    rmovie.RelatedMovies.append(MovieRelated(movieobjectid2=int(relatedid)))
                session.add(rmovie)
                session.flush()
                session.commit()
            except Exception as e:
                logger.info(e)
                logger.exception(f"mislukt {movie_id}")
            if rmovie is None:
                logger.info(f"niet gevonden {movie_id}")

        if rmovie is None:
            continue

        rmovie.title = movie_name
        rmovie.UpdateAt=datetime.now()
        rmovie.year = year
        if num_ratings.isdigit():
            rmovie.NumVotes = num_ratings
        else:
            rmovie.NumVotes=0
        if isfloat(rating_value):
            rmovie.IMDBRating  =rating_value
        else:
            rmovie.IMDBRating= 7.4
        rmovie.Runtime=0
        session.query(Actor).filter(Actor.MovieObjectId == movie_id).delete()
        actors = session.query(FeaturesDef).filter(FeaturesDef.ParentDescription == 'Actors').all()
        actors_dict = {f.Description.lower(): f for f in actors}
        for row in stars:
            row = unicodedata.normalize('NFKD', row).encode("ascii", "ignore").decode("ascii", "ignore").lower()
            nactor = None

            if next((x for x in rmovie.actors if x.Description.lower() == row), None) == None:
                for f in actors:
                    if f.Description.lower() == row:
                        nactor = Actor(MovieObjectId=imdbId, FeatureObjectId=f.ObjectId)
                        break
                    if f.Description.lower().replace(" ", "").replace("-", "").replace(".", "") == row.replace(" ",
                                                                                                               "").replace(
                            "-", "").replace(".", ""):
                        nactor = Actor(MovieObjectId=imdbId, FeatureObjectId=f.ObjectId)
                        f.Description = row.lower()
                        break
                if nactor is None:
                    session.add(FeaturesDef(Description=row.lower(), ParentDescription='Actors', Active=0))
                    fid = session.query(FeaturesDef).filter(and_(FeaturesDef.ParentDescription == 'Actors',
                                                                 FeaturesDef.Description == row)).first().ObjectId
                    logger.info(fid)
                    nactor = Actor(MovieObjectId=imdbId, FeatureObjectId=fid)
                nactors.append(nactor)

            session.flush()
            session.commit()

        #add std info
        if(rmovie!= None and rmovie.ratingCountry1Votes is None and rmovie.NumVotes > 1 and stdrefreshed < 200 ):
            numberslist, arithmeticvalue, std , countrycodes, countryvotes,countryStd= getStdInfo(ImdbID,logger)
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
            rmovie.ratingCountryStd=countryStd
            totalcountryvotes=0
            for vote in countryvotes:
                totalcountryvotes=totalcountryvotes+vote
            l=0
            for vote in countryvotes:
                code=session.query(FeaturesDef).filter(and_(FeaturesDef.Description == countrycodes[l],FeaturesDef.ParentDescription=="countrycodevote")).first()
                if(code is None):
                    code=FeaturesDef(Description=countrycodes[l],ParentDescription="countrycodevote",Active=0)
                    session.add(code)
                    session.flush()
                    session.commit()
                if(l==0):
                    rmovie.ratingCountry1Votes=vote/totalcountryvotes
                    rmovie.ratingCountry1=code.ObjectId
                if(l==1):
                    rmovie.ratingCountry2Votes=vote/totalcountryvotes
                    rmovie.ratingCountry2=code.ObjectId
                if(l==2):
                    rmovie.ratingCountry3Votes=vote/totalcountryvotes
                    rmovie.ratingCountry3=code.ObjectId
                if(l==3):
                    rmovie.ratingCountry4Votes=vote/totalcountryvotes
                    rmovie.ratingCountry4=code.ObjectId
                if(l==4):
                    rmovie.ratingCountry5Votes=vote/totalcountryvotes
                    rmovie.ratingCountry5=code.ObjectId
                l=l+1
            time.sleep(0.5)
            rmovie.UpdateAt = datetime.now()





        if save == True and rmovie != None and ruser != None:
            session.add(CustomList(UpdatedAt=datetime.now(),ObjectId=listname, Description=listdescription, User=ruser, Movie=rmovie))
        session.commit()

    session.commit()
    session.close()