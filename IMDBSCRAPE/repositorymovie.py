class RepositoryMovie:
    def __init__(self, id, title_type, content_rating, countries, genres, related_movies, name, year, votes, runtime, actors,directors, rating_distribution, arithmetic_value, std, country_std, country_votes, country_codes, imdb_rating):
        self.id = id
        self.title_type = title_type
        self.content_rating = content_rating
        self.countries = countries
        self.genres = genres
        self.related_movies = related_movies
        self.name = name
        self.year = year
        self.votes = votes
        self.runtime = runtime
        self.actors= actors
        self.directors=directors
        self.rating_distribution = rating_distribution
        self.arithmetic_value = arithmetic_value
        self.std = std
        self.country_std = country_std
        self.country_votes = country_votes
        self.country_codes = country_codes
        self.imdb_rating = imdb_rating



    def __repr__(self):
        return f"Movie({self.name}, {self.year})"