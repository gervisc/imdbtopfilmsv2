from sqlalchemy import Column, Integer, String, ForeignKey, Date, Float, Table, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class UserFeatures(Base):
   __tablename__ = 'agmuserfeatures'
   UserFeatures = Column(String(2000),primary_key=True, nullable=False)

class FeaturesCoeffs(Base):
    __tablename__ = 'featurescoeffs'
    Col = Column(Integer,primary_key=True)
    Value = Column(Float,nullable=False)
    UserObjectId = Column(ForeignKey('user.ObjectId'),primary_key=True)
    User = relationship("User", back_populates="coeffs")

class User(Base):
    __tablename__ = 'user'
    ObjectId = Column(Integer,primary_key=True)
    UserName = Column(String(255), unique= True,nullable=False)
    CreatedAt = Column(DateTime,nullable=False)
    UpdateAt = Column(DateTime,nullable=False)
    ratings = relationship("Rating", back_populates="User")
    coeffs = relationship("FeaturesCoeffs", back_populates="User")

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
    countrys = relationship("Country", back_populates="Movie")
    directors = relationship("Director", back_populates="Movie")
    genres = relationship("Genre", back_populates="Movie")
    ratings = relationship("Rating",back_populates="Movie")
    ParentRatingScore= relationship("ParentRating",back_populates="movies")

class Actor(Base):
    __tablename__ = 'actor'
    MovieObjectId = Column(ForeignKey('movie.ObjectId'),primary_key=True)
    Description = Column(String(255),primary_key=True)
    Movie = relationship("Movie",back_populates="actors")

class Country(Base):
    __tablename__ = 'country'
    MovieObjectId = Column(ForeignKey('movie.ObjectId'),primary_key=True)
    Description = Column(String(255),primary_key=True)
    Movie = relationship("Movie",back_populates="countrys")

class Director(Base):
    __tablename__ = 'director'
    MovieObjectId = Column(ForeignKey('movie.ObjectId'),primary_key=True)
    Description = Column(String(255),primary_key=True)
    Movie = relationship("Movie",back_populates="directors")

class Genre(Base):
    __tablename__ = 'genre'
    MovieObjectId = Column(ForeignKey('movie.ObjectId'),primary_key=True)
    Description = Column(String(255),primary_key=True)
    Movie = relationship("Movie",back_populates="genres")
