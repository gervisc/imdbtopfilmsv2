from sqlalchemy import Column, Integer, String, ForeignKey, Date, Float, Table, DateTime, Text,Double
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Constant(Base):
    __tablename__ = 'constant'
    Description = Column(String(255),primary_key=True)
    Value = Column(Float,nullable=False)


class ValResult(Base):
    __tablename__ = 'valresult'
    ObjectId = Column(Integer, primary_key=True, autoincrement=True)
    UserObjectId = Column(ForeignKey('user.ObjectId'),nullable=False)
    Score = Column(Float,nullable=False)
    CreatedAt = Column(DateTime, nullable=False)
    Layer0Neurons = Column(Integer,nullable=True)
    F1 = Column(Integer,nullable=True)
    F2 = Column(Integer,nullable=True)
    Description = Column(String(255), nullable=False)

class MovieFeatures(Base):
    __tablename__ = 'moviefeaturematrix'
    MovieObjectId = Column(ForeignKey('movie.ObjectId'),primary_key=True)
    Factor = Column(Float,nullable=False)
    FeatureObjectId = Column(ForeignKey('feature.ObjectId'), primary_key=True)
    FeaturesDef =  relationship("FeaturesDef",back_populates='moviefeatures')
    Movie = relationship("Movie", back_populates="moviefeatures")

class CustomList(Base):
    __tablename__ = 'CustomList'
    ObjectId = Column(String(255),primary_key=True)
    Description = Column(String(255),nullable=False)
    MovieObjectId = Column(ForeignKey('movie.ObjectId'),primary_key=True,nullable=False)
    UserObjectId = Column(ForeignKey('user.ObjectId'),primary_key=True,nullable=False)
    Movie = relationship("Movie", back_populates="Lists")
    User = relationship("User", back_populates="Lists")
    UpdatedAt = Column(DateTime, nullable=False)

class Country(Base):
    __tablename__ = 'country'
    ObjectId = Column(Integer, primary_key=True, autoincrement=True)
    Description = Column(String(255), nullable=False)
    FeatureObjectId = Column(ForeignKey('feature.ObjectId'), primary_key=True)
    FeaturesDef = relationship("FeaturesDef", back_populates='countries')
    countrys = relationship("MovieCountry", back_populates='Country')

class FeaturesDef(Base):
    __tablename__ = 'feature'
    ObjectId = Column(Integer,primary_key=True,autoincrement=True)
    Description =  Column(String(255), nullable=False)
    ParentDescription = Column(String(255), nullable=False)
    Active = Column(Integer,nullable=False)
    moviefeatures = relationship("MovieFeatures", back_populates='FeaturesDef')
    countries = relationship("Country", back_populates='FeaturesDef')
    #CorActors1 =relationship("CorrelationActor",back_populates='Feature1',foreign_keys='CorrelationActor.featureobjectid1')
    #CorActors2 = relationship("CorrelationActor", back_populates='Feature2',foreign_keys='CorrelationActor.featureobjectid2')

class FeaturesCoeffs(Base):
    __tablename__ = 'featurecoefficient'
    FeatureObjectId = Column(Integer, primary_key=True)
    Value = Column(Double,nullable=False)
    UserObjectId = Column(ForeignKey('user.ObjectId'),primary_key=True)
    ColumnId = Column(Integer,primary_key=True)
    Bias = Column(Integer,primary_key=True)
    Layer = Column(Integer,primary_key=True)
    User = relationship("User", back_populates="coeffs")

class User(Base):
    __tablename__ = 'user'
    ObjectId = Column(Integer,primary_key=True)
    UserName = Column(String(255), unique= True,nullable=False)
    CreatedAt = Column(DateTime,nullable=False)
    UpdateAt = Column(DateTime,nullable=False)
    ratings = relationship("Rating", back_populates="User")
    coeffs = relationship("FeaturesCoeffs", back_populates="User")
    Lists = relationship("CustomList", back_populates="User")

class ParentRating(Base):
    __tablename__ = 'parentrating'
    ObjectId = Column(String(255),primary_key=True)
    Score = Column(Integer,nullable=True)
    movies = relationship("Movie",back_populates="ParentRatingScore")


class Rating(Base):
    __tablename__ = 'rating'
    UserObjectId= Column(ForeignKey('user.ObjectId'),primary_key=True)
    MovieObjectId = Column(ForeignKey('movie.ObjectId'), primary_key=True)
    Rating = Column(Float,nullable=False)
    CreatedAt = Column(DateTime,nullable=False)
    UpdatedAt = Column(DateTime, nullable=False)
    Movie = relationship("Movie", back_populates="ratings")
    User = relationship("User",back_populates="ratings")

class Movie(Base):
    __tablename__ = 'movie'
    ObjectId = Column(Integer, primary_key=True)
    CreatedAt = Column(DateTime,nullable=False)
    UpdateAt = Column(DateTime,nullable=False)
    Title = Column(String(255),nullable=False)
    IMDBRating = Column(Float,nullable=False)
    Runtime = Column(Integer,nullable=False)
    Year = Column(Integer,nullable=False)
    NumVotes = Column(Integer,nullable=False)
    TitleType = Column(String(255),nullable=False)
    ParentRating = Column(ForeignKey('parentrating.ObjectId'),nullable=False)
    actors = relationship("Actor",back_populates="Movie")
    #topactors = relationship("TopActor", back_populates="Movie")
    #topdirectors = relationship("TopDirector", back_populates="Movie")
    MovieCountrys = relationship("MovieCountry", back_populates="Movie")
    directors = relationship("Director", back_populates="Movie")
    genres = relationship("Genre", back_populates="Movie")
    ratings = relationship("Rating",back_populates="Movie")
    NumVotes1 = Column(Integer, nullable=True)
    NumVotes2 = Column(Integer, nullable=True)
    NumVotes3 = Column(Integer, nullable=True)
    NumVotes4 = Column(Integer, nullable=True)
    NumVotes5 = Column(Integer, nullable=True)
    NumVotes6 = Column(Integer, nullable=True)
    NumVotes7 = Column(Integer, nullable=True)
    NumVotes8 = Column(Integer, nullable=True)
    NumVotes9 = Column(Integer, nullable=True)
    NumVotes10 = Column(Integer, nullable=True)
    IMDBRatingArithmeticMean = Column(Float, nullable=True)
    Std = Column(Float, nullable=True)
    ParentRatingScore= relationship("ParentRating",back_populates="movies")
    RelatedMovies = relationship("MovieRelated", back_populates="Movie")
    moviefeatures= relationship("MovieFeatures",back_populates="Movie")
    Lists = relationship("CustomList", back_populates="Movie")
    #HighScores = relationship("HighScores",back_populates="Movie")


class Actor(Base):
    __tablename__ = 'movieactor'
    MovieObjectId = Column(ForeignKey('movie.ObjectId'),primary_key=True)
    FeatureObjectId = Column(ForeignKey('feature.ObjectId'),primary_key=True)
    Movie = relationship("Movie",back_populates="actors")

class MovieCountry(Base):
    __tablename__ = 'moviecountry'
    MovieObjectId = Column(ForeignKey('movie.ObjectId'),primary_key=True)
    CountryObjectId = Column(ForeignKey('country.ObjectId'), primary_key=True)
    Movie = relationship("Movie",back_populates="MovieCountrys")
    Country = relationship("Country", back_populates="countrys")

class Director(Base):
    __tablename__ = 'moviedirector'
    MovieObjectId = Column(ForeignKey('movie.ObjectId'),primary_key=True)
    FeatureObjectId = Column(ForeignKey('feature.ObjectId'),primary_key=True)
    Movie = relationship("Movie",back_populates="directors")

class Genre(Base):
    __tablename__ = 'moviegenre'
    MovieObjectId = Column(ForeignKey('movie.ObjectId'),primary_key=True)
    Description = Column(String(255),primary_key=True)
    Movie = relationship("Movie",back_populates="genres")

class ValSet(Base):
    __tablename__ = 'valset'
    score = Column(Float, nullable= False)
    userobjectid = Column(ForeignKey('user.ObjectId'),primary_key=True)

class Levensteinresult(Base):
    __tablename__ = 'levensteinresult'
    Name1 = Column(String(255),primary_key=True)
    Name2 = Column(String(255),primary_key=True)
    Score = Column(Integer, nullable=False)

class MovieRelated(Base):
    __tablename__ = 'movierelated'
    movieobjectid1 = Column(ForeignKey('movie.ObjectId'),primary_key=True)
    movieobjectid2 = Column(Integer,primary_key=True)
    Movie = relationship("Movie", back_populates="RelatedMovies")


class RatedLastYear(Base):
    __tablename__ = 'rated_lastyear'
    title = Column(String(255))
    rated = Column(String(62))
    Year = Column(Integer)
    TitleType = Column(String(255))
    Runtime = Column(Integer)
    imdbrating = Column(Float)
    numvotes = Column(Integer)
    countries = Column(Text)
    directors = Column(Text)
    ratedat = Column(DateTime)
    genres = Column(Text)
    actors = Column(Text)
    parentrating = Column(String(255))
    TitleType = Column(String(255))
    Runtime = Column(Integer)
    objectid = Column(Integer, primary_key=True)


class Expected(Base):
     __tablename__ = 'expected'
     title =  Column(String(255))
     expected = Column(String(62))
     Year = Column(Integer)
     TitleType = Column(String(255))
     Runtime = Column(Integer)
     imdbrating = Column(Float)
     numvotes = Column(Integer)
     countries = Column(Text)
     directors = Column(Text)
     ratedat = Column(DateTime)
     genres = Column(Text)
     actors = Column(Text)

     parentrating = Column(String(255))
     TitleType = Column(String(255))
     Runtime = Column(Integer)
     objectid = Column(Integer, primary_key=True)
     CreatedAt = Column(DateTime)
     updateat = Column(DateTime)

class Expected_Serie(Base):
     __tablename__ = 'expected_serie'
     title =  Column(String(255))
     expected = Column(String(62))
     Year = Column(Integer)
     TitleType = Column(String(255))
     Runtime = Column(Integer)
     imdbrating = Column(Float)
     numvotes = Column(Integer)
     parentrating =Column(String(255))
     directors = Column(Text)
     ratedat = Column(DateTime)
     genres = Column(Text)
     actors = Column(Text)
     countries = Column(Text)
     objectid = Column(Integer, primary_key=True)
     CreatedAt = Column(DateTime)
     updateat = Column(DateTime)




class Expected_documentary(Base):
    __tablename__ = 'expected_documentary'
    title = Column(String(255))
    expected = Column(String(62))
    Year = Column(Integer)
    TitleType = Column(String(255))
    Runtime = Column(Integer)
    imdbrating = Column(Float)
    numvotes = Column(Integer)
    parentrating = Column(String(255))
    directors = Column(Text)
    ratedat = Column(DateTime)
    genres = Column(Text)
    actors = Column(Text)
    countries = Column(Text)
    objectid = Column(Integer, primary_key=True)
    CreatedAt = Column(DateTime)
    updateat = Column(DateTime)

