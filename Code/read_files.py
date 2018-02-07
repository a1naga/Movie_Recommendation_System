import pandas as pd

def collect_movie_data():
    url_df = pd.read_csv("/Users/aarthi/COEN499/Recommendation_system/ml-latest-small/links_with_url.csv")
    movie_df = pd.read_csv("/Users/aarthi/COEN499/Recommendation_system/ml-latest-small/movies.csv", sep=',', encoding="latin-1")
    ratings_df = pd.read_csv("/Users/aarthi/COEN499/Recommendation_system/ml-latest-small/ratings.csv")
    merged_movie_df = url_df.merge(movie_df, on='movieId')
    return merged_movie_df, movie_df, url_df, ratings_df