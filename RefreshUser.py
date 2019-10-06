from IMDBUserImportCSV import importratings,importList,updatedeffeautures
from Analysis import analysis

IMDB_ID ="51273819"
#importratings("gvisscher@gmail.com", "plakkaas10",IMDB_ID)
#importList('ls058067398',False,IMDB_ID,"watchlist")
importList('ls095479606',True,IMDB_ID,"filmhuisfilms gouda")
#updatedeffeautures()
username = 'CSVImport'+IMDB_ID
analysis(username)