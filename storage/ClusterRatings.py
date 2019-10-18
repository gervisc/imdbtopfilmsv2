from DataModel import Country,Actor,Director, Movie,Genre,Rating



def CostFunction(MovieList: [Movie], RatingList: [Rating] ):
    mobjectids = [value.Objectid for value in MovieList]
    userobjectids = []
    nratings = 0
    for r in RatingList:
        if r.MovieObjectId in mobjectids:
            nratings+=1
            if r.UserObjectId not in userobjectids:
                userobjectids.append(r.UserObjectId)
    return nratings/len(userobjectids)



