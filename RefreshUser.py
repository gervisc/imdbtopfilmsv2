from IMDBUserImportCSV import importratings,importList,updatedeffeautures
from Analysis import analysisLinear,analysisNeural

IMDB_ID ="51273819"
#importratings("gvisscher@gmail.com", "plakkaas10",IMDB_ID)
#importList('ls058067398',False,IMDB_ID,"watchlist")
#importList('ls095479606',True,IMDB_ID,"filmhuisfilms gouda")
#updatedeffeautures()
username = 'CSVImport'+IMDB_ID
analysisNeural('Test11357',1,1,1)
#analysisNeural('Test4119')
#analysisNeural('Test45011')
#analysisNeural(username)