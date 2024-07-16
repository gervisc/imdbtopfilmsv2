from bs4 import BeautifulSoup
import requests
import json
import re
import math


def getrelatedItems(imdbId, logger):
    headers = {
        "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.82 Safari/537.36'
    }

    url = 'https://www.imdb.com/title/tt' + imdbId
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
                logger.info("no related items for " + imdbId)
    else:
        logger.info("no related items for " + imdbId)

    genres = []
    countries=[]
    titletype=''
    contentrating=''
    script_tag = soup.find('script', id='__NEXT_DATA__')

    if script_tag:
        # Extract the content inside the script tag
        script_content = script_tag.string

        # Load the content as JSON
        try:
            data = json.loads(script_content)

            # Navigate to access the genres data
            genres_data = data['props']['pageProps']['aboveTheFoldData']['genres']['genres']

            # Extract and print genres
            genres = [genre['text'] for genre in genres_data]
            print("Genres:", genres)

        except json.JSONDecodeError as e:
            print("Error parsing JSON:", e)
        except KeyError as e:
            print("KeyError:", e)

        try:
            data = json.loads(script_content)

            # Navigate to access the countries data
            countries_data = data['props']['pageProps']['mainColumnData']['countriesOfOrigin']['countries']

            # Extract and print country names
            countries = [country['text'] for country in countries_data]
            print("Countries of Origin:", countries)

        except json.JSONDecodeError as e:
            print("Error parsing JSON:", e)
        except KeyError as e:
            print("KeyError:", e)
        try:
            script_tag_info = soup.find('script', type='application/ld+json')
            data = json.loads(script_tag_info.string)

            titletype = data['@type']
            contentrating = data['contentRating']
        except json.JSONDecodeError as e:
            print("Error parsing JSON:", e)
        except KeyError as e:
            print("KeyError:", e)
    else:
        print("Script tag with id '__NEXT_DATA__' not found")
    return relatedlist,genres,countries,titletype,contentrating


def getStdInfo(imdbId, logger):
    try:
        # Downloading imdb top 250 movie's data
        url = 'https://www.imdb.com/title/tt' + imdbId + '/ratings/?ref_=tt_ov_rt'
        headers = {
            "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.82 Safari/537.36',
        }
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'lxml')
        tables = soup.find_all('script', id="__NEXT_DATA__")
        if (len(tables) < 1):
            logger.info("empty table std")
            return None, None, None,[],[]
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
            logger.info("total 0 std")
            return None, None, None,[],[]
        avg = avg / total

        i = 1
        std = 0
        for x in numberslist:
            std = std + x * (i - avg) ** 2
            i = 1 + i
        std = math.sqrt(std / total)
        return numberslist, avg, std, countryCodes, countryVotes,countryStd
    except Exception as e:
        # Handle any exception and print the error message
        print(f"An error occurred: {e}")
        return None, None, None,[],[]