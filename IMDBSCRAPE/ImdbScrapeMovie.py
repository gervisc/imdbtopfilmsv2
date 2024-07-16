class Movied:
    def __init__(self, movie_id, movie_name, year, num_ratings, rating_value, director, stars):
        self.movie_id = movie_id
        self.movie_name = movie_name
        self.year = year
        self.num_ratings = num_ratings
        self.rating_value = rating_value
        self.director = director
        self.stars = stars

    def __repr__(self):
        return (f"MovieInfo(movie_id={self.movie_id}, movie_name='{self.movie_name}', "
                f"year={self.year}, num_ratings={self.num_ratings}, rating_value={self.rating_value}, "
                f"director='{self.director}', stars={self.stars})")