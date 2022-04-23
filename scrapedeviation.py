from bs4 import BeautifulSoup
import requests
import re
import math





def getStdInfo(imdbId):
    # Downloading imdb top 250 movie's data
    url = 'https://www.imdb.com/title/tt'+imdbId+'/ratings/?ref_=tt_ov_rt'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'lxml')
    tables = soup.find_all('table')
    table = tables[0]
    numbers = table.find_all('div', class_='leftAligned')
    numbers.pop(0)
    numberslist = []
    for x in numbers:
        numberslist.append(float(x.text.replace(',', '')))
    i = 10
    avg = 0
    total = 0
    for x in numberslist:
        avg = avg + i * x
        total = total + x
        i -= 1
    avg = avg / total
    i = 10
    std = 0
    for x in numberslist:
        std = std + x * (i - avg) ** 2
        i -= 1
    std = math.sqrt(std / total)
    return numberslist , avg ,std