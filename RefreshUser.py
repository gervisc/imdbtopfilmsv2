from IMDBUserImportCSV import importratings,importList,callStoredProcedure
from Analysis import analysisLinear,analysisNeural
from Spectralclustering import GetLaplacianCountries

IMDB_ID ="51273819"
importratings("gvisscher@gmail.com", "plakkaas10",IMDB_ID)
importList('ls058067398',False,IMDB_ID,"watchlist")
#importList('ls095479606',True,IMDB_ID,"filmhuisfilms gouda")

#callStoredProcedure("SPFeaturesDefWithTruncate")
#GetLaplacianCountries(5)
#callStoredProcedure("SPUpdateFeatures")

username = 'CSVImport'+IMDB_ID
analysisNeural(username,1,8,1)


