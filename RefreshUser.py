from IMDBUserImportCSV import importratings,importList,callStoredProcedure
from Analysis import analysisNeural
from Spectralclustering import GetLaplacianCountries,GetLaplacianDirectors,GetLaplacianActors

IMDB_ID ="51273819"
importratings("gvisscher@gmail.com", "plakkaas10",IMDB_ID)
importList('ls058067398',False,IMDB_ID,"watchlist")
#importList('ls095479606',True,IMDB_ID,"filmhuisfilms gouda")
#importList('ls093865788',True,IMDB_ID,"netflix series")

#callStoredProcedure("SPFeaturesDefWithTruncate")
#callStoredProcedure("SP_CountryFeatures")

callStoredProcedure("SPUpdateFeatures")

username = 'CSVImport'+IMDB_ID
analysisNeural(username,2,0.0002)

#GetLaplacianDirectorsMinimalCut(25,4119)

