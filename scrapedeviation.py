from bs4 import BeautifulSoup
import requests
import json
import re
import math

def getrelatedItems(imdbId):
    headers = {
        "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.82 Safari/537.36'
    }

    url = 'https://www.imdb.com/title/tt' + imdbId
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'lxml')
    relatedlist = []
    interestedsection = soup.find(attrs={"data-testid":"MoreLikeThis"})
    if(interestedsection !=None):
        divsect=interestedsection.select('div[class*="ipc-shoveler ipc-shoveler--base ipc-shoveler--page0"]')
        if (divsect !=None):
            interested = interestedsection.find_all('a', 'ipc-lockup-overlay ipc-focusable')
            if (interested != None):
                for link in interested:
                    id = link.get('href')
                    relatedlist.append((id[9:id.find('/?')]))
            else:
                print("no related items for "+imdbId)
    else:
        print("no related items for "+imdbId)

    return relatedlist




def getStdInfo(imdbId):
    # Downloading imdb top 250 movie's data
    url = 'https://www.imdb.com/title/tt'+imdbId+'/ratings/?ref_=tt_ov_rt'
    headers = {
        "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.82 Safari/537.36',
    }
    response = requests.get(url,headers =headers)
    soup = BeautifulSoup(response.text, 'lxml')
    tables = soup.find_all('script', id="__NEXT_DATA__")
    if (len(tables) < 1):
        print("empty table std")
        return None, None, None
    table = tables[0].string
    json_data = json.loads(table)
    histogramdata = json_data["props"]["pageProps"]["contentData"]["histogramData"]
    avgn = histogramdata["aggregateRating"]
    numberslist = []
    for x in histogramdata["histogramValues"]:
        numberslist.append(float(x["voteCount"]))



    i = 1
    avg = 0
    total = 0
    for x in numberslist:
        avg = avg + i * x
        total = total + x
        i =i+ 1
    if total ==0:
        print("total 0 std")
        return None, None, None
    avg = avg / total

    i = 1
    std = 0
    for x in numberslist:
        std = std + x * (i - avg) ** 2
        i = 1+i
    std = math.sqrt(std / total)
    return numberslist , avg ,std