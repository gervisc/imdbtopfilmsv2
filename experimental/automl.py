import os

import numpy as np
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sklearn.decomposition import PCA
from scipy.sparse import csr_matrix
from Analysis import GetData, GetAandBone
import autosklearn.regression

from repository.DataModel import MovieFeatures, FeaturesDef


def getAllData(session,factorsGM,factorsGDB,n1):
    featursn = session.query(MovieFeatures).join(MovieFeatures.FeaturesDef).filter(FeaturesDef.Active == 1 ).order_by(
        MovieFeatures.MovieObjectId).all()
    m1 = len(set(node.MovieObjectId for node in featursn))

    movieIds = np.zeros(m1, dtype=int)
    j = -1
    kitem = 0
    # getfactor FeaturesM





    j = -1
    cori = []
    coci = []
    cova = []
    i = 0
    for f in featurs:
        if kitem != f.MovieObjectId:
            j += 1
            kitem = f.MovieObjectId
            movieIds[j] = f.MovieObjectId
        if factorsGM[f.FeatureObjectId] == -1:
            factorsGDB.append(f.FeatureObjectId)
            factorsGM[f.FeatureObjectId] = i
            cori.append(j)
            coci.append(i)
            cova.append(f.Factor)
            i += 1
        else:
            cori.append(j)
            coci.append(factorsGM[f.FeatureObjectId])
            cova.append(f.Factor)
    featursa = csr_matrix((cova, (cori, coci)), shape=(m1, n1))
    return featursa.toarray(), movieIds

if __name__ == "__main__":
    cstring = os.environ.get("MOVIEDB")
    engine = create_engine(cstring)
    session = Session(engine)
    IMDB_ID = "51273819"
    username = 'CSVImport' + IMDB_ID
    featurs,coeffs = GetData(session, username)

    # reduce features
    maxn = max( coeffs)
    factorsGDB,factorsGM,  featursM, n, ratingsM = GetAandBone(featurs, maxn)
    featursMR = featursM.toarray()
    input_dim=featursMR.shape[1]

    desired_variance_explained = 0.95  # You can choose any desired percentage
    pca = PCA(n_components=desired_variance_explained)
    reduced_matrix = pca.fit_transform(featursMR)
    FeaturesAll, movies = getAllData(session, factorsGM, factorsGDB, n)
    session.close()
    automl = autosklearn.classification.AutoSklearnClassifier(
        time_left_for_this_task=18000,
        #per_run_time_limit=2000,
        disable_evaluator_output=False
        #ensemble_size=16,
        #include={
        #    'regressor': ["random_forest","gradient_boosting"],
        #    'feature_preprocessor': ["no_preprocessing"]
        #},
        #resampling_strategy="cv",
        #resampling_strategy_arguments={"folds": 400},
    )
    automl.fit(featursMR, ratingsM, dataset_name="movies")
    automl.refit(featursMR, ratingsM)

    best_model = automl.show_models()

    # Access the performance of the best model
    performance = automl.cv_results_

    print("Best Model:")
    print(best_model)

    #print("Performance of the Best Model:")
    #print(performance)


    #reduced_featuresAll = pca.transform(FeaturesAll)
    predictions = automl.predict_proba(FeaturesAll)

    for prediction in predictions:
        formatted_predictions = [f"{prob:.6f}" for prob in prediction]
        print(formatted_predictions)

    losses_and_configurations = [
        (run_value.cost, run_key.config_id)
        for run_key, run_value in automl.automl_.runhistory_.data.items()
    ]
    losses_and_configurations.sort()
    print("Lowest loss:", losses_and_configurations[0][0])
    print(
        "Best configuration:",
        automl.automl_.runhistory_.ids_config[losses_and_configurations[0][1]],
    )