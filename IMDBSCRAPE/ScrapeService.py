import json
import math
import traceback

import requests
from bs4 import BeautifulSoup

from IMDBSCRAPE.ImdbScrapeMovie import Movied
from IMDBSCRAPE.repositorymovie import RepositoryMovie


def importList(url,logger):

    headers = {
        "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.82 Safari/537.36',
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'lxml')

    list_items = soup.find_all('li', class_='ipc-metadata-list-summary-item')
    watchMovies= []
    for li in list_items:
        movie_url = li.find('a', class_='ipc-lockup-overlay ipc-focusable')['href']
        movie_id = movie_url.split('/')[2][2:]
        watchMovies.append(movie_id)
        # try:
        #     movie_name = li.find('h3', class_='ipc-title__text').get_text().split('. ', 1)[1]
        #     yearitem = li.find('span', class_='sc-b189961a-8 kLaxqf dli-title-metadata-item')
        #     if (yearitem is None):
        #         print(f"{movie_name} is without year")
        #         continue
        #     year = yearitem.get_text()[:4]
        #     rating_element = li.find('span',
        #                              class_='ipc-rating-star ipc-rating-star--base ipc-rating-star--imdb ratingGroup--imdb-rating')
        #     rating = rating_element.get_text().strip() if rating_element is not None else None
        #
        #     num_ratings = rating_element.find('span', class_='ipc-rating-star--voteCount').get_text().strip().strip(
        #         '()') if rating_element is not None else 0
        #     rating_value = rating.split('\xa0')[0] if rating is not None else None # 5.7 part
        #     user_rating_element = li.find('span',class_='ipc-rating-star ipc-rating-star--base ipc-rating-star--currentUser')
        #     user_rating = user_rating_element.get_text().strip() if user_rating_element is not None else None
        #     # Extract the director
        #     director = [a.get_text() for a in li.find_all('a', class_='ipc-link ipc-link--base dli-director-item')]
        #
        #     # Extract the stars
        #     stars = [a.get_text() for a in li.find_all('a', class_='ipc-link ipc-link--base dli-cast-item')]
        #
        #     # Store the extracted information in a dictionary
        #     movie_info = Movied(movie_id= movie_id,movie_name= movie_name,year= year,num_ratings= num_ratings,rating_value= rating_value,director= director,stars= stars,user_rating= user_rating)
        #
        #     watchMovies.append(movie_info)
        # except Exception as e:
        #     print(f"failed to interpret movie {movie_id} {e}")
        #     traceback.print_exc()
    return watchMovies

def getmovie(imdbId,logger):
    movie = getrelatedItems(imdbId, logger)
    numberslist, avg, std, countryCodes, countryVotes, countryStd, votes = getStdInfo(imdbId, logger)
    example_movie = RepositoryMovie(
        id=imdbId,
        title_type=movie.titletype,
        content_rating=movie.contentrating,
        countries=movie.countries,
        genres=movie.genres,
        related_movies=movie.related_movies,
        name=movie.movie_name,
        year=movie.year,
        votes=movie.num_ratings,
        runtime=0,
        actors=movie.stars,
        rating_distribution=numberslist,
        arithmetic_value=avg,
        std=std,
        country_std=countryStd,
        country_votes=countryVotes,
        country_codes=countryCodes,
        imdb_rating=movie.rating_value,
        directors=movie.director,
    )
    return example_movie

def getrelatedItems(imdbId, logger):
    headers = {
        "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.82 Safari/537.36'
    }
    imdbId_str=str(int(imdbId)).zfill(7)
    url = 'https://www.imdb.com/title/tt' + imdbId_str
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'lxml')
    relatedlist = []
    interestedsection = soup.find(attrs={"data-testid": "MoreLikeThis"})
    if (interestedsection != None):
        divsect = interestedsection.select('div[class*="ipc-shoveler ipc-shoveler--base ipc-shoveler--page0"]')
        if (divsect != None):
            interested = interestedsection.find_all('a', 'ipc-lockup-overlay ipc-focusable')
            if (interested != None):
                for link in interested:
                    id = link.get('href')
                    relatedlist.append((id[9:id.find('/?')]))
            else:
                if logger is not None:
                    logger.info("no related items for " + imdbId_str)
                else:
                    print("no related items for " + imdbId_str)
    else:
        if logger is not None:
            logger.info("no related items for " + imdbId_str)
        else:
            print("no related items for " + imdbId_str)

    script_tag = soup.find('script', id='__NEXT_DATA__')
    script_content = script_tag.string

    data = json.loads(script_content)

    # Navigate to access the genres data
    genres_data = data['props']['pageProps']['aboveTheFoldData']['genres']['genres']

    # Extract and print genres
    chip_list_div = soup.find('div', class_='ipc-chip-list__scroller')

    # Then, find all the span elements with class 'ipc-chip__text' within this div
    genres = [span.text for span in chip_list_div.find_all('span', class_='ipc-chip__text')]

    #print("Genres:", genres)

    # Navigate to access the countries data
    countries_data = data['props']['pageProps']['mainColumnData']['countriesOfOrigin']['countries']
    title = data['props']['pageProps']['aboveTheFoldData']['originalTitleText']['text']
    year = data['props']['pageProps']['aboveTheFoldData']['releaseYear']['year']
    votes = data['props']['pageProps']['aboveTheFoldData']['ratingsSummary']['voteCount']
    imdbRating = data['props']['pageProps']['aboveTheFoldData']['ratingsSummary']['aggregateRating']
    directors =  [director['credits'][0]['name']['nameText']['text'] for director in  data['props']['pageProps']['mainColumnData']['directors']]
    actors =  set([edge['node']['name']['nameText']['text'] for edge in data['props']['pageProps']['mainColumnData']['cast']['edges']])
    # Extract and print country names
    countries = [country['text'] for country in countries_data]
    #print("Countries of Origin:", countries)

    script_tag_info = soup.find('script', type='application/ld+json')
    data = json.loads(script_tag_info.string)

    titletype = data['@type']
    contentrating =  data.get('contentRating', None)
    movie_info = Movied(movie_id=imdbId, movie_name=title, year=year, num_ratings=votes,
                        rating_value=imdbRating, director=directors, stars=actors,related_movies= relatedlist,genres=genres,countries=countries,titletype=titletype,contentrating=contentrating)

    return movie_info


def getStdInfo(imdbId, logger):
    imdbId_str = str(int(imdbId)).zfill(7)
    url = 'https://www.imdb.com/title/tt' + imdbId_str + '/ratings/?ref_=tt_ov_rt'
    headers = {
        "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.82 Safari/537.36',
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'lxml')
    tables = soup.find_all('script', id="__NEXT_DATA__")
    if (len(tables) < 1):
        logger.info("empty table std")
        return [],  None, None,[],[], None,0
    table = tables[0].string
    json_data = json.loads(table)
    histogramdata = json_data["props"]["pageProps"]["contentData"]["histogramData"]
    numberslist = []
    for x in histogramdata["histogramValues"]:
        numberslist.append(float(x["voteCount"]))

    countryVotes = []
    countryCodes = []
    sum=0
    n=0
    countryStd=0
    for x in histogramdata["countryData"]:
        countryVotes.append(float(x["totalVoteCount"]))
        countryCodes.append(x["countryCode"])
        n=n+1
        sum= sum+float(x["aggregateRating"])
    if(n>0):
        avg=sum/n
        for x in histogramdata["countryData"]:
            countryStd=countryStd+abs(float(x["aggregateRating"])-avg)

    i = 1
    avg = 0
    total = 0
    for x in numberslist:
        avg = avg + i * x
        total = total + x
        i = i + 1
    if total == 0:
        if logger is not None:
            logger.info("total 0 std")
        else:
            print("total 0 std")
        return [],  None, None,[],[], None,0
    avg = avg / total

    i = 1
    std = 0
    for x in numberslist:
        std = std + x * (i - avg) ** 2
        i = 1 + i
    std = math.sqrt(std / total)
    return numberslist, avg, std, countryCodes, countryVotes,countryStd,total
