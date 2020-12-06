from Analysis import analysisNeural
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from datetime import datetime
from DataModel import Base, ValResult,ValSet


# Netflix renders quickly enough, but finishes very slowly


def validateCountry(n,l2,seed):

    f1=8
    f2=1



    #analysisNeural('Test11357', n, f1, f2,l2,seed)
    analysisNeural('Test4119', n, f1, f2,l2,seed)
    #analysisNeural('Test45011', n, f1, f2,l2,seed)

    engine = create_engine(ENGINE_ADDRESS)
    Base.metadata.create_all(engine)
    session = Session(engine)
    vals = session.query(ValSet).all()
    for v in vals:
        session.add(
        ValResult(UserObjectId=v.userobjectid, Score=v.score, CreatedAt=datetime.now(), Layer0Neurons=n, F1=f1, F2=f2, Description = 'l2 {}'.format(l2)+'seed: {}'.format(seed)))
        print(f"user={v.userobjectid} score ={v.score}  l2 = {l2}")
    session.commit()
    session.close()


def validate():
    for i in range(2, 5):
        for j in range(1, 10):
            for k in range(1, 10):
                analysisNeural('Test11357', i, j, k)
                analysisNeural('Test4119', i, j, k)
                analysisNeural('Test45011', i, j, k)

                engine = create_engine(ENGINE_ADDRESS)
                Base.metadata.create_all(engine)
                session = Session(engine)
                vals = session.query(ValSet).all()
                for v in vals:
                    session.add(
                        ValResult(UserObjectId=v.userobjectid, Score=v.score, CreatedAt=datetime.now(), Layer0Neurons=i,
                                  F1=j, F2=k))
                    print(f"user={v.userobjectid} score ={v.score}  layerneurons ={i} F1 = {j} F2 = {k}")
                session.commit()
DRIVER_TIMEOUT = 15

ENGINE_ADDRESS= 'mysql://root:hu78to@127.0.0.1:3307/moviedborm'

#for i  in range (2,6):
    #for j in range(2, 6):
        #for K in range(2, 6):
            #validateCountry(i,j,K)
#callStoredProcedure("SPFeaturesDefWithTruncate")
#GetLaplacianActors(10)
#GetLaplacianDirectors(10)
#GetLaplacianCountries(5)




#callStoredProcedure("SPUpdateFeatures")
validateCountry(2,0.001,12)
validateCountry(2,0.001,11)
validateCountry(2,0.001,71)
validateCountry(2,0.002,12)
validateCountry(2,0.002,11)
validateCountry(2,0.002,71)
validateCountry(2,0.0005,12)
validateCountry(2,0.0005,11)
validateCountry(2,0.0005,71)
validateCountry(3,0.001,12)
validateCountry(3,0.001,11)
validateCountry(3,0.001,71)
validateCountry(3,0.002,12)
validateCountry(3,0.002,11)
validateCountry(3,0.002,71)
validateCountry(3,0.0005,12)
validateCountry(3,0.0005,11)
validateCountry(3,0.0005,71)
#callStoredProcedure("SPFeaturesDefWithTruncate")
#GetLaplacianCountries(5)
#callStoredProcedure("SPUpdateFeatures")



